from utils.scrape_apollo import get_all_apollo_contacts, get_hr_contacts_by_company
from utils.ai_email_writer import generate_email
from utils.schedule_mail import schedule_email

def send_emails_to_hrs(company_link: str, company_name: str, job_description: str):
    
    print("Scraping all Emails")
    get_all_apollo_contacts()

    # TODO: Get Max 20 mails, the HR email should be included if its given in the Job Post
    emails = get_hr_contacts_by_company(company_link)
    print(f"Got {len(emails)} Emails")

    if not emails:
        return
    
    mail_content = generate_email(company_name, job_description)
    print("Generated Email")

    for email in emails:
        schedule_email(email, mail_content)
