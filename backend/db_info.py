import sqlite3

conn = sqlite3.connect('task.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in database:", tables)

# Get users table structure
cursor.execute("PRAGMA table_info(users)")
users_structure = cursor.fetchall()
print("\nUsers table structure:")
for col in users_structure:
    print(f"  {col[1]} ({col[2]}) - Primary Key: {col[5]}, Not Null: {col[3]}")

# Get tasks table structure
cursor.execute("PRAGMA table_info(tasks)")
tasks_structure = cursor.fetchall()
print("\nTasks table structure:")
for col in tasks_structure:
    print(f"  {col[1]} ({col[2]}) - Primary Key: {col[5]}, Not Null: {col[3]}")

# Get sample data
cursor.execute("SELECT * FROM users LIMIT 3")
users_data = cursor.fetchall()
print(f"\nSample users data ({len(users_data)} rows):")
for user in users_data:
    print(f"  {user}")

cursor.execute("SELECT * FROM tasks LIMIT 3")
tasks_data = cursor.fetchall()
print(f"\nSample tasks data ({len(tasks_data)} rows):")
for task in tasks_data:
    print(f"  {task}")

conn.close() 