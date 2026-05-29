# Additional Blade Views - Template Skeletons

This document provides template skeletons for the remaining views needed to complete the Laravel application.

## Admin Submissions List
**Path:** `resources/views/admin/submissions.blade.php`

```blade
@extends('base')
@section('title', 'Form Submissions')
@section('content')
<div class="max-w-7xl mx-auto">
    <h2 class="text-3xl font-bold mb-6">Form Submissions</h2>
    
    <div class="card">
        <table class="w-full">
            <thead>
                <tr class="bg-gray-100 border-b">
                    <th class="px-6 py-3 text-left">ID</th>
                    <th class="px-6 py-3 text-left">Form Type</th>
                    <th class="px-6 py-3 text-left">Email</th>
                    <th class="px-6 py-3 text-left">Status</th>
                    <th class="px-6 py-3 text-left">Submitted</th>
                    <th class="px-6 py-3 text-left">Action</th>
                </tr>
            </thead>
            <tbody>
                @forelse($submissions as $submission)
                    <tr class="border-b hover:bg-gray-50">
                        <td class="px-6 py-3">#{{ $submission->id }}</td>
                        <td class="px-6 py-3">{{ $submission->form_type_display }}</td>
                        <td class="px-6 py-3">{{ $submission->user_email }}</td>
                        <td class="px-6 py-3">
                            <span class="px-3 py-1 rounded-full text-xs font-semibold bg-{{ $submission->status_color }}-100 text-{{ $submission->status_color }}-800">
                                {{ ucfirst(str_replace('_', ' ', $submission->status)) }}
                            </span>
                        </td>
                        <td class="px-6 py-3">{{ $submission->submitted_at->format('M d, Y') }}</td>
                        <td class="px-6 py-3">
                            <a href="{{ route('admin.submission.view', $submission->id) }}" class="text-blue-600 hover:underline">View</a>
                        </td>
                    </tr>
                @empty
                    <tr>
                        <td colspan="6" class="px-6 py-3 text-center text-gray-600">No submissions found</td>
                    </tr>
                @endforelse
            </tbody>
        </table>
    </div>

    @if($submissions->hasPages())
        <div class="mt-6">{{ $submissions->links() }}</div>
    @endif
</div>
@endsection
```

## Admin Submission Detail
**Path:** `resources/views/admin/submission-detail.blade.php`

```blade
@extends('base')
@section('title', 'Submission #' . $submission->id)
@section('content')
<div class="max-w-4xl mx-auto">
    <a href="{{ route('admin.submissions') }}" class="text-blue-600 hover:underline mb-6">&larr; Back to Submissions</a>
    
    <div class="card">
        <div class="flex justify-between items-start mb-6">
            <h2 class="text-3xl font-bold">Submission #{{ $submission->id }}</h2>
            <span class="px-4 py-2 rounded-full font-semibold bg-{{ $submission->status_color }}-100 text-{{ $submission->status_color }}-800">
                {{ ucfirst(str_replace('_', ' ', $submission->status)) }}
            </span>
        </div>

        <div class="grid grid-cols-2 gap-6 mb-8 pb-8 border-b">
            <div>
                <p class="text-gray-600 text-sm">Form Type</p>
                <p class="font-semibold text-lg">{{ $submission->form_type_display }}</p>
            </div>
            <div>
                <p class="text-gray-600 text-sm">Submitted By</p>
                <p class="font-semibold">{{ $submission->user_email }}</p>
            </div>
            <div>
                <p class="text-gray-600 text-sm">Submitted At</p>
                <p class="font-semibold">{{ $submission->submitted_at->format('M d, Y H:i') }}</p>
            </div>
            <div>
                <p class="text-gray-600 text-sm">IP Address</p>
                <p class="font-semibold">{{ $submission->ip_address }}</p>
            </div>
        </div>

        <h3 class="text-xl font-bold mb-4">Form Data</h3>
        <div class="bg-gray-50 p-6 rounded-lg mb-8">
            @foreach($submission->submitted_data as $key => $value)
                <div class="mb-4">
                    <p class="text-gray-600 text-sm">{{ ucwords(str_replace('_', ' ', $key)) }}</p>
                    <p class="font-semibold">{{ is_array($value) ? json_encode($value) : $value }}</p>
                </div>
            @endforeach
        </div>

        @if($submission->status === 'pending_approval')
            <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6">
                <h4 class="font-bold mb-4">Approve or Reject</h4>
                <div class="grid grid-cols-2 gap-6">
                    <form method="POST" action="{{ route('admin.submission.approve', $submission->id) }}" class="space-y-4">
                        @csrf
                        <input type="text" name="approver_position" placeholder="Your Position" required>
                        <button type="submit" class="btn-primary w-full">✓ Approve</button>
                    </form>
                    <form method="POST" action="{{ route('admin.submission.reject', $submission->id) }}" class="space-y-4">
                        @csrf
                        <input type="text" name="rejection_reason" placeholder="Rejection Reason" required>
                        <button type="submit" class="btn-danger w-full">✗ Reject</button>
                    </form>
                </div>
            </div>
        @endif

        @if($submission->approved_at)
            <div class="bg-green-50 border border-green-200 rounded-lg p-6">
                <h4 class="font-bold mb-4">Approval Details</h4>
                <p class="text-gray-700">
                    Approved by <strong>{{ $submission->adminApprover->full_name ?? 'SuperAdmin' }}</strong><br>
                    Position: {{ $submission->approver_position }}<br>
                    Date: {{ $submission->approved_at->format('M d, Y H:i') }}
                </p>
            </div>
        @endif
    </div>
</div>
@endsection
```

