<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\Hash;

class SuperAdmin extends Model
{
    protected $table = 'superadmins';
    protected $fillable = ['username', 'email', 'password'];
    protected $hidden = ['password'];

    /**
     * Hash password before storing
     */
    public function setPasswordAttribute($value)
    {
        $this->attributes['password'] = Hash::make($value);
    }

    /**
     * Relationship: admins created by this superadmin
     */
    public function admins()
    {
        return $this->hasMany(Admin::class, 'created_by');
    }

    /**
     * Relationship: notifications added by this superadmin
     */
    public function notifications()
    {
        return $this->hasMany(NotificationEmail::class, 'added_by_superadmin');
    }

    /**
     * Relationship: form submissions approved by this superadmin
     */
    public function approvedSubmissions()
    {
        return $this->hasMany(FormSubmission::class, 'approved_by_superadmin');
    }
}
