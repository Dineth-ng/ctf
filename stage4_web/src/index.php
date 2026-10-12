<?php
session_start();

mysqli_report(MYSQLI_REPORT_OFF);
$conn = new mysqli("stage4_db", "appuser", "apppass", "portal_db");
if ($conn->connect_error) {
    // If DB is still booting, fallback gracefully
    $db_ready = false;
} else {
    $db_ready = true;
}

$error = "";
if ($_SERVER["REQUEST_METHOD"] == "POST" && $db_ready) {
    $u = $_POST['username'] ?? '';
    $p = $_POST['password'] ?? '';

    // Intentional SQL Injection vulnerability for educational CTF
    $query = "SELECT * FROM users WHERE username = '$u' AND password = '$p'";
    $result = $conn->query($query);

    if ($result && $result->num_rows > 0) {
        $row = $result->fetch_assoc();
        $_SESSION['user'] = $row['username'];
        $_SESSION['role'] = $row['role'];
        header("Location: dashboard.php");
        exit();
    } else {
        $error = "Authentication failed: Invalid username or password.";
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GhostByte C2 // NexaCore Shadow Portal</title>
    <style>
        body { font-family: 'Courier New', monospace; background-color: #0d1117; color: #58a6ff; margin: 0; padding: 60px 20px; }
        .login-box { max-width: 420px; margin: 0 auto; background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 30px; box-shadow: 0 8px 24px rgba(0,0,0,0.6); }
        h2 { text-align: center; color: #f85149; margin-top: 0; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: bold; font-size: 0.9em; }
        input[type="text"], input[type="password"] { width: 100%; box-sizing: border-box; padding: 10px; background: #0d1117; border: 1px solid #30363d; color: #c9d1d9; border-radius: 4px; font-family: monospace; }
        button { width: 100%; padding: 10px; background: #238636; border: none; color: white; font-weight: bold; border-radius: 4px; cursor: pointer; font-size: 1em; }
        button:hover { background: #2ea043; }
        .error { color: #f85149; background: #ffebe9; padding: 10px; border-radius: 4px; font-size: 0.85em; margin-bottom: 15px; }
        .hint { font-size: 0.8em; color: #8b949e; margin-top: 20px; text-align: center; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>[!] NEXACORE SHADOW RELAY</h2>
        <p style="text-align: center; font-size: 0.85em; color: #8b949e;">GhostByte Command &amp; Control Backdoor</p>
        <?php if ($error): ?>
            <div class="error"><?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>
        <form method="POST" action="">
            <div class="form-group">
                <label>OPERATOR IDENTIFIER</label>
                <input type="text" name="username" placeholder="e.g. admin" required>
            </div>
            <div class="form-group">
                <label>SECURITY ACCESS TOKEN</label>
                <input type="password" name="password" placeholder="e.g. **********" required>
            </div>
            <button type="submit">&gt;&gt; AUTHENTICATE</button>
        </form>
        <div class="hint">
            Authorized operators only. All failed queries are monitored.
        </div>
    </div>
</body>
</html>
