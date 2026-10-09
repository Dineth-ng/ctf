<?php
require '/opt/stage4/bootstrap.php';
$user = $_SESSION['user'] ?? null;
if (!$user) {
    header('Location: /legacy/auth/');
    exit;
}
if ($user['role'] !== 'admin') {
    http_response_code(403);
    exit('Administrator clearance required.');
}
require '/opt/stage4/dashboard.php';
