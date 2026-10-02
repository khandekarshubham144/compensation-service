# Employee Compensation Service

An HTTP-triggered Azure Functions application that provides employee management and compensation reporting using Azure SQL Database.

## Technologies

* Python
* Azure Functions
* Azure SQL Database
* pyodbc
* Microsoft SQL Server

## Project Structure

```text
Employee-Compensation-Service/
│
├── database/
│   ├── schema.sql
│   └── seed.sql
│
├── shared/
│   └── db.py
│
├── function_app.py
├── host.json
├── requirements.txt
├── .gitignore
└── README.md
```

## Prerequisites

* Python 3.x
* Azure Functions Core Tools
* Azure SQL Database
* Microsoft ODBC Driver 18 for SQL Server
* Git

## Database Setup

Create the database tables using:

```text
database/schema.sql
```

Insert the sample department and employee data using:

```text
database/seed.sql
```

The database contains two tables:

* `Department`
* `Employee`

`Employee.DepartmentID` is a foreign key referencing `Department.DepartmentID`.

## Configuration

The application reads the Azure SQL connection string from the environment variable:

```text
SQL_CONNECTION_STRING
```

For local development, configure this variable in `local.settings.json`.

Example:

```json
{
    "Values": {
        "AzureWebJobsStorage": "",
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "SQL_CONNECTION_STRING": "<YOUR_AZURE_SQL_CONNECTION_STRING>"
    }
}
```

Do not commit `local.settings.json` or any real credentials to GitHub.

## Install Dependencies

Activate the virtual environment and run:

```powershell
pip install -r requirements.txt
```

## Run Locally

Start the Azure Functions application with:

```powershell
func start
```

The local Functions host normally runs at:

```text
http://localhost:7071
```

## API Endpoints

### Database Test

```http
GET /api/test-db
```

Tests the connection to Azure SQL Database.

### Create Employee

```http
POST /api/employees
```

Required fields:

```json
{
    "FirstName": "John",
    "LastName": "Doe",
    "DepartmentID": 1,
    "Salary": 60000
}
```

`Bonus` and `HireDate` are optional.

### Get Employee

```http
GET /api/employees/{id}
```

Example:

```text
GET /api/employees/1
```

### List Employees

```http
GET /api/employees
```

Optional department filter:

```text
GET /api/employees?departmentId=1
```

### Update Employee

```http
PUT /api/employees/{id}
```

Updates an existing employee's details, including salary and bonus.

### Delete Employee

```http
DELETE /api/employees/{id}
```

Deletes an employee by ID.

## Compensation Reports

### Total Company Bonus

```http
GET /api/reports/total-bonus
```

Returns the total bonus paid across the company. Employees with no bonus are treated as zero.

### Employees With No Bonus

```http
GET /api/reports/no-bonus
```

Returns employees whose bonus is `NULL` or `0`.

### Bonus Percentage

```http
GET /api/reports/bonus-percentage
```

Returns each employee's bonus as a percentage of salary.

### Department Bonus Report

```http
GET /api/reports/department-bonus
```

Returns departments where total bonuses exceed the department's average salary.

### Bonus Ranking

```http
GET /api/reports/bonus-ranking
```

Ranks employees by bonus amount. Employees without a bonus are treated as having a zero bonus.

### Highest Compensation

```http
GET /api/reports/highest-compensation
```

Returns:

* Employee with the highest base salary
* Employee with the highest total compensation (`Salary + Bonus`)
* Whether both are the same employee

## Error Handling

The API returns appropriate HTTP status codes for common situations, including:

* `200` - Successful request
* `201` - Employee successfully created
* `400` - Invalid request or input
* `404` - Employee not found
* `500` - Server or database error

## SQL Scripts

The SQL scripts used for the project are located in the `database` directory:

```text
database/schema.sql
database/seed.sql
```

`schema.sql` creates the database tables and `seed.sql` inserts sample data.
