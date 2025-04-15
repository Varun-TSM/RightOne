import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

GMAIL_USER = "hr.demo.hiring@gmail.com"
GMAIL_PASSWORD = "jfvq qqkq gwrx ovlq"  # Not your real password!

def shortlisted_email(candidate_email, date, time, timezone, for_hr=False):
    subject = "Interview Slot Booking Invitation" if not for_hr else "Interview Confirmation"
    body = f"""
   
    Dear {candidate_email},

    Congratulations on successfully clearing the screening round! We are pleased to invite you to the next stage of our hiring process. 

    To proceed, kindly book an available interview slot at your earliest convenience using the link below:

    📅 <LINK TO BOOK SLOT>

    If you have any scheduling conflicts or require assistance, please reach out to our team. We look forward to meeting you and discussing your potential role with us.
    Looking forward to your response.
    
    
    Best regards,  
    HR Team
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
