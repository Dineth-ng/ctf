<?php
declare(strict_types=1);
session_start();
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');
mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
function db(): mysqli {
    $connection = new mysqli(getenv('DB_HOST') ?: 'stage4-db', getenv('DB_USER') ?: 'portal', getenv('DB_PASSWORD') ?: '', getenv('DB_NAME') ?: 'nighthawk_stage4');
    $connection->set_charset('utf8mb4');
    return $connection;
}
function escape(string $value): string {
    return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}
