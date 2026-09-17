import os
import psycopg2
from dotenv import load_dotenv


load_dotenv()


connection = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)


cursor = connection.cursor()


query = """
    SELECT timestamp
    FROM sensor_data
    WHERE field_id = 'FIELD001'
    ORDER BY timestamp
    LIMIT 20;
"""


cursor.execute(query)

rows = cursor.fetchall()


print("\n========== SENSOR TIMESTAMPS ==========\n")

for row in rows:
    print(row[0])


cursor.close()
connection.close()