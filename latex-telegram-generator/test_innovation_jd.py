import json
import shutil
from src.llm_engine import generate_tailored_content
from src.compiler import compile_pdfs
from src.config import MASTER_PROFILE_PATH

job_desc = """Internship / Working Student - Innovation & Data Science Team

Your key areas of focus will be...
- Building and analyzing knowledge graphs
- Supporting GenAI- and LLM-based use cases
- Conducting machine learning and data science analyses
- Optimizing our retrieval and data processing processes
- Planning and implementing technical analyses and prototypes
- Participating in scientific innovation projects

Your profile
- Enrollment in a degree program such as Computer Science, Data Science, Business Informatics, Mathematics, or a related field (at least 3rd semester or during a gap year between Bachelor's and Master's studies)
- Proficiency in Python and basic experience with data science or machine learning workflows
- Basic knowledge of cloud architectures (preferably Azure) or an interest in developing these skills during the internship
- Initial exposure to topics such as data analysis, knowledge modeling, knowledge graphs, or machine learning is an advantage
- An independent, analytical, and structured working style
- Enthusiasm for research, new technologies, and interdisciplinary collaboration; proficiency in MS Office
- Very good German and good English skills (min. B2 level)"""

if __name__ == "__main__":
    with open(MASTER_PROFILE_PATH, "r", encoding="utf-8") as f:
        master_profile = json.load(f)

    print("Generating LLM content...")
    tailored_data = generate_tailored_content(job_desc, master_profile)
    print("Raw JSON:")
    print(json.dumps(tailored_data, indent=2, ensure_ascii=False))

    cv, cl = compile_pdfs(tailored_data)
    print("Success!", cv, cl)
    shutil.copy(cv, "innovation_cv_output.pdf")
    shutil.copy(cl, "innovation_cl_output.pdf")
    print("Done.")
