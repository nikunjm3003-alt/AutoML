import smtplib
import streamlit as st
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_verification_email(to_email, username, token):
    sender = st.secrets['gmail']['sender']
    app_password = st.secrets['gmail']['app_password']
    verify_link = f"https://automl-woqfu2uxfrmluak9ywhpdi.streamlit.app/?token={token}"

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Verify your AutoML Studio account"
    msg['From'] = sender
    msg['To'] = to_email

    html = f"""
    <html>
    <body style="font-family:Arial,sans-serif; background:#0f0f1a; color:#e0e0ff; padding:40px;">
        <div style="max-width:480px; margin:auto; background:#1a1a2e; border-radius:12px; padding:32px;">
            <h2 style="color:#a78bfa;">AutoML Studio</h2>
            <p>Hey <b>{username}</b>,</p>
            <p>Thanks for registering. Click the button below to verify your email address.</p>
            <a href="{verify_link}" style="display:inline-block; margin:20px 0; padding:12px 28px;
               background:linear-gradient(90deg,#a78bfa,#60a5fa); color:#fff;
               border-radius:8px; text-decoration:none; font-weight:bold;">
               Verify Email
            </a>
            <p style="color:rgba(200,200,255,0.5); font-size:0.85rem;">
                This link expires in 24 hours. If you didn't register, ignore this email.
            </p>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html, 'html'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, app_password)
        smtp.send_message(msg)