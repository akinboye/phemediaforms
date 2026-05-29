@extends('base')

@section('title', 'PHEMEDAA Forms Portal - Home')

@section('content')
<div class="max-w-6xl mx-auto">
    <!-- Hero Section -->
    <div class="bg-gradient-to-r from-blue-600 to-blue-800 text-white rounded-lg shadow-lg p-8 mb-12">
        <h1 class="text-4xl font-bold mb-4">PHEMEDAA Forms Portal</h1>
        <p class="text-xl">Submit and manage your forms efficiently with our secure online portal.</p>
    </div>

    <!-- Forms Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        @foreach($forms as $key => $label)
            <a href="{{ route('form.' . $key) }}" class="card hover:shadow-lg transition transform hover:scale-105">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-xl font-semibold">{{ $label }}</h3>
                    <i class="fas fa-arrow-right text-blue-600"></i>
                </div>
                <p class="text-gray-600 mb-4">Click to fill and submit the {{ $label }} form</p>
                <button class="btn-primary w-full">Open Form</button>
            </a>
        @endforeach
    </div>

    <!-- Quick Information -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="card">
            <h4 class="text-lg font-semibold mb-2"><i class="fas fa-check-circle text-green-500"></i> Secure</h4>
            <p class="text-gray-600">Your data is encrypted and stored securely.</p>
        </div>
        <div class="card">
            <h4 class="text-lg font-semibold mb-2"><i class="fas fa-clock text-blue-500"></i> Fast</h4>
            <p class="text-gray-600">Submit forms quickly with our intuitive interface.</p>
        </div>
        <div class="card">
            <h4 class="text-lg font-semibold mb-2"><i class="fas fa-headset text-purple-500"></i> Support</h4>
            <p class="text-gray-600">Get help when you need it with our support team.</p>
        </div>
    </div>
</div>
@endsection
