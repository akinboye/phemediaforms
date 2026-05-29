<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>@yield('title', 'PHEMEDAA Forms Portal')</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .navbar-brand {
            font-weight: 700;
            font-size: 1.5rem;
            color: #1f2937;
        }
        .btn-primary {
            @apply px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition;
        }
        .btn-secondary {
            @apply px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition;
        }
        .btn-danger {
            @apply px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition;
        }
        .card {
            @apply bg-white rounded-lg shadow-md p-6;
        }
    </style>
    @yield('extra-css')
</head>
<body class="bg-gray-50">
    <!-- Navigation Bar -->
    <nav class="bg-white shadow-md">
        <div class="container mx-auto px-4 py-4 flex justify-between items-center">
            <div class="navbar-brand">
                <i class="fas fa-file-alt text-blue-600"></i> PHEMEDAA Forms
            </div>
            <div class="flex gap-4">
                @if(session('admin_id') || session('superadmin_id'))
                    <span class="text-gray-700">{{ session('user_name') }}</span>
                    <form method="POST" action="{{ route('admin.logout') }}" class="inline">
                        @csrf
                        <button type="submit" class="btn-secondary">Logout</button>
                    </form>
                @else
                    <a href="{{ route('admin.login') }}" class="btn-primary">Admin Login</a>
                @endif
            </div>
        </div>
    </nav>

    <!-- Flash Messages -->
    @if($errors->any())
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg m-4">
            <strong>Error!</strong>
            <ul>
                @foreach($errors->all() as $error)
                    <li>{{ $error }}</li>
                @endforeach
            </ul>
        </div>
    @endif

    @if(session('success'))
        <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg m-4">
            {{ session('success') }}
        </div>
    @endif

    @if(session('error'))
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg m-4">
            {{ session('error') }}
        </div>
    @endif

    <!-- Content -->
    <main class="container mx-auto px-4 py-8">
        @yield('content')
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-6 mt-12">
        <div class="container mx-auto px-4 text-center">
            <p>&copy; 2024 PHEMEDAA Forms Portal. All rights reserved.</p>
        </div>
    </footer>

    @yield('extra-js')
</body>
</html>
