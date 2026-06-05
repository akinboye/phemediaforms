<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        // Create superadmins table
        Schema::create('superadmins', function (Blueprint $table) {
            $table->id();
            $table->string('username')->unique();
            $table->string('email')->unique();
            $table->string('password');
            $table->timestamps();
        });

        // Create admins table
        Schema::create('admins', function (Blueprint $table) {
            $table->id();
            $table->string('first_name');
            $table->string('last_name');
            $table->string('email')->unique();
            $table->string('phone_number');
            $table->string('username')->unique();
            $table->string('password');
            $table->boolean('is_active')->default(true);
            $table->foreignId('created_by')->nullable()->constrained('superadmins')->onDelete('set null');
            $table->timestamps();
        });

        // Create form_submissions table
        Schema::create('form_submissions', function (Blueprint $table) {
            $table->id();
            $table->string('form_type');
            $table->json('submitted_data');
            $table->string('user_email');
            $table->ipAddress('ip_address')->nullable();
            $table->text('user_agent')->nullable();
            $table->string('status')->default('pending_approval');
            $table->foreignId('approved_by_admin')->nullable()->constrained('admins')->onDelete('set null');
            $table->foreignId('approved_by_superadmin')->nullable()->constrained('superadmins')->onDelete('set null');
            $table->timestamp('approved_at')->nullable();
            $table->string('approver_position')->nullable();
            $table->text('rejection_reason')->nullable();
            $table->string('pdf_filename')->nullable();
            $table->string('stamp_filename')->nullable();
            $table->string('photo_filename')->nullable();
            $table->string('nin_filename')->nullable();
            $table->string('client_acceptance_token')->nullable()->unique();
            $table->string('client_acceptance_link')->nullable();
            $table->boolean('client_acceptance_completed')->default(false);
            $table->timestamp('client_acceptance_completed_at')->nullable();
            $table->longText('client_signature_data')->nullable();
            $table->string('final_pdf_filename')->nullable();
            $table->softDeletes();
            $table->timestamps();

            $table->index('form_type');
            $table->index('status');
            $table->index('user_email');
        });

        // Create notification_emails table
        Schema::create('notification_emails', function (Blueprint $table) {
            $table->id();
            $table->string('email');
            $table->string('form_type');
            $table->boolean('is_active')->default(true);
            $table->foreignId('added_by_admin')->nullable()->constrained('admins')->onDelete('set null');
            $table->foreignId('added_by_superadmin')->nullable()->constrained('superadmins')->onDelete('set null');
            $table->timestamps();

            $table->unique(['email', 'form_type']);
            $table->index('form_type');
        });

        // Create company_addresses table
        Schema::create('company_addresses', function (Blueprint $table) {
            $table->id();
            $table->string('company_name');
            $table->text('address');
            $table->string('city');
            $table->string('state');
            $table->string('country');
            $table->string('postal_code');
            $table->timestamps();
        });

        // Create approval_stamps table
        Schema::create('approval_stamps', function (Blueprint $table) {
            $table->id();
            $table->foreignId('submission_id')->constrained('form_submissions')->onDelete('cascade');
            $table->string('stamp_image')->nullable();
            $table->string('approver_name');
            $table->string('approver_position');
            $table->timestamp('stamped_at');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('approval_stamps');
        Schema::dropIfExists('company_addresses');
        Schema::dropIfExists('notification_emails');
        Schema::dropIfExists('form_submissions');
        Schema::dropIfExists('admins');
        Schema::dropIfExists('superadmins');
    }
};
