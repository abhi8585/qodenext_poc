import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_mail(sender_email, sender_password, recipient_email, subject, message):
    # SMTP server configuration
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # Create a MIME message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Add the message body
    body = MIMEText(message, 'plain')
    msg.attach(body)

    try:
        # Create a secure connection with the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, recipient_email, msg.as_string())
        print('Email sent successfully!')
    except Exception as e:
        print('An error occurred while sending the email:', str(e))
    finally:
        # Close the SMTP server connection
        server.quit()

# Example usage
sender_email = 'abhi.sharma1114@gmail.com'
sender_password = 'ZXC961^$#vbn'
recipient_email = 'yogit.singh8585@gmail.com'
subject = 'Test Email'
message = 'This is a test email sent from Python.'

send_mail(sender_email, sender_password, recipient_email, subject, message)
