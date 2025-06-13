import streamlit as st
from resume_parser import get_jobs, get_project_recommendations, parse_resume

st.set_page_config(page_title="Smart Resume Parser", layout="centered")
background_image_url ="https://images.unsplash.com/photo-1506744038136-46273834b3fb"
# CSS to add background image
page_bg_img = f"""
<style>
.stApp {{
    
    background-color:black;
    color:white;

}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)
st.title("📄 Smart Resume Parser")
st.markdown("Upload your PDF resume to extract key information using NLP.")

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file:
    with open("temp_resume.pdf", "wb") as f:
        f.write(uploaded_file.read())

    with st.spinner("🔍 Parsing resume..."):
        result = parse_resume("temp_resume.pdf")

    st.success("✅ Resume parsed successfully!")

    st.subheader("👤 Candidate Info")
    st.write(f"**Name:** {result['name'] or 'Not found'}")
    st.write(f"**Email:** {result['email'] or 'Not found'}")
    st.write(f"**Phone:** {result['phone'] or 'Not found'}")

    st.subheader("🎓 Education")
    st.code(result['education'] or "Not found")

    st.subheader("🧠 Skills")
    if result['skills']:
        st.write(", ".join(result['skills']))
    else:
        st.write("No skills found")

    st.subheader("💼 Projects")
    if result['projects']:
        for i, project in enumerate(result['projects'], 1):
            st.markdown(f"{i}. {project}")
    else:
        st.write("No projects found")
    st.subheader("🚀 Recommended Projects")
    if result['skills']:
        with st.spinner("Generating project ideas with AI..."):
            recommended_projects = get_project_recommendations(result['skills'])
        st.markdown(recommended_projects)
    else:
        st.write("No skills found to generate project recommendations.")

    st.subheader("💼 Job Vacancies")
    if result['skills']:
        with st.spinner("Searching Jobs based on your skills..."):
            job_vacancies = get_jobs(result['skills'])
        if job_vacancies:
            for job in job_vacancies:
                st.markdown(f"- {job}")
        else:
            st.write("No jobs found.")
    else:
        st.write("No skills found to search for job vacancies.")


