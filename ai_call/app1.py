import os
from flask import Flask, request, render_template, jsonify
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Load environment variables
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_NUMBER")
target_number = os.getenv("TARGET_PHONE_NUMBER")
base_url = os.getenv("BASE_URL")

client = Client(account_sid, auth_token)

# Simple storage for transcript
TRANSCRIPT_FILE = "last_transcript.txt"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/make_call", methods=["POST"])
def make_call():
    # Initiates a call from Twilio
    call = client.calls.create(
        to=target_number,
        from_=twilio_number,
        url=f"{base_url}/voice"  # This is what Twilio calls to start
    )
    return jsonify({"status": "calling", "sid": call.sid})

@app.route("/voice", methods=["POST"])
def voice():
    # Twilio hits this when the call connects
    response = VoiceResponse()
    response.say("Hi, this is your AI assistant. Please speak after the beep.", voice='alice')
    response.record(
        action="/process_recording",  # Twilio will POST here after recording
        transcribe=True,
        transcribe_callback="/transcription",
        max_length=10
    )
    return str(response)

@app.route("/process_recording", methods=["POST"])
def process_recording():
    # This was missing before! Twilio expects this.
    print("✅ Received recording data")
    return "", 204

@app.route("/transcription", methods=["POST"])
def transcription():
    # Twilio sends transcription text here
    transcript = request.form.get("TranscriptionText", "")
    print("📝 Transcription received:", transcript)
    with open(TRANSCRIPT_FILE, "w") as f:
        f.write(transcript)
    return "", 204

@app.route("/get_transcript", methods=["GET"])
def get_transcript():
    try:
        with open(TRANSCRIPT_FILE, "r") as f:
            text = f.read()
    except FileNotFoundError:
        text = "No transcript available yet."
    return jsonify({"transcript": text})

# Health check route to test app is running
@app.route("/health")
def health():
    return "OK", 200

# Entry point when running locally
if __name__ == "__main__":
    app.run(debug=True)
