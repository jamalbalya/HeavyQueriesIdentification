import tkinter as tk
import psycopg2
import mysql.connector
import threading

# Default threshold value in milliseconds (customize as needed)
DEFAULT_THRESHOLD = 100

# Function to identify heavy queries in PostgreSQL database
def identify_heavy_queries_postgres(database_url, threshold, output_text):
    try:
        with psycopg2.connect(database_url) as connection:
            cursor = connection.cursor()

            # Enable pg_stat_statements extension (if not enabled already)
            cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_stat_statements;")
            connection.commit()

            # Fetch heavy queries
            cursor.execute(f"""
                SELECT query, total_time, calls
                FROM pg_stat_statements
                WHERE total_time > {threshold}
                ORDER BY total_time DESC;
            """)

            heavy_queries = cursor.fetchall()

            if heavy_queries:
                output_text.insert(tk.END, "PostgreSQL - Heavy Queries:\n")
                for query, total_time, calls in heavy_queries:
                    output_text.insert(tk.END, f"Query: {query}\n")
                    output_text.insert(tk.END, f"Total Time: {total_time}\n")
                    output_text.insert(tk.END, f"Number of Calls: {calls}\n")
                    output_text.insert(tk.END, "-" * 50 + "\n")
            else:
                output_text.insert(tk.END, "No heavy queries found in PostgreSQL.\n")

    except Exception as e:
        error_message = f"PostgreSQL Error: {str(e)}\n"
        output_text.insert(tk.END, error_message)

# Function to identify heavy queries in MySQL database
def identify_heavy_queries_mysql(database_config, threshold, output_text):
    try:
        with mysql.connector.connect(**database_config) as connection:
            cursor = connection.cursor()

            # Enable performance_schema (if not enabled already)
            cursor.execute("SET GLOBAL performance_schema = ON;")

            # Fetch heavy queries
            cursor.execute(f"""
                    SELECT query, exec_count, total_latency
                    FROM performance_schema.events_statements_summary_by_digest
                    WHERE total_latency > {threshold}
                    ORDER BY total_latency DESC;
                """)

            heavy_queries = cursor.fetchall()

            if heavy_queries:
                output_text.insert(tk.END, "MySQL - Heavy Queries:\n")
                for query, exec_count, total_latency in heavy_queries:
                    output_text.insert(tk.END, f"Query: {query}\n")
                    output_text.insert(tk.END, f"Execution Count: {exec_count}\n")
                    output_text.insert(tk.END, f"Total Latency: {total_latency}\n")
                    output_text.insert(tk.END, "-" * 50 + "\n")
            else:
                output_text.insert(tk.END, "No heavy queries found in MySQL.\n")

    except Exception as e:
        error_message = f"MySQL Error: {str(e)}\n"
        output_text.insert(tk.END, error_message)


# Function to process heavy queries when the button is clicked
def process_heavy_queries():
    try:
        # Get user input from the GUI
        db_type = selected_db.get()
        db_url = url_entry.get()
        db_host = host_entry.get()
        db_port = port_entry.get()
        db_database = database_entry.get()
        db_user = user_entry.get()
        db_password = password_entry.get()

        # Clear the output_text widget before running the heavy query identification
        output_text.config(state=tk.NORMAL)
        output_text.delete(1.0, tk.END)

        # Call the heavy query identification functions based on the selected database type
        if db_type == "PostgreSQL":
            identify_heavy_queries_postgres(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}", DEFAULT_THRESHOLD, output_text)
        else:
            db_config = {
                'host': db_host,
                'port': db_port,
                'database': db_database,
                'user': db_user,
                'password': db_password,
            }
            identify_heavy_queries_mysql(db_config, DEFAULT_THRESHOLD, output_text)

    except Exception as e:
        error_message = f"Error: {str(e)}\n"
        output_text.insert(tk.END, error_message)

    finally:
        output_text.config(state=tk.DISABLED)


