import sqlite3


DB_NAME = "company.db"


def create_database():

    connection = sqlite3.connect(DB_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            manager TEXT NOT NULL,
            leave_days INTEGER NOT NULL
        )
    """)

    employees = [
        (101, "Alex", "Engineering", "Sarah", 12),
        (102, "John", "Finance", "Mike", 8)
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO employees
        (employee_id, name, department, manager, leave_days)
        VALUES (?, ?, ?, ?, ?)
    """, employees)

    connection.commit()
    connection.close()

    print("Database created successfully.")


def get_employee(employee_id):

    connection = sqlite3.connect(DB_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT employee_id, name, department, manager, leave_days
        FROM employees
        WHERE employee_id = ?
    """, (employee_id,))

    employee = cursor.fetchone()

    connection.close()

    return employee


if __name__ == "__main__":

    create_database()

    employee = get_employee(101)

    print("\nEmployee:")
    print(employee)