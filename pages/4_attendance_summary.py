import streamlit as st
import pandas as pd
import os
import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import calendar

st.set_page_config(page_title="Attendance Summary", page_icon="📊", layout="wide")

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
    .metric-card {
        background-color: #e87287;
        border-radius: 5px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #555;
    }
    .status-in {
        background-color: #d4edda;
        color: #155724;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .status-out {
        background-color: #f8d7da;
        color: #721c24;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Constants and file paths
APP_PATH = "F:/attendance_app"  # Using forward slashes for path compatibility
DATA_DIR = os.path.join(APP_PATH, "data")
DATA_PATH = os.path.join(DATA_DIR, "students.csv")
ATTENDANCE_PATH = os.path.join(DATA_DIR, "attendance.csv")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)

# App title
st.markdown("<h1 class='main-header'>📊 Attendance Summary</h1>", unsafe_allow_html=True)

# Check if data exists
if not os.path.exists(ATTENDANCE_PATH):
    st.info("No attendance records found. Start marking attendance to see reports.")
    st.stop()

if not os.path.exists(DATA_PATH):
    st.info("No student records found. Please register students first.")
    st.stop()

# Load data
try:
    attendance_df = pd.read_csv(ATTENDANCE_PATH)
    students_df = pd.read_csv(DATA_PATH)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Check if attendance data has the required columns for in/out tracking
if not all(col in attendance_df.columns for col in ['TimeIn', 'TimeOut', 'Status']):
    st.warning("The attendance data doesn't have the required columns for in/out tracking. Some reports may not work correctly.")
    # Try to adapt the old format to the new one
    if 'Time' in attendance_df.columns and 'TimeIn' not in attendance_df.columns:
        attendance_df['TimeIn'] = attendance_df['Time']
        attendance_df['TimeOut'] = ""
        attendance_df['Status'] = "In"

# Convert date strings to datetime objects
attendance_df['Date'] = pd.to_datetime(attendance_df['Date'])

# Create tabs for different reports
tab1, tab2, tab3 = st.tabs(["Overview", "Student Details", "Attendance Records"])

