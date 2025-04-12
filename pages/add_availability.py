import streamlit as st
from streamlit_calendar import calendar
import datetime
from db_manager import get_interviewer_id, add_availability

st.set_page_config(page_title="Add Interviewer Availability", layout="wide")
st.title("📅 Interviewer Availability Management System")

# --- Initialization ---
if "events" not in st.session_state:
    st.session_state.events = []

# --- Input: Interviewer's Email ---
email = st.text_input("Enter Interviewer's Email:")

# --- Main Layout ---
left_col, right_col = st.columns([1, 2])

with left_col:
    st.header("➕ Add New Availability")

    selected_date = st.date_input("Select Date", min_value=datetime.date.today())

    # Skip Sundays
    if selected_date.weekday() == 6:
        st.warning("🚫 Sunday is not allowed. Please pick another day.")
    else:
        # Define time slots (10AM to 8PM, half-hour slots)
        time_options = [datetime.time(hour=h, minute=m) for h in range(10, 20+1) for m in (0, 30)]

        start_time = st.selectbox("Start Time", time_options, key="start_time")
        valid_end_times = [t for t in time_options if t > start_time]

        if valid_end_times:
            end_time = st.selectbox("End Time", valid_end_times, key="end_time")
        else:
            st.error("⚠️ No valid end times available. Adjust start time.")
            end_time = None

        if end_time and st.button("➕ Add Availability"):
            new_event = {
                "id": f"event_{len(st.session_state.events)+1}",
                "title": f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}",
                "start": datetime.datetime.combine(selected_date, start_time).isoformat(),
                "end": datetime.datetime.combine(selected_date, end_time).isoformat(),
            }
            st.session_state.events.append(new_event)
            st.success("✅ Availability Added!")

with right_col:
    st.header("📅 Calendar Preview")

    calendar_options = {
        "editable": False,
        "initialView": "dayGridMonth",
        "selectable": False,
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
st.header("🗂️ Current Availabilities")

if st.session_state.events:
    for idx, ev in enumerate(st.session_state.events):
        col1, col2 = st.columns([6, 1])
        with col1:
            event_date = datetime.datetime.fromisoformat(ev['start']).strftime("%A, %d %B %Y")
            st.write(f"📅 {event_date} | 🕑 {ev['title']}")
        with col2:
            if st.button("❌ Delete", key=f"delete_{idx}"):
                st.session_state.events.pop(idx)
                st.rerun()

else:
    st.info("ℹ️ No availabilities added yet.")

# --- Final Submit ---
st.divider()
if st.session_state.events:
    if st.button("✅ Submit All Availabilities"):
        if email:
            interviewer_id = get_interviewer_id(email)  # Assuming db_manager handles this
            for event in st.session_state.events:
                start_dt = datetime.datetime.fromisoformat(event['start'])
                end_dt = datetime.datetime.fromisoformat(event['end'])
                add_availability(interviewer_id, start_dt.date(), start_dt.time(), end_dt.time())
            st.success("🎉 All availabilities submitted successfully!")
            st.session_state.events = []
        else:
            st.error("🚨 Please enter Interviewer's email first.")





# import streamlit as st
# from streamlit_calendar import calendar
# import datetime
# from db_manager import get_interviewer_id, add_availability

# st.set_page_config(page_title="Add Interviewer Availability", layout="wide")
# st.title("📅 Interviewer Availability Calendar (Auto 30-mins End Time)")

# # Input Email
# email = st.text_input("Enter Interviewer's Email:")

# # Initialize session state
# if "availabilities" not in st.session_state:
#     st.session_state.availabilities = []

# # Calendar Options
# calendar_options = {
#     "selectable": True,
#     "editable": True,
#     "initialView": "timeGridWeek",  # Show week view to pick time
#     "slotDuration": "00:30:00",  
#     "slotMinTime": "10:00:00",  # Start time for the calendar
#     "slotMaxTime": "22:00:00",  # End time for the calendar
#     # 30-min slots
#     "headerToolbar": {
#         "left": "prev,next today",
#         "center": "title",
#         "right": "dayGridMonth,timeGridWeek,timeGridDay"
#     },
# }

# # Render the calendar
# st.subheader("🗓️ Select your availability slots:")
# calendar_events = calendar(options=calendar_options)

# # Process selected events
# if calendar_events and "events" in calendar_events:
#     new_availabilities = []
#     for event in calendar_events["events"]:
#         start_dt = datetime.datetime.fromisoformat(event["start"])
#         end_dt = datetime.datetime.fromisoformat(event["end"])
        
#         # Only save future slots
#         if start_dt.date() >= datetime.date.today():
#             new_availabilities.append({
#                 "date": start_dt.date(),
#                 "start_time": start_dt.time(),
#                 "end_time": end_dt.time(),
#             })

#     st.session_state.availabilities = new_availabilities

# # Divider
# st.divider()

# # Show the captured availability slots
# st.subheader("📋 Captured Availabilities:")

# if st.session_state.availabilities:
#     for idx, slot in enumerate(st.session_state.availabilities):
#         st.write(f"{idx+1}. **{slot['date'].strftime('%A, %d %B %Y')}** — {slot['start_time']} to {slot['end_time']}")
# else:
#     st.info("No availabilities selected yet. Please click and drag on the calendar.")

# # Save to database
# if st.button("💾 Save All to Database"):
#     if email and st.session_state.availabilities:
#         interviewer_id = get_interviewer_id(email)
#         if interviewer_id:
#             for slot in st.session_state.availabilities:
#                 day_name = slot["date"].strftime('%A')
#                 add_availability(interviewer_id, day_name, str(slot["start_time"]), str(slot["end_time"]), slot["date"])
#             st.success("🎉 Successfully saved all availabilities!")
#             st.session_state.availabilities.clear()
#         else:
#             st.error("⚠️ Interviewer email not found.")
#     else:
#         st.error("⚠️ Please enter the email and select at least one availability slot.")
