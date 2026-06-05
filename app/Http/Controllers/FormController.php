<?php

namespace App\Http\Controllers;

use App\Models\FormSubmission;
use App\Models\NotificationEmail;
use App\Services\FormService;
use App\Services\PDFService;
use Illuminate\Http\Request;
use Illuminate\Support\Str;

class FormController extends Controller
{
    protected $formService;
    protected $pdfService;

    public function __construct(FormService $formService, PDFService $pdfService)
    {
        $this->formService = $formService;
        $this->pdfService = $pdfService;
    }

    /**
     * Show home/landing page
     */
    public function index()
    {
        $forms = [
            'backgroundcheck' => 'Background Check',
            'clientengagement' => 'Client Engagement',
            'declarationbyemployee' => 'Employee Declaration',
            'guarantorundertaking' => 'Guarantor Undertaking',
            'serviceagreement' => 'Service Agreement',
            'trackingagreement' => 'Tracking Agreement',
            'oilgasservicerequest' => 'Oil & Gas Service Request'
        ];

        return view('forms.index', compact('forms'));
    }

    /**
     * Show specific form
     */
    public function showForm($form_type)
    {
        $formTypes = [
            'backgroundcheck',
            'clientengagement',
            'declarationbyemployee',
            'guarantorundertaking',
            'serviceagreement',
            'trackingagreement',
            'oilgasservicerequest'
        ];

        if (!in_array($form_type, $formTypes)) {
            abort(404);
        }

        $formData = $this->formService->getFormStructure($form_type);
        return view('forms.form', compact('form_type', 'formData'));
    }

    /**
     * Submit form
     */
    public function submitForm(Request $request)
    {
        $formType = $request->input('form_type');
        
        // Validate form data
        $rules = $this->formService->getValidationRules($formType);
        $validated = $request->validate($rules);

        // Create form submission
        $submission = FormSubmission::create([
            'form_type' => $formType,
            'submitted_data' => $validated,
            'user_email' => $validated['email'] ?? null,
            'ip_address' => $request->ip(),
            'user_agent' => $request->header('User-Agent'),
            'status' => 'pending_approval'
        ]);

        // Generate PDF
        $pdfFilename = $this->pdfService->generatePDF($submission);
        $submission->update(['pdf_filename' => $pdfFilename]);

        // Send notification emails
        $this->formService->sendNotificationEmails($submission);

        // For service agreement, generate signature token
        if ($formType === 'serviceagreement') {
            $token = Str::random(60);
            $submission->update([
                'client_acceptance_token' => $token,
                'client_acceptance_link' => route('form.sign', $token)
            ]);
        }

        return redirect()->route('confirmation')->with([
            'success' => 'Form submitted successfully!',
            'submission_id' => $submission->id
        ]);
    }

    /**
     * Show confirmation page
     */
    public function confirmation()
    {
        return view('forms.confirmation');
    }

    /**
     * Show client signature form (for service agreement)
     */
    public function clientSignForm($token)
    {
        $submission = FormSubmission::where('client_acceptance_token', $token)->first();

        if (!$submission) {
            return view('errors.invalid-token');
        }

        if ($submission->client_acceptance_completed) {
            return view('errors.already-signed', ['submission' => $submission]);
        }

        return view('forms.signature', compact('submission', 'token'));
    }

    /**
     * Save client signature
     */
    public function saveSignature(Request $request, $token)
    {
        $request->validate([
            'signature' => 'required|string'
        ]);

        $submission = FormSubmission::where('client_acceptance_token', $token)->first();

        if (!$submission) {
            return response()->json(['error' => 'Invalid token'], 404);
        }

        $submission->update([
            'client_signature_data' => $request->input('signature'),
            'client_acceptance_completed' => true,
            'client_acceptance_completed_at' => now()
        ]);

        // Generate final PDF with signature
        $finalPdfFilename = $this->pdfService->generateFinalPDF($submission);
        $submission->update(['final_pdf_filename' => $finalPdfFilename]);

        return response()->json(['success' => true, 'message' => 'Signature saved successfully!']);
    }
}
