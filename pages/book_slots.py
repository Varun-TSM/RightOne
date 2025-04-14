import streamlit as st
from datetime import datetime, timedelta, date

from db_manager import get_all_availabilities, book_slot, is_slot_booked, has_candidate_booked, get_candidate_booking,submit_reschedule_request, get_candidate_id,add_candidate
from slot_utils import split_into_half_hour_slots
# from email_utils import send_invite_email

st.set_page_config(page_title="Candidate Slot Booking", layout="wide")
st.title("📅 Candidate Slot Booking")

# User inputs
candidate_email = st.text_input("Enter Your Email 📧:")
candidate_name = st.text_input("Enter Your Full Name 👤:")
candidate_phone = st.text_input("Enter Your Phone Number 📞:")


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
            reschedule_date_str = new_date.strftime("%Y-%m-%d")

            reason = st.text_area("Optional: Reason for Rescheduling 📝")

            all_availabilities = get_all_availabilities()
            reschedule_slots = [slot for slot in all_availabilities if slot[2] == reschedule_date_str]

            new_available_slots = []

            for availability in reschedule_slots:
                interviewer_email = availability[0]
                start_time = datetime.strptime(availability[3], "%H:%M:%S").time()
                end_time = datetime.strptime(availability[4], "%H:%M:%S").time()

                half_hour_slots = split_into_half_hour_slots(start_time, end_time)

                for slot_start in half_hour_slots:
                    slot_str = slot_start.strftime("%H:%M")
                    if not is_slot_booked(interviewer_email, reschedule_date_str, slot_str) and not (
                        reschedule_date_str == current_date and slot_str == start_time_obj.strftime("%H:%M")
                    ):
                        new_available_slots.append((interviewer_email, slot_start))

            if new_available_slots:
                st.write(f"### Available Slots on {new_date.strftime('%A, %d %B %Y')}")

                cols = st.columns(4)
                for idx, (interviewer_email, slot_start) in enumerate(new_available_slots):
                    col = cols[idx % 4]
                    slot_str = slot_start.strftime("%H:%M")
                    with col:
                        if st.button(slot_str, key=f"reschedule_{interviewer_email}_{slot_str}"):
                            new_time = slot_start.strftime("%H:%M:%S")
                            submit_reschedule_request(
                                candidate_email,
                                reschedule_date_str,
                                new_time,
                                reason  # now it captures the input
                            )
                            st.success(f"✅ Reschedule request for {slot_str} on {reschedule_date_str} submitted!")
                            st.stop()
            else:
                st.info("ℹ️ No available slots on the selected reschedule date.")



    
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
                        # Check if candidate exists; if not, add them
                        if not get_candidate_id(candidate_email):
                            if candidate_name and candidate_phone:
                                add_candidate(name=candidate_name, phone=candidate_phone, email=candidate_email)
                            else:
                                st.error("Please enter your name and phone number before booking.")
                                st.stop()

                        # Book the slot
                        book_slot(candidate_email, interviewer_email, selected_date_str, slot_time, timezone)

                        # Send email
                        from email_utils import send_invite_email
                        send_invite_email(
                            candidate_email=candidate_email,
                            interviewer_email=None,  # update this if needed
                            date=selected_date_str,
                            time=slot_start.strftime("%H:%M"),
                            timezone=timezone,
                            for_hr=False
                        )

                        st.success(f"🎉 You have successfully booked {slot_time} on {selected_date_str}")
                        st.stop()
        else:
            st.info("ℹ️ No slots available for the selected date.")


