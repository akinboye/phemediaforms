<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Session;

class CheckAdminAuth
{
    /**
     * Handle an incoming request.
     */
    public function handle(Request $request, Closure $next)
    {
        if (!Session::has('admin_id') || Session::get('user_type') !== 'admin') {
            return redirect()->route('admin.login')->with('error', 'Please log in first');
        }

        return $next($request);
    }
}
