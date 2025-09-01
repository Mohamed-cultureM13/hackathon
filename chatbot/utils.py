import random
import requests
# Import json just kujaribu kuzuia 500 errors with new send_whatsapp_message function
import json
from django.conf import settings
from .models import Question
import random



def send_whatsapp_message(phone_number, message_payload):
    url = f"https://graph.facebook.com/v23.0/{settings.META_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        **message_payload
        
    }
    
    response = requests.post(url, headers=headers, json=payload)
    # return response.status_code, response.text
    print("📤 WhatsApp API response:", response.status_code, response.text)

