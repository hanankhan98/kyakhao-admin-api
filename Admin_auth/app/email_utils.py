import smtplib
from email.mime.text import MIMEText

EMAIL = "lalainfatima523@gmail.com"
PASSWORD = "ctof qgac kgpp pxgr"

def send_otp(email, otp):
    try:
        msg = MIMEText(f"Your OTP is {otp}")
        msg["Subject"] = "Verify your account"
        msg["From"] = EMAIL
        msg["To"] = email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, email, msg.as_string())
        server.quit()

        print("Email sent successfully")

    except Exception as e:
        print(" Email error:", e)