import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

GMAIL_USER = "hr.demo.hiring@gmail.com"
GMAIL_PASSWORD = "jfvq qqkq gwrx ovlq"  # Not your real password!

def send_availability_email(interviewer_email, date, time, timezone, for_hr=False):
    subject = "Interview Invitation" if not for_hr else "Interview Confirmation"
    body = f"""
    
    Dear {interviewer_email},
    
    I hope you're doing well. 
    We are in the process of scheduling interviews and would appreciate it if you could share your availability for at least three upcoming days. This will help us coordinate efficiently and move forward with the hiring process.

    Please provide your available time slots at your earliest convenience via following link.
    
    <LINK TO CALENDAR>
    

    Looking forward to your response.

    
    Regards,
    HR Team
    """

    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = interviewer_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)
        print(f"Email sent to {interviewer_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
