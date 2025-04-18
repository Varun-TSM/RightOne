import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import textwrap

GMAIL_USER = "hr.demo.hiring@gmail.com"
GMAIL_PASSWORD = "jfvq qqkq gwrx ovlq"  # Not your real password!

def shortlisted_email(candidate_email, candidate_name):
    html = textwrap.dedent(f"""\
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; line-height:1.5;">
        <p>Dear {candidate_name},</p>
        
          Congratulations on successfully clearing the screening round!<br>
          We are pleased to invite you to the next stage of our hiring process.

        <p>To proceed, kindly book an available interview slot at your earliest convenience:</p>
        <p>
          👉 <a href="https://example.com/schedule" style="color:#1a73e8; text-decoration:none;">
          Click here to book your slot</a>
        </p>

        <p>If you have any scheduling conflicts or require assistance, feel free to reach out to our team.</p>
        <p>We look forward to meeting you and discussing your potential role with us.</p>

        <p>Best regards,<br><strong>HR Team (TSM)</strong></p>
      </body>
    </html>
    """)

    # Create the email container
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Update on Your Application: Schedule Your Interview"
    msg["From"] = GMAIL_USER
    msg["To"] = candidate_email

    # Attach only the HTML version
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)
        print(f"Email sent to {candidate_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")