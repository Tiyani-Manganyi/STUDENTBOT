import streamlit as st
import pandas as pd
import os
import hashlib
import csv
import time
from groq import Groq

# Define constants
USERS_FILE = 'users.csv'
GROQ_API_KEY = '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'

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, name, surname, email):
    hashed_password = hash_password(password)
    with open(USERS_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, hashed_password, name, surname, email])

def login_user(username, password):
    hashed_password = hash_password(password)
    with open(USERS_FILE, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == username and row[1] == hashed_password:
                return True
    return False

def user_exists(username):
    with open(USERS_FILE, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == username:
                return True
    return False

def get_user_info(username):
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

def create_users_file():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['username', 'password', 'name', 'surname', 'email'])

# Create users file if it doesn't exist
create_users_file()

# Set page configuration
st.set_page_config(page_title="StudentBot App", page_icon="📘", layout="wide")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'name' not in st.session_state:
    st.session_state.name = ''
if 'surname' not in st.session_state:
    st.session_state.surname = ''
if 'email' not in st.session_state:
    st.session_state.email = ''
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Authentication
if not st.session_state.logged_in:
    st.sidebar.title("Authentication")

    with st.sidebar.expander("Register"):
        reg_username = st.text_input("Username", key="reg_username")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_name = st.text_input("Name", key="reg_name")
        reg_surname = st.text_input("Surname", key="reg_surname")
        reg_email = st.text_input("Email", key="reg_email")
        if st.button("Register"):
            if not user_exists(reg_username):
                register_user(reg_username, reg_password, reg_name, reg_surname, reg_email)
                st.success("Registered successfully.")
            else:
                st.error("Username already exists.")

    with st.sidebar.expander("Login"):
        log_username = st.text_input("Username", key="log_username")
        log_password = st.text_input("Password", type="password", key="log_password")
        if st.button("Login"):
            if login_user(log_username, log_password):
                st.session_state.logged_in = True
                st.session_state.username = log_username
                user_info = get_user_info(log_username)
                st.session_state.name = user_info['name'].capitalize()
                st.session_state.surname = user_info['surname'].capitalize()
                st.session_state.email = user_info['email']
                st.success("Logged in successfully.")
            else:
                st.error("Invalid credentials.")

# Dashboard
if st.session_state.logged_in:
    st.sidebar.title(f"Welcome, {st.session_state.name} {st.session_state.surname}")

    with st.sidebar.expander("Profile"):
        st.write(f"**Name:** {st.session_state.name}")
        st.write(f"**Email:** {st.session_state.email}")

    with st.sidebar.expander("Update Profile"):
        new_name = st.text_input("New Name", value=st.session_state.name, key="new_name")
        new_surname = st.text_input("New Surname", value=st.session_state.surname, key="new_surname")
        new_email = st.text_input("New Email", value=st.session_state.email, key="new_email")
        new_password = st.text_input("New Password", type="password", key="new_password")
        if st.button("Update Profile"):
            update_user_info(st.session_state.username, new_name, new_surname, new_email, new_password)
            st.session_state.name = new_name
            st.session_state.surname = new_surname
            st.session_state.email = new_email
            st.success("Profile updated successfully.")

    # Tabs for dashboard
    tabs = st.tabs(["Dashboard", "Chat Assistant", "Manage Users"])

    with tabs[0]:
        st.header("User Analytics")
        if os.path.exists(USERS_FILE):
            user_data = pd.read_csv(USERS_FILE)
            st.metric("Total Users", len(user_data))
            st.metric("Unique Emails", user_data['email'].nunique())
            st.dataframe(user_data)
        else:
            st.error("No user data available.")

    with tabs[1]:
        st.header("Chat Assistant")
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if question := st.chat_input("Ask a question"):
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            chat_completion = client.chat.completions.create(
                messages=[{"role": "system", "content": "You are a student assistant. Answer academic queries only."}] + st.session_state.chat_history,
                model="llama3-8b-8192",
                temperature=0.5,
                max_tokens=1024,
                stop=None
            )
            answer = chat_completion.choices[0].message.content
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            with st.chat_message("assistant"):
                st.markdown(answer)

    with tabs[2]:
        st.header("Manage Users")
        if os.path.exists(USERS_FILE):
            user_data = pd.read_csv(USERS_FILE)
            selected_user = st.selectbox("Select User", user_data['username'])
            if st.button("Delete User"):
                user_data = user_data[user_data['username'] != selected_user]
                user_data.to_csv(USERS_FILE, index=False)
                st.success(f"User '{selected_user}' deleted.")
        else:
            st.error("No user data available.")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.success("Logged out successfully.")
