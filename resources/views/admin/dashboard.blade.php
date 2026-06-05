@extends('base')

@section('title', 'Admin Dashboard')

@section('content')
<div class="max-w-7xl mx-auto">
    <h2 class="text-4xl font-bold mb-8">Admin Dashboard</h2>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
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

        <div class="card bg-green-50 border-l-4 border-green-600">
            <div class="flex justify-between items-start">
                <div>
                    <p class="text-gray-600 text-sm mb-2">Approved</p>
                    <h3 class="text-3xl font-bold text-green-600">{{ $approvedForms }}</h3>
                </div>
                <i class="fas fa-check-circle text-green-600 text-3xl opacity-50"></i>
            </div>
        </div>

        <div class="card bg-red-50 border-l-4 border-red-600">
            <div class="flex justify-between items-start">
                <div>
                    <p class="text-gray-600 text-sm mb-2">Rejected</p>
                    <h3 class="text-3xl font-bold text-red-600">{{ $rejectedForms }}</h3>
                </div>
                <i class="fas fa-times-circle text-red-600 text-3xl opacity-50"></i>
            </div>
        </div>
    </div>

    <!-- Quick Actions -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="card">
            <h3 class="text-lg font-semibold mb-4"><i class="fas fa-list text-blue-600"></i> View Submissions</h3>
            <p class="text-gray-600 mb-4">Review all form submissions and their status</p>
            <a href="{{ route('admin.submissions') }}" class="btn-primary w-full text-center">View All</a>
        </div>

        <div class="card">
            <h3 class="text-lg font-semibold mb-4"><i class="fas fa-envelope text-green-600"></i> Notifications</h3>
            <p class="text-gray-600 mb-4">Manage notification email addresses</p>
            <a href="{{ route('admin.notifications') }}" class="btn-primary w-full text-center">Manage</a>
        </div>

        <div class="card">
            <h3 class="text-lg font-semibold mb-4"><i class="fas fa-user text-purple-600"></i> Profile</h3>
            <p class="text-gray-600 mb-2"><strong>{{ $admin->full_name }}</strong></p>
            <p class="text-gray-600 mb-4">{{ $admin->email }}</p>
        </div>
    </div>

    <!-- Recent Activity -->
    <div class="card">
        <h3 class="text-2xl font-bold mb-4">Recent Activity</h3>
        <p class="text-gray-600 text-center py-8">No recent activity to display</p>
    </div>
</div>
@endsection
