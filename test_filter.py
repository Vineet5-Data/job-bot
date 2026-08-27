"""Self-check for src/main.py's is_relevant_job. Run: python test_filter.py

Cases are real titles taken from GitHub Actions logs (grep "Skipped irrelevant job").
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from main import is_relevant_job as ok

def job(title, desc="", loc="Dortmund, Germany"):
    return {"title": title, "description": desc, "location": loc}

# --- must PASS ---
assert ok(job("Werkstudent Data Science (m/w/d)"))
assert ok(job("Masterarbeit Machine Learning"))
assert ok(job("Praktikum Künstliche Intelligenz"))
# rescued by description matching: student role, tech only in the body
assert ok(job("Werkstudent im Bereich Research & Development (m/w/d)",
              "Du arbeitest mit Python an Machine Learning Modellen."))
# rescued by broadened role keywords
assert ok(job("Trainee Data Analytics (all genders)"))
assert ok(job("Graduate Programme Artificial Intelligence", "AI und Data Science"))

# --- must FAIL ---
assert not ok(job("Principal Data Scientist (m/f/d)")), "senior FT role"
assert not ok(job("Head of AI Engineering (f/m/x)")), "senior FT role"
assert not ok(job("Marketing & Operations Intern (m/f/d)")), "excluded domain"
assert not ok(job("Werkstudent Data Science", loc="Milan, Italy")), "outside Germany"
# student role whose description has no tech at all
assert not ok(job("Praktikum Operative Transportlogistik (m/w/d)",
                  "Unterstuetzung im Transport und der Lagerlogistik."))

# --- regex boundaries: the \b guard must survive future edits ---
# Without \b these match "ai"/"ml" inside ordinary words across a 4000-char body.
assert not ok(job("Werkstudent Fertigung", "Wartung, Training und E-Mail Support.")), \
    "word-boundary regression: 'ai'/'ml' matched inside maintenance/training/email"
assert ok(job("Werkstudent Entwicklung", "Erfahrung mit AI und ML erwuenscht."))

print("All filter checks passed.")
