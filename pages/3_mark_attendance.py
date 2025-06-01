import streamlit as st
import pandas as pd
import os
import datetime
import qrcode
from PIL import Image
import io
import time
import numpy as np

st.set_page_config(page_title="Mark Attendance", page_icon="📋", layout="wide")

# Initialize session state variables
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False
if "last_student_id" not in st.session_state:
    st.session_state.last_student_id = None
if "last_action_time" not in st.session_state:
    st.session_state.last_action_time = None

# Callback function to clear the input
def set_clear_input_flag():
    st.session_state.clear_input = True

# Check login status
if not st.session_state.get("logged_in", False):
    st.error("⚠️ Unauthorized access. Please login as administrator first.")
    st.stop()

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
        background-color: #a0bdd9;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
    }
    .success-msg {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d4edda;
        color: #155724;
        margin: 1rem 0;
    }
    .status-in {
        background-color: #d4edda;
        color: #155724;
        padding: 8px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    .status-out {
        background-color: #f8d7da;
        color: #721c24;
        padding: 8px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    .metric-card {
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 15px;
    }
    .in-metric {
        background-color: #d1f7c4;
        border-left: 5px solid #4caf50;
    }
    .out-metric {
        background-color: #ffecb3;
        border-left: 5px solid #ff9800;
    }
    .total-metric {
        background-color: #bbdefb;
        border-left: 5px solid #2196f3;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #0D47A1;
    }
    .metric-label {
        color: #333;
        font-size: 14px;
        font-weight: 500;
    }
    .student-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #ffffff;
        margin: 10px 0;
        border-left: 5px solid #1976d2;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .student-card h3 {
        color: #1565c0;
        margin-bottom: 15px;
        font-size: 20px;
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 10px;
    }
    .student-card p {
        color: #333;
        margin-bottom: 8px;
        font-size: 15px;
    }
    .student-card strong {
        color: #0D47A1;
    }
    .input-container {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-bottom: 15px;
    }
    /* Quick search styles */
    .stTextInput input {
        font-size: 18px;
        padding: 12px !important;
    }
    /* For better table display */
    .dataframe {
        font-size: 14px !important;
    }
    .dataframe th {
        background-color: #e6f2ff !important;
        color: #0D47A1 !important;
    }
    /* Auto-focusing style */
    .auto-focus {
        border: 2px solid #1E88E5 !important;
        box-shadow: 0 0 8px rgba(30, 136, 229, 0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

# File paths
APP_PATH = "F:/attendance_app"  # Using forward slashes for path compatibility
DATA_DIR = os.path.join(APP_PATH, "data")
QR_FOLDER = os.path.join(APP_PATH, "qr_codes")
DATA_PATH = os.path.join(DATA_DIR, "students.csv")
ATTENDANCE_PATH = os.path.join(DATA_DIR, "attendance.csv")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

# App title
st.markdown("<h1 class='main-header'>📋 Mark Attendance</h1>", unsafe_allow_html=True)

# Function to mark attendance with in/out tracking
def mark_attendance(student_id):
    try:
        # Check if student exists
        if not os.path.exists(DATA_PATH):
            return False, "No students registered in the system."
        
        # Load student data with explicit encoding to handle special characters
        students_df = pd.read_csv(DATA_PATH, encoding='utf-8')
        
        # Case-insensitive matching for student ID
        student_found = False
        for idx, row in students_df.iterrows():
            if str(row['StudentID']).strip().lower() == str(student_id).strip().lower():
                student_id = row['StudentID']  # Use the exact case from the database
                student_found = True
                break
                
        if not student_found:
            return False, f"Student ID {student_id} not found in the system."
        
        # Get student name
        student_name = students_df.loc[students_df['StudentID'] == student_id, 'Name'].values[0]
        
        # Create or load attendance dataframe with new schema for in/out tracking
        if os.path.exists(ATTENDANCE_PATH):
            att_df = pd.read_csv(ATTENDANCE_PATH, encoding='utf-8')
            
            # Check if the dataframe has the new columns, if not, add them
            if 'TimeOut' not in att_df.columns:
                att_df['TimeOut'] = ""
            if 'Status' not in att_df.columns:
                att_df['Status'] = "In"
                
        else:
            att_df = pd.DataFrame(columns=["StudentID", "Name", "Date", "TimeIn", "TimeOut", "Status"])
        
        # Get current date and time
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        
        # Check if student has an entry for today
        today_records = att_df[(att_df['StudentID'] == student_id) & (att_df['Date'] == today)]
        
        if today_records.empty:
            # First entry of the day - mark as "In"
            new_record = {
                "StudentID": student_id,
                "Name": student_name,
                "Date": today,
                "TimeIn": current_time,
                "TimeOut": "",
                "Status": "In"
            }
            att_df = pd.concat([att_df, pd.DataFrame([new_record])], ignore_index=True)
            message = f"{student_name} checked IN at {current_time}"
        else:
            # Student already has an entry today - check last status
            last_record_idx = today_records.index[-1]
            current_status = att_df.loc[last_record_idx, 'Status']
            
            if current_status == "In":
                # Student is currently in, mark as "Out"
                att_df.loc[last_record_idx, 'TimeOut'] = current_time
                att_df.loc[last_record_idx, 'Status'] = "Out"
                message = f"{student_name} checked OUT at {current_time}"
            else:
                # Student already checked out, create new entry for re-entry
                new_record = {
                    "StudentID": student_id,
                    "Name": student_name,
                    "Date": today,
                    "TimeIn": current_time,
                    "TimeOut": "",
                    "Status": "In"
                }
                att_df = pd.concat([att_df, pd.DataFrame([new_record])], ignore_index=True)
                message = f"{student_name} re-entered at {current_time}"
        
        # Save updated attendance data
        try:
            att_df.to_csv(ATTENDANCE_PATH, index=False, encoding='utf-8')
        except Exception as e:
            return False, f"Error saving attendance: {str(e)}"
        
        # Store the student ID and action time for future reference
        st.session_state.last_student_id = student_id
        st.session_state.last_action_time = datetime.datetime.now()
        
        return True, message
    except Exception as e:
        return False, f"Error processing attendance: {str(e)}"

# Function to get pool usage statistics
def get_pool_usage_stats(student_id=None):
    if not os.path.exists(ATTENDANCE_PATH):
        return None, 0
    
    try:
        att_df = pd.read_csv(ATTENDANCE_PATH, encoding='utf-8')
        
        # Make sure we have the required columns
        if 'Status' not in att_df.columns:
            return None, 0
            
        # If student ID is provided, count only for that student
        if student_id:
            # Get the student's attendance records
            student_records = att_df[att_df['StudentID'] == student_id]
            
            # Count instances where Status is "In" (entries)
            total_entries = len(student_records[student_records['Status'] == 'In'])
            
            # Get usage by date
            usage_by_date = student_records.groupby('Date').size().reset_index(name='Visits')
            
            return usage_by_date, total_entries
        else:
            # Count total pool usage for all students
            total_entries = len(att_df[att_df['Status'] == 'In'])
            return None, total_entries
            
    except Exception as e:
        st.error(f"Error calculating pool usage: {str(e)}")
        return None, 0

# Main attendance entry section
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("Quick Entry - Scan QR Code or Enter Student ID")

st.markdown("<div class='input-container'>", unsafe_allow_html=True)
col1, col2 = st.columns([3, 1])

with col1:
    # Check if we need to clear the input
    initial_value = "" if st.session_state.clear_input else st.session_state.get("student_id_input", "")
    if st.session_state.clear_input:
        st.session_state.clear_input = False  # Reset the flag
    
    # Add auto-focus class for better visibility
    st.markdown('<style>.stTextInput > div:first-child {border: 2px solid #1E88E5 !important;}</style>', unsafe_allow_html=True)
    
    # Input field for student ID (will also capture QR code scanner input which acts as keyboard)
    student_id = st.text_input("Student ID", value=initial_value, key="student_id_input", 
                              placeholder="Scan QR Code or Enter Student ID")

with col2:
    st.write("")
    st.write("")
    mark_button_label = "Mark Attendance"
    
    # Button to mark attendance
    if student_id:
        if st.button(mark_button_label, use_container_width=True):
            # Process attendance and automatically determine IN/OUT status
            success, message = mark_attendance(student_id)
            if success:
                # Set clear input flag to reset the input field for next scan
                st.session_state.clear_input = True
                st.success(message)
                # Force rerun to update all displays
                time.sleep(0.3)  # Small delay for better UX
                st.rerun()
            else:
                st.error(message)
    else:
        st.button(mark_button_label, use_container_width=True, disabled=True)
        st.info("Please enter a Student ID or scan a QR code")
st.markdown("</div>", unsafe_allow_html=True)

# Display student information if available
if st.session_state.last_student_id:
    try:
        students_df = pd.read_csv(DATA_PATH, encoding='utf-8')
        student_id = st.session_state.last_student_id
        
        # Find student in database
        student_info = students_df[students_df['StudentID'] == student_id].iloc[0]
        
        # Get pool usage statistics
        usage_by_date, total_entries = get_pool_usage_stats(student_id)
        
        # Check current status
        if os.path.exists(ATTENDANCE_PATH):
            att_df = pd.read_csv(ATTENDANCE_PATH, encoding='utf-8')
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            student_today = att_df[(att_df['StudentID'] == student_id) & (att_df['Date'] == today)]
            
            if not student_today.empty:
                # Create columns for better layout
                col1, col2 = st.columns(2)
                
                with col1:
                    latest_record = student_today.iloc[-1]
                    status = latest_record['Status']
                    
                    # Calculate total time spent today
                    total_duration = 0
                    for _, row in student_today.iterrows():
                        if row['Status'] == 'Out' and row['TimeOut']:
                            # Calculate duration for completed sessions
                            time_in = datetime.datetime.strptime(row['TimeIn'], '%H:%M:%S')
                            time_out = datetime.datetime.strptime(row['TimeOut'], '%H:%M:%S')
                            duration = (time_out - time_in).seconds // 60  # Minutes
                            total_duration += duration
                    
                    # Count total visits today (IN + OUT)
                    total_today_visits = len(student_today)
                    
                    # Display student info card with status
                    st.markdown(f"""
                    <div class="student-card">
                        <h3>Student Information</h3>
                        <p><strong>Name:</strong> {student_info['Name']}</p>
                        <p><strong>ID:</strong> {student_info['StudentID']}</p>
                        <p><strong>Current Status:</strong> <span class="status-{'in' if status == 'In' else 'out'}">{status}</span></p>
                        <p><strong>Today's Time:</strong> {latest_record['TimeIn']}{f" - {latest_record['TimeOut']}" if status == 'Out' else ""}</p>
                        <p><strong>Total Pool Visits Today:</strong> {total_today_visits}</p>
                        <p><strong>Total Pool Visits All-Time:</strong> {total_entries}</p>
                        <p><strong>Time Spent Today:</strong> {total_duration} minutes</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Show today's history
                    st.subheader("Today's Pool Usage")
                    today_records = student_today.sort_values('TimeIn')
                    
                    # Calculate duration for each session
                    today_records_display = today_records.copy()
                    today_records_display['Duration'] = ""
                    
                    for idx, row in today_records_display.iterrows():
                        if row['Status'] == 'Out' and row['TimeOut']:
                            time_in = datetime.datetime.strptime(row['TimeIn'], '%H:%M:%S')
                            time_out = datetime.datetime.strptime(row['TimeOut'], '%H:%M:%S')
                            duration = (time_out - time_in).seconds // 60  # Minutes
                            today_records_display.at[idx, 'Duration'] = f"{duration} mins"
                        elif row['Status'] == 'In':
                            today_records_display.at[idx, 'Duration'] = "In progress"
                    
                    st.dataframe(today_records_display[['TimeIn', 'TimeOut', 'Status', 'Duration']], use_container_width=True)
                    
                    # If there are multiple days of usage, show summary
                    if usage_by_date is not None and len(usage_by_date) > 0:
                        st.subheader("Recent Usage History")
                        st.dataframe(usage_by_date.sort_values('Date', ascending=False).head(7), use_container_width=True)
    except Exception as e:
        st.warning(f"Error displaying student details: {str(e)}")

# Pool status section
st.subheader("Current Pool Status")
try:
    if os.path.exists(ATTENDANCE_PATH):
        att_df = pd.read_csv(ATTENDANCE_PATH, encoding='utf-8')
        
        # Make sure the dataframe has the required columns
        if 'TimeOut' not in att_df.columns or 'Status' not in att_df.columns:
            st.warning("Attendance records need to be updated to the new format.")
        else:
            # Get today's records
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            today_df = att_df[att_df['Date'] == today]
            
            if not today_df.empty:
                # Get latest status for each student
                latest_status = {}
                
                # Find the latest record for each student
                for _, row in today_df.sort_values('TimeIn').iterrows():
                    latest_status[row['StudentID']] = {
                        'Name': row['Name'],
                        'Status': row['Status'],
                        'TimeIn': row['TimeIn'],
                        'TimeOut': row['TimeOut']
                    }
                
                # Create lists for students in pool and checked out
                in_pool = []
                checked_out = []
                
                for student_id, info in latest_status.items():
                    if info['Status'] == 'In':
                        # Calculate how long they've been in
                        time_in = datetime.datetime.strptime(info['TimeIn'], '%H:%M:%S')
                        current_time = datetime.datetime.now()
                        duration_mins = ((current_time.hour * 60 + current_time.minute) - 
                                         (time_in.hour * 60 + time_in.minute))
                        
                        in_pool.append({
                            'StudentID': student_id,
                            'Name': info['Name'],
                            'TimeIn': info['TimeIn'],
                            'Duration': f"{duration_mins} mins"
                        })
                    else:
                        # For checked out students
                        checked_out.append({
                            'StudentID': student_id,
                            'Name': info['Name'],
                            'TimeIn': info['TimeIn'],
                            'TimeOut': info['TimeOut']
                        })
                
                # Convert to dataframes
                in_pool_df = pd.DataFrame(in_pool) if in_pool else pd.DataFrame()
                checked_out_df = pd.DataFrame(checked_out) if checked_out else pd.DataFrame()
                
                # Calculate total visits and add duration for checked out
                if not checked_out_df.empty:
                    checked_out_df['Duration'] = checked_out_df.apply(
                        lambda row: f"{(datetime.datetime.strptime(row['TimeOut'], '%H:%M:%S') - datetime.datetime.strptime(row['TimeIn'], '%H:%M:%S')).seconds // 60} mins",
                        axis=1
                    )
                
                # Display summary stats
                col1, col2, col3 = st.columns(3)
                
                # CORRECTED: Count currently in pool + checked out today
                num_in_pool = len(in_pool)
                num_checked_out = len(checked_out)
                total_visits = num_in_pool + num_checked_out
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card in-metric">
                        <div class="metric-value">{num_in_pool}</div>
                        <div class="metric-label">Currently In Pool</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card out-metric">
                        <div class="metric-value">{num_checked_out}</div>
                        <div class="metric-label">Checked Out Today</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card total-metric">
                        <div class="metric-value">{total_visits}</div>
                        <div class="metric-label">Total Visits Today ({num_in_pool} + {num_checked_out})</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Display tables of students in two columns
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Currently In Pool")
                    if not in_pool_df.empty:
                        st.dataframe(in_pool_df[['Name', 'TimeIn', 'Duration']], use_container_width=True)
                    else:
                        st.info("No students currently in the pool")
                
                with col2:
                    st.subheader("Checked Out Today")
                    if not checked_out_df.empty:
                        st.dataframe(checked_out_df[['Name', 'TimeIn', 'TimeOut', 'Duration']], use_container_width=True)
                    else:
                        st.info("No students have checked out yet today")
            else:
                st.info("No check-ins recorded today.")
    else:
        st.info("No attendance records yet.")
except Exception as e:
    st.error(f"Error loading attendance records: {str(e)}")

st.markdown("</div>", unsafe_allow_html=True)

# Add button to download today's attendance report
st.subheader("Export Today's Attendance")
if st.button("Download Today's Attendance Report"):
    try:
        if os.path.exists(ATTENDANCE_PATH):
            att_df = pd.read_csv(ATTENDANCE_PATH, encoding='utf-8')
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            today_df = att_df[att_df['Date'] == today]
            
            if not today_df.empty:
                # Sort by TimeIn
                today_df = today_df.sort_values('TimeIn')
                
                # Calculate duration for each completed session
                today_df['Duration (mins)'] = ""
                for idx, row in today_df.iterrows():
                    if row['Status'] == 'Out' and row['TimeOut']:
                        time_in = datetime.datetime.strptime(row['TimeIn'], '%H:%M:%S')
                        time_out = datetime.datetime.strptime(row['TimeOut'], '%H:%M:%S')
                        duration = (time_out - time_in).seconds // 60  # Minutes
                        today_df.at[idx, 'Duration (mins)'] = duration
                
                # Create CSV for download
                csv = today_df.to_csv(index=False)
                
                # Provide download button
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"attendance_{today}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No attendance records for today to download.")
        else:
            st.info("No attendance records yet.")
    except Exception as e:
        st.error(f"Error preparing attendance report: {str(e)}")

# Add JS code to keep focus on the input field for scanning
st.markdown("""
<script>
    // Function to focus on the input field
    function focusOnInput() {
        // Get the input element
        const inputElement = document.querySelector('input[aria-label="Student ID"]');
        if (inputElement) {
            inputElement.focus();
        }
    }
    
    // Call the function initially
    focusOnInput();
    
    // Set up a timer to periodically refocus
    setInterval(focusOnInput, 1000);
</script>
""", unsafe_allow_html=True)