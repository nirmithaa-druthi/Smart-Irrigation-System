import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

try:
    conn = psycopg2.connect(
        host="localhost",
        database="smart_irrigation",
        user="postgres",
        password=os.getenv("POSTGRES_PASSWORD"),
        port="5432"
    )

    print("Database connection successful!")

    conn.close()

except Exception as e:
    print("Database connection failed!")
    print(e)