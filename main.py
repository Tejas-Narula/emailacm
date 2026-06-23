from dotenv import load_dotenv
load_dotenv()

import os
import smtplib
import base64

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import List

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

app = FastAPI()

GMAIL = os.getenv("GMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
API_KEY = os.getenv("API_KEY")


class Sender(BaseModel):
    name: str
    email: str


class Recipient(BaseModel):
    email: str
    name: str


class Attachment(BaseModel):
    name: str
    content: str


class EmailRequest(BaseModel):
    sender: Sender
    to: List[Recipient]
    subject: str
    htmlContent: str
    attachment: List[Attachment] = []


@app.get("/")
def home():
    return {
        "status": "Email API Running"
    }

@app.get("/about")
def about():
    return {
        "Description" : "Email API For Get My Certificate developed by ACM"
    }


@app.post("/send-email")
def send_email(
    data: EmailRequest,
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    try:
        msg = MIMEMultipart()

        msg["Subject"] = data.subject
        msg["From"] = f"{data.sender.name} <{data.sender.email}>"

        recipients = [recipient.email for recipient in data.to]
        msg["To"] = ", ".join(recipients)

        msg.attach(
            MIMEText(
                data.htmlContent,
                "html"
            )
        )

        for attachment in data.attachment:

            file_data = base64.b64decode(
                attachment.content
            )

            part = MIMEBase(
                "application",
                "octet-stream"
            )

            part.set_payload(file_data)

            encoders.encode_base64(part)

            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{attachment.name}"'
            )

            msg.attach(part)

        with smtplib.SMTP(
            "smtp.gmail.com",
            587
        ) as server:

            server.starttls()

            server.login(
                GMAIL,
                APP_PASSWORD
            )

            server.send_message(msg)

        return {
            "success": True,
            "message": "Email sent successfully"
        }

    except Exception as e:
        print("ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )