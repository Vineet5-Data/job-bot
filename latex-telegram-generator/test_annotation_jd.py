import json
import shutil
from src.llm_engine import generate_tailored_content
from src.compiler import compile_pdfs
from src.config import MASTER_PROFILE_PATH

job_desc = """Data Labeling & Annotation

* Perform data labeling and annotation activities for training and evaluating machine learning models.
* Help maintain and improve annotation quality standards and guidelines.
* Work with various data types including images, point clouds, and sensor data from robotic systems.

Data Analysis & Preparation

* Assist with data analysis, cleaning, and preparation for model training and evaluation.
* Help build and maintain data pipelines and tooling to streamline data workflows.
* Generate reports and visualizations to enable data-driven decision-making.

ML Activities

* Contribute to model training, evaluation, and related ML activities.
* Help track and document experiment results, model performance metrics, and dataset versions.
* Assist with integrating trained models into the product pipeline for testing and validation.

Qualifications

Education and Experience

* Currently pursuing or recently completed a Bachelor's or Master's degree in Computer Science, Data Science, Machine Learning, Engineering, or a related technical field.
* Coursework or project experience in machine learning, data science, or computer vision is a plus.

Skills

* Proficiency in Python programming.
* Basic understanding of machine learning concepts (supervised learning, model training and evaluation).
* Experience with data manipulation libraries such as NumPy, Pandas, or similar.
* Familiarity with data visualization tools (Matplotlib, Seaborn, or similar).
* Strong attention to detail and a structured approach to working with data.
* Good communication skills and the ability to work collaboratively in a team.

Additional Skills / Nice To Have

* Experience with computer vision libraries (OpenCV, torchvision) or deep learning frameworks (PyTorch, TensorFlow).
* Familiarity with annotation tools (e.g., Label Studio, CVAT, or similar).
* Experience working with Docker or cloud-based ML environments.
* Knowledge of German is a plus."""

if __name__ == "__main__":
    with open(MASTER_PROFILE_PATH, "r", encoding="utf-8") as f:
        master_profile = json.load(f)

    print("Generating LLM content...")
    tailored_data = generate_tailored_content(job_desc, master_profile)
    print("Raw JSON:")
    print(json.dumps(tailored_data, indent=2, ensure_ascii=False))

    cv, cl = compile_pdfs(tailored_data)
    print("Success!", cv, cl)
    shutil.copy(cv, "annotation_cv_output.pdf")
    shutil.copy(cl, "annotation_cl_output.pdf")
    shutil.copy(cv.with_suffix(".tex"), "annotation_cv_output.tex")
    shutil.copy(cl.with_suffix(".tex"), "annotation_cl_output.tex")
    print("Done.")
