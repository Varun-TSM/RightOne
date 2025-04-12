from db_manager import init_db
init_db()
import streamlit as st
from db_manager import get_all_bookings, get_all_reschedule_requests, update_reschedule_status
from email_utils import send_invite_email

st.set_page_config(page_title="HR Panel", layout="wide")
st.title("HR Interview Panel")

tab1, tab2, tab3 = st.tabs(["HR connect","📅 Interview Bookings", "🔁 Reschedule Requests"])

# ------------------ TAB 2: Bookings ------------------ #
with tab2:
    bookings = get_all_bookings()

    if bookings:
        selected = []
        for booking in bookings:
            candidate_email = booking['candidate_email']
            interviewer_email = booking['interviewer_email']
            date = booking['slot_date']
            time = booking['slot_time']
            timezone = booking['timezone']

            checkbox_label = f"{candidate_email} | Interviewer: {interviewer_email} | {date} {time} ({timezone})"
            if st.checkbox(checkbox_label, key=candidate_email):
                selected.append(booking)

        if st.button("Send Invitations"):
            for booking in selected:
                try:
                    send_invite_email(
                        candidate_email=booking['candidate_email'],
                        interviewer_email=booking['interviewer_email'],
                        date=booking['slot_date'],
                        time=booking['slot_time'],
                        timezone=booking['timezone'],
                        for_hr=True
                    )
                    st.success(f"📧 Email sent to {booking['candidate_email']}")
                except Exception as e:
                    st.error(f"Error sending email: {str(e)}")
    else:
        st.info("No bookings found.")

# ------------------ TAB 3: Reschedule Requests ------------------ #
with tab3:
    reschedule_requests = get_all_reschedule_requests()

    if reschedule_requests:
        for request in reschedule_requests:
            with st.expander(f"{request['candidate_email']} wants to reschedule"):
                st.write(f"**Current Slot:** {request['current_slot_date']} {request['current_slot_time']}")
                st.write(f"**Requested Slot:** {request['requested_date']} {request['requested_time']}")
                st.write(f"**Reason:** {request['reason']}")
                st.write(f"**Status:** {request['status']}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Approve Request #{request['id']}", key=f"approve_{request['id']}"):
                        # Update DB status
                        update_reschedule_status(request['id'], 'Approved')

                        # Also update the booking information after approval
                        # Here, update the interview booking based on reschedule request.
                        for booking in bookings:
                            if booking['candidate_email'] == request['candidate_email']:
                                booking['slot_date'] = request['requested_date']
                                booking['slot_time'] = request['requested_time']

                        # Send email
                        send_invite_email(
                            candidate_email=request['candidate_email'],
                            interviewer_email=None,  # Optional if not needed
                            date=request['requested_date'],
                            time=request['requested_time'],
                            timezone="UTC",  # Adjust timezone if needed
                            for_hr=True
                        )
                        st.success("Reschedule approved and email sent.")
                        # Re-fetch the bookings to show updated details
                        bookings = get_all_bookings()

                with col2:
                    if st.button(f"Reject Request #{request['id']}", key=f"reject_{request['id']}"):
                        update_reschedule_status(request['id'], 'Rejected')
                        st.warning("Reschedule request rejected.")
    else:
        st.info("No reschedule requests found.")
