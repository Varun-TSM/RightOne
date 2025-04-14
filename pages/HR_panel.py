from db_manager import init_db, get_all_bookings, get_all_reschedule_requests, update_reschedule_status, update_invite_status
from email_utils import send_invite_email
import streamlit as st

# Initialize the DB
init_db()

st.set_page_config(page_title="HR Panel", layout="wide")
st.title("HR Interview Panel")

# Tabs
tab1, tab2, tab3 = st.tabs(["👤 HR Connect", "📅 Interview invites", "🔁 Reschedule Requests"])

# ------------------ TAB 1: Resume Shortlist ------------------ #
with tab1: 
    st.subheader("Shortlisted Candidates")

    # Sample data (replace with database fetch later)
    candidates = [
        {
            "name": "John Smith",
            "email": "john.smith@example.com",
            "phone": "+1 234-567-8901",
            "status": "Pending"
        },
        {
            "name": "Emily Johnson",
            "email": "emily.johnson@example.com",
            "phone": "+1 234-567-8902",
            "status": "Contacted"
        },
        {
            "name": "Michael Brown",
            "email": "michael.brown@example.com",
            "phone": "+1 234-567-8903",
            "status": "Pending"
        }
    ]

    # Header row with 3 columns
    header1, header2, header3 = st.columns([4, 2, 2])
    header1.markdown("**👤 Candidate Details**")
    header2.markdown("**📌 Status**")
    header3.markdown("**⚙️ Actions**")
    st.markdown("---")

    # Display each candidate row
    for idx, c in enumerate(candidates):
        col1, col2, col3 = st.columns([4, 2, 2])

        # Candidate info
        with col1:
            st.markdown(f"**{c['name']}**  \n📧 {c['email']}  \n📞 {c['phone']}")

        # Status badge
        with col2:
            if c["status"] == "Pending":
                st.markdown(
                    "<span style='background-color:#fff3cd; color:#856404; padding:4px 10px; border-radius:10px;'>Pending</span>",
                    unsafe_allow_html=True)
            elif c["status"] == "Contacted":
                st.markdown(
                    "<span style='background-color:#d4edda; color:#155724; padding:4px 10px; border-radius:10px;'>Contacted</span>",
                    unsafe_allow_html=True)

        # Action buttons
        with col3:
            col3_1, col3_2 = st.columns(2)
            if col3_1.button("✅", key=f"accept_{idx}"):
                st.success(f"Accepted {c['name']}")
                # Update DB or candidate list here
            if col3_2.button("❌", key=f"reject_{idx}"):
                st.warning(f"Rejected {c['name']}")
                # Update DB or candidate list here

        st.markdown("---")



# ------------------ TAB 2: Bookings ------------------ #
with tab2:
    bookings = get_all_bookings()

    if bookings:
        st.subheader("Interview Invitations")

        # Table header
        col1, col2, col3, col4, col5 = st.columns([3, 3, 3, 2, 2])
        col1.markdown("**📧 Candidate Email**")
        col2.markdown("**👤 Interviewer Email**")
        col3.markdown("**📅 Slot (Date & Time)**")
        col4.markdown("**📌 Status**")
        col5.markdown("**✉️ Action**")

        st.markdown("---")

        for idx, booking in enumerate(bookings):
            candidate_email = booking['candidate_email']
            interviewer_email = booking['interviewer_email']
            date = booking['slot_date']
            time = booking['slot_time']
            timezone = booking['timezone']
            email_sent_status = booking.get('email_sent_status', 'Not Sent')
            booking_id = booking['id']  # Unique ID per booking

            col1, col2, col3, col4, col5 = st.columns([3, 3, 3, 2, 2])
            col1.markdown(candidate_email)
            col2.markdown(interviewer_email)
            col3.markdown(f"{date} {time} ({timezone})")

            # Show status tag
            if email_sent_status == "Sent":
                col4.markdown(
                    "<span style='background-color:#d4edda; color:#155724; padding:4px 10px; border-radius:10px;'>Sent</span>",
                    unsafe_allow_html=True
                )
            else:
                col4.markdown(
                    "<span style='background-color:#fff3cd; color:#856404; padding:4px 10px; border-radius:10px;'>Not Sent</span>",
                    unsafe_allow_html=True
                )

            # Action button
            with col5:
                if email_sent_status == "Not Sent":
                    if st.button("Send", key=f"send_{booking_id}"):  # Unique key
                        try:
                            send_invite_email(
                                candidate_email=candidate_email,
                                interviewer_email=interviewer_email,
                                date=date,
                                time=time,
                                timezone=timezone,
                                for_hr=True
                            )
                            update_invite_status(booking_id, "Sent")
                            st.success(f"✅ Invitation sent to {candidate_email}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error sending to {candidate_email}: {str(e)}")
                else:
                    st.button("Sent ✅", key=f"sent_{booking_id}", disabled=True)

        st.markdown("---")

    else:
        st.info("No interview bookings available.")




# ------------------ TAB 3: Reschedule Requests ------------------ #
with tab3:
    reschedule_requests = get_all_reschedule_requests()

    if reschedule_requests:
        for idx, request in enumerate(reschedule_requests):
            with st.expander(f"{request['candidate_email']} wants to reschedule"):
                st.write(f"**Current Slot:** {request['current_slot_date']} {request['current_slot_time']}")
                st.write(f"**Requested Slot:** {request['requested_date']} {request['requested_time']}")
                st.write(f"**Reason:** {request['reason']}")
                st.write(f"**Status:** {request['status']}")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(f"Approve Request #{request['id']}", key=f"approve_{request['id']}_{idx}"):
                        update_reschedule_status(request['id'], 'Approved')
                        st.success(f"Reschedule Request #{request['id']} approved.")
                        st.rerun()

                with col2:
                    if st.button(f"Reject Request #{request['id']}", key=f"reject_{request['id']}_{idx}"):
                        update_reschedule_status(request['id'], 'Rejected')
                        st.warning(f"Reschedule Request #{request['id']} rejected.")
                        st.rerun()

    else:
        st.info("No reschedule requests found.")
