<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\FormController;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\AdminController;
use App\Http\Controllers\SuperAdminController;

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
| Routes for PHEMEDAA Forms Portal
*/

// Public Routes - Form Submission
Route::get('/', [FormController::class, 'index'])->name('home');
Route::get('/confirmation', [FormController::class, 'confirmation'])->name('confirmation');

// Form pages
Route::get('/backgroundcheck', [FormController::class, 'showForm'])->defaults('form_type', 'backgroundcheck')->name('form.backgroundcheck');
Route::get('/clientengagement', [FormController::class, 'showForm'])->defaults('form_type', 'clientengagement')->name('form.clientengagement');
Route::get('/declarationbyemployee', [FormController::class, 'showForm'])->defaults('form_type', 'declarationbyemployee')->name('form.declarationbyemployee');
Route::get('/guarantorundertaking', [FormController::class, 'showForm'])->defaults('form_type', 'guarantorundertaking')->name('form.guarantorundertaking');
Route::get('/serviceagreement', [FormController::class, 'showForm'])->defaults('form_type', 'serviceagreement')->name('form.serviceagreement');
Route::get('/trackingagreement', [FormController::class, 'showForm'])->defaults('form_type', 'trackingagreement')->name('form.trackingagreement');
Route::get('/oilgasservicerequest', [FormController::class, 'showForm'])->defaults('form_type', 'oilgasservicerequest')->name('form.oilgasservicerequest');

// Form submission
Route::post('/submit-form', [FormController::class, 'submitForm'])->name('form.submit');

// Client signature routes
Route::get('/serviceagreement/sign/{token}', [FormController::class, 'clientSignForm'])->name('form.sign');
Route::post('/serviceagreement/sign/{token}', [FormController::class, 'saveSignature'])->name('form.save-signature');

// Authentication Routes
Route::get('/admin/login', [AuthController::class, 'showLogin'])->name('admin.login');
Route::post('/admin/login', [AuthController::class, 'login'])->name('admin.login.submit');
Route::post('/admin/logout', [AuthController::class, 'logout'])->name('admin.logout');

// Protected Admin Routes
Route::middleware(['auth:admin'])->group(function () {
    
    // Admin Dashboard
    Route::get('/admin/dashboard', [AdminController::class, 'dashboard'])->name('admin.dashboard');
    Route::get('/admin/submissions', [AdminController::class, 'submissions'])->name('admin.submissions');
    Route::get('/admin/submission/{id}', [AdminController::class, 'viewSubmission'])->name('admin.submission.view');
    Route::post('/admin/submission/{id}/approve', [AdminController::class, 'approveSubmission'])->name('admin.submission.approve');
    Route::post('/admin/submission/{id}/reject', [AdminController::class, 'rejectSubmission'])->name('admin.submission.reject');
    
    // Notification emails
    Route::get('/admin/notifications', [AdminController::class, 'notifications'])->name('admin.notifications');
    Route::post('/admin/notification/add', [AdminController::class, 'addNotification'])->name('admin.notification.add');
    Route::post('/admin/notification/{id}/delete', [AdminController::class, 'deleteNotification'])->name('admin.notification.delete');
});

// Protected SuperAdmin Routes
Route::middleware(['auth:superadmin'])->group(function () {
    
    // SuperAdmin Dashboard
    Route::get('/superadmin/dashboard', [SuperAdminController::class, 'dashboard'])->name('superadmin.dashboard');
    
    // Admin Management
    Route::get('/superadmin/admins', [SuperAdminController::class, 'admins'])->name('superadmin.admins');
    Route::get('/superadmin/admin/create', [SuperAdminController::class, 'createAdmin'])->name('superadmin.admin.create');
    Route::post('/superadmin/admin/store', [SuperAdminController::class, 'storeAdmin'])->name('superadmin.admin.store');
    Route::get('/superadmin/admin/{id}/edit', [SuperAdminController::class, 'editAdmin'])->name('superadmin.admin.edit');
    Route::post('/superadmin/admin/{id}/update', [SuperAdminController::class, 'updateAdmin'])->name('superadmin.admin.update');
    Route::post('/superadmin/admin/{id}/toggle', [SuperAdminController::class, 'toggleAdmin'])->name('superadmin.admin.toggle');
    
    // Submissions
    Route::get('/superadmin/submissions', [SuperAdminController::class, 'submissions'])->name('superadmin.submissions');
    Route::get('/superadmin/submission/{id}', [SuperAdminController::class, 'viewSubmission'])->name('superadmin.submission.view');
    
    // Notifications
    Route::get('/superadmin/notifications', [SuperAdminController::class, 'notifications'])->name('superadmin.notifications');
    Route::post('/superadmin/notification/add', [SuperAdminController::class, 'addNotification'])->name('superadmin.notification.add');
    Route::post('/superadmin/notification/{id}/delete', [SuperAdminController::class, 'deleteNotification'])->name('superadmin.notification.delete');
});

// 404 handling
Route::fallback(function () {
    return response()->view('errors.404', [], 404);
});
