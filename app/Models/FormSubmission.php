<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class FormSubmission extends Model
{
    use SoftDeletes;

    protected $table = 'form_submissions';
    protected $fillable = [
        'form_type',
        'submitted_data',
        'user_email',
        'ip_address',
        'user_agent',
        'status',
        'approved_by_admin',
        'approved_by_superadmin',
        'approved_at',
        'approver_position',
        'rejection_reason',
        'pdf_filename',
        'stamp_filename',
        'photo_filename',
        'nin_filename',
        'client_acceptance_token',
        'client_acceptance_link',
        'client_acceptance_completed',
        'client_acceptance_completed_at',
        'client_signature_data',
        'final_pdf_filename'
    ];

    protected $casts = [
        'submitted_data' => 'json',
        'approved_at' => 'datetime',
        'client_acceptance_completed_at' => 'datetime'
    ];

    /**
     * Relationship: admin approver
     */
    public function adminApprover()
    {
        return $this->belongsTo(Admin::class, 'approved_by_admin');
    }

    /**
     * Relationship: superadmin approver
     */
    public function superadminApprover()
    {
        return $this->belongsTo(SuperAdmin::class, 'approved_by_superadmin');
    }

    /**
     * Get form type display name
     */
    public function getFormTypeDisplayAttribute()
    {
        $formTypes = [
            'backgroundcheck' => 'Background Check',
            'clientengagement' => 'Client Engagement',
            'declarationbyemployee' => 'Employee Declaration',
            'guarantorundertaking' => 'Guarantor Undertaking',
            'serviceagreement' => 'Service Agreement',
            'trackingagreement' => 'Tracking Agreement',
            'oilgasservicerequest' => 'Oil & Gas Service Request'
        ];

        return $formTypes[$this->form_type] ?? $this->form_type;
    }

    /**
     * Get status badge color
     */
    public function getStatusColorAttribute()
    {
        $colors = [
            'submitted' => 'blue',
            'pending_approval' => 'yellow',
            'approved' => 'green',
            'rejected' => 'red'
        ];

        return $colors[$this->status] ?? 'gray';
    }
}
