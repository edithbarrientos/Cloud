from pydantic import BaseModel, Field
from typing import List

class TextBody(BaseModel):
    body: str

class MessageItem(BaseModel):
    from_field: str = Field(..., alias="from")
    id: str
    timestamp: str
    text: TextBody
    type: str

class MetadataItem(BaseModel):
    display_phone_number: str
    phone_number_id: str

class ProfileItem(BaseModel):
    name: str

class ContactItem(BaseModel):
    profile: ProfileItem
    wa_id: str

class ValueItem(BaseModel):
    messaging_product: str
    metadata: MetadataItem
    contacts: List[ContactItem]
    messages: List[MessageItem]

class ChangeItem(BaseModel):
    value: ValueItem
    field: str

class EntryItem(BaseModel):
    id: str
    changes: List[ChangeItem]

class WhatsAppWebhookSchema(BaseModel):
    object: str
    entry: List[EntryItem]
