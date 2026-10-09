<?php
require '/opt/stage4/bootstrap.php';
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    header('Allow: POST');
    exit;
}
$_SESSION = [];
session_destroy();
header('Location: /legacy/auth/');
