# ACM Email API

A lightweight FastAPI-based email service for ACM projects. The API accepts Brevo-compatible JSON payloads and sends emails through SMTP, making it easy to replace third-party email providers without changing existing application logic.

---

## Features

- HTML email support
- Multiple recipients
- Base64 file attachments
- Brevo-compatible request format
- FastAPI-powered REST API
- Easy deployment on cPanel, VPS, or cloud platforms

---

## Prerequisites

- Python 3.10+
- SMTP-enabled email account
- Gmail App Password (if using Gmail SMTP)

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Create a Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create a `.env` file in the project root:

```env
GMAIL=your-email@gmail.com
APP_PASSWORD=your-google-app-password
```

> If using Gmail, generate an App Password from your Google Account security settings. Your normal Gmail password will not work.

---

## Running the API

Start the development server:

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## API Usage

### Endpoint

```http
POST /send-email
```

### Request Body

```json
{
  "sender": {
    "name": "ACM Student Chapter, MUJ",
    "email": "sender@example.com"
  },
  "to": [
    {
      "email": "recipient@example.com",
      "name": "Recipient Name"
    }
  ],
  "subject": "Your ACM Certificate - Workshop Name",
  "htmlContent": "<p>Hi Recipient Name,</p><p>Your certificate is attached.</p>",
  "attachment": [
    {
      "name": "certificate.png",
      "content": "BASE64_ENCODED_FILE"
    }
  ]
}
```

### Success Response

```json
{
  "success": true,
  "message": "Email sent successfully"
}
```

---

## Project Structure

```text
.
├── main.py
├── requirements.txt
├── .env
└── README.md
```

---

## Deployment

This application can be deployed using:

- cPanel Python Applications
- VPS with Uvicorn
- Docker
- Cloud platforms supporting FastAPI

---

## Tech Stack

- FastAPI
- Python
- SMTP
- Pydantic
- Python Dotenv

---

## License

Developed for Tejas me :) 
