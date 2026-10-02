import azure.functions as func
import datetime
import json
import logging
from shared.db import get_connection

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="test-db", methods=["GET"])
def test_db(req: func.HttpRequest) -> func.HttpResponse:

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT DB_NAME()")

        database_name = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return func.HttpResponse(
            f"Connected to database: {database_name}",
            status_code=200
        )

    except Exception as e:
        return func.HttpResponse(
            f"Database connection failed: {str(e)}",
            status_code=500
        )
#1.	Create a new employee. The bonus is optional and may be left unset.

@app.route(route="employees", methods=["POST"])
def create_employee(req: func.HttpRequest) -> func.HttpResponse:

    try:
        data = req.get_json()

        first_name = data.get("FirstName")
        last_name = data.get("LastName")
        department_id = data.get("DepartmentID")
        salary = data.get("Salary")
        bonus = data.get("Bonus")
        hire_date = data.get("HireDate")

        if not first_name or not last_name or department_id is None or salary is None:
            return func.HttpResponse(
                "FirstName, LastName, DepartmentID and Salary are required.",
                status_code=400
            )

        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO Employee
                (FirstName, LastName, DepartmentID, Salary, Bonus, HireDate)
            OUTPUT INSERTED.EmployeeID
            VALUES (?, ?, ?, ?, ?, ?)
        """

        cursor.execute(
            query,
            first_name,
            last_name,
            department_id,
            salary,
            bonus,
            hire_date
        )

        employee_id = cursor.fetchone()[0]

        conn.commit()

        cursor.close()
        conn.close()

        return func.HttpResponse(
            f"Employee created successfully. EmployeeID: {employee_id}",
            status_code=201
        )

    except Exception as e:
        return func.HttpResponse(
            f"Error creating employee: {str(e)}",
            status_code=500
        )


#2.	Retrieve a single employee by their ID.

@app.route(route="employees/{id}", methods=["GET"])
def get_employee(req: func.HttpRequest) -> func.HttpResponse:

    try:
        employee_id = req.route_params.get("id")

        if not employee_id.isdigit():
            return func.HttpResponse(
                "Employee ID must be a number.",
                status_code=400
            )

        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT
                e.EmployeeID,
                e.FirstName,
                e.LastName,
                e.DepartmentID,
                d.DepartmentName,
                d.Location,
                e.Salary,
                e.Bonus,
                e.HireDate
            FROM Employee e
            JOIN Department d
                ON e.DepartmentID = d.DepartmentID
            WHERE e.EmployeeID = ?
        """

        cursor.execute(query, employee_id)
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row is None:
            return func.HttpResponse(
                "Employee not found.",
                status_code=404
            )

        result = {
            "EmployeeID": row.EmployeeID,
            "FirstName": row.FirstName,
            "LastName": row.LastName,
            "DepartmentID": row.DepartmentID,
            "DepartmentName": row.DepartmentName,
            "Location": row.Location,
            "Salary": float(row.Salary),
            "Bonus": float(row.Bonus) if row.Bonus is not None else None,
            "HireDate": row.HireDate.isoformat() if row.HireDate else None
        }

        import json

        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            f"Error retrieving employee: {str(e)}",
            status_code=500
        )


