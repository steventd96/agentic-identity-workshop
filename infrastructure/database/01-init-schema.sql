-- ============================================================================
-- Agentic Security Lab - Database Initialization Script
-- ============================================================================
-- This script creates the employee database schema with two tables:
-- 1. employee_basic_info - Accessible to hr-basic group
-- 2. employee_salary_info - Restricted to hr-admin group only
-- ============================================================================

-- Create employee_basic_info table
-- This table contains non-sensitive employee information
CREATE TABLE IF NOT EXISTS employee_basic_info (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50) NOT NULL,
    job_title VARCHAR(100) NOT NULL,
    hire_date DATE NOT NULL,
    office_location VARCHAR(100) NOT NULL,
    manager_id INTEGER,
    phone_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create employee_salary_info table
-- This table contains sensitive compensation information
CREATE TABLE IF NOT EXISTS employee_salary_info (
    salary_id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employee_basic_info(employee_id) ON DELETE CASCADE,
    annual_salary DECIMAL(10, 2) NOT NULL,
    bonus_percentage DECIMAL(5, 2) DEFAULT 0.00,
    stock_options INTEGER DEFAULT 0,
    salary_grade VARCHAR(10) NOT NULL,
    last_review_date DATE,
    next_review_date DATE,
    performance_rating VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id)
);

-- Create indexes for better query performance
CREATE INDEX idx_employee_department ON employee_basic_info(department);
CREATE INDEX idx_employee_email ON employee_basic_info(email);
CREATE INDEX idx_salary_employee_id ON employee_salary_info(employee_id);
CREATE INDEX idx_salary_grade ON employee_salary_info(salary_grade);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_employee_basic_info_updated_at
    BEFORE UPDATE ON employee_basic_info
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_employee_salary_info_updated_at
    BEFORE UPDATE ON employee_salary_info
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions to postgres user (for initial setup)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Create a vault user for Vault to manage dynamic credentials
CREATE USER vault WITH PASSWORD 'vault-password';
GRANT ALL PRIVILEGES ON DATABASE employee_db TO vault;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vault WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vault WITH GRANT OPTION;

-- Allow vault user to create roles
ALTER USER vault WITH CREATEROLE;

COMMENT ON TABLE employee_basic_info IS 'Non-sensitive employee information - accessible to hr-basic group';
COMMENT ON TABLE employee_salary_info IS 'Sensitive compensation information - restricted to hr-admin group only';

-- Made with Bob
