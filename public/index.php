<?php

use Illuminate\Http\Request;

define('LARAVEL_START', microtime(true));

/*
|--------------------------------------------------------------------------
| Subdirectory Deployment Fix
|--------------------------------------------------------------------------
| Apache rewrites /forms/* to /forms/public/* internally, but leaves
| SCRIPT_NAME as /forms/public/index.php while REQUEST_URI stays /forms/*.
| Symfony's Request cannot reconcile these, computing pathInfo as /forms/
| instead of / — so no routes match. We correct SCRIPT_NAME before Symfony
| reads it so it strips /forms as the base, leaving the correct pathInfo.
*/
if (isset($_SERVER['SCRIPT_NAME']) && str_contains($_SERVER['SCRIPT_NAME'], '/public/index.php')) {
    $_SERVER['SCRIPT_NAME'] = str_replace('/public/index.php', '/index.php', $_SERVER['SCRIPT_NAME']);
    $_SERVER['PHP_SELF'] = $_SERVER['SCRIPT_NAME'];
}

if (file_exists($maintenance = __DIR__.'/../storage/framework/maintenance.php')) {
    require $maintenance;
}

require __DIR__.'/../vendor/autoload.php';

$app = require_once __DIR__.'/../bootstrap/app.php';

$kernel = $app->make(Illuminate\Contracts\Http\Kernel::class);

$response = $kernel->handle(
    $request = Illuminate\Http\Request::capture()
)->send();

$kernel->terminate($request, $response);
