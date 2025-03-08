from typing import Sequence
from ollama import Client, Message
from pydantic import BaseModel, Field
import os


def extract_resume_info():
    return {
        "name": "Aditya Sharma",
        "location": "Chandigarh, India",
        "email": "aditya.sharma.11072001@gmail.com",
        "phone": "9389263175",
        "linkedin": "https://www.linkedin.com/in/aditya-5harma/",
        "skills": [
            "Angular",
            "Spring Boot",
            "SQL",
            "Docker",
            "Kubernetes",
            "Git",
            "Python",
            "React",
            ".NET Core",
            "Microservices",
            "Apache Kafka",
            "Apache Spark",
        ],
        "experience": [
            "Developed a data synchronization pipeline using Kafka and Spark",
            "Built a high-performance ETL pipeline processing 1.5 crore records in 2 hours",
            "Designed a modular Fraud Reporting System (FINNET2)",
            "Developed scalable Rule Engine with MySQL optimizations",
            "Led AML solutions for Mobile Money Wallet and Insurance Company",
            "Experience with .NET Core, Angular, and MySQL",
            "Developed Slack notifications, Google OpenID Connect integration, and E2E Cypress tests",
        ],
    }


os.environ["OLLAMA_HOST"] = "https://df83-34-124-135-20.ngrok-free.app/"
client = Client(host=os.environ.get("OLLAMA_HOST", "localhost:11434"))


def pull_model(client: Client):
    models = client.list()
    for model in models.models:
        print("Printing")
        print(model)
    client.pull("phi4:14b")


class MailContent(BaseModel):
    """
    Contains the e-mail content information to send to an e-mail
    """

    subject: str = Field(..., max_length=100)
    """
    Subject of the mail. e.g. -> {ApplicantName}'s Application for {RoleName} ({JobId}) Role at {CompanyName}
    """

    content: str
    """
    Main Content of the e-mail.
    Contains ->
    - Introduction (e.g. -> 'I hope this email finds you well, My name is ... and I am ...', 'I hope you are having a great day, My name is ... and I am ...')
    - Content -> Bullet points mapping skills and experience to job requirements
    - Closing Statement -> A Call To Action (e.g. -> "Thank you for considering me, I hope to connect with you soon")
    """


def get_mail_response(messages: Sequence[Message]):
    for attempt in range(10):
        try:
            return client.chat(
                # model="llama3.2:3b",
                # model="phi4:14b",
                model="qwen2.5:14b",
                messages=messages,
                format=MailContent.model_json_schema(),
            )
        except Exception as e:
            print(str(e))


def generate_email(company_name: str, job_description: str) -> MailContent:
    resume_info = extract_resume_info()

    system_prompt = """
    You are an AI assistant that generates professional job application emails.
    
    - The **subject** should contain with Applicant's name, Job Id (If found), Role and Company
    - The **introduction** should be a short paragraph introducing the applicant and expressing interest in the role. Do NOT use bullet points or dashes here.
    - The **key qualifications** should be in a bulleted list, mapping relevant skills/experience to the job description.
    - The **closing statement** should be a paragraph thanking the recruiter and expressing interest in further discussion. Again, do NOT use bullet points here.
    
    **Do NOT include:**
    - Salutations (e.g., "Dear Hiring Manager")
    - Email signatures (e.g., "Best Regards, Aditya")
    - Any unnecessary dashes or asterisks
    """

    user_prompt = f"""
    Resume Details:
    - Name: {resume_info['name']}
    - Location: {resume_info['location']}
    - Email: {resume_info['email']}
    - Phone: {resume_info['phone']}
    - LinkedIn: {resume_info['linkedin']}
    - Skills: {', '.join(resume_info['skills'])}
    - Experience: {'; '.join(resume_info['experience'])}

    Company Name: {company_name}
    
    Job Description:
    {job_description}

    Please follow the system instructions and generate a **structured** email response.
    """
    messages: Sequence[Message] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response = get_mail_response(messages)
    print(f"Model Response Time: {response.total_duration / 1e+9}")

    mail_content = MailContent.model_validate_json(response.message.content)

    # Ensure bullet points don't have unnecessary dashes
    mail_content.content = mail_content.content.replace("*", "")

    print(f"Subject:\n {mail_content.subject}")
    print(f"\n\n\nContent:\n {mail_content.content}")

    return mail_content


# Example usage:
# job_desc = "We are looking for a backend engineer with expertise in Spring Boot and Kafka."
# email = generate_email(job_desc)
# print(email)

print("\n\n\n\n\n")
# print(MailContentInfo.model_json_schema())

