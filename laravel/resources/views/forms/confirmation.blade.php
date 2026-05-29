@extends('base')

@section('title', 'Form Submission Confirmation')

@section('content')
<div class="flex justify-center items-center min-h-96">
    <div class="card w-full max-w-2xl">
        <div class="text-center">
            <div class="text-6xl text-green-600 mb-4">
                <i class="fas fa-check-circle"></i>
            </div>
            <h2 class="text-3xl font-bold mb-4 text-green-600">Form Submitted Successfully!</h2>
            <p class="text-gray-700 mb-6 text-lg">
                Thank you for submitting your form. We have received your submission and will process it shortly.
            </p>

            <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
                <h3 class="font-semibold mb-4">What's Next?</h3>
                <ul class="text-left text-gray-700 space-y-2">
                    <li><i class="fas fa-envelope text-blue-600"></i> You will receive a confirmation email shortly</li>
                    <li><i class="fas fa-hourglass text-blue-600"></i> An admin will review your submission</li>
                    <li><i class="fas fa-bell text-blue-600"></i> You'll be notified once your form is approved or if changes are needed</li>
                </ul>
            </div>

            <div class="flex gap-4 justify-center">
                <a href="{{ route('home') }}" class="btn-primary">
                    <i class="fas fa-home"></i> Back to Home
                </a>
                <a href="{{ route('admin.login') }}" class="btn-secondary">
                    <i class="fas fa-sign-in-alt"></i> Admin Login
                </a>
            </div>
        </div>
    </div>
</div>
@endsection
