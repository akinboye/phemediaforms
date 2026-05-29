<?php

namespace App\Http\Controllers;

use App\Models\Admin;
use App\Models\SuperAdmin;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Session;

class AuthController extends Controller
{
    /**
     * Show admin/superadmin login form
     */
    public function showLogin()
    {
        return view('auth.login');
    }

    /**
     * Handle login request
     */
    public function login(Request $request)
    {
        $validated = $request->validate([
            'username' => 'required|string',
            'password' => 'required|string'
        ]);

        // Try SuperAdmin login
        $superadmin = SuperAdmin::where('username', $validated['username'])->first();
        if ($superadmin && Hash::check($validated['password'], $superadmin->password)) {
            Session::put('superadmin_id', $superadmin->id);
            Session::put('user_type', 'superadmin');
            Session::put('user_name', $superadmin->username);
            Session::put('user_email', $superadmin->email);
            
            return redirect()->route('superadmin.dashboard')->with('success', 'SuperAdmin login successful!');
        }

        // Try Admin login
        $admin = Admin::where('username', $validated['username'])
            ->where('is_active', true)
            ->first();
        
        if ($admin && Hash::check($validated['password'], $admin->password)) {
            Session::put('admin_id', $admin->id);
            Session::put('user_type', 'admin');
            Session::put('user_name', $admin->full_name);
            Session::put('user_email', $admin->email);
            
            return redirect()->route('admin.dashboard')->with('success', 'Admin login successful!');
        }

        return back()->withErrors(['credentials' => 'Invalid username or password']);
    }

    /**
     * Handle logout request
     */
    public function logout(Request $request)
    {
        Session::flush();
        return redirect()->route('home')->with('success', 'You have been logged out successfully!');
    }
}
