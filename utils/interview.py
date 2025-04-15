import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

GMAIL_USER = "hr.demo.hiring@gmail.com"
GMAIL_PASSWORD = "jfvq qqkq gwrx ovlq"  



def send_interview_email(candidate_email, interviewer_email, date, time, timezone):
    subject = "Official Interview Invitation"
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            Hi {interviewer_email} as we discussed about this candidate for JD 
            <p>Dear {candidate_email},</p>

            <p>We are pleased to inform you that you have been shortlisted for the next round of interviews with <b>{interviewer_email}</b>.</p>
            
            <table style="border: 1px solid #ddd; padding: 10px; background-color: #f9f9f9;">
                <tr><td><b>Interview Date:</b></td><td>{date}</td></tr>
                <tr><td><b>Interview Time:</b></td><td>{time} ({timezone})</td></tr>
                <tr><td><b>Interviewer:</b></td><td>{interviewer_email}</td></tr>
                <tr><td><b>Mode:</b></td><td>Virtual/Physical (as per discussion)</td></tr>
            </table>

            <p>Please ensure you are available at the specified date and time. If you have any scheduling conflicts, kindly notify us at the earliest.</p>

            <p>Looking forward to your participation.</p>

            <p>Best regards,<br><b>HR Team</b></p>
        </body>
    </html>
    """

    # Create email message
    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = candidate_email
    msg["Cc"] = interviewer_email  # CC to interviewer
    msg["Subject"] = subject

    # Attach the HTML-formatted email
    msg.attach(MIMEText(body, "html"))

    try:
        # Connect to SMTP server and send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, [candidate_email, interviewer_email], msg.as_string())
        
        print(f"✅ Email successfully sent to {candidate_email} and {interviewer_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# # Example usage:
# send_interview_email("candidate@example.com", "interviewer@example.com", "April 15, 2025", "10:00 AM", "IST")