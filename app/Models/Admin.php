<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\Hash;

class Admin extends Model
{
    protected $table = 'admins';
    protected $fillable = [
        'first_name',
        'last_name',
        'email',
        'phone_number',
        'username',
        'password',
        'is_active',
        'created_by'
    ];
    protected $hidden = ['password'];

    /**
     * Hash password before storing
     */
    public function setPasswordAttribute($value)
    {
        $this->attributes['password'] = Hash::make($value);
    }

    /**
     * Relationship: superadmin who created this admin
     */
    public function creator()
    {
        return $this->belongsTo(SuperAdmin::class, 'created_by');
    }

    /**
     * Relationship: form submissions approved by this admin
     */
    public function approvedSubmissions()
    {
        return $this->hasMany(FormSubmission::class, 'approved_by_admin');
    }

    /**
     * Relationship: notifications added by this admin
     */
    public function notifications()
    {
        return $this->hasMany(NotificationEmail::class, 'added_by_admin');
    }

    /**
     * Get admin full name
     */
    public function getFullNameAttribute()
    {
        return "{$this->first_name} {$this->last_name}";
    }
}
