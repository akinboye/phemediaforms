<?php

namespace App\Services;

use App\Models\FormSubmission;
use App\Models\NotificationEmail;
use Illuminate\Support\Facades\Mail;

class FormService
{
    /**
     * Get form structure/fields for a specific form type
     */
    public function getFormStructure($formType)
    {
        $structures = [
            'backgroundcheck' => [
                'fullname' => ['type' => 'text', 'label' => 'Full Name', 'required' => true],
                'email' => ['type' => 'email', 'label' => 'Email Address', 'required' => true],
                'phone' => ['type' => 'tel', 'label' => 'Phone Number', 'required' => true],
                'date_of_birth' => ['type' => 'date', 'label' => 'Date of Birth', 'required' => true],
                'nin' => ['type' => 'text', 'label' => 'NIN', 'required' => true],
                'nin_file' => ['type' => 'file', 'label' => 'NIN Document', 'required' => true]
            ],
            'clientengagement' => [
                'company_name' => ['type' => 'text', 'label' => 'Company Name', 'required' => true],
                'contact_person' => ['type' => 'text', 'label' => 'Contact Person', 'required' => true],
                'email' => ['type' => 'email', 'label' => 'Email', 'required' => true],
                'phone' => ['type' => 'tel', 'label' => 'Phone', 'required' => true],
                'engagement_type' => ['type' => 'select', 'label' => 'Engagement Type', 'required' => true],
                'description' => ['type' => 'textarea', 'label' => 'Description', 'required' => false]
            ],
            'declarationbyemployee' => [
                'employee_name' => ['type' => 'text', 'label' => 'Employee Name', 'required' => true],
                'employee_id' => ['type' => 'text', 'label' => 'Employee ID', 'required' => true],
                'email' => ['type' => 'email', 'label' => 'Email', 'required' => true],
                'department' => ['type' => 'text', 'label' => 'Department', 'required' => true],
                'declaration_text' => ['type' => 'textarea', 'label' => 'Declaration', 'required' => true]
            ],
            'guarantorundertaking' => [
                'guarantor_name' => ['type' => 'text', 'label' => 'Guarantor Name', 'required' => true],
                'email' => ['type' => 'email', 'label' => 'Email', 'required' => true],
                'phone' => ['type' => 'tel', 'label' => 'Phone', 'required' => true],
                'principal' => ['type' => 'text', 'label' => 'Principal', 'required' => true],
                'undertaking_amount' => ['type' => 'number', 'label' => 'Undertaking Amount', 'required' => true]
            ],
            'serviceagreement' => [
                'client_name' => ['type' => 'text', 'label' => 'Client Name', 'required' => true],
                'email' => ['type' => 'email', 'label' => 'Email', 'required' => true],
                'phone' => ['type' => 'tel', 'label' => 'Phone', 'required' => true],
                'service_type' => ['type' => 'text', 'label' => 'Service Type', 'required' => true],
                'service_duration' => ['type' => 'text', 'label' => 'Duration', 'required' => true],
                'amount' => ['type' => 'number', 'label' => 'Amount', 'required' => true]
            ],
            'trackingagreement' => [
                'participant_name' => ['type' => 'text', 'label' => 'Participant Name', 'required' => true],
                'email' => ['type' => 'email', 'label' => 'Email', 'required' => true],
                'tracking_id' => ['type' => 'text', 'label' => 'Tracking ID', 'required' => true],
                'start_date' => ['type' => 'date', 'label' => 'Start Date', 'required' => true],
                'end_date' => ['type' => 'date', 'label' => 'End Date', 'required' => true]
            ],
            'oilgasservicerequest' => [
                'company_name' => ['type' => 'text', 'label' => 'Company Name', 'required' => true],
                'email' => ['type' => 'email', 'label' => 'Email', 'required' => true],
                'phone' => ['type' => 'tel', 'label' => 'Phone', 'required' => true],
                'service_requested' => ['type' => 'textarea', 'label' => 'Service Requested', 'required' => true],
                'preferred_date' => ['type' => 'date', 'label' => 'Preferred Date', 'required' => true]
            ]
        ];

        return $structures[$formType] ?? [];
    }

    /**
     * Get validation rules for a form type
     */
    public function getValidationRules($formType)
    {
        $rules = [
            'form_type' => 'required|string',
            'email' => 'required|email'
        ];

        // Add type-specific rules
        if ($formType === 'backgroundcheck') {
            $rules['fullname'] = 'required|string';
            $rules['phone'] = 'required|string';
            $rules['date_of_birth'] = 'required|date';
            $rules['nin'] = 'required|string';
            $rules['nin_file'] = 'required|file|mimes:pdf,jpg,jpeg,png';
        } elseif ($formType === 'clientengagement') {
            $rules['company_name'] = 'required|string';
            $rules['contact_person'] = 'required|string';
            $rules['phone'] = 'required|string';
            $rules['engagement_type'] = 'required|string';
        } elseif ($formType === 'serviceagreement') {
            $rules['client_name'] = 'required|string';
            $rules['phone'] = 'required|string';
            $rules['service_type'] = 'required|string';
            $rules['service_duration'] = 'required|string';
            $rules['amount'] = 'required|numeric|min:0';
        }
        // Add more rules for other form types as needed

        return $rules;
    }

    /**
     * Send notification emails to configured recipients
     */
    public function sendNotificationEmails(FormSubmission $submission)
    {
        $emails = NotificationEmail::getEmailsForForm($submission->form_type);

        foreach ($emails as $email) {
            try {
                Mail::raw(
                    "New form submission received.\n\n" .
                    "Form Type: {$submission->form_type_display}\n" .
                    "Submitted By: {$submission->user_email}\n" .
                    "Submitted At: {$submission->submitted_at}\n" .
                    "Submission ID: {$submission->id}",
                    function ($message) use ($email, $submission) {
                        $message->to($email)
                            ->subject("New Form Submission - {$submission->form_type_display}");
                    }
                );
            } catch (\Exception $e) {
                // Log email error but don't fail the submission
                \Log::error("Failed to send notification email: " . $e->getMessage());
            }
        }
    }
}
