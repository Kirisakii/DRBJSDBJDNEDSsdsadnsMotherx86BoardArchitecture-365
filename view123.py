import sqlite3

def print_db_contents(db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Retrieve the list of all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # Iterate through all tables and print their contents
    for table_name in tables:
        print(f"Table: {table_name[0]}")
        cursor.execute(f"SELECT * FROM {table_name[0]}")
        columns = [description[0] for description in cursor.description]
        print(f"Columns: {columns}")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        print("\n")  # Add a newline for better separation between tables
    
    # Close the connection to the database
    cursor.close()
    conn.close()

# Example usage
print_db_contents("db/welcome.db")
