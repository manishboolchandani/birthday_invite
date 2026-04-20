import csv
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="static")

CSV_FILE = "rsvps.csv"

# ── Email config (set these environment variables) ──
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")        # e.g. yourname@gmail.com
SMTP_PASS = os.getenv("SMTP_PASS", "")        # app-password
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", "")   # host's email to receive RSVPs


def _init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            csv.writer(f).writerow(
                ["timestamp", "guest_name", "email", "num_guests", "attending", "message"]
            )


def _send_email(data: dict):
    if not (SMTP_USER and SMTP_PASS and NOTIFY_EMAIL):
        print("⚠️  Email not configured – skipping notification.")
        return
    body = (
        f"New RSVP!\n\n"
        f"Name: {data['guest_name']}\n"
        f"Email: {data['email']}\n"
        f"Attending: {data['attending']}\n"
        f"Number of guests: {data['num_guests']}\n"
        f"Message: {data['message']}\n"
        f"Time: {data['timestamp']}"
    )
    msg = MIMEText(body)
    msg["Subject"] = f"🎂 Birthday RSVP from {data['guest_name']}"
    msg["From"] = SMTP_USER
    msg["To"] = NOTIFY_EMAIL
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        print("✅ Email sent.")
    except Exception as e:
        print(f"❌ Email failed: {e}")


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/rsvp", methods=["POST"])
def rsvp():
    data = request.json
    row = {
        "timestamp": datetime.now().isoformat(),
        "guest_name": data.get("guest_name", ""),
        "email": data.get("email", ""),
        "num_guests": data.get("num_guests", 1),
        "attending": data.get("attending", "yes"),
        "message": data.get("message", ""),
    }
    _init_csv()
    print("Row initialized.")
    _send_email(row)
    return jsonify({"status": "ok", "message": "RSVP received! 🎉"})


if __name__ == "__main__":
    _init_csv()
    port = int(os.getenv("PORT", "8080"))
    app.run(debug=True, host="0.0.0.0", port=port)
