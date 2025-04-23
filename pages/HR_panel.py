from db_manager import init_db, get_all_bookings, get_all_reschedule_requests, update_reschedule_status, update_invite_status
import streamlit as st
from utils.interview import send_interview_email
import sqlite3
from utils.candidate_email import shortlisted_email

def HrPanel():
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css"/>', unsafe_allow_html=True)
    init_db()
    st.markdown('<h1><i class="fa-solid fa-users-line"></i>HR Panel</h1>', unsafe_allow_html=True)
    st.markdown("Welcome to the HR dashboard. Manage candidates, send invites, and handle reschedule requests from one place.")

    tab1, tab2, tab3 = st.tabs([
        "HR Connect", 
        "Interview Invites", 
        "Reschedule Requests"
    ])

    # ------------------ TAB 1: Resume Shortlist ------------------ #
    with tab1:

        def get_candidates():
            conn = sqlite3.connect("candidates.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, phone, status FROM candidates")
            rows = cursor.fetchall()
            conn.close()
            return [{"id": row[0], "name": row[1], "email": row[2], "phone": row[3], "status": row[4]} for row in rows]

        def update_status(candidate_id, new_status):
            conn = sqlite3.connect("candidates.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE candidates SET status = ? WHERE id = ?", (new_status, candidate_id))
            conn.commit()
            conn.close()

        candidates = get_candidates()

        st.divider()

        for idx, c in enumerate(candidates):
            with st.container(border=True):
                col1, col2, col3 = st.columns([4, 2, 2])
                with col1:
                    st.markdown(f"**🧑 {c['name']}**")
                    st.markdown(f"📧 `{c['email']}`  \n📞 `{c['phone']}`")

                with col2:
                    badge_colors = {
                        "Pending": ("#fff3cd", "#856404"),
                        "Contacted": ("#d4edda", "#155724"),
                        "Rejected": ("#f8d7da", "#721c24"),
                    }
                    bg, color = badge_colors.get(c["status"], ("#e2e3e5", "#383d41"))
                    st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; height: 100%;">
                        <span style='background-color:{bg}; color:{color}; padding:6px 12px; border-radius:20px;'>
                            {c['status']}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                with col3:
                    accept_col, reject_col = col3.columns(2)
                    disabled = c["status"] in ["Contacted", "Rejected"]

                    if accept_col.button("✅", key=f"accept_{idx}", disabled=disabled):
                        update_status(c["id"], "Contacted")
                        shortlisted_email(c["email"], c["name"])
                        st.success(f"🎯 {c['name']} marked as Contacted.")
                        st.rerun()

                    if reject_col.button("❌", key=f"reject_{idx}", disabled=disabled):
                        update_status(c["id"], "Rejected")
                        st.warning(f"🚫 {c['name']} marked as Rejected.")
                        st.rerun()

    # ------------------ TAB 2: Interview Invites ------------------ #
    with tab2:
        bookings = get_all_bookings()
        st.markdown("<h3><i class='fa-solid fa-calendar-circle-user'></i>Manage interview invitations</h3>", unsafe_allow_html=True)

        if bookings:
            if "selected_bookings" not in st.session_state:
                st.session_state.selected_bookings = set()

            unsent_bookings = [b for b in bookings if b.get('email_sent_status') != "Sent"]

            select_all = st.checkbox("📌 Select All Unsents", key="select_all_checkbox", disabled=not unsent_bookings)

            st.divider()

            for idx, booking in enumerate(bookings):
                status = booking.get("email_sent_status", "Not Sent")
                with st.container(border=True):
                    col1, col2, col3, col4, col5, col6 = st.columns([0.5, 3, 3, 3, 2, 2])

                    checked = False
                    if status == "Not Sent":
                        if select_all:
                            checked = True
                        checked = col1.checkbox("", value=checked, key=f"select_{booking['id']}")
                        if checked:
                            st.session_state.selected_bookings.add(booking['id'])
                        else:
                            st.session_state.selected_bookings.discard(booking['id'])

                    else:
                        col1.markdown("✅")

                    col2.markdown(f"📧 `{booking['candidate_email']}`")
                    col3.markdown(f"👤 `{booking['interviewer_email']}`")
                    col4.markdown(f"📅 `{booking['slot_date']} {booking['slot_time']} ({booking['timezone']})`")

                    status_color = "#d4edda" if status == "Sent" else "#fff3cd"
                    status_text_color = "#155724" if status == "Sent" else "#856404"
                    col5.markdown(
                        f"<span style='background-color:{status_color}; color:{status_text_color}; padding:6px 12px; border-radius:20px;'>{status}</span>",
                        unsafe_allow_html=True
                    )

                    with col6:
                        if status == "Not Sent":
                            if st.button("Send", key=f"send_{booking['id']}"):
                                try:
                                    send_interview_email(
                                        candidate_email=booking['candidate_email'],
                                        interviewer_email=booking['interviewer_email'],
                                        date=booking['slot_date'],
                                        time=booking['slot_time'],
                                        timezone=booking['timezone'],
                                    )
                                    update_invite_status(booking['id'], "Sent")
                                    st.success(f"📨 Sent to {booking['candidate_email']}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                        else:
                            st.button("Sent ✅", key=f"sent_{booking['id']}", disabled=True)

            st.divider()

            if st.session_state.selected_bookings:
                if st.button("📨 Send Invitations to All Selected"):
                    for booking in bookings:
                        if booking['id'] in st.session_state.selected_bookings and booking.get('email_sent_status') != "Sent":
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
                                st.error(f"Error sending to {booking['candidate_email']}: {e}")
                    st.success("All selected invitations sent.")
                    st.rerun()
            else:
                st.info("No invitations selected.")

        else:
            st.info("No interview bookings found.")

    # ------------------ TAB 3: Reschedule Requests ------------------ #
    with tab3:
        reschedule_requests = get_all_reschedule_requests()

        if reschedule_requests:
            for idx, request in enumerate(reschedule_requests):
                with st.expander(f"🔄 {request['candidate_email']} requested reschedule", expanded=False):
                    st.markdown(f"**🕒 Current Slot:** `{request['current_slot_date']} {request['current_slot_time']}`")
                    st.markdown(f"**📅 Requested Slot:** `{request['requested_date']} {request['requested_time']}`")
                    st.markdown(f"**📝 Reason:** _{request['reason']}_")
                    st.markdown(f"**📌 Status:** `{request['status']}`")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Approve #{request['id']}", key=f"approve_{request['id']}"):
                            update_reschedule_status(request['id'], 'Approved')
                            st.success(f"Request #{request['id']} approved.")
                            st.rerun()

                    with col2:
                        if st.button(f"Reject #{request['id']}", key=f"reject_{request['id']}"):
                            update_reschedule_status(request['id'], 'Rejected')
                            st.warning(f"Request #{request['id']} rejected.")
                            st.rerun()
        else:
            st.info("No reschedule requests at the moment.")
