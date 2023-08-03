import subprocess

# PostgreSQL database connection details
host = "localhost"
port = "5433"
database = "your_database_name"
user = "DB_USER"
password = "DB_PASSWORD"

# SQL statement
sql_statement = "INSERT INTO agent_table (agent, pub_did) VALUES ('Agent A', 'pub_did_1')"

# Construct the psql command
psql_command = [
    "psql",
    "-h",
    host,
    "-p",
    port,
    "-U",
    user
]

# Execute the psql command
psql_process = subprocess.run(psql_command, stdin=subprocess.PIPE)
psql_process = subprocess.run(sql_statement, stdin=subprocess.PIPE)
psql_process.communicate(input=str(password))
