import streamlit as st
import pandas as pd
import time
import os
import datetime
import pytz

# Function to get current date and time in Sri Lanka time zone
def get_sri_lanka_time():
    # Set Sri Lanka time zone (Asia/Colombo)
    sri_lanka_tz = pytz.timezone('Asia/Colombo')
    # Get current time in Sri Lanka
    return datetime.datetime.now(sri_lanka_tz)

# Function to get current timestamp in seconds (Sri Lanka time)
def get_sri_lanka_timestamp():
    return get_sri_lanka_time().timestamp()

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
    .time-display {
        text-align: center;
        font-size: 0.9rem;
        color: #555;
        margin-bottom: 15px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #f1f3f4;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5;
        color: white;
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

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)
admin_file = "data/admin.csv"

# Initialize admin credentials file if it doesn't exist
if not os.path.exists(admin_file):
    admin_df = pd.DataFrame([{"username": "Jayanath", "password": "Rangika123", "role": "admin"}])
    admin_df.to_csv(admin_file, index=False)
else:
    # Load existing credentials
    admin_df = pd.read_csv(admin_file)
    # Ensure role column exists
    if "role" not in admin_df.columns:
        admin_df["role"] = "admin"
        admin_df.to_csv(admin_file, index=False)

# Title
st.markdown("<h1 class='main-header'>🏊‍♂️ Swimming Pool Management</h1>", unsafe_allow_html=True)

# Display current Sri Lanka time
current_sl_time = get_sri_lanka_time()
st.markdown(f"<p class='time-display'>Current Time in Sri Lanka: {current_sl_time.strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)

# Display login form or success message
if st.session_state.logged_in:
    st.success(f"✅ You are logged in as Administrator")
    
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
            # Get username of the current admin
            admin_df = pd.read_csv(admin_file)
            admin_records = admin_df[admin_df["role"] == "admin"]
            
            if not admin_records.empty:
                admin_username = admin_records.iloc[0]["username"]
                admin_password = admin_records.iloc[0]["password"]
                
                if current_password == admin_password:
                    if new_password == confirm_password and new_password:
                        admin_df.loc[admin_df["username"] == admin_username, "password"] = new_password
                        admin_df.to_csv(admin_file, index=False)
                        st.success("Password updated successfully!")
                    else:
                        st.error("New passwords don't match or password is empty")
                else:
                    st.error("Current password is incorrect")
            else:
                st.error("No admin account found")
else:
    # Check if user is locked out
    if st.session_state.lockout_until and get_sri_lanka_timestamp() < st.session_state.lockout_until:
        remaining_time = int(st.session_state.lockout_until - get_sri_lanka_timestamp())
        st.error(f"Account is locked due to too many failed attempts. Please try again in {remaining_time} seconds.")
    else:
        # If lockout period is over, reset lockout
        if st.session_state.lockout_until:
            st.session_state.lockout_until = None
            st.session_state.login_attempts = 0
        
        # Create tabs for login and signup
        login_tab, signup_tab = st.tabs(["Login", "Sign Up"])
        
        # Login Tab
        with login_tab:
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)
            
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                login_button = st.button("Login")
            with col2:
                reset_button = st.button("Reset")
            
            if reset_button:
                st.session_state.login_attempts = 0
                st.rerun()
                
            if login_button:
                # Load the latest credentials
                admin_df = pd.read_csv(admin_file)
                
                # Check credentials
                user_match = admin_df[(admin_df["username"] == username) & (admin_df["password"] == password)]
                
                if not user_match.empty:
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
                        st.session_state.lockout_until = get_sri_lanka_timestamp() + 30  # 30 second lockout
                        st.error("Too many failed attempts. Please try again in 30 seconds.")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Signup Tab
        with signup_tab:
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)
            st.subheader("Create New Account")
            
            new_username = st.text_input("Username", key="signup_username")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            signup_button = st.button("Create Account")
            
            if signup_button:
                if new_username and new_password:
                    if new_password != confirm_password:
                        st.error("Passwords don't match")
                    else:
                        # Load the latest admin data
                        admin_df = pd.read_csv(admin_file)
                        
                        # Check if username already exists
                        if new_username in admin_df["username"].values:
                            st.error("Username already exists. Please choose another username.")
                        else:
                            # Add new user
                            new_user = pd.DataFrame([{"username": new_username, "password": new_password, "role": "user"}])
                            admin_df = pd.concat([admin_df, new_user], ignore_index=True)
                            admin_df.to_csv(admin_file, index=False)
                            st.success("Account created successfully! You can now log in.")
                else:
                    st.error("Username and password are required")
            st.markdown("</div>", unsafe_allow_html=True)