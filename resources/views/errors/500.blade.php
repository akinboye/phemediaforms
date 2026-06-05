@extends('base')

@section('title', 'Server Error')

@section('content')
<div class="flex flex-col items-center justify-center min-h-64 text-center">
    <h1 class="text-6xl font-bold text-gray-300 mb-4">500</h1>
    <h2 class="text-2xl font-semibold text-gray-700 mb-4">Server Error</h2>
    <p class="text-gray-500 mb-8">Something went wrong. Please try again later.</p>
    <a href="{{ url('/') }}" class="btn-primary">Go Home</a>
</div>
@endsection
