import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
import pytz

# Function to get current date and time in Sri Lanka time zone
def get_sri_lanka_time():
    # Set Sri Lanka time zone (Asia/Colombo)
    sri_lanka_tz = pytz.timezone('Asia/Colombo')
    # Get current time in Sri Lanka
    return datetime.datetime.now(sri_lanka_tz)

# Function to get current date in Sri Lanka as string (YYYY-MM-DD)
def get_sri_lanka_date_str():
    return get_sri_lanka_time().strftime('%Y-%m-%d')

st.set_page_config(page_title="Swimming Attendance", layout="wide", 
                   page_icon="🏊‍♂️", initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-bottom: 1rem;
    }
    .card {
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        background-color: #f0f8ff;
    }
    .stat-card {
        text-align: center;
        padding: 1rem;
        border-radius: 8px;
        background-color: #1E88E5;
        color: white;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .stat-label {
        font-size: 1rem;
        opacity: 0.8;
    }
    .time-display {
        text-align: center;
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.markdown("<h1 class='main-header'>🏊‍♂️ Swimming Pool Attendance System</h1>", unsafe_allow_html=True)

# Display current Sri Lanka time
current_sl_time = get_sri_lanka_time()
st.markdown(f"<p class='time-display'>Current Time in Sri Lanka: {current_sl_time.strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)

# Dashboard metrics
col1, col2, col3 = st.columns(3)

# Load data for dashboard metrics
try:
    os.makedirs("data", exist_ok=True)
    students_file = "data/students.csv"
    attendance_file = "data/attendance.csv"
    
    if os.path.exists(students_file):
        students_df = pd.read_csv(students_file)
        student_count = len(students_df)
    else:
        student_count = 0
        
    if os.path.exists(attendance_file):
        attendance_df = pd.read_csv(attendance_file)
        total_attendances = len(attendance_df)
        
        # Use Sri Lanka date for filtering today's attendances
        today_sl = get_sri_lanka_date_str()
        today_attendances = len(attendance_df[attendance_df['Date'] == today_sl])
    else:
        total_attendances = 0
        today_attendances = 0
        
    with col1:
        st.markdown("""
        <div class="stat-card" style="background-color: #1E88E5;">
            <div class="stat-value">{}</div>
            <div class="stat-label">Registered Students</div>
        </div>
        """.format(student_count), unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="stat-card" style="background-color: #43A047;">
            <div class="stat-value">{}</div>
            <div class="stat-label">Today's Attendances</div>
        </div>
        """.format(today_attendances), unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="stat-card" style="background-color: #FB8C00;">
            <div class="stat-value">{}</div>
            <div class="stat-label">Total Attendances</div>
        </div>
        """.format(total_attendances), unsafe_allow_html=True)
except Exception as e:
    st.error(f"Error loading dashboard metrics: {e}")

# Welcome section
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<h2 class='sub-header'>Welcome to the Swimming Pool Attendance System</h2>", unsafe_allow_html=True)
st.markdown("""
This system helps you manage swimming pool attendance efficiently with QR code-based check-in.

**Use the sidebar to:**
- 🔐 Login as Administrator
- 📝 Register new students and generate QR codes
- 📲 Mark student attendance using ID or QR code
- 📊 View detailed attendance reports and analytics
""")
st.markdown("</div>", unsafe_allow_html=True)

# Recent activity - FIXED SECTION WITH SRI LANKA TIME
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<h2 class='sub-header'>Recent Activity</h2>", unsafe_allow_html=True)

try:
    # Check if both files exist
    if os.path.exists(attendance_file) and os.path.exists(students_file):
        attendance_df = pd.read_csv(attendance_file)
        students_df = pd.read_csv(students_file)
        
        if not attendance_df.empty:
            # Sort by date (most recent first) and take last 5
            attendance_df['Date'] = pd.to_datetime(attendance_df['Date'])
            recent_df = attendance_df.sort_values(['Date', 'TimeIn'], ascending=[False, False]).head(5)
            
            # Check if the attendance records already have names
            if 'Name' in recent_df.columns:
                recent_with_names = recent_df
            else:
                # Merge with student info to get names
                try:
                    # Make sure both DataFrames have the required columns
                    if 'StudentID' in recent_df.columns and 'StudentID' in students_df.columns and 'Name' in students_df.columns:
                        # Use suffixes to avoid column name conflicts
                        recent_with_names = pd.merge(recent_df, students_df[['StudentID', 'Name']], 
                                                    on='StudentID', how='left', suffixes=('_att', ''))
                    else:
                        st.warning("Some required columns are missing from the data files.")
                        if 'StudentID' not in recent_df.columns:
                            st.write("Missing StudentID in attendance records")
                        if 'StudentID' not in students_df.columns:
                            st.write("Missing StudentID in student records")
                        if 'Name' not in students_df.columns:
                            st.write("Missing Name in student records")
                        
                        # Create a placeholder DataFrame with a StudentID column
                        recent_with_names = recent_df.copy()
                        recent_with_names['Name'] = "Student " + recent_df['StudentID'].astype(str)
                except Exception as merge_error:
                    st.warning(f"Error merging data: {merge_error}")
                    recent_with_names = recent_df.copy()
                    recent_with_names['Name'] = "Student " + recent_df['StudentID'].astype(str)
            
            # Display in a more attractive format with Sri Lanka time zone
            for _, row in recent_with_names.iterrows():
                # Safely access the Name column with a fallback
                student_name = row.get('Name', f"Student {row['StudentID']}")
                
                # Format date and include time if available
                try:
                    date_str = row['Date'].strftime('%b %d, %Y')
                    time_info = ""
                    status = ""
                    
                    if 'TimeIn' in row and not pd.isna(row['TimeIn']):
                        time_info = f" at {row['TimeIn']}"
                    
                    if 'Status' in row and not pd.isna(row['Status']):
                        status_color = "#4CAF50" if row['Status'] == "In" else "#F44336"
                        status = f" <span style='color:{status_color};font-weight:bold;'>({row['Status']})</span>"
                    
                    st.markdown(f"**{student_name}** ({row['StudentID']}) checked in on {date_str}{time_info}{status}", unsafe_allow_html=True)
                except Exception as date_error:
                    # Fallback if date formatting fails
                    st.markdown(f"**{student_name}** ({row['StudentID']}) checked in recently")
            
            if len(recent_with_names) >= 5:
                st.markdown("*View full history in the Attendance Summary page*")
        else:
            st.info("No attendance records yet.")
    else:
        if not os.path.exists(attendance_file):
            st.info("No attendance records file found. Start marking attendance to see records.")
        if not os.path.exists(students_file):
            st.info("No student records file found. Please register students first.")
except Exception as e:
    st.error(f"Error displaying recent activity: {str(e)}")
    st.info("Recent activity will be available once students are registered and attendance is marked.")

st.markdown("</div>", unsafe_allow_html=True)
        
st.markdown("""
<div class='card' style='background-color: #e8f4f8;'>
    <h2 class='sub-header'>Quick Guide</h2>
    <ol>
        <li><strong>First time?</strong> Login as administrator (default: admin/1234)</li>
        <li><strong>Register students</strong> with their details and generate unique QR codes</li>
        <li><strong>Mark attendance</strong> by entering student ID or scanning their QR code</li>
        <li><strong>View reports</strong> to track attendance patterns and download data</li>
    </ol>
</div>
""", unsafe_allow_html=True)