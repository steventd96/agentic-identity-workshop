-- ============================================================================
-- Agentic Security Lab - Sample Employee Data
-- ============================================================================
-- This script populates the database with realistic sample employee data
-- for testing the agentic security lab scenarios
-- ============================================================================

-- Insert sample employees into employee_basic_info
INSERT INTO employee_basic_info (first_name, last_name, email, department, job_title, hire_date, office_location, manager_id, phone_number) VALUES
    ('Sarah', 'Johnson', 'sarah.johnson@company.com', 'Engineering', 'Senior Software Engineer', '2020-03-15', 'San Francisco, CA', NULL, '+1-415-555-0101'),
    ('Michael', 'Chen', 'michael.chen@company.com', 'Engineering', 'Software Engineer', '2021-06-01', 'San Francisco, CA', 1, '+1-415-555-0102'),
    ('Emily', 'Rodriguez', 'emily.rodriguez@company.com', 'Engineering', 'DevOps Engineer', '2021-09-20', 'Austin, TX', 1, '+1-512-555-0103'),
    ('David', 'Kim', 'david.kim@company.com', 'Engineering', 'Frontend Developer', '2022-01-10', 'New York, NY', 1, '+1-212-555-0104'),
    
    ('Jennifer', 'Williams', 'jennifer.williams@company.com', 'Human Resources', 'HR Manager', '2019-05-12', 'San Francisco, CA', NULL, '+1-415-555-0201'),
    ('Robert', 'Brown', 'robert.brown@company.com', 'Human Resources', 'HR Specialist', '2021-11-03', 'San Francisco, CA', 5, '+1-415-555-0202'),
    
    ('Lisa', 'Anderson', 'lisa.anderson@company.com', 'Sales', 'Sales Director', '2018-08-22', 'New York, NY', NULL, '+1-212-555-0301'),
    ('James', 'Martinez', 'james.martinez@company.com', 'Sales', 'Account Executive', '2020-10-15', 'New York, NY', 7, '+1-212-555-0302'),
    ('Amanda', 'Taylor', 'amanda.taylor@company.com', 'Sales', 'Sales Representative', '2022-03-01', 'Chicago, IL', 7, '+1-312-555-0303'),
    
    ('Christopher', 'Lee', 'christopher.lee@company.com', 'Finance', 'Finance Manager', '2019-02-18', 'San Francisco, CA', NULL, '+1-415-555-0401'),
    ('Michelle', 'Garcia', 'michelle.garcia@company.com', 'Finance', 'Financial Analyst', '2021-07-12', 'San Francisco, CA', 10, '+1-415-555-0402'),
    
    ('Daniel', 'Wilson', 'daniel.wilson@company.com', 'Marketing', 'Marketing Director', '2020-04-05', 'Austin, TX', NULL, '+1-512-555-0501'),
    ('Jessica', 'Moore', 'jessica.moore@company.com', 'Marketing', 'Content Strategist', '2021-12-08', 'Austin, TX', 12, '+1-512-555-0502'),
    
    ('Thomas', 'Jackson', 'thomas.jackson@company.com', 'Product', 'Product Manager', '2019-11-20', 'San Francisco, CA', NULL, '+1-415-555-0601'),
    ('Rachel', 'White', 'rachel.white@company.com', 'Product', 'Product Designer', '2022-02-14', 'San Francisco, CA', 14, '+1-415-555-0602');

-- Insert corresponding salary information into employee_salary_info
INSERT INTO employee_salary_info (employee_id, annual_salary, bonus_percentage, stock_options, salary_grade, last_review_date, next_review_date, performance_rating) VALUES
    -- Engineering
    (1, 145000.00, 15.00, 5000, 'E5', '2023-03-15', '2024-03-15', 'Exceeds Expectations'),
    (2, 110000.00, 10.00, 2000, 'E3', '2023-06-01', '2024-06-01', 'Meets Expectations'),
    (3, 125000.00, 12.00, 3000, 'E4', '2023-09-20', '2024-09-20', 'Exceeds Expectations'),
    (4, 95000.00, 8.00, 1500, 'E2', '2023-01-10', '2024-01-10', 'Meets Expectations'),
    
    -- Human Resources
    (5, 135000.00, 15.00, 4000, 'M3', '2023-05-12', '2024-05-12', 'Exceeds Expectations'),
    (6, 75000.00, 8.00, 1000, 'S2', '2023-11-03', '2024-11-03', 'Meets Expectations'),
    
    -- Sales
    (7, 160000.00, 20.00, 6000, 'M4', '2023-08-22', '2024-08-22', 'Outstanding'),
    (8, 95000.00, 15.00, 2500, 'S3', '2023-10-15', '2024-10-15', 'Exceeds Expectations'),
    (9, 70000.00, 10.00, 1000, 'S1', '2023-03-01', '2024-03-01', 'Meets Expectations'),
    
    -- Finance
    (10, 140000.00, 15.00, 4500, 'M3', '2023-02-18', '2024-02-18', 'Exceeds Expectations'),
    (11, 85000.00, 10.00, 1500, 'S2', '2023-07-12', '2024-07-12', 'Meets Expectations'),
    
    -- Marketing
    (12, 150000.00, 18.00, 5000, 'M4', '2023-04-05', '2024-04-05', 'Exceeds Expectations'),
    (13, 80000.00, 10.00, 1200, 'S2', '2023-12-08', '2024-12-08', 'Meets Expectations'),
    
    -- Product
    (14, 155000.00, 18.00, 5500, 'M4', '2023-11-20', '2024-11-20', 'Outstanding'),
    (15, 105000.00, 12.00, 2500, 'S3', '2023-02-14', '2024-02-14', 'Exceeds Expectations');

-- Create some views for common queries
CREATE OR REPLACE VIEW employee_directory AS
SELECT 
    e.employee_id,
    e.first_name,
    e.last_name,
    e.email,
    e.department,
    e.job_title,
    e.office_location,
    e.phone_number,
    m.first_name || ' ' || m.last_name AS manager_name
FROM employee_basic_info e
LEFT JOIN employee_basic_info m ON e.manager_id = m.employee_id
ORDER BY e.department, e.last_name;

CREATE OR REPLACE VIEW department_summary AS
SELECT 
    department,
    COUNT(*) as employee_count,
    COUNT(DISTINCT office_location) as office_count
FROM employee_basic_info
GROUP BY department
ORDER BY employee_count DESC;

-- Grant SELECT on views to public (will be restricted by Vault policies)
GRANT SELECT ON employee_directory TO PUBLIC;
GRANT SELECT ON department_summary TO PUBLIC;

-- Display summary statistics
DO $$
DECLARE
    total_employees INTEGER;
    total_departments INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_employees FROM employee_basic_info;
    SELECT COUNT(DISTINCT department) INTO total_departments FROM employee_basic_info;
    
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Database Initialization Complete';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Total Employees: %', total_employees;
    RAISE NOTICE 'Total Departments: %', total_departments;
    RAISE NOTICE '========================================';
END $$;

-- Made with Bob
