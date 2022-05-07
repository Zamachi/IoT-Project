import smtplib, time

def sendEmail():
    while True:
        time.sleep(60)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
    
        EMAIL_ADDRESS = input("Unesite vas E-mail: ")#NOTE: Staviti staticku vrednost 
        PASSWORD = input("Unesite Vas password: ")#NOTE: Staviti staticku vrednost
    
        DESTINATION_EMAIL_ADDRESS = EMAIL_ADDRESS
    
        resCode = server.login(EMAIL_ADDRESS, PASSWORD)
    
        subject = "Dnevni izvestaj"
        body = "Neki tekst u telu email"
        fullEmail = "Subject: {}\n\n{}".format(subject, body)
    
        resCode = server.sendmail(from_addr=EMAIL_ADDRESS, to_addrs=DESTINATION_EMAIL_ADDRESS, msg=fullEmail)
    
        server.quit()
