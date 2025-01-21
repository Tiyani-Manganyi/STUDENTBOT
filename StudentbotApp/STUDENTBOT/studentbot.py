import os
import hashlib
import csv

USERS_FILE = 'users.csv'

def hash_password(password):
    """Hash the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, name, surname, email):
    """Register a new user."""
    hashed_password = hash_password(password)
    with open(USERS_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, hashed_password, name, surname, email])

def login_user(username, password):
    """Authenticate a user."""
    hashed_password = hash_password(password)
    if not os.path.exists(USERS_FILE):
        return False
    with open(USERS_FILE, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == username and row[1] == hashed_password:
                return True
    return False

def user_exists(username):
    """Check if a user exists."""
    if not os.path.exists(USERS_FILE):
        return False
    with open(USERS_FILE, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == username:
                return True
    return False

def get_user_info(username):
    """Retrieve user information."""
    if not os.path.exists(USERS_FILE):
        return None
    with open(USERS_FILE, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == username:
                return {
                    'name': row[2],
                    'surname': row[3],
                    'email': row[4]
                }
    return None

def update_user_info(username, new_name, new_surname, new_email, new_password):
    """Update user information."""
    if not os.path.exists(USERS_FILE):
        return False
    updated = False
    rows = []
    with open(USERS_FILE, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == username:
                hashed_password = hash_password(new_password) if new_password else row[1]
                rows.append([username, hashed_password, new_name, new_surname, new_email])
                updated = True
            else:
                rows.append(row)
    if updated:
        with open(USERS_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
    return updated

def create_users_file():
    """Create the users file if it doesn't exist."""
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['username', 'password', 'name', 'surname', 'email'])
