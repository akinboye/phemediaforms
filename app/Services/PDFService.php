<?php

namespace App\Services;

use App\Models\FormSubmission;
use Barryvdh\DomPDF\Facade\Pdf;
use Illuminate\Support\Str;

class PDFService
{
    /**
     * Generate PDF for form submission
     */
    public function generatePDF(FormSubmission $submission)
    {
        $filename = "form_{$submission->form_type}_{$submission->id}.pdf";
        $path = storage_path("app/uploads/pdfs/{$filename}");

        // Ensure directory exists
        \File::ensureDirectoryExists(storage_path("app/uploads/pdfs"));

        try {
            // Create PDF from submission data
            $pdf = Pdf::loadView('pdfs.form', [
                'submission' => $submission,
                'data' => $submission->submitted_data
            ]);

            // Save PDF
            $pdf->save($path);

            return $filename;
        } catch (\Exception $e) {
            \Log::error("PDF generation failed: " . $e->getMessage());
            throw new \Exception("Failed to generate PDF: " . $e->getMessage());
        }
    }

    /**
     * Add approval stamp to PDF
     */
    public function addApprovalStamp(FormSubmission $submission)
    {
        $filename = "stamp_{$submission->id}.pdf";
        $path = storage_path("app/uploads/stamps/{$filename}");

        // Ensure directory exists
        \File::ensureDirectoryExists(storage_path("app/uploads/stamps"));

        try {
            // Create stamped PDF
            $pdf = Pdf::loadView('pdfs.stamp', [
                'submission' => $submission,
                'approver' => $submission->adminApprover ?? $submission->superadminApprover,
                'approver_position' => $submission->approver_position,
                'approved_at' => $submission->approved_at
            ]);

            $pdf->save($path);

            return $filename;
        } catch (\Exception $e) {
            \Log::error("Stamp PDF generation failed: " . $e->getMessage());
            throw new \Exception("Failed to add stamp: " . $e->getMessage());
        }
    }

    /**
     * Generate final PDF with signature for service agreement
     */
    public function generateFinalPDF(FormSubmission $submission)
    {
        $filename = "final_{$submission->form_type}_{$submission->id}.pdf";
        $path = storage_path("app/uploads/pdfs/{$filename}");

        // Ensure directory exists
        \File::ensureDirectoryExists(storage_path("app/uploads/pdfs"));

        try {
            // Create final PDF with signature
            $pdf = Pdf::loadView('pdfs.form-with-signature', [
                'submission' => $submission,
                'data' => $submission->submitted_data,
                'signature' => $submission->client_signature_data,
                'signed_at' => $submission->client_acceptance_completed_at
            ]);

            $pdf->save($path);

            return $filename;
        } catch (\Exception $e) {
            \Log::error("Final PDF generation failed: " . $e->getMessage());
            throw new \Exception("Failed to generate final PDF: " . $e->getMessage());
        }
    }

    /**
     * Download PDF file
     */
    public function downloadPDF($filename)
    {
        $path = storage_path("app/uploads/pdfs/{$filename}");

        if (!\File::exists($path)) {
            throw new \Exception("PDF file not found");
        }

        return \response()->download($path);
    }

    /**
     * Delete PDF file
     */
    public function deletePDF($filename)
    {
        $path = storage_path("app/uploads/pdfs/{$filename}");

        if (\File::exists($path)) {
            \File::delete($path);
        }
    }
}
