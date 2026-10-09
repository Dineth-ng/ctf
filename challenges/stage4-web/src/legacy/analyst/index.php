<?php
require '/opt/stage4/bootstrap.php';
$user = $_SESSION['user'] ?? null;
if (!$user) {
    header('Location: /legacy/auth/');
    exit;
}
if ($user['role'] !== 'analyst') {
    header('Location: /legacy/admin/');
    exit;
}
require '/opt/stage4/dashboard.php';
