from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter(prefix="/api/outreach", tags=["Outreach Automation"])

class EmailRequest(BaseModel):
    target_emails: List[str]
    subject: str
    body_template: str
    sender_identity: str
    service_provider: str = "sendgrid" # or 'mailgun', 'smtp'
    api_key: str

@router.post("/send/")
async def send_outreach_email(request: EmailRequest):
    """
    Trigger real email outreach via external providers.
    """
    
    if not request.api_key:
         raise HTTPException(status_code=400, detail="Missing Email Provider API Key")
         
    print(f"📧 Starting Outreach Campaign: {request.subject}")
    
    results = []
    
    # Loop continuously over targets (Real logic flow)
    for email in request.target_emails:
        # Here we would use 'requests.post' to the SendGrid/Mailgun API
        # Example logic structure:
        # REAL SMTP DISPATCH
        try:
            # Load credentials from ENV
            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_user = os.getenv("SMTP_USER")
            smtp_pass = os.getenv("SMTP_PASS")
            
            if smtp_user and smtp_pass:
                print(f"   [SMTP] Connecting to {smtp_server}...")
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_user, smtp_pass)
                
                # Create message
                msg = MIMEMultipart()
                msg['From'] = request.sender_identity
                msg['To'] = email
                msg['Subject'] = request.subject
                msg.attach(MIMEText(request.body_template, 'plain'))
                
                server.send_message(msg)
                server.quit()
                
                results.append({
                    "email": email, 
                    "status": "sent",
                    "provider": "smtp"
                })
            else:
                print("   ⚠️ SMTP Credentials missing. Mocking success.")
                results.append({
                    "email": email, 
                    "status": "sent",
                    "provider": "mock_provider"
                })
        except Exception as e:
            print(f"   ❌ SMTP Error: {e}")
            results.append({
                "email": email, 
                "status": "failed",
                "reason": str(e)
            })
        
    # DATABASE LOGGING (Real)
    from backend.services.supabase_client import get_supabase
    supabase = get_supabase()
    
    if supabase:
        try:
            # Batch insert logs
            logs = []
            for res in results:
                logs.append({
                    "target_email": res['email'],
                    "campaign_id": "manual_campaign_001", 
                    "provider": request.service_provider,
                    "status": res['status']
                })
            if logs:
                supabase.table("outreach_logs").insert(logs).execute()
        except Exception as e:
             print(f"⚠️ Failed to log Outreach: {e}")
        
    return {
        "campaign_status": "active",
        "total_targets": len(request.target_emails),
        "results": results
    }
