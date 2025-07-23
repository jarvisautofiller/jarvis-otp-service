import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_initiate_call_invalid_number():
    response = client.post("/verifyService/initiate-call", json={"mobile": "12345"})
    assert response.status_code == 400

def test_call_response_dtmf_success():
    response = client.post("/verifyService/call-response", data={
        "Digits": "1",
        "CallSid": "test-sid",
        "From": "+911234567890"
    })
    assert "<Say>You pressed 1. Your response is recorded as validated." in response.text
def test_call_response_dtmf_failed():
    response = client.post("/verifyService/call-response", data={
        "Digits": "5",
        "CallSid": "test-sid",
        "From": "+911234567890"
    })
    assert "<Say>You pressed 5. Your response is recorded as failed." in response.text
def test_call_response_dtmf_no_input():
    response = client.post("/verifyService/call-response", data={
        "CallSid": "test-sid",
        "From": "+911234567890"
    })
    assert "<Say>No input received. Please try again later." in response.text

def test_call_response_speech_yes():
    response = client.post("/verifyService/call-response", data={
        "SpeechResult": "yes",
        "CallSid": "test-sid",
        "From": "+911234567890"
    })
    assert "<Say>You said 'yes'. Your response is recorded as validated." in response.text
