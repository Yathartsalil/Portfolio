from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RegisterRequest(BaseModel):
    email: str

# CHANGE THIS
SENDER_EMAIL = "kelkaryatharth1@gmail.com"
APP_PASSWORD = "lyqa rtbq lxtr kudn"  # replace with your real app password

@app.get("/")
def home():
    return {"message": "Email server running!"}

@app.post("/send-welcome")
def send_welcome(data: RegisterRequest):
    receiver_email = data.email

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Welcome to Our Website!"
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email

    html_content = f"""
    <html>
        <body>
            <h2>Welcome, {receiver_email} 🎉</h2>
            <p>Your account has been created successfully.</p>
            <p>We are excited to have you with us!</p>
            <br>
            <p>— Team</p>
        </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return {"status": "success", "message": "Email sent!"}

    except Exception as e:
        print("SMTP ERROR:", e)  # <-- This will show the exact Gmail error
        raise HTTPException(status_code=500, detail=str(e))