# Tab 1: Overview
with tab1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", 
                                  value=attendance_df['Date'].min() if not attendance_df.empty else datetime.datetime.now(),
                                  min_value=attendance_df['Date'].min() if not attendance_df.empty else None,
                                  max_value=datetime.datetime.now())
    with col2:
        end_date = st.date_input("End Date", 
                                value=datetime.datetime.now(),
                                min_value=attendance_df['Date'].min() if not attendance_df.empty else None,
                                max_value=datetime.datetime.now())
    
    # Filter data by date range
    filtered_df = attendance_df[(attendance_df['Date'] >= pd.Timestamp(start_date)) & 
                               (attendance_df['Date'] <= pd.Timestamp(end_date))]
    
    # Key metrics
    total_students = len(students_df)
    total_visits = len(filtered_df)
    unique_visitors = filtered_df['StudentID'].nunique()
    
    # Count the number of check-ins per day and calculate average
    daily_counts = filtered_df.groupby(filtered_df['Date'].dt.date)['StudentID'].nunique()
    avg_daily = daily_counts.mean() if not filtered_df.empty else 0
    
    # Display metrics
    st.subheader("Key Metrics")
    metric_cols = st.columns(4)
    
    with metric_cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_students}</div>
            <div class="metric-label">Total Students</div>
        </div>
        """, unsafe_allow_html=True)
        
    with metric_cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_visits}</div>
            <div class="metric-label">Total Visits</div>
        </div>
        """, unsafe_allow_html=True)
        
    with metric_cols[2]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{unique_visitors}</div>
            <div class="metric-label">Unique Visitors</div>
        </div>
        """, unsafe_allow_html=True)
        
    with metric_cols[3]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_daily:.1f}</div>
            <div class="metric-label">Avg. Daily Attendance</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    st.subheader("Attendance Trends")
    chart_cols = st.columns(2)
    
    with chart_cols[0]:
        # Attendance by day
        daily_unique = filtered_df.groupby(filtered_df['Date'].dt.date)['StudentID'].nunique().reset_index()
        daily_unique.columns = ['Date', 'Count']
        
        if not daily_unique.empty:
            fig = px.line(daily_unique, x='Date', y='Count', 
                          title='Daily Unique Visitors',
                          labels={'Count': 'Students', 'Date': 'Date'})
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected period.")
    
    with chart_cols[1]:
        # Attendance by day of week
        if not filtered_df.empty:
            filtered_df['DayOfWeek'] = filtered_df['Date'].dt.day_name()
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            # Group by day of week and count unique students per day
            weekday_data = filtered_df.groupby(['DayOfWeek', filtered_df['Date'].dt.date])['StudentID'].nunique().reset_index()
            weekday_avg = weekday_data.groupby('DayOfWeek')['StudentID'].mean().reindex(day_order).fillna(0)
            
            fig = px.bar(x=weekday_avg.index, y=weekday_avg.values,
                         title='Average Attendance by Day of Week',
                         labels={'x': 'Day', 'y': 'Average Students'})
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected period.")
    
    # Check if School Name exists in student data
    if 'SchoolName' in students_df.columns:
        st.subheader("Attendance by School")
        
        # Merge attendance with student info to get school data
        merged_df = pd.merge(filtered_df, students_df[['StudentID', 'SchoolName']], on='StudentID', how='left')
        
        # Group by school and count unique students
        school_counts = merged_df.groupby('SchoolName')['StudentID'].nunique().reset_index()
        school_counts.columns = ['SchoolName', 'Count']
        
        if not school_counts.empty:
            # Sort by count in descending order
            school_counts = school_counts.sort_values('Count', ascending=False)
            
            fig = px.pie(school_counts, values='Count', names='SchoolName', 
                         title='Attendance Distribution by School')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No school data available.")
    
    # Show In/Out tracking statistics if available
    if 'Status' in filtered_df.columns:
        st.subheader("Check-In/Out Statistics")
        
        # Count records by status
        status_counts = filtered_df['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        
        if not status_counts.empty:
            fig = px.pie(status_counts, values='Count', names='Status', 
                        title='Distribution of Check-Ins vs Check-Outs',
                        color='Status', 
                        color_discrete_map={'In': '#28a745', 'Out': '#dc3545'})
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate average time spent in pool
            if 'TimeIn' in filtered_df.columns and 'TimeOut' in filtered_df.columns:
                # Filter records with both in and out times
                complete_visits = filtered_df[
                    (filtered_df['Status'] == 'Out') & 
                    (filtered_df['TimeOut'] != "")
                ].copy()
                
                if not complete_visits.empty:
                    # Convert time strings to datetime
                    complete_visits['TimeIn'] = pd.to_datetime(
                        complete_visits['Date'].dt.strftime('%Y-%m-%d') + ' ' + complete_visits['TimeIn']
                    )
                    complete_visits['TimeOut'] = pd.to_datetime(
                        complete_visits['Date'].dt.strftime('%Y-%m-%d') + ' ' + complete_visits['TimeOut']
                    )
                    
                    # Calculate duration in minutes
                    complete_visits['Duration'] = (complete_visits['TimeOut'] - complete_visits['TimeIn']).dt.total_seconds() / 60
                    
                    # Filter out negative durations (in case of data errors)
                    complete_visits = complete_visits[complete_visits['Duration'] > 0]
                    
                    if not complete_visits.empty:
                        avg_duration = complete_visits['Duration'].mean()
                        max_duration = complete_visits['Duration'].max()
                        
                        st.metric("Average Time in Pool", f"{avg_duration:.1f} minutes")
                        
                        # Create histogram of visit durations
                        fig = px.histogram(complete_visits, x='Duration', nbins=20,
                                          title='Distribution of Visit Durations',
                                          labels={'Duration': 'Duration (minutes)'})
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No valid duration data available.")
                else:
                    st.info("No complete visits (with both check-in and check-out) found.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Tab 2: Student Details
with tab2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Individual Student Attendance")
    
    # Search for student
    search = st.text_input("Search Student by Name or ID")
    
    if search:
        search_results = students_df[students_df['Name'].str.contains(search, case=False) | 
                                     students_df['StudentID'].str.contains(search, case=False)]
    else:
        search_results = students_df
    
    # Select student
    if not search_results.empty:
        selected_student = st.selectbox(
            "Select Student", 
            options=search_results['StudentID'].tolist(),
            format_func=lambda x: f"{search_results[search_results['StudentID'] == x]['Name'].values[0]} ({x})"
        )
        
        if selected_student:
            # Get student info
            student_info = students_df[students_df['StudentID'] == selected_student].iloc[0]
            
            # Display student details
            st.markdown(f"""
            <div style="padding:15px; background-color:#faf8fa; border-radius:5px; margin-bottom:20px; border: 1px solid #dee2e6;">
                <h3 style="color:#f8f8fa;">{student_info['Name']}</h3>
                <p><strong>Student ID:</strong> {student_info['StudentID']}</p>
                <p><strong>Date of Birth:</strong> {student_info.get('DOB', 'N/A')}</p>
                <p><strong>School:</strong> {student_info.get('SchoolName', 'N/A')}</p>
                <p><strong>Registered On:</strong> {student_info.get('RegisteredOn', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Get student attendance
            student_attendance = attendance_df[attendance_df['StudentID'] == selected_student]
            
            if not student_attendance.empty:
                # Show attendance stats
                first_attendance = student_attendance['Date'].min()
                last_attendance = student_attendance['Date'].max()
                total_days = student_attendance['Date'].dt.date.nunique()  # Count unique days
                total_visits = len(student_attendance)
                
                # Create columns for metrics
                stat_cols = st.columns(4)
                with stat_cols[0]:
                    st.metric("First Visit", first_attendance.strftime('%Y-%m-%d'))
                with stat_cols[1]:
                    st.metric("Last Visit", last_attendance.strftime('%Y-%m-%d'))
                with stat_cols[2]:
                    st.metric("Days Visited", total_days)
                with stat_cols[3]:
                    st.metric("Total Check-ins", total_visits)
                
                # Monthly attendance chart
                student_attendance['Month'] = student_attendance['Date'].dt.strftime('%Y-%m')
                monthly_counts = student_attendance.groupby('Month')['StudentID'].count().reset_index()
                monthly_counts.columns = ['Month', 'Count']
                
                fig = px.bar(monthly_counts, x='Month', y='Count',
                             title=f'Monthly Attendance for {student_info["Name"]}',
                             labels={'Count': 'Visits', 'Month': 'Month'})
                st.plotly_chart(fig, use_container_width=True)
                
                # Show attendance records
                st.subheader("Attendance Records")
                
                # Prepare the display data based on available columns
                if all(col in student_attendance.columns for col in ['TimeIn', 'TimeOut', 'Status']):
                    # New format with in/out tracking
                    display_df = student_attendance.sort_values('Date', ascending=False)
                    
                    # Format the display
                    for idx, row in display_df.iterrows():
                        status_class = "status-in" if row['Status'] == "In" else "status-out"
                        time_info = f"{row['TimeIn']}"
                        if row['Status'] == "Out" and row['TimeOut']:
                            time_info += f" to {row['TimeOut']}"
                        
                        st.markdown(f"""
                        <div style="padding:10px; border-bottom:1px solid #eee; margin-bottom:5px;">
                            <div style="display:flex; justify-content:space-between;">
                                <div><strong>Date:</strong> {row['Date'].strftime('%Y-%m-%d')}</div>
                                <div><strong>Status:</strong> <span class="{status_class}">{row['Status']}</span></div>
                            </div>
                            <div><strong>Time:</strong> {time_info}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    # Old format
                    display_df = student_attendance.sort_values('Date', ascending=False)
                    time_col = 'Time' if 'Time' in display_df.columns else 'TimeIn'
                    st.dataframe(display_df[['Date', time_col]], use_container_width=True)
                
                # Download option
                st.download_button(
                    label="Download Attendance Records",
                    data=student_attendance.to_csv(index=False),
                    file_name=f"{student_info['Name']}_attendance.csv",
                    mime="text/csv"
                )
                
                # Calculate and show average time spent if data available
                if 'TimeIn' in student_attendance.columns and 'TimeOut' in student_attendance.columns:
                    complete_visits = student_attendance[
                        (student_attendance['Status'] == 'Out') & 
                        (student_attendance['TimeOut'] != "")
                    ].copy()
                    
                    if not complete_visits.empty:
                        try:
                            # Convert time strings to datetime
                            complete_visits['TimeIn_DT'] = pd.to_datetime(
                                complete_visits['Date'].dt.strftime('%Y-%m-%d') + ' ' + complete_visits['TimeIn']
                            )
                            complete_visits['TimeOut_DT'] = pd.to_datetime(
                                complete_visits['Date'].dt.strftime('%Y-%m-%d') + ' ' + complete_visits['TimeOut']
                            )
                            
                            # Calculate duration in minutes
                            complete_visits['Duration'] = (complete_visits['TimeOut_DT'] - complete_visits['TimeIn_DT']).dt.total_seconds() / 60
                            
                            # Filter out negative durations
                            complete_visits = complete_visits[complete_visits['Duration'] > 0]
                            
                            if not complete_visits.empty:
                                avg_duration = complete_visits['Duration'].mean()
                                st.subheader("Visit Duration Analysis")
                                st.metric("Average Time in Pool", f"{avg_duration:.1f} minutes")
                                
                                # Show duration by date
                                fig = px.bar(complete_visits, x='Date', y='Duration',
                                           title='Visit Duration by Date',
                                           labels={'Duration': 'Duration (minutes)', 'Date': 'Date'})
                                st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.warning(f"Could not analyze visit durations: {e}")
            else:
                st.info(f"No attendance records found for {student_info['Name']}.")
    else:
        st.info("No students found matching your search criteria.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Tab 3: Attendance Records
with tab3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Daily Attendance Records")
    
    # Date filter
    date_filter = st.date_input(
        "Select Date",
        value=datetime.datetime.now(),
        min_value=attendance_df['Date'].min() if not attendance_df.empty else None,
        max_value=datetime.datetime.now()
    )
    
    # Filter by selected date
    date_records = attendance_df[attendance_df['Date'].dt.date == pd.Timestamp(date_filter).date()]
    
    if not date_records.empty:
        # Calculate attendance stats for the day
        total_records = len(date_records)
        unique_students = date_records['StudentID'].nunique()
        
        # Create metrics row
        stat_cols = st.columns(3)
        with stat_cols[0]:
            st.metric("Total Records", total_records)
        with stat_cols[1]:
            st.metric("Unique Students", unique_students)
            
        # Count students currently in the pool
        if 'Status' in date_records.columns:
            # Get the latest status for each student
            latest_status = date_records.sort_values('TimeIn').groupby('StudentID').last()
            currently_in = sum(latest_status['Status'] == 'In')
            
            with stat_cols[2]:
                st.metric("Currently In Pool", currently_in)
        
        # Show records with formatting for status
        st.subheader("Attendance Records for the Day")
        
        if all(col in date_records.columns for col in ['TimeIn', 'TimeOut', 'Status']):
            # New format with in/out tracking
            sorted_records = date_records.sort_values('TimeIn', ascending=False)
            
            # Create a custom display
            for idx, row in sorted_records.iterrows():
                status_class = "status-in" if row['Status'] == "In" else "status-out"
                time_info = f"{row['TimeIn']}"
                if row['Status'] == "Out" and row['TimeOut']:
                    time_info += f" to {row['TimeOut']}"
                
                st.markdown(f"""
                <div style="padding:10px; border-bottom:1px solid #eee; margin-bottom:5px; display:flex; justify-content:space-between;">
                    <div style="flex:2;"><strong>{row['Name']}</strong> ({row['StudentID']})</div>
                    <div style="flex:1;"><span class="{status_class}">{row['Status']}</span></div>
                    <div style="flex:2;">{time_info}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Old format
            st.dataframe(date_records.sort_values('Time' if 'Time' in date_records.columns else 'TimeIn', ascending=False), 
                        use_container_width=True)
        
        # Download option
        st.download_button(
            label="Download Daily Records",
            data=date_records.to_csv(index=False),
            file_name=f"attendance_{date_filter}.csv",
            mime="text/csv"
        )
        
        # Show pool status by time of day
        if 'Status' in date_records.columns:
            st.subheader("Pool Occupancy Throughout the Day")
            
            try:
                # Create a timeline of check-ins and check-outs
                timeline = []
                
                for _, row in date_records.iterrows():
                    # Add check-in event
                    date_str = row['Date'].strftime('%Y-%m-%d')
                    timeline.append({
                        'Time': pd.to_datetime(f"{date_str} {row['TimeIn']}"),
                        'Event': 'In',
                        'StudentID': row['StudentID']
                    })
                    
                    # Add check-out event if available
                    if row['Status'] == 'Out' and row['TimeOut'] and row['TimeOut'].strip():
                        timeline.append({
                            'Time': pd.to_datetime(f"{date_str} {row['TimeOut']}"),
                            'Event': 'Out',
                            'StudentID': row['StudentID']
                        })
                
                if timeline:
                    # Sort by time
                    timeline_df = pd.DataFrame(timeline).sort_values('Time')
                    
                    # Calculate running count of students in pool
                    count = 0
                    occupancy = []
                    
                    for _, event in timeline_df.iterrows():
                        if event['Event'] == 'In':
                            count += 1
                        else:
                            count = max(0, count - 1)  # Ensure count doesn't go negative
                        
                        occupancy.append({
                            'Time': event['Time'],
                            'Count': count
                        })
                    
                    occupancy_df = pd.DataFrame(occupancy)
                    
                    # Create occupancy chart
                    fig = px.line(occupancy_df, x='Time', y='Count',
                                title='Pool Occupancy Throughout the Day',
                                labels={'Count': 'Students in Pool', 'Time': 'Time'})
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not generate occupancy chart: {e}")
        
        # List of present students
        st.subheader("Students Present Today")
        
        # Merge with student info
        try:
            present_students = pd.merge(date_records[['StudentID']].drop_duplicates(), 
                                        students_df, 
                                        on='StudentID', 
                                        how='left')
            
            if not present_students.empty:
                st.dataframe(present_students[['Name', 'StudentID', 'SchoolName']], use_container_width=True)
            else:
                st.error("Could not retrieve student details")
        except Exception as e:
            st.error(f"Error merging data: {e}")
        
        # List of absent students
        st.subheader("Students Absent Today")
        present_ids = date_records['StudentID'].unique()
        absent_students = students_df[~students_df['StudentID'].isin(present_ids)]
        
        if not absent_students.empty:
            st.dataframe(absent_students[['Name', 'StudentID', 'SchoolName']], use_container_width=True)
        else:
            st.success("All registered students were present!")
    else:
        st.info(f"No attendance records found for {date_filter}.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Generate reports section
with st.expander("Generate Reports"):
    st.subheader("Custom Reports")
    
    report_type = st.selectbox(
        "Report Type",
        ["Monthly Summary", "School Analysis", "Attendance Trends", "Student Participation"]
    )
    
    if report_type == "Monthly Summary":
        # Allow selecting month and year
        current_year = datetime.datetime.now().year
        year_options = range(current_year - 2, current_year + 1)
        selected_year = st.selectbox("Year", options=year_options, index=2)
        month_options = list(range(1, 13))
        selected_month = st.selectbox("Month", options=month_options, 
                                     format_func=lambda x: calendar.month_name[x])
        
        # Generate monthly report
        if st.button("Generate Monthly Report"):
            # Filter data for selected month and year
            monthly_data = attendance_df[
                (attendance_df['Date'].dt.year == selected_year) & 
                (attendance_df['Date'].dt.month == selected_month)
            ]
            
            if not monthly_data.empty:
                st.success(f"Report generated for {calendar.month_name[selected_month]} {selected_year}")
                
                # Summary metrics
                total_records = len(monthly_data)
                unique_students = monthly_data['StudentID'].nunique()
                attendance_days = monthly_data['Date'].dt.date.nunique()
                
                metrics_col = st.columns(3)
                with metrics_col[0]:
                    st.metric("Total Records", total_records)
                with metrics_col[1]:
                    st.metric("Unique Students", unique_students)
                with metrics_col[2]:
                    st.metric("Days with Attendance", attendance_days)
                
                # Attendance by day chart
                daily_data = monthly_data.groupby(monthly_data['Date'].dt.date)['StudentID'].nunique().reset_index()
                daily_data.columns = ['Date', 'Count']
                
                fig = px.bar(daily_data, x='Date', y='Count',
                            title=f'Daily Attendance - {calendar.month_name[selected_month]} {selected_year}')
                st.plotly_chart(fig, use_container_width=True)
                
                # Check-in times analysis if available
                if 'TimeIn' in monthly_data.columns:
                    try:
                        # Extract hour from time
                        monthly_data['Hour'] = pd.to_datetime(monthly_data['TimeIn']).dt.hour
                        
                        # Count check-ins by hour
                        hourly_data = monthly_data['Hour'].value_counts().sort_index().reset_index()
                        hourly_data.columns = ['Hour', 'Count']
                        
                        # Create bar chart of check-in times
                        fig = px.bar(hourly_data, x='Hour', y='Count',
                                    title=f'Check-in Times - {calendar.month_name[selected_month]} {selected_year}',
                                    labels={'Hour': 'Hour of Day (24h)', 'Count': 'Number of Check-ins'})
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not analyze check-in times: {e}")
                
                # Download report
                st.download_button(
                    label="Download Report Data",
                    data=monthly_data.to_csv(index=False),
                    file_name=f"report_{selected_year}_{selected_month}.csv",
                    mime="text/csv"
                )
            else:
                st.error(f"No attendance data found for {calendar.month_name[selected_month]} {selected_year}")
    
    elif report_type == "School Analysis":
        st.info("Analyze attendance patterns by school")
        
        if 'SchoolName' in students_df.columns:
            # Merge attendance with student info
            merged_data = pd.merge(attendance_df, students_df[['StudentID', 'SchoolName']], on='StudentID', how='left')
            
            if not merged_data.empty:
                # Group by school and date
                school_data = merged_data.groupby(['SchoolName', merged_data['Date'].dt.date])['StudentID'].nunique().reset_index()
                school_data.columns = ['SchoolName', 'Date', 'Count']
                
                # Create pivot table for plotting
                pivot_data = school_data.pivot_table(index='Date', columns='SchoolName', values='Count', fill_value=0)
                
                # Plot attendance by school
                st.subheader("Attendance by School Over Time")
                fig = px.line(pivot_data, title='Attendance Trends by School')
                st.plotly_chart(fig, use_container_width=True)
                
                # Average attendance by school
                avg_by_school = school_data.groupby('SchoolName')['Count'].mean().reset_index()
                avg_by_school.columns = ['SchoolName', 'Average Attendance']
                avg_by_school = avg_by_school.sort_values('Average Attendance', ascending=False)
                
                st.subheader("Average Daily Attendance by School")
                fig = px.bar(avg_by_school, x='SchoolName', y='Average Attendance',
                           title='Average Students per Day by School')
                fig.update_layout(xaxis_title='School', yaxis_title='Average Students')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("No attendance data found with school information")
        else:
            st.error("School information not available in student records")
    
    elif report_type == "Attendance Trends":
        st.info("Analyze long-term attendance patterns")
        
        # Time period selection
        period = st.radio("Select Time Period", ["Weekly", "Monthly", "Quarterly"])
        
        if period == "Weekly":
            # Group by week
            attendance_df['Week'] = attendance_df['Date'].dt.isocalendar().week
            attendance_df['Year'] = attendance_df['Date'].dt.isocalendar().year
            
            # Count unique students per week
            weekly_data = attendance_df.groupby(['Year', 'Week'])['StudentID'].nunique().reset_index()
            weekly_data.columns = ['Year', 'Week', 'Count']
            weekly_data['Period'] = weekly_data['Year'].astype(str) + '-W' + weekly_data['Week'].astype(str)
            
            st.subheader("Weekly Attendance Trends")
            fig = px.line(weekly_data, x='Period', y='Count', title='Weekly Unique Students')
            fig.update_layout(xaxis_title='Year-Week', yaxis_title='Unique Students')
            st.plotly_chart(fig, use_container_width=True)
        
        elif period == "Monthly":
            # Group by month
            attendance_df['YearMonth'] = attendance_df['Date'].dt.strftime('%Y-%m')
            
            # Count unique students per month
            monthly_data = attendance_df.groupby('YearMonth')['StudentID'].nunique().reset_index()
            monthly_data.columns = ['YearMonth', 'Count']
            
            st.subheader("Monthly Attendance Trends")
            fig = px.line(monthly_data, x='YearMonth', y='Count', title='Monthly Unique Students')
            fig.update_layout(xaxis_title='Year-Month', yaxis_title='Unique Students')
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate month-over-month growth
            if len(monthly_data) > 1:
                monthly_data['Previous'] = monthly_data['Count'].shift(1)
                monthly_data['Growth'] = (monthly_data['Count'] - monthly_data['Previous']) / monthly_data['Previous'] * 100
                monthly_data = monthly_data.dropna()  # Remove first row with NaN growth
                
                fig = px.bar(monthly_data, x='YearMonth', y='Growth',
                           title='Month-over-Month Growth (%)',
                           labels={'Growth': 'Growth %', 'YearMonth': 'Year-Month'})
                fig.update_layout(yaxis_ticksuffix='%')
                st.plotly_chart(fig, use_container_width=True)
        
        else:  # Quarterly
            # Group by quarter
            attendance_df['Quarter'] = attendance_df['Date'].dt.to_period('Q').astype(str)
            
            # Count unique students per quarter
            quarterly_data = attendance_df.groupby('Quarter')['StudentID'].nunique().reset_index()
            quarterly_data.columns = ['Quarter', 'Count']
            
            st.subheader("Quarterly Attendance Trends")
            fig = px.line(quarterly_data, x='Quarter', y='Count', title='Quarterly Unique Students')
            fig.update_layout(xaxis_title='Year-Quarter', yaxis_title='Unique Students')
            st.plotly_chart(fig, use_container_width=True)
    
    elif report_type == "Student Participation":
        st.info("Analyze individual student participation patterns")
        
        # Calculate attendance frequency for each student
        student_freq = attendance_df.groupby('StudentID').size().reset_index()
        student_freq.columns = ['StudentID', 'VisitCount']
        
        # Merge with student info
        student_freq = pd.merge(student_freq, students_df, on='StudentID', how='left')
        
        # Sort by visit count
        student_freq = student_freq.sort_values('VisitCount', ascending=False)
        
        # Display top attendees
        st.subheader("Top 10 Students by Attendance")
        if 'SchoolName' in student_freq.columns:
            st.dataframe(student_freq.head(10)[['Name', 'StudentID', 'SchoolName', 'VisitCount']], use_container_width=True)
        else:
            st.dataframe(student_freq.head(10)[['Name', 'StudentID', 'VisitCount']], use_container_width=True)
        
        # Create histogram of visit counts
        fig = px.histogram(student_freq, x='VisitCount', nbins=20, 
                          title='Distribution of Student Visit Frequency')
        fig.update_layout(xaxis_title='Number of Visits', yaxis_title='Number of Students')
        st.plotly_chart(fig, use_container_width=True)
        
        # Identify students with low attendance
        low_attendance = student_freq[student_freq['VisitCount'] <= 3]
        
        if not low_attendance.empty:
            st.subheader("Students with Low Attendance (3 or fewer visits)")
            if 'SchoolName' in low_attendance.columns:
                st.dataframe(low_attendance[['Name', 'StudentID', 'SchoolName', 'VisitCount']], use_container_width=True)
            else:
                st.dataframe(low_attendance[['Name', 'StudentID', 'VisitCount']], use_container_width=True)
                
            # Download option for low attendance students
            st.download_button(
                label="Download Low Attendance List",
                data=low_attendance.to_csv(index=False),
                file_name="low_attendance_students.csv",
                mime="text/csv"
            )