## Admin Notifications Management
**Path:** `resources/views/admin/notifications.blade.php`

```blade
@extends('base')
@section('title', 'Notification Email Settings')
@section('content')
<div class="max-w-4xl mx-auto">
    <h2 class="text-3xl font-bold mb-6">Notification Email Settings</h2>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="card">
            <form method="POST" action="{{ route('admin.notification.add') }}" class="space-y-4">
                @csrf
                <h3 class="font-bold text-lg mb-4">Add Email Address</h3>
                <input type="email" name="email" placeholder="Email address" required>
                <select name="form_type" required>
                    <option value="">Select Form Type</option>
                    <option value="all">All Forms</option>
                    <option value="backgroundcheck">Background Check</option>
                    <option value="serviceagreement">Service Agreement</option>
                </select>
                <button type="submit" class="btn-primary w-full">Add Email</button>
            </form>
        </div>

        <div class="card md:col-span-2">
            <h3 class="font-bold text-lg mb-4">Current Emails</h3>
            @forelse($notifications as $notif)
                <div class="flex justify-between items-center mb-3 pb-3 border-b">
                    <div>
                        <p class="font-semibold">{{ $notif->email }}</p>
                        <p class="text-sm text-gray-600">{{ $notif->form_type }}</p>
                    </div>
                    <form method="POST" action="{{ route('admin.notification.delete', $notif->id) }}" class="inline">
                        @csrf
                        <button type="submit" class="text-red-600 hover:text-red-800">Delete</button>
                    </form>
                </div>
            @empty
                <p class="text-gray-600">No notification emails configured</p>
            @endforelse
        </div>
    </div>
</div>
@endsection
```

## SuperAdmin - Admins List
**Path:** `resources/views/superadmin/admins.blade.php`

```blade
@extends('base')
@section('title', 'Admin Management')
@section('content')
<div class="max-w-7xl mx-auto">
    <div class="flex justify-between items-center mb-6">
        <h2 class="text-3xl font-bold">Admin Management</h2>
        <a href="{{ route('superadmin.admin.create') }}" class="btn-primary">+ Create Admin</a>
    </div>

    <div class="card">
        <table class="w-full">
            <thead>
                <tr class="bg-gray-100 border-b">
                    <th class="px-6 py-3 text-left">Name</th>
                    <th class="px-6 py-3 text-left">Username</th>
                    <th class="px-6 py-3 text-left">Email</th>
                    <th class="px-6 py-3 text-left">Status</th>
                    <th class="px-6 py-3 text-left">Created</th>
                    <th class="px-6 py-3 text-left">Actions</th>
                </tr>
            </thead>
            <tbody>
                @forelse($admins as $admin)
                    <tr class="border-b hover:bg-gray-50">
                        <td class="px-6 py-3">{{ $admin->full_name }}</td>
                        <td class="px-6 py-3">{{ $admin->username }}</td>
                        <td class="px-6 py-3">{{ $admin->email }}</td>
                        <td class="px-6 py-3">
                            <span class="px-3 py-1 rounded-full text-xs font-semibold {{ $admin->is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800' }}">
                                {{ $admin->is_active ? 'Active' : 'Inactive' }}
                            </span>
                        </td>
                        <td class="px-6 py-3">{{ $admin->created_at->format('M d, Y') }}</td>
                        <td class="px-6 py-3 space-x-2">
                            <a href="{{ route('superadmin.admin.edit', $admin->id) }}" class="text-blue-600 hover:underline">Edit</a>
                            <form method="POST" action="{{ route('superadmin.admin.toggle', $admin->id) }}" class="inline">
                                @csrf
                                <button type="submit" class="text-purple-600 hover:underline">
                                    {{ $admin->is_active ? 'Deactivate' : 'Activate' }}
                                </button>
                            </form>
                        </td>
                    </tr>
                @empty
                    <tr>
                        <td colspan="6" class="px-6 py-3 text-center text-gray-600">No admins found</td>
                    </tr>
                @endforelse
            </tbody>
        </table>
    </div>

    @if($admins->hasPages())
        <div class="mt-6">{{ $admins->links() }}</div>
    @endif
</div>
@endsection
```

