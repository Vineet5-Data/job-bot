import shutil
import tempfile
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple
from src.config import CV_TEMPLATE_PATH, CL_TEMPLATE_PATH
from src.sanitizer import escape_latex

logger = logging.getLogger(__name__)

# --- LaTeX rendering: turns plain LLM content into exact LaTeX. The LLM never
# writes LaTeX itself, so formatting (columns, tables, escaping) is always
# correct regardless of what the model does or doesn't remember to do. ---

def render_skills(categories: List[Dict[str, Any]]) -> str:
    """Two-column skills block. Balances columns by content length (not just
    category count) and always places "Language Skills" last, right column."""
    lang_skills = None
    rest = []
    for cat in categories:
        if cat.get("category", "").strip().lower() == "language skills":
            lang_skills = cat
        else:
            rest.append(cat)

    left, right = [], []
    left_weight = right_weight = 0
    for cat in rest:
        weight = len(cat.get("category", "")) + sum(len(i) for i in cat.get("items", []))
        if left_weight <= right_weight:
            left.append(cat)
            left_weight += weight
        else:
            right.append(cat)
            right_weight += weight
    if lang_skills:
        right.append(lang_skills)

    def render_column(cats: List[Dict[str, Any]]) -> str:
        blocks = []
        for cat in cats:
            name = escape_latex(cat.get("category", ""))
            items = escape_latex(", ".join(cat.get("items", [])))
            blocks.append(f"\\textbf{{{name}}}\\\\\n{items}")
        return "\n\n\\vspace{0.7em}\n".join(blocks)

    return (
        "\\begin{minipage}[t]{0.48\\textwidth}\n"
        f"{render_column(left)}\n"
        "\\end{minipage}\n"
        "\\hfill\n"
        "\\begin{minipage}[t]{0.48\\textwidth}\n"
        f"{render_column(right)}\n"
        "\\end{minipage}"
    )

def _needspace(num_bullets: int) -> str:
    # ponytail: flat heuristic (header line + ~2 lines per bullet), not measured
    # per block — tune the multiplier if bullets routinely wrap to 3+ lines.
    return f"\\needspace{{{2 + 2 * max(num_bullets, 1)}\\baselineskip}}\n"

def render_experience(experience: List[Dict[str, Any]]) -> str:
    blocks = []
    for exp in experience:
        role = escape_latex(exp.get("role", ""))
        duration = escape_latex(exp.get("duration", ""))
        company = escape_latex(exp.get("company", ""))
        bullet_list = exp.get("bullets", [])
        bullets = "\n".join(f"    \\item {escape_latex(b)}" for b in bullet_list)
        blocks.append(
            _needspace(len(bullet_list)) +
            f"\\textbf{{{role}}}\n"
            "\\begin{tabular}{@{}p{0.70\\textwidth}r@{}}\n"
            f"    \\textbf{{{duration}}}  \\hspace{{1.3ex}} \\textbf{{{company}}} \\\\\n"
            "\\end{tabular}\n"
            f"\\begin{{itemize}}\n{bullets}\n\\end{{itemize}}"
        )
    return "\n\n".join(blocks)

def render_projects(projects: List[Dict[str, Any]]) -> str:
    blocks = []
    for proj in projects:
        title = escape_latex(proj.get("title", ""))
        duration = escape_latex(proj.get("duration", ""))
        grade = proj.get("grade")
        grade_cell = f"\\raggedleft\\textbf{{Grade: {escape_latex(grade)}}}" if grade else ""
        bullet_list = proj.get("bullets", [])
        bullets = "\n".join(f"    \\item {escape_latex(b)}" for b in bullet_list)
        blocks.append(
            _needspace(len(bullet_list)) +
            "\\item\n"
            "\\begin{tabular}{@{}p{0.20\\textwidth}p{0.57\\textwidth}p{0.13\\textwidth}@{}}\n"
            f"    \\textit{{{duration}}}\n"
            f"    & \\textbf{{{title}}}\n"
            f"    & {grade_cell} \\\\\n"
            "\\end{tabular}\n"
            f"\\begin{{itemize}}\n{bullets}\n\\end{{itemize}}"
        )
    return "\n\n".join(blocks)

