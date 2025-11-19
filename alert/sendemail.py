import smtplib
from email.mime.text import MIMEText

def sendemail(subject, text, type='plain'):
    msg = """\
From: celaenomail@gmail.com
To: celaenomail@gmail.com
Subject: %s
""" % subject

    if type == 'html':
        msg += 'MIME-Version: 1.0\nContent-type: text/html\n\n'
    else:
        msg += '\n'
    msg += text

    try:
        # Replace the non-ASCII characters with a space
        msg = msg.encode('ascii', 'ignore').decode('ascii')

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login('celaenomail@gmail.com', 'uvervyhorkjwkbpa')
        server.sendmail('celaenomail@gmail.com', 'celaenomail@gmail.com', msg)
        server.close()
        return True
    except Exception as e:
        print('Failed to send email:', e)
        return False
