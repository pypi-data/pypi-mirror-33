 

def send_email(subject, cuerpo, send_plt):
    
    #Functions for email
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
    #import config
    from ie_mbdbl2017_C_yahoo_ks_datareader.config import config
    
    try:
        fromaddr = config.EMAIL_ADDRESS
        toaddr = config.MAIL
         
        msg = MIMEMultipart()
         
        msg['From'] = fromaddr
        msg['To'] = ", ".join(toaddr)
        msg['Subject'] = subject
         
        body =  cuerpo
         
        msg.attach(MIMEText(body, 'plain'))
         
        filename = send_plt
        attachment = open(send_plt, "rb")
         
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
         
        msg.attach(part)
         
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(fromaddr, config.PASSWORD)
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
    except:
        print("Email failed to send")