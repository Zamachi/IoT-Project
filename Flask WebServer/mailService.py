import smtplib, time
from thnigspeak import receiveData

def sendEmail():
    while True:
        time.sleep(120)
        podaci_sa_thing_speak = receiveData()
        broj_zapisa = len(podaci_sa_thing_speak)

        avgTemp = 0
        avgLight = 0
        sumDoor = 0
        sumRelay = 0

        for ocitavanje in podaci_sa_thing_speak:
            avgTemp = avgTemp + float(ocitavanje['field1'])
            avgLight = avgLight + float(ocitavanje['field2'])
            sumDoor= sumDoor + int(ocitavanje['field3'])
            sumRelay= sumRelay + int(ocitavanje['field4'])

        avgTemp = avgTemp/broj_zapisa
        avgLight = avgLight/broj_zapisa

        #WARNING Prvo pitaj za pristupne parametre, pa tek onda startuj server, u suprotnom se dobija timeout!
        EMAIL_ADDRESS = input("Unesite vas E-mail: ")#NOTE: Staviti staticku vrednost 
        PASSWORD = input("Unesite Vas password: ")#NOTE: Staviti staticku vrednost

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
    
    
        DESTINATION_EMAIL_ADDRESS = EMAIL_ADDRESS
    
        resCode = server.login(EMAIL_ADDRESS, PASSWORD)
    
        subject = "Dnevni izvestaj"
        body = "Prosecna temperatura iznosila je {} C\nProsecno osvetljenje iznosilo je {} lux\nVrata su otvorena sveukupno {} puta\nRelej je otvoren sveukupno {} puta".format(avgTemp,avgLight,sumDoor,sumRelay)
        fullEmail = "Subject: {}\n\n{}".format(subject, body)
    
        resCode = server.sendmail(from_addr=EMAIL_ADDRESS, to_addrs=DESTINATION_EMAIL_ADDRESS, msg=fullEmail)
    
        server.quit()