if __name__ == "__main__":
    # pull_model(client)
    company_name = "Swiggy"
    jd = """
ID: 17689 | 1-3 yrs | Bangalore_Embassy Tech Village | careers
Way of working - Remote : Employees will have the freedom to work remotely all through the year. These employees, who form a large majority, will come together in their base location for a week, once every quarter.



Job Title: Software Dev Engineer I [Native iOS] 

Location: Remote first

Tenure: 1- 3years



ABOUT THE TEAM & ROLE:

Swiggy is India’s leading on-demand delivery platform with a tech-first approach to logistics and a solution-first approach to consumer demands. With a presence in 500 cities across India, partnerships with hundreds of thousands of restaurants, an employee base of over 5000, and a 2 lakh+ strong independent fleet of Delivery Executives, we deliver unparalleled convenience driven by continuous innovation. 

Built on the back of robust ML technology and fuelled by terabytes of data processed every day, Swiggy offers a fast, seamless and reliable delivery experience for millions of customers across India. 

From starting out as a hyperlocal food delivery service in 2014 to becoming a logistics hub of excellence today, our capabilities result not only in lightning-fast delivery for customers but also in a productive and fulfilling experience for our employees. 

With Swiggy’s New Supply and the recent launches of Swiggy Instamart, Swiggy Genie, and Guiltfree, we are consistently making waves in the market, while continually growing the opportunities we offer our people.



Position Overview: 




We are looking for highly motivated individuals who can join our engineering team as SDE-1. As an iOS SDE-1 at Swiggy, you will play a crucial role in developing and enhancing our iOS mobile application, which millions of users rely on to order food, groceries, dine in and enjoy a seamless delivery experience. This opportunity offers you a chance to work closely with our talented team of iOS developers and gain valuable hands-on experience in the fast-paced world of app development. We are seeking a highly skilled iOS Software Development Engineer (SDE-1) to join our dynamic team. The ideal candidate should have a passion for mobile technology and a proven track record of delivering high-quality iOS applications. As an SDE-1, you will be responsible for designing, developing, and maintaining iOS applications that delight our users and exceed industry standards.



What will you get to do here?



Design and Architecture: Collaborate with cross-functional teams to make our app more scalable and robust. Architect solutions that adhere to best practices and promote code reusability.
Development: Write clean, maintainable, reusable code in Swift/SwiftUI. Implement new features, enhancements, and bug fixes according to project requirements and timelines.
Testing: Develop and execute comprehensive unit tests and integration tests to ensure the reliability and stability of our Consumer App. Implement automated testing frameworks and strategies to streamline the testing process.
Performance Optimization: Identify performance bottlenecks and optimize iOS applications for speed, responsiveness, and resource efficiency. Conduct code reviews and performance profiling to maintain high performance standards.
Documentation: Create technical documentation, including design documents, API specifications, and release notes. Document codebase changes, architecture decisions, and development processes to facilitate knowledge sharing and onboarding.
Collaboration: Collaborate closely with product managers, designers, and other engineers to translate product requirements into technical solutions. Participate in Agile ceremonies, such as sprint planning, daily stand-ups, and retrospectives.
Continuous Improvement: Stay updated on the latest trends, tools, and technologies in iOS development. Continuously improve development processes, coding standards, and software quality through innovation and experimentation.

What qualities are we looking for?



Bachelor's degree in Computer Science, Engineering, or related field (Master's degree preferred).
1+ years of professional experience in iOS application development.
Proficiency in Swift programming languages.
Strong understanding of iOS SDK, X-Code, and related development tools.
Experience with iOS architecture components
Solid understanding of software design principles, patterns, and best practices.
Experience with RESTful APIs, JSON/Proto etc
Familiarity with version control systems (e.g., Git) and continuous integration tools (e.g., Jenkins).
Excellent problem-solving skills and attention to detail.
Strong communication and collaboration skills.
Ability to thrive in a fast-paced, dynamic environment and adapt to changing priorities.
Knowledge and hands on experience of Kotlin Multiplatform will be cherry on the top. 
Visit our tech blogs to learn more about some of the challenges we deal with:

Making Swiggy Buttery Smooth. A good mobile developer not only does… | by Agam Mahajan

Insight into Swiggy’s new Multimedia Card | by Mayank Jha

Build Time Optimizations (Xcode). As an iOS developer, we have… | by Dhruvil Patel | Swiggy Bytes — Tech Blog

Handling multiple caches in App

Designing the Swiggy app to be truly ‘accessible’ | Episode-3 | by Agam Mahajan

We are an equal opportunity employer and all qualified applicants will receive consideration for employment without regard to race, colour, religion, sex, disability status, or any other characteristic protected by the law.
"""
    email = generate_email(company_name, jd)
