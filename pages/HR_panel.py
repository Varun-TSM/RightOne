from db_manager import init_db, get_all_bookings, get_all_reschedule_requests, update_reschedule_status, update_invite_status
import streamlit as st
from utils.interview import send_interview_email
import sqlite3
from utils.candidate_email import shortlisted_email
def HrPanel():
    # Initialize the DB
    init_db()
    st.title("HR Interview Panel")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["👤 HR Connect", "📅 Interview invites", "🔁 Reschedule Requests"])

    # ------------------ TAB 1: Resume Shortlist ------------------ #
    with tab1:
        st.subheader("Shortlisted Candidates")

        def get_candidates():
            conn = sqlite3.connect("candidates.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, phone, status FROM candidates")
            rows = cursor.fetchall()
            conn.close()
            return [
                {"id": row[0], "name": row[1], "email": row[2], "phone": row[3], "status": row[4]}
                for row in rows
            ]

        def update_status(candidate_id, new_status):
            conn = sqlite3.connect("candidates.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE candidates SET status = ? WHERE id = ?", (new_status, candidate_id))
            conn.commit()
            conn.close()

        candidates = get_candidates()

        # Header
        header1, header2, header3 = st.columns([4, 2, 2])
        header1.markdown("**👤 Candidate Details**")
        header2.markdown("**📌 Status**")
        header3.markdown("**⚙️ Actions**")
        st.markdown("---")

        for idx, c in enumerate(candidates):
            col1, col2, col3 = st.columns([4, 2, 2])

            with col1:
                st.markdown(f"**{c['name']}**  \n📧 {c['email']}  \n📞 {c['phone']}")

            with col2:
                badge = {
                    "Pending": ("#fff3cd", "#856404"),
                    "Contacted": ("#d4edda", "#155724"),
                    "Rejected": ("#f8d7da", "#721c24"),
                }
                bg, color = badge.get(c["status"], ("#e2e3e5", "#383d41"))
                st.markdown(
                    f"<span style='background-color:{bg}; color:{color}; padding:4px 10px; border-radius:10px;'>{c['status']}</span>",
                    unsafe_allow_html=True
                )

            with col3:
                col3_1, col3_2 = col3.columns(2)

                # Disable buttons if already Contacted or Rejected
                disabled = c["status"] in ["Contacted", "Rejected"]

                if col3_1.button("✅", key=f"accept_{idx}", disabled=disabled):
                    update_status(c["id"], "Contacted")
                    st.success(f"{c['name']} marked as Contacted")
                    shortlisted_email(c["email"], c["name"])
                    st.rerun()

                if col3_2.button("❌", key=f"reject_{idx}", disabled=disabled):
                    update_status(c["id"], "Rejected")
                    st.warning(f"{c['name']} marked as Rejected")
                    st.rerun()

            st.markdown("---")





    with tab2:
        bookings = get_all_bookings()

        if bookings:
            st.subheader("Interview Invitations")

            # Initialize session state for selected bookings
            if "selected_bookings" not in st.session_state:
                st.session_state.selected_bookings = set()

            # Filter only those not sent yet
            unsent_bookings = [b for b in bookings if b.get('email_sent_status', 'Not Sent') == "Not Sent"]

            # Select All Checkbox
            select_all = st.checkbox("Select All Invitations to Send", key="select_all_checkbox", disabled=not unsent_bookings)

            # Table headers
            col1, col2, col3, col4, col5, col6 = st.columns([0.5, 3, 3, 3, 2, 2])
            col1.markdown("**✅**")
            col2.markdown("**📧 Candidate Email**")
            col3.markdown("**👤 Interviewer Email**")
            col4.markdown("**📅 Slot (Date & Time)**")
            col5.markdown("**📌 Status**")
            col6.markdown("**✉️ Action**")

            st.markdown("---")

            # Track selection
            selected_ids = []

            for idx, booking in enumerate(bookings):
                candidate_email = booking['candidate_email']
                interviewer_email = booking['interviewer_email']
                date = booking['slot_date']
                time = booking['slot_time']
                timezone = booking['timezone']
                email_sent_status = booking.get('email_sent_status', 'Not Sent')
                booking_id = booking['id']

                # Use columns
                col1, col2, col3, col4, col5, col6 = st.columns([0.5, 3, 3, 3, 2, 2])

                # Select checkbox
                checked = False
                if email_sent_status == "Not Sent":
                    if select_all:
                        checked = True
                    checked = col1.checkbox("", value=checked, key=f"select_{booking_id}")
                    if checked:
                        selected_ids.append(booking_id)
                else:
                    col1.markdown("")

                # Booking Info
                col2.markdown(candidate_email)
                col3.markdown(interviewer_email)
                col4.markdown(f"{date} {time} ({timezone})")

                # Status Tag
                if email_sent_status == "Sent":
                    col5.markdown(
                        "<span style='background-color:#d4edda; color:#155724; padding:4px 10px; border-radius:10px;'>Sent</span>",
                        unsafe_allow_html=True
                    )
                else:
                    col5.markdown(
                        "<span style='background-color:#fff3cd; color:#856404; padding:4px 10px; border-radius:10px;'>Not Sent</span>",
                        unsafe_allow_html=True
                    )

                # Individual send
                with col6:
                    if email_sent_status == "Not Sent":
                        if st.button("Send", key=f"send_{booking_id}"):
                            try:
                                send_interview_email(
                                    candidate_email=candidate_email,
                                    interviewer_email=interviewer_email,
                                    date=date,
                                    time=time,
                                    timezone=timezone,
                                )
                                update_invite_status(booking_id, "Sent")
                                st.success(f"✅ Invitation sent to {candidate_email}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error sending to {candidate_email}: {str(e)}")
                    else:
                        st.button("Sent ✅", key=f"sent_{booking_id}", disabled=True)

            st.markdown("---")

            # Send to all selected
            if selected_ids:
                if st.button("📨 Send Invitations to All Selected"):
                    for booking in bookings:
                        if booking['id'] in selected_ids and booking.get('email_sent_status', 'Not Sent') == "Not Sent":
                            try:
                                send_interview_email(
                                    candidate_email=booking['candidate_email'],
                                    interviewer_email=booking['interviewer_email'],
                                    date=booking['slot_date'],
                                    time=booking['slot_time'],
                                    timezone=booking['timezone'],
                                
                                )
                                update_invite_status(booking['id'], "Sent")
                            except Exception as e:
                                st.error(f"❌ Error sending to {booking['candidate_email']}: {str(e)}")
                    st.success("✅ Invitations sent to all selected candidates.")
                    st.rerun()
            else:
                st.warning("No invitations selected to send.")

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
