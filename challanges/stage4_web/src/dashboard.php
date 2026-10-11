<?php
session_start();
if (!isset($_SESSION['user'])) {
    header("Location: index.php");
    exit();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GhostByte Admin Console // Internal Hub</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; background: #0b0f19; color: #f1f5f9; padding: 30px; }
        .container { max-width: 900px; margin: 0 auto; background: #1e293b; border-radius: 8px; padding: 25px; border: 1px solid #334155; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #475569; padding-bottom: 15px; }
        .flag-box { background: #0f172a; border-left: 5px solid #10b981; padding: 15px; margin: 25px 0; border-radius: 4px; font-family: monospace; }
        .note-card { background: #334155; padding: 15px; border-radius: 6px; margin: 15px 0; font-size: 0.95em; }
        code { color: #38bdf8; }
        a.logout { color: #f43f5e; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h2>OPERATIONAL COMMAND DASHBOARD</h2>
                <span>Authenticated Session: <b><?php echo htmlspecialchars($_SESSION['user']); ?></b> (Role: <?php echo htmlspecialchars($_SESSION['role']); ?>)</span>
            </div>
            <a href="logout.php" class="logout">[DISCONNECT]</a>
        </div>

        <div class="flag-box">
            <h3 style="color:#34d399; margin-top:0;">STAGE 4 FLAG CAPTURED:</h3>
            <span style="font-size: 1.2em; font-weight: bold;">NH{sqli_4dm1n_p0rt4l_byp4ss}</span>
        </div>

        <h3>GhostByte Mission Status Briefing:</h3>
        <div class="note-card">
            <strong>Subject:</strong> Prometheus Exfiltration Pipe<br>
            <strong>Status:</strong> Completed via covert network channel.<br>
            <strong>Investigator Brief:</strong> Packet captures (<code>exfil.pcap</code>) and deleted storage forensic snapshots (<code>disk.img</code>) have been recovered by blue team analysts. Retrace the TCP network stream and file carver logs to locate Stage 6 vault credentials!
        </div>

        <div class="note-card">
            <strong>Target Machine Location:</strong> Hardened Ubuntu Storage Node (Port 2222 SSH)<br>
            <strong>Note to Operatives:</strong> Check disk image residual sectors for access credentials.
        </div>
        <!-- Secret HTML Comment: Vault target user is 'runner'. Search deleted blocks for login password. -->
    </div>
</body>
</html>
