from pydantic import BaseModel, Field, validator
from typing import Optional, Type 
from datetime import datetime, date
import decimal

# --- Customers Table Model ---
class Customer(BaseModel):
    # Fields that are NOT nullable (must always have a value when creating or reading)
    full_name: str
    email: str
    phone: str
    date_of_birth: str  # Keep as string, will be converted later if needed
    gender: str
    marital_status: str
    occupation: str
    address: str
    city: str
    state: str
    pincode: str
    aadhaar_number: str
    pan_number: str
    kyc_status: str

    # Fields that ARE nullable (can be None)
    customer_id: Optional[int] = None
    alternate_phone: Optional[str] = None
    
    # Auto-conversion for datetime objects to strings
    @validator('date_of_birth', pre=True)
    def convert_date_to_string(cls, v):
        if isinstance(v, (datetime, date)):
            return v.isoformat()
        return v
    
    class Config:
        # This allows the model to accept extra fields and ignore them
        extra = "ignore"

# --- Nominees Table Model ---
class Nominee(BaseModel):
    # Non-nullable fields
    customer_id: int
    full_name: str
    date_of_birth: str  # Keep as string
    relationship: str
    contact_number: str
    address: str

    # Nullable fields
    nominee_id: Optional[int] = None
    
    @validator('date_of_birth', pre=True)
    def convert_date_to_string(cls, v):
        if isinstance(v, (datetime, date)):
            return v.isoformat()
        return v
    
    class Config:
        extra = "ignore"

# --- Policies Table Model ---
class Policy(BaseModel):
    # Non-nullable fields
    policy_id: str
    customer_id: int
    policy_type: str
    insurer_name: str
    start_date: str  # Keep as string
    end_date: str    # Keep as string
    sum_insured: float  # Use float for simplicity
    premium_amount: float  # Use float for simplicity

    # Nullable fields
    policy_status: Optional[str] = None
    
    @validator('start_date', 'end_date', pre=True)
    def convert_date_to_string(cls, v):
        if isinstance(v, (datetime, date)):
            return v.isoformat()
        return v
    
    # Auto-convert Decimal to float for database compatibility
    @validator('sum_insured', 'premium_amount', pre=True)
    def convert_decimal_to_float(cls, v):
        if isinstance(v, decimal.Decimal):
            return float(v)
        return v
    
    class Config:
        extra = "ignore"

# --- Endorsements Table Model ---
class Endorsement(BaseModel):
    # Required fields (non-nullable or with default)
    policy_id: str
    type: str
    request_date: Optional[str] = None  # Can be omitted to use DB default (now())
    status: Optional[str] = "pending"
    old_value: Optional[str] = None
    new_value: Optional[str] = None

    # Nullable fields
    endorsement_id: Optional[int] = None
    approved_date: Optional[str] = None
    remarks: Optional[str] = None

    @validator('request_date', 'approved_date', pre=True)
    def convert_date_to_string(cls, v):
        if v is None:
            return v
        if isinstance(v, (datetime, date)):
            return v.isoformat()
        return v

    class Config:
        extra = "ignore"

# --- Claims Table Model ---
class Claim(BaseModel):
    # Non-nullable fields
    policy_id: str
    customer_id: int
    claim_date: str  # Keep as string
    claim_type: str
    claim_amount_requested: float  # Use float for simplicity
    status: str
    reason: str

    # Nullable fields
    claim_id: Optional[int] = None
    claim_amount_approved: Optional[float] = None  # Use float for simplicity
    remarks: Optional[str] = None
    
    @validator('claim_date', pre=True)
    def convert_date_to_string(cls, v):
        if isinstance(v, (datetime, date)):
            return v.isoformat()
        return v
    
    @validator('claim_amount_requested', 'claim_amount_approved', pre=True)
    def convert_decimal_to_float(cls, v):
        if v is None:
            return v
        if isinstance(v, decimal.Decimal):
            return float(v)
        return v
    
    class Config:
        extra = "ignore"

# --- Conversation History Table Model ---
class ConversationHistory(BaseModel):
    # Non-nullable fields
    customer_email: str
    customer_message: str
    bot_response: str

    # Nullable fields (as per table's "Not Null" column)
    intent_captured: Optional[str] = None
    status: Optional[str] = None
    attachments_sent: Optional[str] = None
    response_time_ms: Optional[float] = None
    bot_version: Optional[str] = None
    
    class Config:
        extra = "ignore"

# --- Utility Functions ---

def get_model_field_names(model_class: Type[BaseModel]) -> list[str]:
    """
    Dynamically gets the field names from a Pydantic model.
    This respects the order of declaration if using Pydantic v1.
    For Pydantic v2, model_fields.keys() maintains insertion order.
    """
    return list(model_class.model_fields.keys()) # For Pydantic v2
    # If you are using Pydantic v1, use: return list(model_class.__fields__.keys())

def convert_db_row_to_model(row: tuple, model_class: Type[BaseModel]):
    """
    Convert a database row (tuple) to a Pydantic model instance,
    automatically determining column names from the model.
    """
    column_names = get_model_field_names(model_class)
    
    # Create a dictionary from the row and dynamically determined column names
    data_dict = dict(zip(column_names, row))
    return model_class(**data_dict)

