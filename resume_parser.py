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
    skills_section = re.search(r"Technical Skills\s*(.*?)\s*(?=\n\S|\Z)", text, re.DOTALL | re.IGNORECASE)
    if skills_section:
        raw_skills = skills_section.group(1)
        skills = re.findall(r"[A-Za-z0-9#\+.\-]+", raw_skills)
        return list(set([s.strip() for s in skills if len(s) > 1]))
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
        }

# Example
if __name__ == "__main__":
    result = parse_resume("1cr21cs156.pdf")
    for key, value in result.items():
        print(f"{key.upper()}: {value}\n")
