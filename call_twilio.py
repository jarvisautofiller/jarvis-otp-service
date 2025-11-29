from twilio.rest import Client
import os


TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_PHONE_NUMBER")
GATHER_URL = os.getenv("TWILIO_TWIML_URL")

client = Client(TWILIO_SID, TWILIO_AUTH)

def initiate_voice_call(to_number: str) -> str:
    call = client.calls.create(
        to=to_number,
        from_=TWILIO_FROM,
        url=GATHER_URL,
    )
    return call.sid
