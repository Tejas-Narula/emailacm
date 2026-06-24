import os
import smtplib
import base64
import modal

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from typing import List

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

app = modal.App("acm-email-api")

image = (
    modal.Image.debian_slim()
    .pip_install(
        "fastapi",
        "pydantic"
    )
)

web_app = FastAPI()


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
    attachment: List[Attachment] = Field(default_factory=list)


class BulkEmailItem(BaseModel):
    recipient: Recipient
    subject: str | None = None
    htmlContent: str | None = None
    attachment: List[Attachment] = Field(default_factory=list)


class BulkEmailRequest(BaseModel):
    sender: Sender
    subject: str
    htmlContent: str
    emails: List[BulkEmailItem]
    attachment: List[Attachment] = Field(default_factory=list)


@web_app.get("/")
def home():
    return {
        "status": "Email API Running"
    }


@web_app.get("/about")
def about():
    return {
        "Description": "Email API For Get My Certificate developed by ACM"
    }
@web_app.get("/about2")
def about():
    return {
        "hi": "Email API For Get My Certificate developed by ACM"
    }


def build_message(
    sender: Sender,
    subject: str,
    html_content: str,
    recipients: List[Recipient],
    attachments: List[Attachment],
):
    msg = MIMEMultipart()

    msg["Subject"] = subject
    msg["From"] = f"{sender.name} <{sender.email}>"
    msg["To"] = ", ".join(
        recipient.email for recipient in recipients
    )

    msg.attach(
        MIMEText(
            html_content,
            "html"
        )
    )

    for attachment in attachments:
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

    return msg


def open_smtp_connection(gmail: str, app_password: str):
    server = smtplib.SMTP(
        "smtp.gmail.com",
        587
    )

    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(
        gmail,
        app_password
    )

    return server

@web_app.post("/send-email")
def send_email(
    data: EmailRequest,
    x_api_key: str = Header(None)
):
    GMAIL = os.environ["GMAIL"]
    APP_PASSWORD = os.environ["APP_PASSWORD"]
    API_KEY = os.environ["API_KEY"]

    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    try:
        msg = build_message(
            sender=data.sender,
            subject=data.subject,
            html_content=data.htmlContent,
            recipients=data.to,
            attachments=data.attachment,
        )

        with open_smtp_connection(
            GMAIL,
            APP_PASSWORD
        ) as server:
            server.send_message(msg)

        return {
            "success": True,
            "message": "Email sent successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@web_app.post("/send-bulk-email")
def send_bulk_email(
    data: BulkEmailRequest,
    x_api_key: str = Header(None)
):
    GMAIL = os.environ["GMAIL"]
    APP_PASSWORD = os.environ["APP_PASSWORD"]
    API_KEY = os.environ["API_KEY"]

    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    if len(data.emails) > 100:
        raise HTTPException(
            status_code=400,
            detail="Maximum 100 emails per request"
        )

    sent_count = 0
    failed = []

    try:
        server = open_smtp_connection(
            GMAIL,
            APP_PASSWORD
        )

        for email_item in data.emails:
            try:
                subject = (
                    email_item.subject
                    or data.subject
                )

                html_content = (
                    email_item.htmlContent
                    or data.htmlContent
                )

                attachments = (
                    data.attachment
                    + email_item.attachment
                )

                msg = build_message(
                    sender=Sender(
                        name=data.sender.name,
                        email=GMAIL
                    ),
                    subject=subject,
                    html_content=html_content,
                    recipients=[
                        email_item.recipient
                    ],
                    attachments=attachments,
                )

                server.send_message(
                    msg,
                    from_addr=GMAIL,
                    to_addrs=[
                        email_item.recipient.email
                    ]
                )

                sent_count += 1

            except Exception as e:
                failed.append({
                    "email": email_item.recipient.email,
                    "error": str(e)
                })

        server.quit()

        return {
            "success": len(failed) == 0,
            "sentCount": sent_count,
            "failedCount": len(failed),
            "failed": failed
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("acm-email-secrets")
    ]
)
@modal.asgi_app()
def fastapi_app():
    return web_app
