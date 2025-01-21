import streamlit as st
import pandas as pd
import os

# Ensure the users file exists
USERS_FILE = 'users.csv'
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['username', 'password', 'name', 'surname', 'email'])

# Set up dashboard layout
st.set_page_config(page_title="Admin Dashboard", page_icon="📊", layout="wide")
st.title("Admin Dashboard")

# Tabs for dashboard features
analytics_tab, chat_tab, users_tab = st.tabs(["User Analytics", "Chat Summary", "Manage Users"])

# User Analytics Tab
with analytics_tab:
    st.header("User Analytics")
    
    # Load user data
    if os.path.exists(USERS_FILE):
        user_data = pd.read_csv(USERS_FILE)

        # Display basic stats
        st.subheader("User Statistics")
        st.metric("Total Users", len(user_data))
        st.metric("Unique Emails", user_data['email'].nunique())
        
        # Display user data table
        st.subheader("Registered Users")
        st.dataframe(user_data)
    else:
        st.error("No user data available.")

# Chat Summary Tab
with chat_tab:
    st.header("Chat Summary")

    if 'chat_history' in st.session_state and st.session_state['chat_history']:
        st.subheader("Recent Conversations")
        for i, chat in enumerate(st.session_state['chat_history'][-10:]):
            with st.expander(f"Message {i + 1} ({chat['role'].capitalize()}):"):
                st.write(chat['content'])
    else:
        st.info("No chat history available.")

# Manage Users Tab
with users_tab:
    st.header("Manage Users")

    # Load user data
    if os.path.exists(USERS_FILE):
        user_data = pd.read_csv(USERS_FILE)

        # Display and allow admin to delete users
        selected_user = st.selectbox("Select a User to Delete", user_data['username'])

        if st.button("Delete User"):
            user_data = user_data[user_data['username'] != selected_user]
            user_data.to_csv(USERS_FILE, index=False)
            st.success(f"User '{selected_user}' deleted successfully.")
    else:
        st.error("No user data available.")

# Footer
st.markdown("---")
st.caption("Admin Dashboard - Built with Streamlit")
