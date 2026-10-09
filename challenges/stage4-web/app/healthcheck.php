<?php
require '/opt/stage4/bootstrap.php';
try {
    db()->query('SELECT id FROM users LIMIT 1');
    exit(0);
} catch (Throwable $error) {
    exit(1);
}
