import streamlit as st
from datetime import datetime, timedelta, date
from collections import defaultdict

from db_manager import (
    get_all_availabilities, book_slot, is_slot_booked, has_candidate_booked,
    get_candidate_booking, submit_reschedule_request, get_candidate_id, add_candidate,
    get_all_bookings, is_candidate_already_booked_for_interviewer
)
from slot_utils import split_into_half_hour_slots

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
        booking = get_candidate_booking(candidate_email)
        if booking:
            current_date, current_time = booking['slot_date'], booking['slot_time']
            try:
                start_time_obj = datetime.strptime(current_time, "%H:%M:%S").time()
            except ValueError:
                start_time_obj = datetime.strptime(current_time, "%H:%M").time()

            start_datetime = datetime.combine(date.today(), start_time_obj)
            end_datetime = start_datetime + timedelta(minutes=30)
            start_str = start_datetime.strftime("%I:%M %p")
            end_str = end_datetime.strftime("%I:%M %p")

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
                    label = f"{slot_str}"
                    with col:
                        if st.button(label, key=f"reschedule_{interviewer_email}_{slot_str}"):
                            new_time = slot_start.strftime("%H:%M:%S")
                            submit_reschedule_request(
                                candidate_email,
                                reschedule_date_str,
                                new_time,
                                reason
                            )
                            st.success(f"✅ Reschedule request for {slot_str} on {reschedule_date_str} submitted!")
                            st.stop()
            else:
                st.info("ℹ️ No available slots on the selected reschedule date.")

    else:
        # Fetch all availability
        all_availabilities = get_all_availabilities()
        slots_for_date = [slot for slot in all_availabilities if slot[2] == selected_date_str]

                # Fetch all bookings once
        all_bookings = get_all_bookings()

        # Create a set of booked slots for quick lookup
        booked_slots_set = set(
            (booking['interviewer_email'], booking['slot_date'], booking['slot_time'][:5])  # truncate seconds
            for booking in all_bookings
        )

        # Track booked slots for each interviewer for the selected date
        interviewer_booked_slots = defaultdict(list)

        for availability in slots_for_date:
            interviewer_email = availability[0]
            start_time = datetime.strptime(availability[3], "%H:%M:%S").time()
            end_time = datetime.strptime(availability[4], "%H:%M:%S").time()
            half_hour_slots = split_into_half_hour_slots(start_time, end_time)

            for slot_start in half_hour_slots:
                slot_str = slot_start.strftime("%H:%M")
                if (
                    (interviewer_email, selected_date_str, slot_str) in booked_slots_set
                    or is_candidate_already_booked_for_interviewer(candidate_email, interviewer_email, selected_date_str)
                ):
                    interviewer_booked_slots[slot_str].append(interviewer_email)


        # Map time slots to a list of interviewers available at that time
        slot_interviewer_map = defaultdict(list)

        for availability in slots_for_date:
            interviewer_email = availability[0]
            start_time = datetime.strptime(availability[3], "%H:%M:%S").time()
            end_time = datetime.strptime(availability[4], "%H:%M:%S").time()
            half_hour_slots = split_into_half_hour_slots(start_time, end_time)

            for slot_start in half_hour_slots:
                slot_str = slot_start.strftime("%H:%M")

                # Check if this interviewer is already booked for this slot or candidate already booked with this interviewer
                if (
                    (interviewer_email, selected_date_str, slot_str) not in booked_slots_set
                    and not is_candidate_already_booked_for_interviewer(candidate_email, interviewer_email, selected_date_str)
                ):
                    slot_interviewer_map[slot_str].append(interviewer_email)

        # Only show one button per slot time
        if slot_interviewer_map:
            st.subheader(f"Available Slots on {selected_date.strftime('%A, %d %B %Y')}")
            cols = st.columns(4)

            for idx, (slot_str, interviewers) in enumerate(slot_interviewer_map.items()):
                if not interviewers:
                    continue
                col = cols[idx % 4]
                with col:
                    if st.button(slot_str, key=f"slot_{slot_str}"):
                        # Ensure candidate is registered
                        if not get_candidate_id(candidate_email):
                            if candidate_name and candidate_phone:
                                add_candidate(name=candidate_name, phone=candidate_phone, email=candidate_email)
                            else:
                                st.error("Please enter your name and phone number before booking.")
                                st.stop()

                        # Assign first available interviewer for that slot
                        selected_interviewer = interviewers[0]

                        # Book the slot
                        book_slot(candidate_email, selected_interviewer, selected_date_str, slot_str, timezone)
                        st.success(f"🎉 You have successfully booked {slot_str} on {selected_date_str}")
                        st.stop()
        else:
            st.info("ℹ️ No slots available for the selected date.")


