from typing import List
from person import Person
import mysql.connector
from os import environ
import time # ***חדש: ייבוא מודול time***
from flask import Response

db_user = environ.get('DB_USER')
db_pass = environ.get('DB_PASS')
db_host = environ.get('DB_HOST')
db_name = environ.get('DB_NAME')

config = {
    "host": db_host,
    "user": db_user,
    "password": db_pass,
    "database": db_name,
    "port": 3306
}

# ***חדש: פונקציה עזר להתחברות עם Retry***
def _connect_with_retry(max_retries=20, retry_delay=3): # הגדלתי את ה-retries ו-delay
    for i in range(max_retries):
        try:
            cnx = mysql.connector.connect(**config)
            if cnx.is_connected():
                print(f"Successfully connected to DB on attempt {i+1}")
                return cnx
        except mysql.connector.errors.InterfaceError as err:
            print(f"Attempt {i+1} failed to connect to DB: {err}")
            if i < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Could not connect to the database.")
                raise # זרוק את השגיאה אם כל הניסיונות נכשלו
    return None # לא אמור להגיע לכאן אם raise מופעל

def demo_data() -> List[Person]:
    person1 = Person(1, "John", "Doe", 30, "76 Ninth Avenue St, New York, NY 10011, USA", "Google")
    person2 = Person(2, "Jane", "Doe", 28, "15 Aabogade St, Aarhus, Denmark 8200", "Microsoft")
    person3 = Person(3, "Jack", "Doe", 25, "98 Yigal Alon St, Tel Aviv, Israel 6789141", "Amazon")

    return [person1, person2, person3]

def db_data() -> List[Person]:
    if not db_host:
        return demo_data()

    if not (db_user and db_pass):
        raise Exception("DB_USER and DB_PASS are not set")

    # ***שונה: השתמש בפונקציית _connect_with_retry***
    cnx = _connect_with_retry() 
    if cnx is None: # אם החיבור נכשל לאחר retries
        return [] # או זרוק שגיאה מתאימה, או תחזיר demo_data

    result = []
    if cnx.is_connected():
        cursor = cnx.cursor()
        try:
            cursor.execute("SELECT * FROM people")
            for item in cursor:
                result.append(Person(item[0], item[1], item[2], item[3], item[4], item[5]))
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()
    return result

def db_delete(id: int) -> Response:
    if not db_host:
        return Response(status=200)

    # ***שונה: השתמש בפונקציית _connect_with_retry***
    cnx = _connect_with_retry()
    if cnx is None:
        return Response(status=500, response="Failed to connect to database for delete operation") # החזר שגיאה מתאימה

    status = 200
    if cnx.is_connected():
        cursor = cnx.cursor()
        try:
            cursor.execute(f"DELETE FROM people WHERE id = {id}")
            cnx.commit()
        except Exception as e: # תפוס שגיאה ספציפית יותר
            print(f"Error deleting person: {e}")
            status = 404
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()
    return Response(status=status)

def db_add(person: Person) -> Response:
    if not db_host:
        return Response(status=200)

    # ***שונה: השתמש בפונקציית _connect_with_retry***
    cnx = _connect_with_retry()
    if cnx is None:
        return Response(status=500, response="Failed to connect to database for add operation") # החזר שגיאה מתאימה

    status = 200
    personId = 0
    if cnx.is_connected():
        cursor = cnx.cursor()
        try:
            cursor.execute(f"INSERT INTO people (firstName, lastName, age, address, workplace) VALUES ('{person.first_name}', '{person.last_name}', {person.age}, '{person.address}', '{person.workplace}')")
            cnx.commit()
            personId = cursor.lastrowid
        except Exception as e: # תפוס שגיאה ספציפית יותר
            print(f"Error adding person: {e}")
            status = 404
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()
    return Response(status=status, response=str(personId))

def health_check() -> bool:
    if not db_host:
        return True

    # ***שונה: לולאת retry ובדיקת קיום טבלה***
    max_health_retries = 10 # מספר ניסיונות לבדיקת health
    health_retry_delay = 5 # השהייה בין ניסיונות

    for i in range(max_health_retries):
        try:
            cnx = _connect_with_retry(max_retries=1, retry_delay=0) # נסה להתחבר פעם אחת
            if cnx:
                cursor = cnx.cursor()
                try:
                    # בדוק אם הטבלה 'people' קיימת
                    cursor.execute("SHOW TABLES LIKE 'people'")
                    if cursor.fetchone():
                        print(f"Health check: Table 'people' exists on attempt {i+1}.")
                        return True
                    else:
                        print(f"Health check: Table 'people' does not exist on attempt {i+1}. Retrying...")
                finally:
                    if cnx.is_connected():
                        cursor.close()
                        cnx.close()
            else:
                print(f"Health check: Could not connect to DB on attempt {i+1}. Retrying...")
        except Exception as e:
            print(f"Health check connection or table check failed on attempt {i+1}: {e}")

        if i < max_health_retries - 1:
            time.sleep(health_retry_delay)
        else:
            print("Health check: Max retries reached. Table 'people' not found or DB not ready.")
    return False