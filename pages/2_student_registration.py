import streamlit as st
import pandas as pd
import qrcode
import os
import io
from PIL import Image, ImageDraw, ImageFont
import time
import random
import string
import datetime
import matplotlib.pyplot as plt
import numpy as np
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

st.set_page_config(page_title="Student Registration", page_icon="📝", layout="wide")

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
        background-color: #f0f8ff;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
    }
    .download-btn {
        margin-top: 10px;
    }
    .attendance-card {
        background-color: #f5f9ff;
        border-left: 4px solid #1976d2;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .status-in {
        background-color: #d4edda;
        color: #155724;
        padding: 3px 8px;
        border-radius: 3px;
        font-weight: bold;
    }
    .status-out {
        background-color: #f8d7da;
        color: #721c24;
        padding: 3px 8px;
        border-radius: 3px;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f5f9ff;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #1565C0;
    }
    .metric-label {
        font-size: 14px;
        color: #555;
    }
    .time-display {
        text-align: center;
        font-size: 0.9rem;
        color: #555;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# CORRECTION: Use the exact application path
APP_PATH = "F:/attendance_app"  # Using forward slashes for path compatibility
DATA_DIR = os.path.join(APP_PATH, "data")
QR_FOLDER = os.path.join(APP_PATH, "qr_codes")
DATA_PATH = os.path.join(DATA_DIR, "students.csv")
ATTENDANCE_PATH = os.path.join(DATA_DIR, "attendance.csv")

# Create directories with proper error handling
try:
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(QR_FOLDER, exist_ok=True)
except Exception as e:
    st.warning(f"Could not create directories: {e}. Please ensure you have write permissions to {APP_PATH}")

# Initialize session state for backup data storage
if "students_df" not in st.session_state:
    if os.path.exists(DATA_PATH):
        try:
            st.session_state.students_df = pd.read_csv(DATA_PATH)
        except Exception:
            st.session_state.students_df = pd.DataFrame(
                columns=["Name", "StudentID", "DOB", "SchoolName", "RegisteredOn"])
    else:
        st.session_state.students_df = pd.DataFrame(
            columns=["Name", "StudentID", "DOB", "SchoolName", "RegisteredOn"])

# Initialize session state for ID generation
if "generate_new_id" not in st.session_state:
    st.session_state.generate_new_id = False

# App title
st.markdown("<h1 class='main-header'>📝 Student Registration</h1>", unsafe_allow_html=True)

# Display current Sri Lanka time
current_sl_time = get_sri_lanka_time()
st.markdown(f"<p class='time-display'>Current Time in Sri Lanka: {current_sl_time.strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)

# Function to get attendance records for a specific student
def get_student_attendance(student_id):
    if not os.path.exists(ATTENDANCE_PATH):
        return pd.DataFrame()  # Return empty DataFrame if no attendance records
    
    try:
        # Load attendance data
        att_df = pd.read_csv(ATTENDANCE_PATH, encoding='utf-8')
        
        # Filter for the specific student
        student_att = att_df[att_df['StudentID'] == student_id]
        
        if student_att.empty:
            return pd.DataFrame()
            
        # Sort by date and time
        student_att = student_att.sort_values(by=['Date', 'TimeIn'], ascending=[False, False])
        
        return student_att
    except Exception as e:
        st.error(f"Error loading attendance data: {e}")
        return pd.DataFrame()

# Function to generate student ID
def generate_student_id(prefix="STU"):
    """Generate a unique student ID with prefix and random alphanumeric"""
    random_part = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{random_part}"

# Function to set flag for new ID generation
def set_generate_id_flag():
    st.session_state.generate_new_id = True

# Function to create branded QR code
def create_branded_qr(student_id, student_name):
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(student_id)
    qr.make(fit=True)
    
    # Create QR code image with white background
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGBA')
    
    # Create a larger image for adding text and logo
    canvas_width = qr_img.width + 80
    canvas_height = qr_img.height + 120
    canvas = Image.new('RGBA', (canvas_width, canvas_height), (255, 255, 255, 255))
    
    # Paste QR in the center
    qr_pos_x = (canvas_width - qr_img.width) // 2
    qr_pos_y = 60
    canvas.paste(qr_img, (qr_pos_x, qr_pos_y))
    
    # Add text
    draw = ImageDraw.Draw(canvas)
    
    # Try to load font, use default if not available
    try:
        title_font = ImageFont.truetype("arial.ttf", 24)
        name_font = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        title_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
    
    # Add Swimming Pool title
    title_text = "Swimming Pool Pass"
    title_width = draw.textlength(title_text, font=title_font)
    draw.text(((canvas_width - title_width) // 2, 15), title_text, font=title_font, fill=(30, 136, 229))
    
    # Add student name and ID at bottom
    name_text = f"Name: {student_name}"
    id_text = f"ID: {student_id}"
    
    name_width = draw.textlength(name_text, font=name_font)
    id_width = draw.textlength(id_text, font=name_font)
    
    bottom_y = qr_pos_y + qr_img.height + 20
    draw.text(((canvas_width - name_width) // 2, bottom_y), name_text, font=name_font, fill=(0, 0, 0))
    draw.text(((canvas_width - id_width) // 2, bottom_y + 25), id_text, font=name_font, fill=(0, 0, 0))
    
    # CORRECTION: Save to application's QR folder
    qr_path = os.path.join(QR_FOLDER, f"{student_id}.png")
    try:
        canvas.save(qr_path)
    except Exception as e:
        st.warning(f"Could not save QR code to {qr_path}: {e}")
        st.warning("Please check if you have write permissions to this folder.")
        qr_path = None
    
    return qr_path, canvas

# Function to save student data (simplified)
def save_student(name, student_id, dob, school_name):
    # Try to load existing data or create new
    try:
        if os.path.exists(DATA_PATH):
            df = pd.read_csv(DATA_PATH)
        else:
            df = pd.DataFrame(columns=["Name", "StudentID", "DOB", "SchoolName", "RegisteredOn"])
    except Exception as e:
        st.warning(f"Could not load data file: {e}")
        df = st.session_state.students_df.copy()
    
    # Check if student ID already exists
    if student_id not in df['StudentID'].values:
        # Create a new row with all student data
        new_row = {
            "Name": name,
            "StudentID": student_id,
            "DOB": dob.strftime('%Y-%m-%d'),
            "SchoolName": school_name,
            "RegisteredOn": get_sri_lanka_date_str()  # Use Sri Lanka date
        }
        
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        
        # Try to save to application's data folder
        try:
            df.to_csv(DATA_PATH, index=False)
            # Also update session state
            st.session_state.students_df = df
        except Exception as e:
            st.error(f"Error saving data to {DATA_PATH}: {e}")
            st.error("Please check if the file is open in another program or if you have write permissions.")
            # Store in session state as backup
            st.session_state.students_df = df
            return False, f"Could not save data: {e}", None
        
        # Create QR code
        qr_path, qr_image = create_branded_qr(student_id, name)
        if qr_path is None:
            return True, "Student data saved but QR code could not be generated", qr_image
        
        return True, qr_path, qr_image
    else:
        return False, "Student ID already exists in the system.", None

# Function to create QR code preview only if name field is complete
def create_preview_qr(name, student_id):
    if not name or not student_id:
        return None
    
    # Create a simple in-memory QR code without saving
    _, preview_img = create_branded_qr(student_id, name)
    return preview_img

# Create tabs for registration and student list
tab1, tab2 = st.tabs(["Register New Student", "View Students"])

# Tab 1: Registration Form (Simplified)
with tab1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Student Information")
        name = st.text_input("Full Name*")
        
        # Date of birth instead of age - Use Sri Lanka time for max value
        dob = st.date_input("Date of Birth*", 
                          value=get_sri_lanka_time().date() - datetime.timedelta(days=365*10),
                          min_value=datetime.date(1990, 1, 1),
                          max_value=get_sri_lanka_time().date())
        
        # New field for school name
        school_name = st.text_input("School Name*")
        
        # Generate ID button with option to customize - FIXED
        col_id1, col_id2 = st.columns([3, 1])
        with col_id1:
            # Check if we need to generate a new ID
            if st.session_state.generate_new_id:
                initial_id = generate_student_id()
                st.session_state.generate_new_id = False  # Reset the flag
            else:
                initial_id = generate_student_id() if "student_id_input" not in st.session_state else st.session_state.student_id_input
            
            student_id = st.text_input("Student ID", value=initial_id, key="student_id_input")
        with col_id2:
            st.button("Generate New ID", on_click=set_generate_id_flag)
    
    with col2:
        st.subheader("Preview")
        # Only show preview when name is entered (mandatory field)
        if name:
            st.info("This is a preview only. Click 'Register Student' to save and generate official QR code.")
            try:
                preview_img = create_preview_qr(name, student_id)
                if preview_img:
                    st.image(preview_img, caption="Preview - Student QR Pass", width=300)
            except Exception as e:
                st.error(f"Error generating preview: {e}")
        else:
            st.info("Enter student details to see a preview of their pass")
    
    # Registration button
    if st.button("Register Student", type="primary", use_container_width=True):
        if name and student_id and school_name:  # Verify mandatory fields
            with st.spinner("Registering student..."):
                success, result, qr_image = save_student(name, student_id, dob, school_name)
                
                if success:
                    if isinstance(result, str) and "could not be generated" in result:
                        st.warning(result)
                    else:
                        st.success("✅ Student registered successfully!")
                    
                    if qr_image:
                        st.image(qr_image, caption=f"QR Code for {name}", width=300)
                        
                        # Convert QR to bytes for download
                        buf = io.BytesIO()
                        qr_image.save(buf, format='PNG')
                        st.download_button(
                            label="Download QR Pass",
                            data=buf.getvalue(),
                            file_name=f"{student_id}_pass.png",
                            mime="image/png",
                            key="download_new_qr"
                        )
                else:
                    st.error(result)
        else:
            st.error("Name, Student ID, and School Name are required fields.")
    st.markdown("</div>", unsafe_allow_html=True)

# Tab 2: Student List with Attendance View
with tab2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Registered Students")
    
    # Try to load data from the specific file path
    try:
        if os.path.exists(DATA_PATH):
            df = pd.read_csv(DATA_PATH)
        else:
            df = st.session_state.students_df
            if df.empty:
                st.info("No students registered yet. Use the registration form to add students.")
                st.markdown("</div>", unsafe_allow_html=True)
                st.stop()
    except Exception as e:
        st.warning(f"Could not load student data: {e}")
        df = st.session_state.students_df
        if df.empty:
            st.info("No students registered yet. Use the registration form to add students.")
            st.markdown("</div>", unsafe_allow_html=True)
            st.stop()
    
    # Add search functionality
    search = st.text_input("Search by Name or ID")
    if search:
        df = df[df['Name'].str.contains(search, case=False) | 
                df['StudentID'].str.contains(search, case=False)]
    
    # Sort options
    sort_by = st.selectbox("Sort by", ["Name", "RegisteredOn", "SchoolName"])
    df = df.sort_values(by=sort_by)
    
    # Display student data with formatting
    st.dataframe(df, use_container_width=True)
    
    # Add individual QR code download and attendance view functionality
    st.write("### Student Details")
    selected_student = st.selectbox("Select a student to view details:", 
                                   options=df['Name'].tolist(),
                                   format_func=lambda x: f"{x} (ID: {df[df['Name']==x]['StudentID'].values[0]})")
    
    if selected_student:
        student_row = df[df['Name'] == selected_student].iloc[0]
        student_id = student_row['StudentID']
        student_name = student_row['Name']
        
        # Create tabs for student details
        detail_tabs = st.tabs(["QR Code", "Attendance Records"])
        
        # QR Code Tab
        with detail_tabs[0]:
            # Check if QR exists or generate it
            qr_file_path = os.path.join(QR_FOLDER, f"{student_id}.png")
            
            if os.path.exists(qr_file_path):
                qr_image = Image.open(qr_file_path)
                st.image(qr_image, caption=f"QR Code for {student_name}", width=300)
            else:
                # Generate new QR code
                try:
                    _, qr_image = create_branded_qr(student_id, student_name)
                    st.image(qr_image, caption=f"QR Code for {student_name}", width=300)
                except Exception as e:
                    st.error(f"Could not generate QR code: {e}")
                    st.stop()
            
            # Convert QR to bytes for download
            buf = io.BytesIO()
            qr_image.save(buf, format='PNG')
            st.download_button(
                label="Download QR Pass",
                data=buf.getvalue(),
                file_name=f"{student_id}_pass.png",
                mime="image/png",
                key="download_existing_qr"
            )
        
        # Attendance Records Tab
        with detail_tabs[1]:
            # Get attendance records
            attendance_df = get_student_attendance(student_id)
            
            if not attendance_df.empty:
                # Create summary statistics
                total_days = attendance_df['Date'].nunique()
                
                # Calculate total time spent
                total_duration = 0
                if 'TimeOut' in attendance_df.columns and 'TimeIn' in attendance_df.columns:
                    for _, row in attendance_df.iterrows():
                        if row['Status'] == 'Out' and row['TimeOut']:
                            try:
                                time_in = datetime.datetime.strptime(row['TimeIn'], '%H:%M:%S')
                                time_out = datetime.datetime.strptime(row['TimeOut'], '%H:%M:%S')
                                duration = (time_out - time_in).seconds // 60  # Minutes
                                total_duration += duration
                            except Exception:
                                pass
                
                # Display summary metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{total_days}</div>
                        <div class="metric-label">Days Attended</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{len(attendance_df)}</div>
                        <div class="metric-label">Total Check-ins</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{total_duration}</div>
                        <div class="metric-label">Total Minutes</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Create attendance history visualization
                if total_days > 1:
                    st.subheader("Attendance Pattern")
                    try:
                        # Group by date and count
                        date_counts = attendance_df.groupby('Date').size().reset_index(name='Count')
                        # Convert dates to datetime for better plotting
                        date_counts['Date'] = pd.to_datetime(date_counts['Date'])
                        
                        # Create a simple bar chart
                        fig, ax = plt.subplots(figsize=(10, 3))
                        ax.bar(date_counts['Date'], date_counts['Count'], color='#1976d2')
                        ax.set_ylabel('Check-ins')
                        ax.set_title('Attendance by Date')
                        
                        # Format x-axis dates
                        fig.autofmt_xdate()
                        
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Could not create attendance visualization: {e}")
                
                # Show detailed attendance records
                st.subheader("Detailed Records")
                
                # Add duration column to display
                display_df = attendance_df.copy()
                if 'TimeOut' in display_df.columns and 'TimeIn' in display_df.columns:
                    display_df['Duration'] = ""
                    for idx, row in display_df.iterrows():
                        if row['Status'] == 'Out' and row['TimeOut']:
                            try:
                                time_in = datetime.datetime.strptime(row['TimeIn'], '%H:%M:%S')
                                time_out = datetime.datetime.strptime(row['TimeOut'], '%H:%M:%S')
                                duration = (time_out - time_in).seconds // 60  # Minutes
                                display_df.at[idx, 'Duration'] = f"{duration} mins"
                            except Exception:
                                display_df.at[idx, 'Duration'] = "N/A"
                        elif row['Status'] == 'In':
                            display_df.at[idx, 'Duration'] = "In progress"
                
                # Format status with color indicators
                def format_status(status):
                    return f"<span class='status-{status.lower()}'>{status}</span>"
                
                # Apply custom formatting if possible
                if 'Duration' in display_df.columns:
                    cols_to_display = ['Date', 'TimeIn', 'TimeOut', 'Status', 'Duration']
                else:
                    cols_to_display = ['Date', 'TimeIn', 'Status']
                
                st.dataframe(display_df[cols_to_display], use_container_width=True)
                
                # Add download button for attendance records
                st.download_button(
                    label="Download Attendance Records",
                    data=display_df.to_csv(index=False),
                    file_name=f"{student_id}_attendance.csv",
                    mime="text/csv"
                )
            else:
                st.info(f"No attendance records found for {student_name}")
                st.write("This student has not checked in to the swimming pool yet.")
    
    # Export options
    st.write("### Batch Operations")
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        st.download_button(
            "Download Student List as CSV",
            df.to_csv(index=False),
            file_name="students_list.csv",
            mime="text/csv"
        )
    with col_exp2:
        if st.button("Generate All QR Codes"):
            with st.spinner("Generating QR codes for all students..."):
                success_count = 0
                for _, row in df.iterrows():
                    try:
                        create_branded_qr(row['StudentID'], row['Name'])
                        success_count += 1
                    except Exception as e:
                        st.error(f"Error creating QR for {row['Name']}: {e}")
                st.success(f"Generated {success_count} QR codes in {QR_FOLDER}")
    st.markdown("</div>", unsafe_allow_html=True)

# Bulk import section
with st.expander("Bulk Import Students"):
    st.info("Upload a CSV file with columns: Name, StudentID (optional), DOB, SchoolName")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            import_df = pd.read_csv(uploaded_file)
            st.write("Preview of data to import:")
            st.dataframe(import_df.head())
            
            if st.button("Import Students"):
                with st.spinner("Importing students..."):
                    # Create required columns if they don't exist
                    required_cols = ["Name", "StudentID", "DOB", "SchoolName"]
                    for col in required_cols:
                        if col not in import_df.columns:
                            if col == "StudentID":
                                import_df[col] = [generate_student_id() for _ in range(len(import_df))]
                            else:
                                import_df[col] = ""
                    
                    # Add registration date with Sri Lanka time
                    import_df["RegisteredOn"] = get_sri_lanka_date_str()
                    
                    # Read existing data
                    try:
                        if os.path.exists(DATA_PATH):
                            existing_df = pd.read_csv(DATA_PATH)
                        else:
                            existing_df = pd.DataFrame(columns=["Name", "StudentID", "DOB", "SchoolName", "RegisteredOn"])
                    except Exception as e:
                        st.warning(f"Could not load existing data: {e}")
                        existing_df = st.session_state.students_df
                    
                    # Filter out students that already exist
                    existing_ids = existing_df["StudentID"].tolist()
                    import_df = import_df[~import_df["StudentID"].isin(existing_ids)]
                    
                    # Combine DataFrames
                    combined_df = pd.concat([existing_df, import_df], ignore_index=True)
                    
                    # Save with error handling
                    try:
                        combined_df.to_csv(DATA_PATH, index=False)
                        # Update session state
                        st.session_state.students_df = combined_df
                    except Exception as e:
                        st.error(f"Error saving data: {e}")
                        st.session_state.students_df = combined_df
                    
                    # Generate QR codes for new students
                    qr_count = 0
                    for _, row in import_df.iterrows():
                        try:
                            create_branded_qr(row["StudentID"], row["Name"])
                            qr_count += 1
                        except Exception as e:
                            st.error(f"Error creating QR for {row['Name']}: {e}")
                    
                    st.success(f"Successfully imported {len(import_df)} new students and generated {qr_count} QR codes!")
                    time.sleep(1)
                    st.rerun()
        except Exception as e:
            st.error(f"Error importing data: {e}")