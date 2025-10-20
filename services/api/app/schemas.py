from pydantic import BaseModel, EmailStr
from typing import List, Optional


class ProductItem(BaseModel):
name: str
quantity: float
unit: Optional[str] = None


class ExtractedEmail(BaseModel):
customer_name: Optional[str] = None
customer_email: Optional[EmailStr] = None
company: Optional[str] = None
products: List[ProductItem] = []
availability_needed: bool = True
pricing_needed: bool = False
raw_subject: Optional[str] = None
raw_id: Optional[str] = None