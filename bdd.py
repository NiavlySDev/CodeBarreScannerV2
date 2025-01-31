from Params import *
import mysql.connector
import json

connection = None

def getconnection():
    global connection
    if connection is None:
        connection = mysql.connector.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
    return connection


def start():
    conn = getconnection()


def stop():
    global connection
    if connection is not None:
        connection.close()
        connection = None


def loadfrombdd():
    conn = getconnection()
    cursor = conn.cursor(dictionary=True)

    # SQL query to fetch all the data from the "articles" table
    query = "SELECT * FROM articles"
    cursor.execute(query)

    # Fetch all rows from the result and convert to a dictionary using the 'codeBarre' as the key
    rows = cursor.fetchall()
    data_dict = {row['codeBarre']: row for row in rows}

    # Save the data into the output.json file
    with open("output.json", "w", encoding="utf-8") as file:
        json.dump(data_dict, file, ensure_ascii=False, indent=4)

    # Close the cursor
    cursor.close()


def savetobdd():
    conn = getconnection()
    cursor = conn.cursor()

    # Read data from output.json
    with open("output.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    # SQL query for inserting data into the database
    query = """
        INSERT INTO articles (codeBarre, marque, nom, type, image, nombre)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            marque=VALUES(marque),
            nom=VALUES(nom),
            type=VALUES(type),
            image=VALUES(image),
            nombre=VALUES(nombre)
    """

    # Iterate through data and insert into the database
    for key, values in data.items():
        cursor.execute(query, (
            key,
            values.get("marque"),
            values.get("nom"),
            values.get("type"),
            values.get("image"),
            values.get("nombre"),
        ))

    # Commit changes and close cursor
    conn.commit()
    cursor.close()


