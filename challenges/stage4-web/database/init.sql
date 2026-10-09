-- Fictional credentials for the intentionally vulnerable teaching lab.
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(64) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    role VARCHAR(16) NOT NULL
);
INSERT INTO users (username, password, role) VALUES
('admin', 'Prometheus-Archive-7392!', 'admin'),
('analyst', 'ReadOnly-Nexa-214!', 'analyst');
