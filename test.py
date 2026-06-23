import smtplib

server = smtplib.SMTP("smtp.gmail.com", 587)
print("Connected")
server.quit()