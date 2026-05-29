<?php

namespace App\Http\Controllers;

use App\Models\Admin;
use App\Models\SuperAdmin;
use App\Models\FormSubmission;
use App\Models\NotificationEmail;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Session;

class SuperAdminController extends Controller
{
    /**
     * SuperAdmin dashboard
     */
    public function dashboard()
    {
        $superadmin = SuperAdmin::find(Session::get('superadmin_id'));
        $totalAdmins = Admin::count();
        $activeAdmins = Admin::where('is_active', true)->count();
        $totalSubmissions = FormSubmission::count();
        $pendingApprovals = FormSubmission::where('status', 'pending_approval')->count();

        return view('superadmin.dashboard', compact(
            'superadmin',
            'totalAdmins',
            'activeAdmins',
            'totalSubmissions',
            'pendingApprovals'
        ));
    }

    /**
     * View all admins
     */
    public function admins()
    {
        $admins = Admin::orderBy('created_at', 'desc')->paginate(20);
        return view('superadmin.admins', compact('admins'));
    }

    /**
     * Show create admin form
     */
    public function createAdmin()
    {
        return view('superadmin.admin-create');
    }

    /**
     * Store new admin
     */
    public function storeAdmin(Request $request)
    {
        $validated = $request->validate([
            'first_name' => 'required|string',
            'last_name' => 'required|string',
            'email' => 'required|email|unique:admins',
            'phone_number' => 'required|string',
            'username' => 'required|string|unique:admins',
            'password' => 'required|string|min:6'
        ]);

        $superadmin = SuperAdmin::find(Session::get('superadmin_id'));

        Admin::create([
            'first_name' => $validated['first_name'],
            'last_name' => $validated['last_name'],
            'email' => $validated['email'],
            'phone_number' => $validated['phone_number'],
            'username' => $validated['username'],
            'password' => $validated['password'],
            'is_active' => true,
            'created_by' => $superadmin->id
        ]);

        return redirect()->route('superadmin.admins')
            ->with('success', "Admin '{$validated['username']}' created successfully!");
    }

    /**
     * Show edit admin form
     */
    public function editAdmin($id)
    {
        $admin = Admin::findOrFail($id);
        return view('superadmin.admin-edit', compact('admin'));
    }

    /**
     * Update admin
     */
    public function updateAdmin(Request $request, $id)
    {
        $admin = Admin::findOrFail($id);

        $validated = $request->validate([
            'first_name' => 'required|string',
            'last_name' => 'required|string',
            'email' => 'required|email|unique:admins,email,' . $id,
            'phone_number' => 'required|string'
        ]);

        $admin->update($validated);

        return redirect()->route('superadmin.admins')
            ->with('success', 'Admin updated successfully!');
    }

    /**
     * Toggle admin active/inactive
     */
    public function toggleAdmin($id)
    {
        $admin = Admin::findOrFail($id);
        $admin->update(['is_active' => !$admin->is_active]);

        $status = $admin->is_active ? 'activated' : 'deactivated';
        return redirect()->back()->with('success', "Admin {$status} successfully!");
    }

    /**
     * View all submissions
     */
    public function submissions()
    {
        $submissions = FormSubmission::orderBy('submitted_at', 'desc')->paginate(20);
        return view('superadmin.submissions', compact('submissions'));
    }

    /**
     * View single submission
     */
    public function viewSubmission($id)
    {
        $submission = FormSubmission::findOrFail($id);
        return view('superadmin.submission-detail', compact('submission'));
    }

    /**
     * View notification emails
     */
    public function notifications()
    {
        $superadmin = SuperAdmin::find(Session::get('superadmin_id'));
        $notifications = NotificationEmail::orderBy('form_type')->get();

        return view('superadmin.notifications', compact('superadmin', 'notifications'));
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

        $superadmin = SuperAdmin::find(Session::get('superadmin_id'));

        NotificationEmail::create([
            'email' => $request->input('email'),
            'form_type' => $request->input('form_type'),
            'is_active' => true,
            'added_by_superadmin' => $superadmin->id
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
