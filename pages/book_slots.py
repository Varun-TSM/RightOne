import streamlit as st
from datetime import datetime, timedelta, date

from db_manager import get_all_availabilities, book_slot, is_slot_booked, has_candidate_booked, get_candidate_booking,submit_reschedule_request
from slot_utils import split_into_half_hour_slots
# from email_utils import send_invite_email

st.set_page_config(page_title="Candidate Slot Booking", layout="wide")
st.title("📅 Candidate Slot Booking")

# User inputs
candidate_email = st.text_input("Enter Your Email 📧:")

timezone = st.selectbox(
    "Select Your Timezone 🌎",
    ["UTC", "Asia/Kolkata", "America/New_York", "Europe/London"]
)

selected_date = st.date_input("Pick a Date 🗓️", date.today())

if candidate_email and selected_date:
    st.write("---")
    selected_date_str = selected_date.strftime("%Y-%m-%d")

    # Check if candidate already booked
    if has_candidate_booked(candidate_email):
        st.warning("⚠️ You have already booked a slot. You can request a reschedule after a day.")
        booking = get_candidate_booking(candidate_email)  # Create this function if not exists
        if booking:
            current_date, current_time = booking['slot_date'], booking['slot_time']
            # st.subheader(f"Current Booking: {current_date} at {current_time}")
            try:
               start_time_obj = datetime.strptime(current_time, "%H:%M:%S").time()
            except ValueError:
              start_time_obj = datetime.strptime(current_time, "%H:%M").time()

        # Create a datetime object for today with that time
        start_datetime = datetime.combine(date.today(), start_time_obj)

        # Add 30 minutes to get end time
        end_datetime = start_datetime + timedelta(minutes=30)

        # Format times to readable strings
        start_str = start_datetime.strftime("%I:%M %p")  # Ex: 11:30 AM
        end_str = end_datetime.strftime("%I:%M %p")      # Ex: 12:00 PM

        # Display
        st.subheader("📋 Your Current Booking Details")
        st.info(f"**Date:** {current_date}  \n**Slot:** {start_str} - {end_str}  \n**Timezone:** {timezone}")
        
        
        
        with st.expander("📋 Request Reschedule"):
            new_date = st.date_input("Select New Preferred Date 📅", date.today() + timedelta(days=1))
            new_time = st.time_input("Select New Preferred Time ⏰")
            reason = st.text_area("Reason for Rescheduling (Optional)")

            if st.button("Submit Reschedule Request"):
                # Fetch current booking info
                    new_date =  new_date.strftime("%Y-%m-%d")
                    new_time = new_time.strftime("%H:%M:%S")
                    submit_reschedule_request(
                        candidate_email,
                        new_date, 
                        new_time, 
                        reason
                    )
                    st.success("✅ Reschedule request submitted! We will get back to you soon.")
                # else:
                #     st.error("❌ Could not fetch your current booking. Please contact support.")

    
    else:
        # Fetch all availability
        all_availabilities = get_all_availabilities()

        # Filter for selected date
        slots_for_date = [slot for slot in all_availabilities if slot[2] == selected_date_str]

        available_slots = []  # (interviewer_email, slot_time) pairs

        for availability in slots_for_date:
            interviewer_email = availability[0]
            start_time = datetime.strptime(availability[3], "%H:%M:%S").time()
            end_time = datetime.strptime(availability[4], "%H:%M:%S").time()

            half_hour_slots = split_into_half_hour_slots(start_time, end_time)

            for slot_start in half_hour_slots:
                slot_str = slot_start.strftime("%H:%M")
                if not is_slot_booked(interviewer_email, selected_date_str, slot_str):
                    available_slots.append((interviewer_email, slot_str))

        if available_slots:
            st.subheader(f"Available Slots on {selected_date.strftime('%A, %d %B %Y')}")

            cols = st.columns(4)  # 4 slots per row

            for idx, (interviewer_email, slot_time) in enumerate(available_slots):
                col = cols[idx % 4]
                with col:
                    if st.button(slot_time, key=f"{interviewer_email}_{slot_time}"):
                        # Book the slot
                        book_slot(candidate_email, interviewer_email, selected_date_str, slot_time, timezone)
                        #send_invite_email(candidate_email, interviewer_email, selected_date_str)
                        from email_utils import send_invite_email

# After successful booking:
                        send_invite_email(
                            candidate_email=candidate_email,
                            interviewer_email=None,  # No interviewer now
                            date=selected_date_str,
                            time=slot_start.strftime("%H:%M"),
                            timezone=timezone,
                            for_hr=False
                        )

                        st.success(f"🎉 You have successfully booked {slot_time} on {selected_date_str}")
                        st.stop()
        else:
            st.info("ℹ️ No slots available for the selected date.")