# Function to start monitoring heavy queries
def start_monitoring():
    global stop_monitoring_flag

    stop_monitoring_flag = False
    monitor_button.config(state=tk.DISABLED)  # Disable the monitoring button while monitoring

    # Function to run the monitoring in intervals
    def monitor_interval():
        if not stop_monitoring_flag:
            try:
                # Clear the output_text widget before running the heavy query identification
                output_text.config(state=tk.NORMAL)
                output_text.delete(1.0, tk.END)

                # Get user input from the GUI
                db_type = selected_db.get()
                db_url = url_entry.get()
                db_host = host_entry.get()
                db_port = port_entry.get()
                db_database = database_entry.get()
                db_user = user_entry.get()
                db_password = password_entry.get()
                db_threshold = DEFAULT_THRESHOLD  # Use the default threshold value

                # Call the heavy query identification functions based on the selected database type
                if db_type == "PostgreSQL":
                    identify_heavy_queries_postgres(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}", db_threshold, output_text)
                else:
                    db_config = {
                        'host': db_host,
                        'port': db_port,
                        'database': db_database,
                        'user': db_user,
                        'password': db_password,
                    }
                    identify_heavy_queries_mysql(db_config, db_threshold, output_text)

            except Exception as e:
                error_message = f"Error during monitoring: {str(e)}\n"
                output_text.insert(tk.END, error_message)

            output_text.config(state=tk.DISABLED)

            if not stop_monitoring_flag:
                # Repeat the monitoring after a 5-second interval
                root.after(5000, monitor_interval)
        else:
            # Re-enable the monitoring button after stopping
            monitor_button.config(state=tk.NORMAL)

    # Start the monitoring loop
    monitor_interval()

# Function to stop monitoring heavy queries
def stop_monitoring():
    global stop_monitoring_flag
    stop_monitoring_flag = True

# Function to clear the output_text widget
def clear_output_text():
    output_text.config(state=tk.NORMAL)
    output_text.delete(1.0, tk.END)
    output_text.config(state=tk.DISABLED)

# Function to close the main window and destroy all connections
def close_window():
    global stop_monitoring_flag

    # Stop monitoring if it's running
    stop_monitoring_flag = True

    # Close the main window
    root.destroy()

# Create the main GUI window
root = tk.Tk()
root.title("Heavy Query Identification By Jamal Balya v1.0")
root.geometry("800x850")

# Function to center the main window on the screen
def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"+{x}+{y}")

# Center the main window on the screen
center_window(root)

# Create a label for selecting the database type
db_type_label = tk.Label(root, text="Select Database Type:")
db_type_label.pack()

# Create a variable to store the selected database type
selected_db = tk.StringVar()
selected_db.set("PostgreSQL")

# Create radio buttons to select the database type (PostgreSQL or MySQL)
postgres_radio = tk.Radiobutton(root, text="PostgreSQL", variable=selected_db, value="PostgreSQL")
postgres_radio.pack()

mysql_radio = tk.Radiobutton(root, text="MySQL", variable=selected_db, value="MySQL")
mysql_radio.pack()

# Create input fields and labels for database connections
url_label = tk.Label(root, text="URL:")
url_label.pack()
url_entry = tk.Entry(root)
url_entry.pack()

host_label = tk.Label(root, text="Host:")
host_label.pack()
host_entry = tk.Entry(root)
host_entry.pack()

port_label = tk.Label(root, text="Port:")
port_label.pack()
port_entry = tk.Entry(root)
port_entry.pack()

database_label = tk.Label(root, text="Database:")
database_label.pack()
database_entry = tk.Entry(root)
database_entry.pack()

user_label = tk.Label(root, text="User Authentication:")
user_label.pack()
user_entry = tk.Entry(root)
user_entry.pack()

password_label = tk.Label(root, text="Password Authentication:")
password_label.pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

# Create a text widget to display heavy query information
output_text = tk.Text(root, wrap=tk.WORD, state=tk.DISABLED)
output_text.pack(expand=True, fill=tk.BOTH)

# Create a button to trigger heavy query identification
process_button = tk.Button(root, text="Process Heavy Queries", command=process_heavy_queries)
process_button.pack()

# Create buttons for monitoring heavy queries
monitor_button = tk.Button(root, text="Start Monitoring", command=lambda: threading.Thread(target=start_monitoring).start())
monitor_button.pack()

stop_button = tk.Button(root, text="Stop Monitoring", command=stop_monitoring)
stop_button.pack()

# Create a button to clear the output_text widget
clear_button = tk.Button(root, text="Clear", command=clear_output_text)
clear_button.pack()

# Create a button to close the window
close_button = tk.Button(root, text="Close", command=close_window)
close_button.pack()

# Run the GUI main loop
root.mainloop()