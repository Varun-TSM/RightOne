import streamlit as st
from streamlit_calendar import calendar
import datetime
from db_manager import get_all_interviewers, get_interviewer_id, add_availability

def add_availabilities():
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css"/>', unsafe_allow_html=True)
    # Font Awesome Icons
    st.markdown("""
    <style>
        h1, h2, h3, h4, h5 {
            color: #007BFF;
            font-weight: 600;
        }

        /* Section styling */
        .availability-box {
            background-color: #FAFAFA;
            padding: 25px 20px;
            border-radius: 12px;
            border: 1px solid #E0E0E0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.04);
            margin-bottom: 25px;
        }

        /* Selectbox and inputs */
        .stSelectbox, .stDateInput {
            margin-bottom: 20px;
        }

        /* Buttons */
        .stButton > button {
            background-color: #007BFF;
            color: white;
            font-weight: 600;
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            transition: all 0.2s ease;
        }
        .stButton > button:hover {
            background-color: #0056b3;
            transform: scale(1.02);
        }

        /* Event listing */
        .event-item {
            border: 1px solid #e0e0e0;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .event-item:hover {
            background-color: #004c97;
            color: white;
        }

        .event-item .delete-btn {
            background: none;
            border: none;
            color: red;
            font-size: 18px;
            cursor: pointer;
        }
        
        .event-item .delete-btn:hover {
            transform: scale(1.1);
        }

        .info-message {
            color: #17a2b8;
            font-size: 16px;
            margin-top: 10px;
        }

    </style>
    """, unsafe_allow_html=True)
    st.markdown("<h2><i class='fas fa-calendar-check'></i> Interviewer Availability Management</h2>", unsafe_allow_html=True)

    # --- Initialization ---
    if "events" not in st.session_state:
        st.session_state.events = []

    interviewers = get_all_interviewers()

    # Determine what to show in the select box
    if interviewers:
        interviewers_with_placeholder = ["Your email-id"] + interviewers
    else:
        interviewers_with_placeholder = ["No interviewers available"]

    # Always show the select box
    email = st.selectbox("Select your email", interviewers_with_placeholder, index=0)

    # Logic to handle invalid selections
    if email in ["Your email-id", "No interviewers available"]:
        st.warning("Note : Add interviewer email to database")

    # --- Main Layout ---
    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.markdown("<h4><i class='fas fa-plus-circle'></i> Add New Availability</h4>", unsafe_allow_html=True)

        selected_date = st.date_input("Select Date", min_value=datetime.date.today())

        # Skip Sundays
        if selected_date.weekday() == 6:
            st.warning("Sunday is not allowed. Please pick another day.")
        else:
            # Define time slots (10AM to 8PM, half-hour slots)
            time_options = [datetime.time(hour=h, minute=m) for h in range(10, 20+1) for m in (0, 30)]
            current_time = datetime.datetime.now().time()
            one_hour_later = (datetime.datetime.combine(datetime.date.today(), current_time) + datetime.timedelta(hours=1)).time()

            # Filter time options to only include times at least one hour ahead
            valid_start_times = [t for t in time_options if t >= one_hour_later]
            
            if selected_date == datetime.date.today():
                valid_start_times = [t for t in time_options if t >= one_hour_later]
            else:
                valid_start_times = time_options  # Use full range for future dates
                
            start_time = st.selectbox("Start Time", valid_start_times, key="start_time")
            valid_end_times = [t for t in time_options if t > start_time] if start_time is not None else []

            if valid_end_times:
                end_time = st.selectbox("End Time", valid_end_times, key="end_time")
            else:
                st.error("No valid end times available. Adjust start time.")
                end_time = None

            if end_time and st.button("Add Availability"):
                new_start = datetime.datetime.combine(selected_date, start_time).isoformat()
                new_end = datetime.datetime.combine(selected_date, end_time).isoformat()

                # Check for duplicates
                is_duplicate = any(
                    ev["start"] == new_start and ev["end"] == new_end
                    for ev in st.session_state.events
                )

                if is_duplicate:
                    st.warning(":warning: This availability slot already exists!")
                else:
                    new_event = {
                        "id": f"event_{len(st.session_state.events)+1}",
                        "title": f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}",
                        "start": new_start,
                        "end": new_end,
                    }
                    st.session_state.events.append(new_event)
                    st.success("Availability Added!")

    with right_col:
        st.markdown("<h4><i class='fas fa-calendar-alt'></i> Calendar Preview</h4>", unsafe_allow_html=True)

        calendar_options = {
            "editable": False,
            "initialView": "dayGridMonth",
            "slotMinTime": "10:00:00",
            "slotMaxTime": "22:00:00",
            "selectable": False,
            "height":"450px",
            "events": st.session_state.events,
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek,timeGridDay"
            }
        }

        calendar(events=st.session_state.events, options=calendar_options)

    # --- List all added events with Delete Option ---
    st.divider()
    st.markdown("<h4><i class='fas fa-folder-open'></i> Current Availabilities</h4>", unsafe_allow_html=True)

    if st.session_state.events:
        for idx, ev in enumerate(st.session_state.events):
            col1, col2 = st.columns([6, 1])
            with col1:
                event_date = datetime.datetime.fromisoformat(ev['start']).strftime("%A, %d %B %Y")
                st.markdown(f"<div class='event-item'>📅 {event_date} | 🕑 {ev['title']}</div>", unsafe_allow_html=True)
            with col2:
                if st.button("Delete", key=f"delete_{idx}"):
                    st.session_state.events.pop(idx)
                    st.rerun()
    else:
        st.markdown("<div class='info-message'><i class='fas fa-info-circle'></i> No availabilities added yet.</div>", unsafe_allow_html=True)

    # --- Final Submit ---
    st.divider()
    if st.session_state.events:
        if st.button("Submit All Availabilities"):
            if email:
                interviewer_id = get_interviewer_id(email)  # Check if the email exists in the DB
                if interviewer_id:
                    # Proceed with saving availability
                    for event in st.session_state.events:
                        start_dt = datetime.datetime.fromisoformat(event['start'])
                        end_dt = datetime.datetime.fromisoformat(event['end'])
                        add_availability(interviewer_id, start_dt.date(), start_dt.time(), end_dt.time())
                    st.success("All availabilities submitted successfully!")
                    st.session_state.events = []  # Clear the events list after submission
                else:
                    st.error("Access Denied: Interviewer email not found.")
            else:
                st.error("Please enter Interviewer's email first.")
