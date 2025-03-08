from datetime import datetime
import time
import random
import json
from typing import List, Optional
import psycopg2
from playwright.sync_api import sync_playwright
from psycopg2.extras import execute_values
from pydantic import BaseModel
import re
# PostgreSQL Connection Details
DB_NAME = "job_application"
DB_USER = "postgres"
DB_PASSWORD = "root"
DB_HOST = "localhost"
DB_PORT = "5432"


# Connect to PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

class ApolloContact(BaseModel):
    email: str
    name: Optional[str] = None
    title: Optional[str] = None
    organization_name: Optional[str] = None
    linkedin_url: Optional[str] = None
    company_linkedin_url: Optional[str] = None
    created_at: Optional[datetime] = None
    json_data: dict

def get_company_slug(linkedin_url: str) -> str:
    match = re.search(r"linkedin\.com/company/([^/]+)/?", linkedin_url)
    return match.group(1) if match else linkedin_url

# Create Table if not exists
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS apollo_contacts (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE,
            name TEXT,
            title TEXT,
            organization_name TEXT,
            linkedin_url TEXT,
            company_linkedin_url TEXT,
            created_at TIMESTAMPTZ,
            json_data JSONB
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Bulk Insert Contacts
def save_contacts_bulk(contacts):
    if not contacts:
        return  # Skip if no data

    conn = get_db_connection()
    cursor = conn.cursor()

    data_to_insert = []
    for contact in contacts:
        email = contact.get("email")
        if not email:
            continue  # Skip records without an email (since it's the unique key)

        name = contact.get("name")
        title = contact.get("title")
        organization_name = contact.get("organization_name")
        linkedin_url = contact.get("linkedin_url")
        company_linkedin_url = contact.get("account", {}).get("linkedin_url")
        created_at = contact.get("created_at")

        data_to_insert.append(
            (email, name, title, organization_name, linkedin_url, company_linkedin_url, created_at, json.dumps(contact))
        )

    # Perform bulk insert
    execute_values(cursor, """
        INSERT INTO apollo_contacts (email, name, title, organization_name, linkedin_url, company_linkedin_url, created_at, json_data)
        VALUES %s
        ON CONFLICT (email) DO NOTHING;
    """, data_to_insert)

    conn.commit()
    cursor.close()
    conn.close()

# Fetch All Apollo Contacts
def get_all_apollo_contacts():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = context.new_page()
        page.goto("https://app.apollo.io/#/people")
        page.wait_for_load_state()

        page_num = 1
        all_contacts = []
        while True:
            print(f"Fetching page {page_num}...")

            js_script = f"""
            (async () => {{
                const response = await fetch("https://app.apollo.io/api/v1/mixed_people/search", {{
                    method: "POST",
                    headers: {{
                        "Content-Type": "application/json"
                    }},
                    body: JSON.stringify({{
                        "prospected_by_current_team": ["yes"],
                        "sort_ascending": false,
                        "sort_by_field": "contact_created_at",
                        "display_mode": "explorer_mode",
                        "per_page": 100,
                        "open_factor_names": [],
                        "num_fetch_result": 3,
                        "context": "people-index-page",
                        "show_suggestions": false,
                        "include_account_engagement_stats": false,
                        "include_contact_engagement_stats": false,
                        "finder_version": 2,
                        "fields": [
                            "id", "name", "contact_emails", "email", "title",
                            "organization_name", "linkedin_url", "created_date", "account.linkedin_url"
                        ],
                        "page": {page_num}
                    }})
                }});

                const data = await response.json();
                return JSON.stringify(data.contacts, null, 2);
            }})();
            """

            contacts_json = page.evaluate(js_script)
            contacts = json.loads(contacts_json)

            if not contacts:
                print("No more contacts found. Stopping.")
                break
            all_contacts.extend(contacts)
            print(f"Fetched {len(contacts)} contacts from page {page_num}.")

            delay = random.uniform(1, 4)
            print(f"Waiting {delay:.2f} seconds to avoid rate limiting...")
            time.sleep(delay)

            page_num += 1

            # Bulk insert all contacts
        save_contacts_bulk(all_contacts)
        print("All contacts saved to PostgreSQL.")
        page.close()


# Fetch HR Contacts by Company LinkedIn URL
def get_hr_contacts_by_company(company_linkedin_url: str) -> List[ApolloContact]:
    conn = get_db_connection()
    cursor = conn.cursor()

    company_name = get_company_slug(company_linkedin_url)
    cursor.execute(f"""
        SELECT email, name, title, organization_name, linkedin_url, company_linkedin_url, created_at, json_data
        FROM apollo_contacts
        WHERE company_linkedin_url LIKE '%{company_name}%';
    """)

    raw_contacts = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert raw database rows to list of Pydantic models
    return [ApolloContact(
        email=row[0],
        name=row[1],
        title=row[2],
        organization_name=row[3],
        linkedin_url=row[4],
        company_linkedin_url=row[5],
        created_at=row[6],
        json_data=row[7]  # This is already JSONB in PostgreSQL
    ) for row in raw_contacts]


# Run the script
if __name__ == "__main__":
    create_table()
    # get_all_apollo_contacts()

    # Example: Fetch HR contacts for a company
    company_url = "http://www.linkedin.com/company/bristlecone"
    hr_contacts = get_hr_contacts_by_company(company_url)
    print(f"HR Contacts for {company_url}:")
    for hr in hr_contacts:
        print(hr)