def render_projects_section(projects: List[Dict[str, Any]]) -> str:
    """Full RESEARCH PROJECTS section, header included. Section heading is glued
    to the first project via one needspace check covering both, so the heading
    can never strand alone at the bottom of a page with its project pushed on."""
    if not projects:
        return ""
    first_bullets = len(projects[0].get("bullets", []))
    heading_lines = 3  # rSection title + hrule + spacing, roughly fixed height
    glued_space = f"\\needspace{{{heading_lines + 2 * max(first_bullets, 1)}\\baselineskip}}\n"
    return (
        glued_space +
        "\\begin{rSection}{RESEARCH PROJECTS}\n\n"
        "\\begin{itemize}\n\n"
        f"{render_projects(projects)}\n\n"
        "\\end{itemize}\n\n"
        "\\end{rSection}"
    )

def render_cover_letter_body(greeting: str, paragraphs: List[str]) -> str:
    parts = [escape_latex(greeting)] + [escape_latex(p) for p in paragraphs]
    return "\n\n".join(parts)

def compile_pdfs(tailored_data: Dict[str, Any]) -> Tuple[Path, Path]:
    company_name_safe = "".join(c if c.isalnum() else "_" for c in tailored_data.get("company_name", "Company")).strip("_")
    
    tmp_dir = Path(tempfile.mkdtemp(prefix=f"app_{company_name_safe}_"))
    
    try:
        # Copy cls file
        templates_dir = Path(CV_TEMPLATE_PATH).parent
        shutil.copy(templates_dir / "resume.cls", tmp_dir / "resume.cls")
        
        # Read templates
        with open(CV_TEMPLATE_PATH, "r", encoding="utf-8") as f:
            cv_tex = f.read()
            
        with open(CL_TEMPLATE_PATH, "r", encoding="utf-8") as f:
            cl_tex = f.read()
            
        # Replace CV tags - rendered deterministically from plain LLM content
        cv_tex = cv_tex.replace("<<TITLE>>", escape_latex(tailored_data.get("title", "")))
        cv_tex = cv_tex.replace("<<TAILORED_PROFILE>>", escape_latex(tailored_data.get("profile_summary", "")))
        cv_tex = cv_tex.replace("<<TAILORED_SKILLS>>", render_skills(tailored_data.get("skills", [])))
        cv_tex = cv_tex.replace("<<TAILORED_EXPERIENCE>>", render_experience(tailored_data.get("experience", [])))
        cv_tex = cv_tex.replace("<<TAILORED_PROJECTS_SECTION>>", render_projects_section(tailored_data.get("projects", [])))

        # Replace CL tags - Sanitize plain text fields
        cl_tex = cl_tex.replace("<<COMPANY_NAME>>", escape_latex(tailored_data.get("company_name", "")))
        cl_tex = cl_tex.replace("<<COMPANY_LOCATION>>", escape_latex(tailored_data.get("company_location", "")))
        cl_tex = cl_tex.replace("<<JOB_TITLE>>", escape_latex(tailored_data.get("job_title", "")))

        body_sanitized = render_cover_letter_body(
            tailored_data.get("cover_letter_greeting", ""),
            tailored_data.get("cover_letter_paragraphs", [])
        )
        cl_tex = cl_tex.replace("<<LETTER_BODY>>", body_sanitized)

        # Write tailored tex files
        cv_out_path = tmp_dir / f"CV_{company_name_safe}.tex"
        cl_out_path = tmp_dir / f"Cover_Letter_{company_name_safe}.tex"
        
        with open(cv_out_path, "w", encoding="utf-8") as f:
            f.write(cv_tex)
            
        with open(cl_out_path, "w", encoding="utf-8") as f:
            f.write(cl_tex)
            
        # Compile twice for layout
        for tex_path in [cv_out_path, cl_out_path]:
            for _ in range(2):
                result = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", "-output-directory", str(tmp_dir), str(tex_path)],
                    cwd=str(tmp_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if result.returncode != 0:
                    log_file = tex_path.with_suffix(".log")
                    error_tail = ""
                    if log_file.exists():
                        with open(log_file, "r", encoding="utf-8") as lf:
                            lines = lf.readlines()
                            error_tail = "".join(lines[-30:])
                    raise RuntimeError(f"pdflatex compilation failed for {tex_path.name}.\nLog tail:\n{error_tail}")
                    
        return (cv_out_path.with_suffix(".pdf"), cl_out_path.with_suffix(".pdf"))
        
    except Exception as e:
        raise e
