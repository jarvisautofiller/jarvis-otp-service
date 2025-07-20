from fastapi import APIRouter, FastAPI, Request, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import datetime, time, phonenumbers
from call_twilio import initiate_voice_call
from threading import Lock

app = FastAPI()
router = APIRouter(prefix="/verifyService")

# In-memory store for call status
call_status_store = {}
store_lock = Lock()

class CallRequest(BaseModel):
    mobile: str

@router.post("/initiate-call")
def call_user(req: CallRequest):
    try:
        num = phonenumbers.parse(req.mobile)
        if not phonenumbers.is_valid_number(num):
            raise HTTPException(status_code=404, detail="Bad request")
    except Exception:
        raise HTTPException(status_code=404, detail="Bad request")

    sid = initiate_voice_call(req.mobile)

    # Store initial status
    with store_lock:
        call_status_store[sid] = "pending"

    # Wait up to 30 seconds for result
    timeout = 30
    interval = 2
    waited = 0

    while waited < timeout:
        with store_lock:
            status = call_status_store.get(sid)
            if status and status != "pending":
                return {"call_sid": sid, "status": status}

        time.sleep(interval)
        waited += interval

    return {"call_sid": sid, "status": "timeout"}

@router.post("/call-response")
async def call_response(request: Request):
    try:
        form = await request.form()
        digits = form.get("Digits")
        call_sid = form.get("CallSid")
        caller = form.get("From")

        if digits is None:
            result = "no-input"
        elif digits == "1":
            result = "validated"
        else:
            result = "failed"

        # Update call status
        with store_lock:
            call_status_store[call_sid] = result

        print(f"[{datetime.datetime.now()}] CallSid={call_sid} From={caller} Result={result}")

        response_twiml = f"""
        <Response>
            <Say>Thank you. Your input has been recorded as {digits}.</Say>
            <Hangup/>
        </Response>
        """
        return Response(content=response_twiml, media_type="application/xml")

    except Exception as e:
        print("Error in /call-response:", e)
        return Response(
            content="<Response><Say>Error occurred.</Say></Response>",
            media_type="application/xml"
        )
 
app.include_router(router)


# @app.post("/call-status")
# async def call_status(request: Request):
#     form = await request.form()
#     call_sid = form.get("CallSid")
#     call_status = form.get("CallStatus")
#     to_number = form.get("To")

#     print(f"📞 Call Status: {call_sid} → {to_number} → Status: {call_status}")

#     # Example logic
#     if call_status == "no-answer":
#         print("❌ User did not pick up.")
#     elif call_status == "completed":
#         print("✅ Call was answered and completed.")
#     elif call_status == "failed":
#         print("⚠️ Failed to connect. Possibly invalid number.")
#     # etc...

#     return {"ok": True}



# Uncomment this section if you want to serve TwiML directly
# @app.get("/voice.xml")
# def serve_twiml():
#     xml = """
#     <Response>
#       <Say>Press 1 to confirm your action.</Say>
#       <Gather action="/call-response" method="POST" numDigits="1" timeout="10"/>
#     </Response>
#     """
#     return Response(content=xml, media_type="application/xml")

