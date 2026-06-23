from dotenv import load_dotenv
load_dotenv()
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText

app = FastAPI()

GMAIL = os.getenv("GMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

class EmailRequest(BaseModel):
    to: str
    subject: str
    message: str

print("GMAIL:", GMAIL)
print("APP_PASSWORD:", APP_PASSWORD)


@app.post("/send-email")
def send_email(data: EmailRequest):
    try:
        msg = MIMEText(data.message)
        msg["Subject"] = data.subject
        msg["From"] = GMAIL
        msg["To"] = data.to

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL, APP_PASSWORD)
            server.send_message(msg)

        return {"success": True}

    except Exception as e:
        print("ERROR:", repr(e))
        raise HTTPException(status_code=500, detail=str(e)) 