CREATE DATABASE IF NOT EXISTS portal_db;
USE portal_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'user'
);

INSERT INTO users (username, password, role) VALUES 
('admin', 'GhostOpsPass2026!', 'administrator'),
('mvance', 'P@ssw0rd2024#Prometheus', 'developer'),
('c2_runner', 'gh0st_byt3_t0k3n', 'c2_agent');

CREATE TABLE IF NOT EXISTS system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_name VARCHAR(100) NOT NULL,
    details TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO system_logs (event_name, details) VALUES
('PROMETHEUS_EXFIL', 'Relay connection opened to vault storage on internal port 2222'),
('CREDENTIAL_LEAK', 'Workstation dump archived to /tmp/exfil_dump.zip'),
('FLAG_REGISTRATION', 'Flag verified: NH{sqli_4dm1n_p0rt4l_byp4ss}');
