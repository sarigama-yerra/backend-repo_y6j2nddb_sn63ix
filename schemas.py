"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

# Example schemas (keep for reference)
class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# CampusClean Tech Booking schema
class Booking(BaseModel):
    """
    Booking leads submitted from the website
    Collection name: "booking"
    """
    full_name: str = Field(..., description="Customer full name")
    whatsapp_number: str = Field(..., description="WhatsApp number with country code")
    student_id: Optional[str] = Field(None, description="Student ID (optional)")
    device_type: Literal["Laptop", "Phone"] = Field(..., description="Type of device")
    brand_model: Optional[str] = Field(None, description="Brand and model of the device")
    service_requested: Literal[
        "Laptop Basic",
        "Laptop Deep",
        "Phone Basic",
        "Phone Deep"
    ] = Field(..., description="Requested service")
    pickup_or_dropoff: Literal["Drop-off", "Pickup"] = Field(..., description="Logistics preference")
    preferred_time: Optional[datetime] = Field(None, description="Preferred date & time")
    notes: Optional[str] = Field(None, description="Additional notes")
    consent_photos_and_terms: bool = Field(False, description="Consent to intake photos and terms")

    # Server-side enrichments
    classification: Optional[Literal["Laptop-Deep", "Laptop-Basic", "Phone-Deep", "Phone-Basic"]] = Field(
        None, description="AI lightweight classification tag"
    )
    priority: Optional[bool] = Field(False, description="True if priority lead")
