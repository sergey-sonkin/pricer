import hashlib
import os

import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

# Your verification token (32-80 chars, alphanumeric + underscore + hyphen only)
VERIFICATION_TOKEN = os.environ["EBAY_DELETION_SECRET"]
ENDPOINT_URL = "https://0b73772496fe.ngrok-free.app"


class MetaData(BaseModel):
    topic: str
    schemaVersion: str
    deprecated: bool


class NotificationData(BaseModel):
    username: str
    userId: str
    eiasToken: str


class NotificationPayload(BaseModel):
    notificationId: str
    eventDate: str
    publishDate: str
    publishAttemptCount: int
    data: NotificationData


class EBayNotification(BaseModel):
    metadata: MetaData
    notification: NotificationPayload


@app.get("/")
async def handle_challenge(challenge_code: str | None = None):
    """
    Handle eBay's challenge code validation
    eBay sends: GET https://your-url?challenge_code=123
    """
    if not challenge_code:
        return {
            "status": "Server is running",
            "message": "Waiting for eBay challenge or notifications",
        }

    print(f"Received challenge code: {challenge_code}")

    # Create the hash: challengeCode + verificationToken + endpoint
    hash_input = challenge_code + VERIFICATION_TOKEN + ENDPOINT_URL
    challenge_hash = hashlib.sha256(hash_input.encode()).hexdigest()

    print(f"Hash input: {hash_input}")
    print(f"Challenge response: {challenge_hash}")

    # Return the response eBay expects
    return {"challengeResponse": challenge_hash}


@app.post("/")
async def handle_account_deletion(request: Request):
    """
    Handle eBay account deletion notifications
    """
    try:
        payload = await request.json()
        notification = EBayNotification(**payload)

        print("=" * 50)
        print("ACCOUNT DELETION NOTIFICATION RECEIVED")
        print("=" * 50)
        print(f"Notification ID: {notification.notification.notificationId}")
        print(f"User to delete: {notification.notification.data.username}")
        print(f"User ID: {notification.notification.data.userId}")
        print(f"EIAS Token: {notification.notification.data.eiasToken}")
        print(f"Event Date: {notification.notification.eventDate}")
        print("=" * 50)

        # TODO: Add actual data deletion logic here once needed
        # Example: delete_user_data(notification.notification.data.userId)

        # eBay requires immediate acknowledgment with 200/201/202/204
        return {
            "status": "acknowledged",
            "notificationId": notification.notification.notificationId,
        }

    except Exception as e:
        print(f"Error processing notification: {e}")
        # Still return 200 to acknowledge receipt, but log the error
        return {"status": "error", "message": str(e)}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "eBay Account Deletion Handler"}


if __name__ == "__main__":
    print("Starting eBay Account Deletion Notification Server...")
    print(f"Verification Token: {VERIFICATION_TOKEN}")
    print(f"Endpoint URL: {ENDPOINT_URL}")
    print("Remember to:")
    print("1. Update VERIFICATION_TOKEN with your actual token")
    print("2. Update ENDPOINT_URL with your ngrok URL")
    print("3. Start ngrok: ngrok http 8000")
    print("4. Use the ngrok HTTPS URL in eBay developer portal")

    uvicorn.run(app, host="0.0.0.0", port=8000)
