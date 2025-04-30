import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

GMAIL_USER = "hr.demo.hiring@gmail.com"
GMAIL_PASSWORD = "jfvq qqkq gwrx ovlq"  # Consider moving this to an environment variable

def send_availability_email(interviewer_email):
    subject = (
        "Request for Interview Availability"
    )
    
    body = f"""
Dear Interviewer,

I hope this message finds you well.

We are currently organizing interviews for prospective candidates and would greatly appreciate it if you could share your availability for the upcoming days. Kindly provide your availability for at least three suitable dates to help us schedule efficiently.

You can conveniently share your preferred time slots by visiting the following link:

[Click here to provide your availability](https://your-calendar-link.com)  

Your prompt response would be highly appreciated.

Thank you for your support and cooperation.

Warm regards,  
HR Team (TSM)
hr.demo.hiring@gmail.com
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
        print(f"✅ Email successfully sent to {interviewer_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
