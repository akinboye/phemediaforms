<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class NotificationEmail extends Model
{
    protected $table = 'notification_emails';
    protected $fillable = [
        'email',
        'form_type',
        'is_active',
        'added_by_admin',
        'added_by_superadmin'
    ];

    protected $casts = [
        'is_active' => 'boolean'
    ];

    /**
     * Relationship: admin who added this email
     */
    public function addedByAdmin()
    {
        return $this->belongsTo(Admin::class, 'added_by_admin');
    }

    /**
     * Relationship: superadmin who added this email
     */
    public function addedBySuperadmin()
    {
        return $this->belongsTo(SuperAdmin::class, 'added_by_superadmin');
    }

    /**
     * Get emails for a specific form type
     */
    public static function getEmailsForForm($formType)
    {
        return self::where('is_active', true)
            ->where(function ($query) use ($formType) {
                $query->where('form_type', 'all')
                    ->orWhere('form_type', $formType);
            })
            ->pluck('email')
            ->toArray();
    }
}
