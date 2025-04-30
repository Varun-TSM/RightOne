import streamlit as st
from datetime import datetime, timedelta, date
from collections import defaultdict

from db_manager import (
    get_all_availabilities, book_slot, is_slot_booked, has_candidate_booked,
    get_candidate_booking, submit_reschedule_request, get_candidate_id, add_candidate,
    get_all_bookings, is_candidate_already_booked_for_interviewer
)
from slot_utils import split_into_half_hour_slots

def book_slots():
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css"/>', unsafe_allow_html=True)

    st.markdown("""
    <h3 style='font-weight:600;'>
        <i class="fa-solid fa-user-tie" style="margin-right:10px; color:#007BFF;"></i>Interview Slot Booking - Candidate's space
    </h3>
    """, unsafe_allow_html=True)
    # Custom CSS for improved styling
    st.markdown("""
    <style>
        /* Main container styling */
        
        /* Section headers */
        .section-header {
            background: #a2aec1;
            padding: 12px 15px;
            border-radius: 8px;
            border-left: 4px solid #007BFF;
            margin-bottom: 20px;
        }
        
        /* Form input styling */
        .form-label {
            font-weight: 500;
            color: #495057;
            margin-bottom: 8px;
        }
        
        /* Input field hints */
        .field-hint {
            font-size: 0.85rem;
            color: #6c757d;
            margin-top: 4px;
        }
        
        /* Divider styling */
        .divider {
            height: 1px;
            background-color: #e9ecef;
            margin: 25px 0;
        }
    </style>
    """, unsafe_allow_html=True)

    # Load FontAwesome
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css"/>', unsafe_allow_html=True)
    st.markdown("Complete the form below to book your interview slot.")

    # Personal Information Section
    st.markdown("""
    <div class="section-header">
        <i class="fas fa-user" style="margin-right:10px; color:#007BFF;"></i>
        <span style="font-weight:600; color:#212529;">Personal Information</span>
    </div>
    """, unsafe_allow_html=True)

    # Two-column layout for name and email
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="form-label">Full Name</p>', unsafe_allow_html=True)
        candidate_name = st.text_input("", placeholder="Enter your full name", label_visibility="collapsed")
        st.markdown('<p class="field-hint">Please enter your name as it appears on your ID</p>', unsafe_allow_html=True)

    with col2:
        st.markdown('<p class="form-label">Email Address</p>', unsafe_allow_html=True)
        candidate_email = st.text_input("", placeholder="Enter your email address", label_visibility="collapsed")
        st.markdown('<p class="field-hint">We\'ll send the confirmation to this email</p>', unsafe_allow_html=True)

    # Phone number in its own row
    st.markdown('<p class="form-label">Phone Number</p>', unsafe_allow_html=True)
    candidate_phone = st.text_input("", placeholder="Enter your contact number", label_visibility="collapsed")
    st.markdown('<p class="field-hint">Please include country code (e.g. +91 87777 98888)</p>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Time & Date Selection Section
    st.markdown("""
    <div class="section-header">
        <i class="fas fa-clock" style="margin-right:10px; color:#007BFF;"></i>
        <span style="font-weight:600; color:#212529;">Time & Date Selection</span>
    </div>
    """, unsafe_allow_html=True)

    # Date picker and timezone in columns
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<p class="form-label">Preferred Interview Date</p>', unsafe_allow_html=True)
        selected_date = st.date_input("", date.today(), min_value=date.today(), label_visibility="collapsed")
        
        # Display selected date in a nicer format
        if selected_date:
            formatted_date = selected_date.strftime("%A, %B %d, %Y")
            st.markdown(f"""
            <div style="background-color: rgb(0 44 107);; border-radius: 6px; padding: 8px 12px; margin-top: 8px; display: inline-block;">
                <i class="fas fa-calendar-check" style="color: #007BFF; margin-right: 8px;"></i>
                {formatted_date}
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown('<p class="form-label">Your Timezone</p>', unsafe_allow_html=True)
        
        # Dictionary of timezone options with readable names
        timezone_options = {
            "UTC": "UTC (GMT+0)",
            "Asia/Kolkata": "Asia/Kolkata (GMT+5:30)",
            "America/New_York": "New York (GMT-5/4)",
            "Europe/London": "London (GMT+0/1)"
        }
        
        # Show friendly timezone names in the dropdown
        timezone = st.selectbox(
            "", 
            options=list(timezone_options.keys()),
            format_func=lambda x: timezone_options[x],
            label_visibility="collapsed"
        )


    if candidate_email and selected_date:
        st.markdown("---")
        selected_date_str = selected_date.strftime("%Y-%m-%d")

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

                st.markdown("""
                <h5><i class="fas fa-calendar-check" style="margin-right:10px; color:#007BFF;"></i> Your Current Booking</h5>
                """, unsafe_allow_html=True)
                st.info(f"**📅 Date:** {current_date}  \n**🕒 Slot:** {start_str} - {end_str}  \n**🕰️ Timezone:** {timezone}")

            with st.expander("🔁 Request a Reschedule"):
                new_date = st.date_input("📆 Select New Preferred Date", date.today() + timedelta(days=1))
                reschedule_date_str = new_date.strftime("%Y-%m-%d")
                reason = st.text_area("✏️ Reason for Rescheduling (Optional)")

                # Fetch availability and bookings
                all_availabilities = get_all_availabilities()
                all_bookings = get_all_bookings()

                # Set of (interviewer_email, date, time) tuples for booked slots
                booked_slots_set = set(
                    (booking['interviewer_email'], booking['slot_date'], booking['slot_time'][:5])
                    for booking in all_bookings
                )

                # Filter availability for selected date
                slots_for_date = [slot for slot in all_availabilities if slot[2] == reschedule_date_str]

                # slot_str -> list of available interviewers
                slot_interviewer_map = defaultdict(list)

                for availability in slots_for_date:
                    interviewer_email = availability[0]
                    start_time = datetime.strptime(availability[3], "%H:%M:%S").time()
                    end_time = datetime.strptime(availability[4], "%H:%M:%S").time()
                    half_hour_slots = split_into_half_hour_slots(start_time, end_time)

                    for slot_start in half_hour_slots:
                        slot_str = slot_start.strftime("%H:%M")
                        # Avoid current booking slot and duplicates
                        if (
                            (interviewer_email, reschedule_date_str, slot_str) not in booked_slots_set
                            # and not is_candidate_already_booked_for_interviewer(candidate_email, interviewer_email, reschedule_date_str)
                            and not (
                                reschedule_date_str == current_date
                                and slot_str == start_time_obj.strftime("%H:%M")
                            )
                        ):
                            slot_interviewer_map[slot_str].append(interviewer_email)

                # Display reschedule options
                if slot_interviewer_map:
                    st.markdown(f"<h5> Available Time Slots on {new_date.strftime('%A, %d %B %Y')}</h5>", unsafe_allow_html=True)
                    cols = st.columns(4)

                    for idx, (slot_str, interviewers) in enumerate(slot_interviewer_map.items()):
                        if interviewers:
                            col = cols[idx % 4]
                            with col:
                                if st.button(f"🕓 {slot_str}", key=f"reschedule_{slot_str}"):
                                    st.session_state["pending_reschedule"] = {
                                        "slot_str": slot_str,
                                        "interviewer": interviewers[0],  # Choosing the first available
                                        "date": reschedule_date_str,
                                        "reason": reason,
                                        "candidate_email": candidate_email
                                    }

                else:
                    st.info("No available slots for the selected reschedule date.")

                # Confirm reschedule
                if "pending_reschedule" in st.session_state:
                    req = st.session_state["pending_reschedule"]
                    st.info(f"Confirm reschedule to {req['slot_str']} on {req['date']}?")
                    if st.button("✅ Confirm Reschedule"):
                        submit_reschedule_request(
                            candidate_email=req["candidate_email"],
                            new_date=req["date"],
                            new_time=f"{req['slot_str']}:00",
                            reason=req["reason"]
                        )
                        st.success(f"Reschedule request for {req['slot_str']} on {req['date']} submitted!")
                        del st.session_state["pending_reschedule"]
                        st.stop()



        else:
            # Fresh Booking Flow
            all_availabilities = get_all_availabilities()
            slots_for_date = [slot for slot in all_availabilities if slot[2] == selected_date_str]
            all_bookings = get_all_bookings()

            booked_slots_set = set(
                (booking['interviewer_email'], booking['slot_date'], booking['slot_time'][:5])
                for booking in all_bookings
            )

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

            slot_interviewer_map = defaultdict(list)

            for availability in slots_for_date:
                interviewer_email = availability[0]
                start_time = datetime.strptime(availability[3], "%H:%M:%S").time()
                end_time = datetime.strptime(availability[4], "%H:%M:%S").time()
                half_hour_slots = split_into_half_hour_slots(start_time, end_time)

                for slot_start in half_hour_slots:
                    slot_str = slot_start.strftime("%H:%M")
                    if (
                        (interviewer_email, selected_date_str, slot_str) not in booked_slots_set
                        and not is_candidate_already_booked_for_interviewer(candidate_email, interviewer_email, selected_date_str)
                    ):
                        slot_interviewer_map[slot_str].append(interviewer_email)

            if slot_interviewer_map:
                st.markdown(f"<h5><i class='fas fa-clock' style='margin-right:10px; color:#007BFF;'></i> Available Time Slots on {selected_date.strftime('%A, %d %B %Y')}</h5>", unsafe_allow_html=True)
                cols = st.columns(4)

                for idx, (slot_str, interviewers) in enumerate(slot_interviewer_map.items()):
                    if not interviewers:
                        continue
                    col = cols[idx % 4]
                    with col:
                        if st.button(f"🕒 {slot_str}", key=f"slot_{slot_str}"):
                            if not candidate_name or not candidate_phone:
                                st.error("Please enter your name and phone number before booking.")
                                st.stop()

                            st.session_state["pending_booking"] = {
                                "slot_str": slot_str,
                                "interviewer": interviewers[0],
                                "date": selected_date_str,
                                "timezone": timezone,
                                "candidate_name": candidate_name,
                                "candidate_phone": candidate_phone,
                                "candidate_email": candidate_email
                            }

                # Show confirmation if booking is pending
                if "pending_booking" in st.session_state:
                    booking = st.session_state["pending_booking"]
                    st.info(f"Confirm slot for {booking['slot_str']} on {booking['date']}?")
                    confirm = st.button("Slot Confirmed")

                    if confirm:
                        if not get_candidate_id(booking["candidate_email"]):
                            add_candidate(
                                name=booking["candidate_name"],
                                phone=booking["candidate_phone"],
                                email=booking["candidate_email"]
                            )

                        book_slot(
                            booking["candidate_email"],
                            booking["interviewer"],
                            booking["date"],
                            booking["slot_str"],
                            booking["timezone"]
                        )
                        st.success(f"Successfully booked {booking['slot_str']} on {booking['date']}")
                        del st.session_state["pending_booking"]
                        st.stop()

            else:
                st.info("No slots available for the selected date.")
