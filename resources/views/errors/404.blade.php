@extends('base')

@section('title', 'Page Not Found')

@section('content')
<div class="flex flex-col items-center justify-center min-h-64 text-center">
    <h1 class="text-6xl font-bold text-gray-300 mb-4">404</h1>
    <h2 class="text-2xl font-semibold text-gray-700 mb-4">Page Not Found</h2>
    <p class="text-gray-500 mb-8">The page you are looking for does not exist.</p>
    <a href="{{ url('/') }}" class="btn-primary">Go Home</a>
</div>
@endsection
