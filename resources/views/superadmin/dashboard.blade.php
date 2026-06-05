@extends('base')

@section('title', 'SuperAdmin Dashboard')

@section('content')
<div class="max-w-7xl mx-auto">
    <h2 class="text-4xl font-bold mb-8">SuperAdmin Dashboard</h2>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="card bg-purple-50 border-l-4 border-purple-600">
            <div class="flex justify-between items-start">
                <div>
                    <p class="text-gray-600 text-sm mb-2">Total Admins</p>
                    <h3 class="text-3xl font-bold text-purple-600">{{ $totalAdmins }}</h3>
                </div>
                <i class="fas fa-users text-purple-600 text-3xl opacity-50"></i>
            </div>
        </div>

        <div class="card bg-green-50 border-l-4 border-green-600">
            <div class="flex justify-between items-start">
                <div>
                    <p class="text-gray-600 text-sm mb-2">Active Admins</p>
                    <h3 class="text-3xl font-bold text-green-600">{{ $activeAdmins }}</h3>
                </div>
                <i class="fas fa-user-check text-green-600 text-3xl opacity-50"></i>
            </div>
        </div>

        <div class="card bg-blue-50 border-l-4 border-blue-600">
            <div class="flex justify-between items-start">
                <div>
                    <p class="text-gray-600 text-sm mb-2">Total Submissions</p>
                    <h3 class="text-3xl font-bold text-blue-600">{{ $totalSubmissions }}</h3>
                </div>
                <i class="fas fa-file-alt text-blue-600 text-3xl opacity-50"></i>
            </div>
        </div>

        <div class="card bg-yellow-50 border-l-4 border-yellow-600">
            <div class="flex justify-between items-start">
                <div>
                    <p class="text-gray-600 text-sm mb-2">Pending Approval</p>
                    <h3 class="text-3xl font-bold text-yellow-600">{{ $pendingApprovals }}</h3>
                </div>
                <i class="fas fa-hourglass-half text-yellow-600 text-3xl opacity-50"></i>
            </div>
        </div>
    </div>

    <!-- Quick Actions -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="card">
            <h3 class="text-lg font-semibold mb-4"><i class="fas fa-user-plus text-purple-600"></i> Admin Management</h3>
            <p class="text-gray-600 mb-4 text-sm">Manage admin accounts</p>
            <a href="{{ route('superadmin.admins') }}" class="btn-primary w-full text-center text-sm">Manage</a>
        </div>

        <div class="card">
            <h3 class="text-lg font-semibold mb-4"><i class="fas fa-list text-blue-600"></i> Submissions</h3>
            <p class="text-gray-600 mb-4 text-sm">View all submissions</p>
            <a href="{{ route('superadmin.submissions') }}" class="btn-primary w-full text-center text-sm">View</a>
        </div>

        <div class="card">
            <h3 class="text-lg font-semibold mb-4"><i class="fas fa-envelope text-green-600"></i> Notifications</h3>
            <p class="text-gray-600 mb-4 text-sm">Email settings</p>
            <a href="{{ route('superadmin.notifications') }}" class="btn-primary w-full text-center text-sm">Configure</a>
        </div>

        <div class="card">
            <h3 class="text-lg font-semibold mb-4"><i class="fas fa-user text-gray-600"></i> Profile</h3>
            <p class="text-gray-600 mb-2 text-sm"><strong>{{ $superadmin->username }}</strong></p>
            <p class="text-gray-600 text-sm">{{ $superadmin->email }}</p>
        </div>
    </div>
</div>
@endsection
