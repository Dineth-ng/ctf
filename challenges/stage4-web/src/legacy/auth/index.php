<?php
require '/opt/stage4/bootstrap.php';
$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    unset($_SESSION['user']);
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';
    if (!is_string($username) || !is_string($password) || $username === '' || $password === '') {
        $error = 'Enter a username and password.';
    } else {
        try {
            $connection = db();
        } catch (mysqli_sql_exception $exception) {
            http_response_code(503);
            $error = 'Operations database unavailable. Please try again shortly.';
        }
        if (isset($connection)) {
            // INTENTIONAL CTF VULNERABILITY: input concatenation creates SQL injection.
            // This legacy flow is only for the isolated Stage 4 teaching lab.
            $sql = "SELECT id, username, role FROM users WHERE username = '$username'  AND password = '$password' LIMIT 1";
            try {
                $user = $connection->query($sql)->fetch_assoc();
                if ($user) {
                    session_regenerate_id(true);
                    $_SESSION['user'] = $user;
                    header('Location: ' . ($user['role'] === 'admin' ? '/legacy/admin/' : '/legacy/analyst/'));
                    exit;
                }
                $error = 'Invalid credentials.';
            } catch (mysqli_sql_exception $exception) {
                $error = 'Legacy authentication query failed. Check your input syntax.';
            }
        }
    }
}
?>
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Sign in | NexaCore</title><link rel="stylesheet" href="/assets/style.css"></head>
<body class="login-page"><main class="login-card"><a class="brand" href="/"><span class="brand-mark">N</span> NexaCore <span class="brand-detail">Dynamics</span></a><h1>Sign in to your workspace</h1><p>Access your projects, reports, and operations records.</p>
<?php if ($error !== ''): ?><div class="error" role="alert"><?= escape($error) ?></div><?php endif; ?>
<form method="post" action="/legacy/auth/">
<label for="username">Username</label><input id="username" name="username" autocomplete="username" required>
<label for="password">Password</label><input id="password" name="password" type="password" autocomplete="current-password" required>
<button class="primary full" type="submit">Sign in</button></form><p class="login-note">Need access? Contact your operations administrator.</p></main><footer class="login-footer">NexaCore Dynamics · Internal operations</footer></body>
</html>
