<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Session;

class CheckSuperAdminAuth
{
    /**
     * Handle an incoming request.
     */
    public function handle(Request $request, Closure $next)
    {
        if (!Session::has('superadmin_id') || Session::get('user_type') !== 'superadmin') {
            return redirect()->route('admin.login')->with('error', 'SuperAdmin access required');
        }

        return $next($request);
    }
}