## SuperAdmin - Create Admin
**Path:** `resources/views/superadmin/admin-create.blade.php`

```blade
@extends('base')
@section('title', 'Create New Admin')
@section('content')
<div class="max-w-2xl mx-auto">
    <a href="{{ route('superadmin.admins') }}" class="text-blue-600 hover:underline mb-6">&larr; Back to Admins</a>

    <div class="card">
        <h2 class="text-3xl font-bold mb-6">Create New Admin</h2>

        <form method="POST" action="{{ route('superadmin.admin.store') }}" class="space-y-6">
            @csrf

            <div class="grid grid-cols-2 gap-6">
                <div>
                    <label class="block text-gray-700 font-semibold mb-2">First Name</label>
                    <input type="text" name="first_name" required class="w-full px-4 py-2 border rounded-lg" value="{{ old('first_name') }}">
                    @error('first_name') <span class="text-red-600">{{ $message }}</span> @enderror
                </div>

                <div>
                    <label class="block text-gray-700 font-semibold mb-2">Last Name</label>
                    <input type="text" name="last_name" required class="w-full px-4 py-2 border rounded-lg" value="{{ old('last_name') }}">
                    @error('last_name') <span class="text-red-600">{{ $message }}</span> @enderror
                </div>
            </div>

            <div class="grid grid-cols-2 gap-6">
                <div>
                    <label class="block text-gray-700 font-semibold mb-2">Email</label>
                    <input type="email" name="email" required class="w-full px-4 py-2 border rounded-lg" value="{{ old('email') }}">
                    @error('email') <span class="text-red-600">{{ $message }}</span> @enderror
                </div>

                <div>
                    <label class="block text-gray-700 font-semibold mb-2">Phone</label>
                    <input type="tel" name="phone_number" required class="w-full px-4 py-2 border rounded-lg" value="{{ old('phone_number') }}">
                    @error('phone_number') <span class="text-red-600">{{ $message }}</span> @enderror
                </div>
            </div>

            <div class="grid grid-cols-2 gap-6">
                <div>
                    <label class="block text-gray-700 font-semibold mb-2">Username</label>
                    <input type="text" name="username" required class="w-full px-4 py-2 border rounded-lg" value="{{ old('username') }}">
                    @error('username') <span class="text-red-600">{{ $message }}</span> @enderror
                </div>

                <div>
                    <label class="block text-gray-700 font-semibold mb-2">Password</label>
                    <input type="password" name="password" required class="w-full px-4 py-2 border rounded-lg">
                    @error('password') <span class="text-red-600">{{ $message }}</span> @enderror
                </div>
            </div>

            <div class="flex gap-4 mt-8">
                <button type="submit" class="btn-primary flex-1">Create Admin</button>
                <a href="{{ route('superadmin.admins') }}" class="btn-secondary flex-1 text-center">Cancel</a>
            </div>
        </form>
    </div>
</div>
@endsection
```

## PDF Form Template
**Path:** `resources/views/pdfs/form.blade.php`

```blade
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Form Submission</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .field { margin-bottom: 15px; }
        .label { font-weight: bold; color: #555; }
        .value { margin-top: 5px; color: #333; }
        .timestamp { color: #999; font-size: 12px; margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; }
    </style>
</head>
<body>
    <h1>Form Submission Report</h1>
    
    <div class="field">
        <div class="label">Form Type:</div>
        <div class="value">{{ $submission->form_type_display }}</div>
    </div>

    <div class="field">
        <div class="label">Submission ID:</div>
        <div class="value">#{{ $submission->id }}</div>
    </div>

    <h2>Form Data</h2>
    @foreach($data as $key => $value)
        <div class="field">
            <div class="label">{{ ucwords(str_replace('_', ' ', $key)) }}:</div>
            <div class="value">{{ is_array($value) ? json_encode($value) : $value }}</div>
        </div>
    @endforeach

    <div class="timestamp">
        Generated: {{ now()->format('M d, Y H:i:s') }}
    </div>
</body>
</html>
```

## Error Pages
**Path:** `resources/views/errors/404.blade.php`

```blade
@extends('base')
@section('title', '404 - Page Not Found')
@section('content')
<div class="flex justify-center items-center min-h-96">
    <div class="card text-center">
        <h1 class="text-6xl font-bold text-gray-400 mb-4">404</h1>
        <h2 class="text-2xl font-bold mb-4">Page Not Found</h2>
        <p class="text-gray-600 mb-6">The page you're looking for doesn't exist.</p>
        <a href="{{ route('home') }}" class="btn-primary">Go Back Home</a>
    </div>
</div>
@endsection
```

---

## Instructions

1. Create each file in the specified `resources/views/` path
2. Customize styling as needed to match your branding
3. Update form field names to match your actual form structure
4. Test each view in your development environment
5. Adjust color schemes and spacing to preference

**Note:** These are template skeletons. Customize the content and styling to fully match your application's needs.
