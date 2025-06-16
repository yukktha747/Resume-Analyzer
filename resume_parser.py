import fitz  # this is imported from the PyMuPDF librrary which is also a alias for pyMUPDF which can extract the text,images from the pdf 
import re
import spacy #this is a spacy library which is a powerful nlp library.It is used for the tokenization,NER,POS
import g4f
from serpapi import GoogleSearch
import os
from dotenv import load_dotenv
load_dotenv()

nlp = spacy.load("en_core_web_trf")#english transformer model provided by spacy based on BERT

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def extract_email(text):
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    return match.group(0) if match else None

def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def extract_skills(text):
    # Match the TECHNICAL SKILLS section until the next uppercase section title
    match = re.search(r"TECHNICAL SKILLS\s*((?:\n[•\-\*\s]*[^\n]+)+)", text, re.IGNORECASE)
    if match:
        raw_lines = match.group(1).strip().split("\n")
        skills = []
        for line in raw_lines:
            line = re.sub(r"^[•\-\*\s]+", "", line).strip()
            # Skip irrelevant lines
            if not line or len(line.split()) > 6:
                continue
            for part in re.split(r",|/|;|\|", line):
                cleaned = part.strip()
                if cleaned and len(cleaned) > 1:
                    skills.append(cleaned)
        return list(set(skills))
    return []


def extract_education(text):
    match = re.search(r"Education\s*(.*?)\s*(?=Summary|Experience)", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def extract_projects(text):
    projects_section = re.search(r"Projects\s*(.*?)\s*(?=Certifications|Technical Skills|Achievements)", text, re.DOTALL | re.IGNORECASE)
    if projects_section:
        projects = re.findall(r"\n\s*(.*?)\|", projects_section.group(1))
        return [p.strip() for p in projects]
    return []
def get_project_recommendations(skills):
    prompt = f"I have the following technical skills: {', '.join(skills)}. Suggest 5 relevant software development project ideas that would help me build a portfolio and improve in these areas."
    response = g4f.ChatCompletion.create(
        model=g4f.models.default,
        messages=[{"role": "user", "content": prompt}],
      
    )
    
    return response
def get_jobs(skills):
    job_links = []

    # Set of noisy keywords to ignore
    ignore_keywords = {
        "code", "languages", "developer", "co-curricular", "activities",
        "framework", "vs", "tools", "technologies", "js", "", ".", ","
    }

    # Filter and lowercase
    cleaned_skills = [
        skill.lower().strip(".").strip(",") for skill in skills
        if skill.lower().strip(".").strip(",") not in ignore_keywords
    ]

    # Remove duplicates
    cleaned_skills = list(set(cleaned_skills))

    print("Cleaned Skills for Search:", cleaned_skills)

    if not cleaned_skills:
        return ["⚠️ No valid skills found to search for jobs."]

    # Create search query
    search_query = " ".join(cleaned_skills) + " software developer jobs"

    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        return ["⚠️ SerpAPI key not found. Please set SERPAPI_KEY environment variable."]

    params = {
        "engine": "google_jobs",
        "q": search_query,
        "hl": "en",
        "api_key": api_key
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        jobs_results = results.get("jobs_results", [])

        for job in jobs_results[:5]:
            title = job.get("title")
            company = job.get("company_name")
            link = job.get("via", "N/A")
            job_links.append(f"{title} at {company} → {link}")

        return job_links if job_links else ["⚠️ No jobs found."]
    
    except Exception as e:
        return [f"❌ Error occurred while fetching jobs: {str(e)}"]

def generate_cover_letter(name, skills, job_title="Software Developer", company_name="Your Company"):
    skill_text = ", ".join(skills[:5]) if skills else "various relevant skills"
    return f"""
Dear Hiring Manager,

I am writing to express my keen interest in the {job_title} position at {company_name}. With a strong foundation in {skill_text}, I am confident in my ability to contribute effectively to your team.

My background in software development, coupled with my passion for problem-solving and continuous learning, makes me a strong fit for your organization. I am particularly drawn to {company_name} because of its commitment to innovation and excellence.

I would welcome the opportunity to discuss how my skills and experiences align with your goals. Thank you for considering my application.

Sincerely,  
{name if name else 'Your Name'}
"""

def parse_resume(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "education": extract_education(text),
        "skills": extract_skills(text),
        "projects": extract_projects(text),
        "projects reccomendations":get_project_recommendations(text),
        "Job Vacancy Links":get_jobs(text),
        "Cover letter":generate_cover_letter(text,text,text,text),
        }

# Example
if __name__ == "__main__":
    result = parse_resume("1cr21cs156.pdf")
    for key, value in result.items():
        print(f"{key.upper()}: {value}\n")
