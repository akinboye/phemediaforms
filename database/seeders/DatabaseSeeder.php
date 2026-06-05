<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\SuperAdmin;
use App\Models\Admin;
use App\Models\NotificationEmail;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        // Create SuperAdmin
        $superadmin = SuperAdmin::create([
            'username' => 'admin',
            'email' => 'admin@phemediaa.com',
            'password' => 'admin123'
        ]);

        // Create Admin
        $admin = Admin::create([
            'first_name' => 'John',
            'last_name' => 'Approver',
            'email' => 'user@phemediaa.com',
            'phone_number' => '+234 123 456 7890',
            'username' => 'user',
            'password' => 'user123',
            'is_active' => true,
            'created_by' => $superadmin->id
        ]);

        // Create default notification emails
        NotificationEmail::create([
            'email' => 'admin@phemediaa.com',
            'form_type' => 'all',
            'is_active' => true,
            'added_by_superadmin' => $superadmin->id
        ]);

        echo "✓ SuperAdmin created: username=admin, password=admin123\n";
        echo "✓ Admin created: username=user, password=user123\n";
        echo "✓ Default notification email configured\n";
    }
}
