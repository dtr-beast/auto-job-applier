import os
import time
import random
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from utils.scrape_apollo import ApolloContact

class MailContentInfo(BaseModel):
    """
    Contains the e-mail content information to send to an e-mail
    """

    subject: str = Field(..., max_length=60)
    """
    Subject of the mail, should max (max 60 chars)
    """

    content: str
    """
    Main Content of the e-mail.
    Contains ->
    - Greeting (e.g -> 'I hope this email finds you well')
    - Introduction (e.g. -> My name is ... and I am ...)
    - Content -> User's skills mapped to the Job Description requirements in bullet points form
    """

def get_email_message(receiver_name: str, job_application_reasoning: str) -> str:
    return f"""Dear {receiver_name},

{job_application_reasoning}
"""

def pick_scheduled_datetime() -> datetime:
    """
    Pick the next weekday (Monday-Friday) and a random time between 10:00 AM and 11:30 AM.
    Returns a datetime object representing the scheduled date and time.
    """
    today = datetime.now()
    days_to_add = 1
    # Find the next weekday (skip Saturday=5 and Sunday=6)
    while (today + timedelta(days=days_to_add)).weekday() >= 5:
        days_to_add += 1
    next_weekday_date = today + timedelta(days=days_to_add)
    
    # Base time: 10:00 AM on the next weekday
    base_time = datetime(next_weekday_date.year, next_weekday_date.month, next_weekday_date.day, 10, 0)
    # Randomly add between 0 and 90 minutes to get a time between 10:00 and 11:30 AM
    rand_minutes = random.randint(0, 90)
    scheduled_datetime = base_time + timedelta(minutes=rand_minutes)
    return scheduled_datetime

def schedule_email(contact_info: ApolloContact, mail_content: MailContentInfo, resume_file: str | None = None) -> None:
    if not resume_file:
        resume_file = os.getenv("RESUME_FILE_PATH", "C:\\Users\\mc5to\\OneDrive\\Desktop\\Resumes\\Aditya-Sharma-Resume.pdf")
    with sync_playwright() as p:
        # Connect to a running browser instance (headed mode)
        browser = p.chromium.connect_over_cdp("http://localhost:9222", slow_mo=300)
        context = browser.contexts[0]
        page = context.new_page()
        
        # Open Gmail compose window
        page.goto("https://mail.google.com/mail/u/0/#inbox?compose=new")
        page.get_by_label("To recipients").fill(contact_info.email)
        page.get_by_label("To recipients").press("Tab")

        page.get_by_placeholder("Subject").fill(mail_content.subject)
        page.get_by_placeholder("Subject").press("Tab")

        message = f"Dear {contact_info.name.split(" ")[0]},\n\n{mail_content.content}"
        # TODO: Sometimes this does not type the full message, make some kind of validation to fix this flakiness
        page.get_by_role("textbox", name="Message Body").type(message)

        # Attach resume file loaded from environment variable
        with page.expect_file_chooser() as fc_info:
            page.get_by_label("Attach files").click()
        file_chooser = fc_info.value
        file_chooser.set_files(resume_file)

        page.get_by_label("More send options").click()
        page.get_by_text("Schedule send").click()
        page.get_by_text("Pick date & time").click()

        # Use the extracted function to get the scheduled datetime
        scheduled_datetime = pick_scheduled_datetime()
        # Fill in the date and time fields using the scheduled_datetime object
        page.get_by_label("Date", exact=True).fill(scheduled_datetime.strftime("%b %d, %Y"))
        page.get_by_label("Time", exact=True).fill(scheduled_datetime.strftime("%I:%M %p"))

        page.get_by_role("button", name="Schedule send").click()
        # Sleep before closing the page
        time.sleep(random.uniform(2, 5))
        # TODO: 
        page.close()

if __name__ == "__main__":
    # Load environment variables from the .env file
    load_dotenv()
    resume_file = os.getenv("RESUME_FILE", "C:\\Users\\mc5to\\OneDrive\\Desktop\\Resumes\\Aditya-Sharma-Resume.pdf")
    
    mail_content = MailContentInfo(subject="Aditya Sharma's Job Application", content="I am very smart, please select me!")
    # Generate the email message
    mail_message = get_email_message("mc5torkpro@gmail.com", mail_content)
    
    # Schedule the email
    schedule_email(mail_message, mail_content, resume_file)