# 3.	Retrieve a list of employees, with optional filtering by department.
@app.route(route="employees", methods=["GET"])
def list_employees(req: func.HttpRequest) -> func.HttpResponse:

    try:
        department_id = req.params.get("departmentId")

        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT
                e.EmployeeID,
                e.FirstName,
                e.LastName,
                e.DepartmentID,
                d.DepartmentName,
                d.Location,
                e.Salary,
                e.Bonus,
                e.HireDate
            FROM Employee e
            JOIN Department d
                ON e.DepartmentID = d.DepartmentID
        """

        params = []

        if department_id:
            if not department_id.isdigit():
                return func.HttpResponse(
                    "departmentId must be a number.",
                    status_code=400
                )

            query += " WHERE e.DepartmentID = ?"
            params.append(department_id)

        query += " ORDER BY e.EmployeeID"

        cursor.execute(query, params)

        rows = cursor.fetchall()

        employees = []

        for row in rows:
            employees.append({
                "EmployeeID": row.EmployeeID,
                "FirstName": row.FirstName,
                "LastName": row.LastName,
                "DepartmentID": row.DepartmentID,
                "DepartmentName": row.DepartmentName,
                "Location": row.Location,
                "Salary": float(row.Salary),
                "Bonus": float(row.Bonus) if row.Bonus is not None else None,
                "HireDate": row.HireDate.isoformat() if row.HireDate else None
            })

        cursor.close()
        conn.close()

        import json

        return func.HttpResponse(
            json.dumps(employees),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            f"Error retrieving employees: {str(e)}",
            status_code=500
        )        



# 4.	Update an existing employee (for example, changing their bonus).

@app.route(route="employees/{id}", methods=["PUT"])
def update_employee(req: func.HttpRequest) -> func.HttpResponse:

    try:
        employee_id = req.route_params.get("id")

        if not employee_id.isdigit():
            return func.HttpResponse(
                "Employee ID must be a number.",
                status_code=400
            )

        data = req.get_json()

        first_name = data.get("FirstName")
        last_name = data.get("LastName")
        department_id = data.get("DepartmentID")
        salary = data.get("Salary")
        bonus = data.get("Bonus")
        hire_date = data.get("HireDate")

        if not first_name or not last_name or department_id is None or salary is None:
            return func.HttpResponse(
                "FirstName, LastName, DepartmentID and Salary are required.",
                status_code=400
            )

        conn = get_connection()
        cursor = conn.cursor()

        # Check whether employee exists
        cursor.execute(
            "SELECT EmployeeID FROM Employee WHERE EmployeeID = ?",
            employee_id
        )

        if cursor.fetchone() is None:
            cursor.close()
            conn.close()

            return func.HttpResponse(
                "Employee not found.",
                status_code=404
            )

        query = """
            UPDATE Employee
            SET
                FirstName = ?,
                LastName = ?,
                DepartmentID = ?,
                Salary = ?,
                Bonus = ?,
                HireDate = ?
            WHERE EmployeeID = ?
        """

        cursor.execute(
            query,
            first_name,
            last_name,
            department_id,
            salary,
            bonus,
            hire_date,
            employee_id
        )

        conn.commit()

        cursor.close()
        conn.close()

        return func.HttpResponse(
            "Employee updated successfully.",
            status_code=200
        )

    except Exception as e:
        return func.HttpResponse(
            f"Error updating employee: {str(e)}",
            status_code=500
        )

# 5.	Delete an employee.

@app.route(route="employees/{id}", methods=["DELETE"])
def delete_employee(req: func.HttpRequest) -> func.HttpResponse:
    try:
        employee_id = req.route_params.get("id")

        if not employee_id.isdigit():
            return func.HttpResponse(
                "Employee ID must be a number.",
                status_code=400
            )

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM Employee WHERE EmployeeID = ?",
            employee_id
        )

        if cursor.rowcount == 0:
            cursor.close()
            conn.close()

            return func.HttpResponse(
                "Employee not found.",
                status_code=404
            )

        conn.commit()

        cursor.close()
        conn.close()

        return func.HttpResponse(
            "Employee deleted successfully.",
            status_code=200
        )

    except Exception as e:
        return func.HttpResponse(
            f"Error deleting employee: {str(e)}",
            status_code=500
        )

#part-B   

# 1.	The total bonus paid across the whole company, treating employees with no bonus as 0.

@app.route(route="reports/total-bonus", methods=["GET"])
def total_company_bonus(req: func.HttpRequest) -> func.HttpResponse:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COALESCE(SUM(Bonus), 0) AS TotalBonus
            FROM Employee
        """)

        row = cursor.fetchone()

        conn.close()

        return func.HttpResponse(
            json.dumps({
                "total_bonus": float(row.TotalBonus)
            }),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

#   2.	A list of all employees who have never received a bonus
@app.route(route="reports/no-bonus", methods=["GET"])
def employees_with_no_bonus(req: func.HttpRequest) -> func.HttpResponse:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                EmployeeID,
                FirstName,
                LastName,
                Salary,
                Bonus
            FROM Employee
            WHERE Bonus IS NULL OR Bonus = 0
        """)

        rows = cursor.fetchall()

        employees = []

        for row in rows:
            employees.append({
                "employee_id": row.EmployeeID,
                "first_name": row.FirstName,
                "last_name": row.LastName,
                "salary": float(row.Salary),
                "bonus": 0 if row.Bonus is None else float(row.Bonus)
            })

        conn.close()

        return func.HttpResponse(
            json.dumps(employees),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )    

# 3.	For each employee who has a bonus, their bonus as a percentage of their salary, rounded to 2 decimal places.

@app.route(route="reports/bonus-percentage", methods=["GET"])
def bonus_percentage(req: func.HttpRequest) -> func.HttpResponse:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                EmployeeID,
                FirstName,
                LastName,
                Salary,
                COALESCE(Bonus, 0) AS Bonus,
                CASE
                    WHEN Salary = 0 THEN 0
                    ELSE (COALESCE(Bonus, 0) / Salary) * 100
                END AS BonusPercentage
            FROM Employee
        """)

        rows = cursor.fetchall()

        employees = []

        for row in rows:
            employees.append({
                "employee_id": row.EmployeeID,
                "first_name": row.FirstName,
                "last_name": row.LastName,
                "salary": float(row.Salary),
                "bonus": float(row.Bonus),
                "bonus_percentage": float(row.BonusPercentage)
            })

        conn.close()

        return func.HttpResponse(
            json.dumps(employees),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

# 
# 4.	Departments where the total bonus paid exceeds the department's average salary.

@app.route(route="reports/department-bonus", methods=["GET"])
def department_bonus(req: func.HttpRequest) -> func.HttpResponse:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                d.DepartmentID,
                d.DepartmentName,
                SUM(COALESCE(e.Bonus, 0)) AS TotalBonus,
                AVG(e.Salary) AS AverageSalary
            FROM Department d
            JOIN Employee e
                ON d.DepartmentID = e.DepartmentID
            GROUP BY
                d.DepartmentID,
                d.DepartmentName
            HAVING
                SUM(COALESCE(e.Bonus, 0)) > AVG(e.Salary)
        """)

        rows = cursor.fetchall()

        departments = []

        for row in rows:
            departments.append({
                "department_id": row.DepartmentID,
                "department_name": row.DepartmentName,
                "total_bonus": float(row.TotalBonus),
                "average_salary": float(row.AverageSalary)
            })

        conn.close()

        return func.HttpResponse(
            json.dumps(departments),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

#  5.	Employees ranked by bonus amount, with employees who have no bonus ranked last rather than excluded.
@app.route(route="reports/bonus-ranking", methods=["GET"])
def bonus_ranking(req: func.HttpRequest) -> func.HttpResponse:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                EmployeeID,
                FirstName,
                LastName,
                Salary,
                COALESCE(Bonus, 0) AS Bonus,
                RANK() OVER (
                    ORDER BY COALESCE(Bonus, 0) DESC
                ) AS BonusRank
            FROM Employee
            ORDER BY BonusRank
        """)

        rows = cursor.fetchall()

        employees = []

        for row in rows:
            employees.append({
                "employee_id": row.EmployeeID,
                "first_name": row.FirstName,
                "last_name": row.LastName,
                "salary": float(row.Salary),
                "bonus": float(row.Bonus),
                "bonus_rank": int(row.BonusRank)
            })

        conn.close()

        return func.HttpResponse(
            json.dumps(employees),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )  
 
