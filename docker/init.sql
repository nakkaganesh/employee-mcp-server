CREATE DATABASE IF NOT EXISTS employee_mcp;
USE employee_mcp;

CREATE TABLE IF NOT EXISTS employees (
    employee_id VARCHAR(10) NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    leave_balance INT NOT NULL DEFAULT 0,
    PRIMARY KEY (employee_id)
);

CREATE TABLE IF NOT EXISTS tickets (
    id INT NOT NULL AUTO_INCREMENT,
    employee_id VARCHAR(10) NOT NULL,
    issue VARCHAR(500) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'created',
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY employee_id (employee_id),
    CONSTRAINT tickets_ibfk_1
        FOREIGN KEY (employee_id)
        REFERENCES employees (employee_id)
);

INSERT INTO employees (employee_id, name, department, leave_balance)
VALUES
    ('EMP001', 'Rahul Sharma', 'Engineering', 12),
    ('EMP002', 'Priya Reddy', 'Finance', 6),
    ('EMP003', 'Arjun Kumar', 'Operations', 8)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    department = VALUES(department),
    leave_balance = VALUES(leave_balance);