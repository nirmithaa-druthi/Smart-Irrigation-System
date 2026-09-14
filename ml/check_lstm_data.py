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
    SELECT
        DATE(timestamp) AS date,
        COUNT(*) AS records
    FROM sensor_data
    WHERE field_id = 'FIELD001'
    GROUP BY DATE(timestamp)
    ORDER BY date;
"""

cursor.execute(query)

rows = cursor.fetchall()

print("\n========== DAILY SENSOR RECORDS ==========\n")

for date, count in rows:
    print(f"{date}  →  {count} records")

print(f"\nTotal days: {len(rows)}")
print(f"Total records: {sum(row[1] for row in rows)}")

cursor.close()
connection.close()