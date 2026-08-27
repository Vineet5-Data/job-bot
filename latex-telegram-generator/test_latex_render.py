"""Self-check for src/compiler.py's LaTeX renderers. Run: python test_latex_render.py"""
from src.compiler import render_skills, render_experience, render_projects, render_cover_letter_body

# Project with no grade must render an EMPTY grade cell, not a "-" placeholder.
no_grade_tex = render_projects([{
    "title": "RL for Autonomous Driving", "duration": "03/2026 - 06/2026",
    "grade": None, "bullets": ["Built a GNN world model."]
}])
assert "Grade" not in no_grade_tex, "missing-grade project should not print any Grade label"
last_cell = no_grade_tex.split("&")[-1].split("\\\\")[0]
assert last_cell.strip() == "", f"missing-grade project's grade cell should be empty, got {last_cell!r}"

# Project with a grade must show it.
graded_tex = render_projects([{
    "title": "Bird Classification", "duration": "04/2025 - 09/2025",
    "grade": "1.0", "bullets": ["Trained a CNN ensemble."]
}])
assert "Grade: 1.0" in graded_tex

# Skills: Language Skills must land in the right-hand column (last minipage).
skills_tex = render_skills([
    {"category": "Programming Languages", "items": ["Python", "SQL"]},
    {"category": "Language Skills", "items": ["English (C1)"]},
])
left_col, right_col = skills_tex.split("\\hfill")
assert "Language Skills" not in left_col
assert "Language Skills" in right_col

# Escaping: LLM content is plain text and may contain raw LaTeX-special chars.
exp_tex = render_experience([{
    "role": "Data Analyst", "duration": "2023", "company": "R&D Labs",
    "bullets": ["Improved accuracy by 15% using A&B testing."]
}])
assert "R\\&D Labs" in exp_tex
assert "15\\% using A\\&B" in exp_tex
assert "\\%" in exp_tex and "15%" not in exp_tex  # raw % must not survive unescaped

# Cover letter body: greeting + paragraphs joined, escaped, no LaTeX from the model needed.
cl_tex = render_cover_letter_body("Dear Hiring Manager,", ["First para.", "Second para with 50% focus."])
assert cl_tex.startswith("Dear Hiring Manager,")
assert "50\\%" in cl_tex
assert cl_tex.count("\n\n") == 2  # greeting + 2 paragraphs => 2 blank-line separators

print("All render checks passed.")
