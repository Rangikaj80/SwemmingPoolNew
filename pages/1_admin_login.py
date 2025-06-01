import streamlit as st
import pandas as pd
import time
import os

st.set_page_config(page_title="Admin Login", page_icon="🔐", layout="centered")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .login-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
        padding: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "login_attempts" not in st.session_state:
    st.session_state.login_attempts = 0
if "lockout_until" not in st.session_state:
    st.session_state.lockout_until = None

# Create admin credentials file if it doesn't exist
os.makedirs("data", exist_ok=True)
admin_file = "data/admin.csv"

# Reset admin credentials to the specified values
if not os.path.exists(admin_file) or True:  # Always reset to ensure correct credentials
    admin_df = pd.DataFrame([{"username": "Jayanath", "password": "Rangika123"}])
    admin_df.to_csv(admin_file, index=False)

# Load admin credentials
admin_df = pd.read_csv(admin_file)
admin_credentials = dict(zip(admin_df["username"], admin_df["password"]))

st.markdown("<h1 class='main-header'>🔐 Administrator Login</h1>", unsafe_allow_html=True)

# Display login form or success message
if st.session_state.logged_in:
    st.success("✅ You are logged in as Administrator")
    
    # Add option to log out
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.login_attempts = 0
        st.session_state.lockout_until = None
        st.rerun()
    
    # Show admin options
    st.subheader("Administrator Options")
    with st.expander("Change Password"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.button("Update Password"):
            if current_password == admin_credentials["Jayanath"]:
                if new_password == confirm_password and new_password:
                    admin_df.loc[admin_df["username"] == "Jayanath", "password"] = new_password
                    admin_df.to_csv(admin_file, index=False)
                    st.success("Password updated successfully!")
                    admin_credentials["Jayanath"] = new_password
                else:
                    st.error("New passwords don't match or password is empty")
            else:
                st.error("Current password is incorrect")
else:
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    
    # Display login credentials for reference (you can remove this in production)
    st.info("Login with username: Jayanath and password: Rangika123")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        login_button = st.button("Login")
    with col2:
        reset_button = st.button("Reset")
    
    if reset_button:
        st.session_state.login_attempts = 0
        st.rerun()
        
    if login_button:
        if username in admin_credentials and password == admin_credentials[username]:
            st.session_state.logged_in = True
            st.session_state.login_attempts = 0
            st.success("Login successful!")
            st.balloons()
            time.sleep(1)
            st.rerun()
        else:
            st.session_state.login_attempts += 1
            remaining_attempts = 3 - st.session_state.login_attempts
            
            if remaining_attempts > 0:
                st.error(f"Invalid credentials. {remaining_attempts} attempts remaining.")
            else:
                st.session_state.lockout_until = time.time() + 30  # 30 second lockout
                st.error("Too many failed attempts. Please try again in 30 seconds.")
    st.markdown("</div>", unsafe_allow_html=True)