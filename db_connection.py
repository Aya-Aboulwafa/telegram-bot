import psycopg2
import pandas as pd

# Define your connection parameters
connection_params = {
    'dbname': 'postgres',
    'user': 'postgres.lqqgdcrwqjdnitylujub',
    'password': 'Tele@2#Data',
    'host': 'aws-0-eu-central-1.pooler.supabase.com',
    'port': '6543'
}

# Establish the connection and load data into DataFrame
try:
    connection = psycopg2.connect(**connection_params)
    query = "SELECT * FROM messages;"  # Replace with your table name

    df = pd.read_sql(query, connection)
    print("Data loaded into DataFrame successfully")

    # Save the DataFrame to a CSV file
    df.to_csv('output.csv', index=False)
    print("Data saved to output.csv successfully")

except Exception as error:
    print(f"Error: {error}")

finally:
    if connection:
        connection.close()
        print("PostgreSQL connection is closed")

# Perform some basic analysis (optional)
print(df.describe())
print(df.head())