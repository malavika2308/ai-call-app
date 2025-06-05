from flask import Flask, request, Response
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Say, Record
import os

app = Flask(__name__)

# Twilio credentials (store securely in env vars in production)
account_sid = os.environ.get("account_sid ")
auth_token = os.environ.get("auth_token ")
twilio_number =os.environ.get("twilio_number")
client = Client(account_sid, auth_token)

# Route to make the call
@app.route('/make_call', methods=['GET'])
def make_call():
    call = client.calls.create(
        to='+916304102437',  # Replace with the recipient's number
        from_=twilio_number,
        url='https://ai-call-app.com/voice'  # This URL must be publicly accessible
    )
    return f"Call initiated. SID: {call.sid}"

# What Twilio does when the call connects
@app.route('/voice', methods=['POST'])
def voice():
    response = VoiceResponse()
    response.say("Hello! This is your AI assistant. Please tell me what's on your mind after the beep.", voice='Polly.Joanna')
    response.record(max_length=15, action='/process_recording', transcribe=True, transcribe_callback='/transcription')
    return Response(str(response), mimetype='application/xml')

# Handle transcription
@app.route('/transcription', methods=['POST'])
def transcription():
    transcript = request.form.get('TranscriptionText')
    print("User said:", transcript)  # You can return this or log it
    return '', 204

# After recording finishes
@app.route('/process_recording', methods=['POST'])
def process_recording():
    response = VoiceResponse()
    response.say("Thanks! Your response has been recorded. Goodbye.")
    response.hangup()
    return Response(str(response), mimetype='application/xml')

if __name__ == '__main__':
    app.run()
