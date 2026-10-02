

-- Departments
INSERT INTO Department (DepartmentID, DepartmentName, Location)
VALUES
(1, 'Engineering', 'Bangalore'),
(2, 'HR', 'Pune'),
(3, 'Finance', 'Mumbai'),
(4, 'Sales', 'Delhi');

-- Employees
INSERT INTO Employee
    (FirstName, LastName, DepartmentID, Salary, Bonus, HireDate)
VALUES
('Rahul', 'Sharma', 1, 75000.00, 5000.00, '2025-01-15'),
('Priya', 'Patil', 1, 68000.00, NULL, '2026-03-20'),
('Amit', 'Kumar', 2, 55000.00, 3000.00, '2025-07-10'),
('Sneha', 'Joshi', 3, 62000.00, NULL, '2024-01-05'),
('Vikas', 'Singh', 4, 50000.00, 2500.00, '2026-06-12');

SELECT * from Employee;
-- SELECT * from Department;