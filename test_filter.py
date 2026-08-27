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
# description tier: needs TWO distinct strong terms, not one
assert ok(job("Werkstudent im Bereich Research & Development (m/w/d)",
              "Du arbeitest mit Python an Machine Learning Modellen."))
# one strong term alone must NOT be enough -- this is what let
# "Werkstudent Cyber and IT Security" through when any single hit counted
assert not ok(job("Werkstudent Cyber and IT Security Engineering (m/w/d)",
                  "Wir nutzen Python fuer Automatisierung der Security-Pipelines.")),     "single strong term in description must not pass"
# generic body words must never qualify a non-tech role
assert not ok(job("Werkstudent Recruiting (m/w/d)",
                  "Du arbeitest mit Daten und Analytics im HR Bereich.")),     "generic 'daten/analytics' in body must not pass"
# rescued by broadened role keywords
assert ok(job("Trainee Data Analytics (all genders)"))
assert ok(job("Graduate Programme Artificial Intelligence"))  # title-tier match

# --- must FAIL ---
assert not ok(job("Principal Data Scientist (m/f/d)")), "senior FT role"
assert not ok(job("Head of AI Engineering (f/m/x)")), "senior FT role"
assert not ok(job("Marketing & Operations Intern (m/f/d)")), "excluded domain"
assert not ok(job("Werkstudent Data Science", loc="Milan, Italy")), "outside Germany"
# student role whose description has no tech at all
assert not ok(job("Praktikum Operative Transportlogistik (m/w/d)",
                  "Unterstuetzung im Transport und der Lagerlogistik."))

# --- short-token regex boundaries: this guard must survive future edits ---
# The regex (ai|ml|cv|ki|rl|etl|rag) applies to the TITLE only. Without its
# \b anchors it matches inside ordinary words -- m-ai-ntenance,
# tr-ai-ning, e-m-ai-l -- which would pass very nearly everything.
assert ok(job("Werkstudent AI Entwicklung (m/w/d)")), "standalone AI must match"
assert not ok(job("Werkstudent Maintenance und Training (m/w/d)")), "ai matched inside maintenance/training"
assert not ok(job("Werkstudent E-Mail Marketing (m/w/d)")), "ai matched inside e-mail"

print("All filter checks passed.")
