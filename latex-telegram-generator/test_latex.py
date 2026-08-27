import os
import json
from src.llm_engine import generate_tailored_content
from src.compiler import compile_pdfs

job_desc = """The role: Data & Product Engineer InternSmall team, high bar. You'll own the data our platform runs on — finding new sources, getting them into production, and building the features that make them useful to corporate finance teams. Over six months you'll work on the same codebase and the same roadmap as the rest of the engineering team. Your responsibilities will include:
Research and evaluate new data sources: company registers, filings, industry databases and the open web.
Build and maintain Python integrations that bring those sources into production reliably.
Develop LLM-powered pipelines that extract structured data from PDFs, filings and free text.
Design and ship end-to-end features that turn new data into something deal teams can work with.
Take ownership of data quality through validation, monitoring and automated checks.

🔷 Qualifications - to be successful in this role, you will need:Must-haves
We expect the motivation and ownership of a founder. You own problems end-to-end and care more about the user outcome than your ticket description.
Degree in CS, Data Science, Mathematics, Physics or Engineering, completed or in progress, or equivalent practical experience.
Proficiency in Python. You can handle messy real-world data and build the APIs and services your features rely on.
Comfortable working with third-party data sources: authentication, pagination, rate limits, JSON/XML/CSV, plus parsing or scraping when there is no API.
Hands-on experience with databases such as PostgreSQL.
Experience handling large, complex datasets, whether from a project, a thesis or your own work.
You use AI/LLM tools to move faster, but you have the technical depth to audit their output and maintain high code quality. No "AI slop".
Strong communication and structured problem-solving skills.
Available full-time for 6 months, based in or moving to Munich (hybrid)."""

if __name__ == "__main__":
    from src.config import MASTER_PROFILE_PATH
    with open(MASTER_PROFILE_PATH, "r", encoding="utf-8") as f:
        master_profile = json.load(f)
    print("Generating LLM content...")
    tailored_data = generate_tailored_content(job_desc, master_profile)
    print("Writing raw JSON:")
    print(json.dumps(tailored_data, indent=2))
    
    import shutil
    cv, cl = compile_pdfs(tailored_data)
    print("Success!", cv, cl)
    shutil.copy(cv, "local_cv_output.pdf")
    shutil.copy(cl, "local_cl_output.pdf")
    print("Done.")
