from sqlmodel import Column, SQLModel, Field, create_engine, Session, select
from typing import Optional
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
import requests
import time

import requests
import itertools

PROXY_URLS = [
    "https://test1.loca.lt/validate-email",
    "https://test2.loca.lt/validate-email",
    "https://test3.loca.lt/validate-email",
    "https://test4.loca.lt/validate-email",
    "https://test5.loca.lt/validate-email",
    "https://test6.loca.lt/validate-email",
    "https://test7.loca.lt/validate-email",
    "https://test8.loca.lt/validate-email",
    "https://test9.loca.lt/validate-email",
    "https://test10.loca.lt/validate-email",
]

proxy_cycle = itertools.cycle(PROXY_URLS)  # Round-robin iterator

# Database configuration
DB_NAME = "job_application"
DB_USER = "postgres"
DB_PASSWORD = "root"
DB_HOST = "localhost"
DB_PORT = "5432"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

class ApolloContact(SQLModel, table=True):
    __tablename__ = "apollo_contact"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: Optional[str] = Field(default=None, unique=True, index=True)
    name: Optional[str] = None
    title: Optional[str] = None
    organization_name: Optional[str] = None
    linkedin_url: Optional[str] = None
    company_linkedin_url: Optional[str] = None
    created_at: Optional[datetime] = None
    json_data: Optional[dict] = Field(sa_column=Column(JSONB))
    first_name: Optional[str] = None
    is_valid: Optional[bool] = None
    email_validity_response: Optional[dict] = Field(sa_column=Column(JSONB))

API_URL = "https://www.site24x7.com/tools/email-validator"
HEADERS = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://www.site24x7.com',
    'Pragma': 'no-cache',
    'Referer': 'https://www.site24x7.com/tools/email-validator.html',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}

def check_email_validity(email):
    payload = {"email": email}
    
    for _ in range(3):  # Retry logic
        try:
            proxy_url = next(proxy_cycle)  # Get the next proxy URL
            print(f"Using proxy: {proxy_url}")

            response = requests.post(proxy_url, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json() 
        except requests.exceptions.RequestException:
            time.sleep(20)  # Wait before retry
    return None

# def check_email_validity(email):
#     payload = f'emails={email}'
#     for _ in range(3):  # Retry logic
#         try:
#             response = requests.post(API_URL, headers=HEADERS, data=payload, timeout=5)
#             if response.status_code == 200:
#                 return response.json()
#             if response.status_code == 400:
#                 print(response.json())
#                 time.sleep(60)  # Wait before retry
#         except requests.exceptions.RequestException:
#             time.sleep(60)  # Wait before retry
#     return None

def process_emails(contacts: ApolloContact, session: Session):
    for contact in contacts:
        result = check_email_validity(contact.email)
        if result:
            status = result.get("results", {}).get(contact.email.split('@')[-1], {}).get(contact.email, {}).get("status")
            contact.is_valid = status == 250
            print(contact.email, contact.is_valid)
            contact.email_validity_response = result
            session.add(contact)
            session.commit()


def verify_emails(thread_count=1):
    with Session(engine) as session:
        contacts = session.exec(select(ApolloContact).where(ApolloContact.is_valid == None)).all()
        if not contacts:
            return
        
        process_emails(contacts, session)

verify_emails()