# 6.	The employee with the highest base salary, and — separately — whether that same person also has the highest total compensation (salary + bonus). 
@app.route(route="reports/highest-compensation", methods=["GET"])
def highest_compensation(req: func.HttpRequest) -> func.HttpResponse:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Highest base salary
        cursor.execute("""
            SELECT TOP 1
                EmployeeID,
                FirstName,
                LastName,
                Salary,
                COALESCE(Bonus, 0) AS Bonus
            FROM Employee
            ORDER BY Salary DESC
        """)

        salary_row = cursor.fetchone()

        # Highest total compensation
        cursor.execute("""
            SELECT TOP 1
                EmployeeID,
                FirstName,
                LastName,
                Salary,
                COALESCE(Bonus, 0) AS Bonus,
                Salary + COALESCE(Bonus, 0) AS TotalCompensation
            FROM Employee
            ORDER BY TotalCompensation DESC
        """)

        compensation_row = cursor.fetchone()

        conn.close()

        highest_salary = {
            "employee_id": salary_row.EmployeeID,
            "first_name": salary_row.FirstName,
            "last_name": salary_row.LastName,
            "salary": float(salary_row.Salary),
            "bonus": float(salary_row.Bonus)
        }

        highest_compensation = {
            "employee_id": compensation_row.EmployeeID,
            "first_name": compensation_row.FirstName,
            "last_name": compensation_row.LastName,
            "salary": float(compensation_row.Salary),
            "bonus": float(compensation_row.Bonus),
            "total_compensation": float(
                compensation_row.TotalCompensation
            )
        }

        same_employee = (
            salary_row.EmployeeID == compensation_row.EmployeeID
        )

        result = {
            "highest_base_salary": highest_salary,
            "highest_total_compensation": highest_compensation,
            "same_employee": same_employee
        }

        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )   

    