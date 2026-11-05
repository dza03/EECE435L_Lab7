#!/usr/bin/python
import sqlite3


def connect_to_db():
    conn = sqlite3.connect('database.db')
    return conn


def create_db_table():
    try:
        conn = connect_to_db()
        conn.execute('''
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                country TEXT NOT NULL
            );
        ''')
        conn.commit()
        print("User table created successfully")
    except:
        print("User table creation failed - Maybe table already exists")
    finally:
        conn.close()


def insert_user(user):
    inserted_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, email, phone, address, country) VALUES (?, ?, ?, ?, ?)",
                    (user['name'], user['email'], user['phone'], user['address'], user['country']))
        conn.commit()
        inserted_user = get_user_by_id(cur.lastrowid)
    except:
        conn.rollback()
    finally:
        conn.close()
    return inserted_user


def get_users():
    users = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        # convert row objects to dictionary
        for i in rows:
            user = {}
            user["user_id"] = i["user_id"]
            user["name"] = i["name"]
            user["email"] = i["email"]
            user["phone"] = i["phone"]
            user["address"] = i["address"]
            user["country"] = i["country"]
            users.append(user)
    except:
        users = []
    finally:
        conn.close()
    return users


def get_user_by_id(user_id):
    user = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        # convert row object to dictionary
        user["user_id"] = row["user_id"]
        user["name"] = row["name"]
        user["email"] = row["email"]
        user["phone"] = row["phone"]
        user["address"] = row["address"]
        user["country"] = row["country"]
    except:
        user = {}
    finally:
        conn.close()
    return user


def update_user(user):
    updated_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE users SET name = ?, email = ?, phone = ?, address = ?, country = ? WHERE user_id = ?",
                    (user["name"], user["email"], user["phone"], user["address"], user["country"], user["user_id"],))
        conn.commit()
        # return the user
        updated_user = get_user_by_id(user["user_id"])
    except:
        conn.rollback()
        updated_user = {}
    finally:
        conn.close()
    return updated_user


def delete_user(user_id):
    message = {}
    try:
        conn = connect_to_db()
        conn.execute("DELETE from users WHERE user_id = ?", (user_id,))
        conn.commit()
        message["status"] = "User deleted successfully"
    except:
        conn.rollback()
        message["status"] = "Cannot delete user"
    finally:
        conn.close()
    return message


# ---------- NEW FOR LAB 7 ----------
# The users the database should contain the first time the app runs.
initial_users = [
    {
        "name": "John Doe",
        "email": "jondoe@gmail.com",
        "phone": "067765434567",
        "address": "John Doe Street, Innsbruck",
        "country": "Austria"
    },
    {
        "name": "Jane Smith",
        "email": "janesmith@gmail.com",
        "phone": "03123456",
        "address": "Hamra Street, Beirut",
        "country": "Lebanon"
    },
    {
        "name": "Ali Hassan",
        "email": "alihassan@gmail.com",
        "phone": "70987654",
        "address": "Bliss Street, Beirut",
        "country": "Lebanon"
    }
]


def init_db():
    # Create the table, and add the initial users only if the table is empty
    # (so running the app a second time does not add them twice).
    create_db_table()
    if len(get_users()) == 0:
        for user in initial_users:
            insert_user(user)


if __name__ == "__main__":
    init_db()
