import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database import db, create_document, get_documents
from schemas import Booking

app = FastAPI(title="CampusClean Tech API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "CampusClean Tech API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set"
            response["database_name"] = getattr(db, 'name', '✅ Connected')
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# -------- Booking Endpoints --------

class BookingCreate(BaseModel):
    full_name: str
    whatsapp_number: str
    student_id: Optional[str] = None
    device_type: str
    brand_model: Optional[str] = None
    service_requested: str
    pickup_or_dropoff: str
    preferred_time: Optional[datetime] = None
    notes: Optional[str] = None
    consent_photos_and_terms: bool = False


def classify(service_requested: str, device_type: str, pickup_or_dropoff: str) -> (str, bool):
    # Normalize
    s = service_requested.lower()
    d = device_type.lower()
    tag = None
    if "laptop" in d:
        tag = "Laptop-Deep" if "deep" in s else "Laptop-Basic"
    else:
        tag = "Phone-Deep" if "deep" in s else "Phone-Basic"
    priority = (tag == "Laptop-Deep") or (pickup_or_dropoff.lower() == "pickup")
    return tag, priority


@app.post("/api/bookings")
def create_booking(payload: BookingCreate):
    tag, priority = classify(payload.service_requested, payload.device_type, payload.pickup_or_dropoff)
    booking = Booking(
        **payload.model_dump(),
        classification=tag,
        priority=priority,
    )
    try:
        booking_id = create_document("booking", booking)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Auto-reply message
    number = os.getenv("BUSINESS_WHATSAPP_NUMBER", "<your-number>")
    base = f"https://wa.me/{number}?text="
    text = (
        f"Hi CampusClean — Confirm Booking for {booking.device_type} {booking.brand_model or ''}. "
        f"Service: {booking.service_requested}. Name: {booking.full_name}."
    )
    import urllib.parse
    wa_link = base + urllib.parse.quote(text)

    auto_reply = (
        f"Thanks {booking.full_name}! We received your request for a {booking.service_requested} "
        f"on your {booking.device_type}. Please confirm & pay via WhatsApp: {wa_link} "
        f"Payment via mobile money on pickup. We will reply with pickup slots shortly."
    )

    return {"id": booking_id, "ok": True, "auto_reply": auto_reply, "whatsapp_link": wa_link, "classification": tag, "priority": priority}


@app.get("/api/bookings")
def list_bookings(
    device_type: Optional[str] = Query(None),
    service_requested: Optional[str] = Query(None),
    priority: Optional[bool] = Query(None),
    limit: int = Query(100, ge=1, le=500)
):
    filt = {}
    if device_type:
        filt["device_type"] = device_type
    if service_requested:
        filt["service_requested"] = service_requested
    if priority is not None:
        filt["priority"] = priority
    try:
        docs = get_documents("booking", filt if filt else None, limit=limit)
        # Convert ObjectId
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
