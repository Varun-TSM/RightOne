import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

GMAIL_USER = "hr.demo.hiring@gmail.com"
GMAIL_PASSWORD = "jfvq qqkq gwrx ovlq"  # Not your real password!

def send_invite_email(candidate_email, interviewer_email, date, time, timezone, for_hr=False):
    subject = "Interview Invitation" if not for_hr else "Interview Confirmation"
    body = f"""
    Hello {candidate_email},

    This is to confirm your interview scheduled with {interviewer_email or 'our HR Team'}.

    Date: {date}
    Time: {time} ({timezone})
    
    Best,
    Interview Scheduler
    """

    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = candidate_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)
        print(f"Email sent to {candidate_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
