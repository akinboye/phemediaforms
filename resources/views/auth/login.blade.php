@extends('base')

@section('title', 'Admin Login')

@section('content')
<div class="flex justify-center items-center min-h-96">
    <div class="card w-full max-w-md">
        <h2 class="text-2xl font-bold mb-6 text-center">Admin Login</h2>

        <form method="POST" action="{{ route('admin.login.submit') }}">
            @csrf

            <div class="mb-4">
                <label class="block text-gray-700 font-semibold mb-2">Username</label>
                <input 
                    type="text" 
                    name="username" 
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                    value="{{ old('username') }}"
                >
                @error('username')
                    <span class="text-red-600 text-sm">{{ $message }}</span>
                @enderror
            </div>

            <div class="mb-6">
                <label class="block text-gray-700 font-semibold mb-2">Password</label>
                <input 
                    type="password" 
                    name="password" 
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                >
                @error('password')
                    <span class="text-red-600 text-sm">{{ $message }}</span>
                @enderror
            </div>

            @error('credentials')
                <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-4">
                    {{ $message }}
                </div>
            @enderror

            <button 
                type="submit" 
                class="w-full btn-primary"
            >
                Login
            </button>
        </form>

        <div class="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h4 class="font-semibold mb-2">Demo Credentials:</h4>
            <p class="text-sm text-gray-700 mb-1"><strong>SuperAdmin:</strong> admin / admin123</p>
            <p class="text-sm text-gray-700"><strong>Admin:</strong> user / user123</p>
        </div>
    </div>
</div>
@endsection
