<?php

namespace App\Http\Controllers;

use App\Models\Admin;
use App\Models\FormSubmission;
use App\Models\NotificationEmail;
use App\Services\PDFService;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Mail;
use Illuminate\Support\Facades\Session;

class AdminController extends Controller
{
    protected $pdfService;

    public function __construct(PDFService $pdfService)
    {
        $this->pdfService = $pdfService;
    }

    /**
     * Admin dashboard
     */
    public function dashboard()
    {
        $admin = Admin::find(Session::get('admin_id'));
        $totalSubmissions = FormSubmission::count();
        $pendingApprovals = FormSubmission::where('status', 'pending_approval')->count();
        $approvedForms = FormSubmission::where('status', 'approved')->count();
        $rejectedForms = FormSubmission::where('status', 'rejected')->count();

        return view('admin.dashboard', compact(
            'admin',
            'totalSubmissions',
            'pendingApprovals',
            'approvedForms',
            'rejectedForms'
        ));
    }

    /**
     * View all submissions
     */
    public function submissions()
    {
        $submissions = FormSubmission::orderBy('submitted_at', 'desc')
            ->paginate(20);

        return view('admin.submissions', compact('submissions'));
    }

    /**
     * View single submission
     */
    public function viewSubmission($id)
    {
        $submission = FormSubmission::findOrFail($id);
        return view('admin.submission-detail', compact('submission'));
    }

    /**
     * Approve submission
     */
    public function approveSubmission(Request $request, $id)
    {
        $request->validate([
            'approver_position' => 'required|string'
        ]);

        $submission = FormSubmission::findOrFail($id);
        $admin = Admin::find(Session::get('admin_id'));

        $submission->update([
            'status' => 'approved',
            'approved_by_admin' => $admin->id,
            'approved_at' => now(),
            'approver_position' => $request->input('approver_position')
        ]);

        // Generate stamp PDF
        $stampFilename = $this->pdfService->addApprovalStamp($submission);
        $submission->update(['stamp_filename' => $stampFilename]);

        // Send approval email
        Mail::raw(
            "Form '{$submission->form_type_display}' has been approved by {$admin->full_name}\n\n" .
            "Submission ID: {$submission->id}\nApproved at: {$submission->approved_at}",
            function ($message) use ($submission) {
                $message->to($submission->user_email)
                    ->subject("Form Approval - {$submission->form_type_display}");
            }
        );

        return redirect()->back()->with('success', 'Form approved successfully!');
    }

    /**
     * Reject submission
     */
    public function rejectSubmission(Request $request, $id)
    {
        $request->validate([
            'rejection_reason' => 'required|string'
        ]);

        $submission = FormSubmission::findOrFail($id);
        $admin = Admin::find(Session::get('admin_id'));

        $submission->update([
            'status' => 'rejected',
            'approved_by_admin' => $admin->id,
            'rejection_reason' => $request->input('rejection_reason')
        ]);

        // Send rejection email
        Mail::raw(
            "Your form submission has been rejected.\n\n" .
            "Reason: {$submission->rejection_reason}\n\n" .
            "Please resubmit your form with the corrections.",
            function ($message) use ($submission) {
                $message->to($submission->user_email)
                    ->subject("Form Rejection - {$submission->form_type_display}");
            }
        );

        return redirect()->back()->with('success', 'Form rejected successfully!');
    }

    /**
     * View notification email settings
     */
    public function notifications()
    {
        $admin = Admin::find(Session::get('admin_id'));
        $notifications = NotificationEmail::orderBy('form_type')->get();

        return view('admin.notifications', compact('admin', 'notifications'));
    }

    /**
     * Add notification email
     */
    public function addNotification(Request $request)
    {
        $request->validate([
            'email' => 'required|email',
            'form_type' => 'required|string'
        ]);

        $admin = Admin::find(Session::get('admin_id'));

        NotificationEmail::create([
            'email' => $request->input('email'),
            'form_type' => $request->input('form_type'),
            'is_active' => true,
            'added_by_admin' => $admin->id
        ]);

        return redirect()->back()->with('success', 'Notification email added successfully!');
    }

    /**
     * Delete notification email
     */
    public function deleteNotification($id)
    {
        $notification = NotificationEmail::findOrFail($id);
        $notification->delete();

        return redirect()->back()->with('success', 'Notification email deleted successfully!');
    }
}
