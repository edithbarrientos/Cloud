from pydantic import BaseModel

class DeviceMetadata(BaseModel):
    operatingSystem: str
    browserName: str
    ipAddress: str

class MessagePayload(BaseModel):
    timestamp: str
    inputType: str
    text: str

class WebchatMessageSchema(BaseModel):
    clientId: str
    anonymousSessionToken: str
    deviceMetadata: DeviceMetadata
    messagePayload: MessagePayload
