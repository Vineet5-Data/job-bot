import os
import json
import re
import logging
from typing import Dict, Any
from google import genai
from openai import OpenAI
from src.config import (
    GEMINI_API_KEY,
    PRIMARY_GEMINI_MODEL,
    GEMINI_FALLBACK_MODELS,
    OPENROUTER_API_KEY,
    OPENROUTER_FALLBACK_MODELS,
    LLM_TIMEOUT_SECONDS,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a technical career advisor specializing in the German job market (internships, Werkstudent, master thesis, full-time).
Your task is to analyze the provided Job Description (JD) and a Master Candidate Profile, and select + write TAILORED CONTENT for a CV and Cover Letter.

You control CONTENT ONLY — which skills, experiences, and projects to include, and what to write about them. A separate renderer owns all LaTeX formatting and layout. Do NOT output any LaTeX commands (\\textbf, \\item, tabular, etc.) and do NOT escape special characters (%, &, $, _, #) yourself — write plain, natural text; the renderer handles formatting and escaping.

Rules:
1. Detect if the JD is in German or English; write the cover letter in that exact language.
1b. Title: write a short specialization headline (3-6 words) that completes "Master's Student in Data Science | ___" in the CV header, tailored to what this JD needs (e.g. "Applied Machine Learning & Predictive Modeling", "Graph Machine Learning & Self-supervised Learning", "Computer Vision & Autonomous Systems"). Return only the specialization part, not the "Master's Student..." prefix.
1c. Profile Summary: write a 3-4 sentence professional summary paragraph tailored to this JD: mention the university/program, 2-3 core technical strengths from the Master Profile most relevant to this specific JD, and close with what kind of role/opportunity is being sought, phrased to reflect this JD. The Master Profile's top-level "positioning" field describes the candidate's overall voice and brand (research-to-production, honest evaluation over hype) — let it inform tone, not literal wording. Plain prose, no LaTeX.
2. Skills: pick 6-8 relevant categories from the Master Profile (reuse, merge, or rename categories if it better fits the JD). For each, list only the relevant skill items as plain strings.
2a. ALWAYS include a "Language Skills" category, copied verbatim from the Master Profile, even when the JD sets a language bar the candidate does not meet. Omitting it reads as evasive to a recruiter and is worse than an honest lower level. Never upgrade a stated language level.
2b. Each skill/experience/project entry in the Master Profile has a "keywords" field listing its domain/technique tags. Match those keywords against the JD's requirements to decide which experiences, projects, and skills are most relevant — prefer concrete keyword overlap over generic guessing.
3. Experience: pick the most relevant experiences and write 3-4 impactful bullet points per experience, tailored to the JD, as plain strings.
3a. LENGTH BUDGET — the CV must fit on 2 pages and the cover letter on 1. You cannot see the page count, so respect these hard caps instead: every CV bullet <= 200 characters (one to two rendered lines); profile_summary <= 550 characters; each cover_letter_paragraph <= 700 characters. Cut the weakest detail to stay inside the cap — never run long. Verbosity costs a page and a recruiter's attention.
4. Projects: pick the 2-3 most relevant projects and write tailored bullet points as plain strings. Copy the "grade" field from the Master Profile verbatim if that project has one; if the Master Profile project has no grade field, set "grade" to null — do NOT invent a placeholder like "-" or "N/A".
5. Cover Letter: write one greeting line ("Dear Hiring Manager," / "Dear Hiring Team," in English, or "Sehr geehrte Damen und Herren," in German) and exactly 3 body paragraphs (Role alignment -> Technical contributions & project relevance -> Motivation & availability), as plain text. Do NOT include a closing sign-off, farewell, or the sender's name — that is added automatically.
5b. The final cover letter paragraph MUST state concrete availability, taken from the Master Profile's top-level "availability" field (start date and hours/week). German employers filter on this — never write a vague "I am available" without the dates.
6. job_title: copy the posting's own job title from the JD as literally as possible. Do NOT invent, merge, or embellish a title. If the JD gives no explicit title, use the shortest accurate description of the role, still without inventing seniority or extra domains.
7. NEVER paraphrase a number, metric, grade, or complexity claim. Copy quantitative statements from the Master Profile verbatim (e.g. write "from O(n^2) to O(n log n)", never restate it in words like "from quadratic to logarithmic"). Rewording maths introduces factual errors that a technical reviewer will catch.
8. Only claim a skill, tool, or domain that is actually evidenced in the Master Profile's experience, projects, or skills. Do not stretch an adjacent capability into a stronger claim (graph neural networks are NOT knowledge graphs; a tree index is NOT a graph). If the JD asks for something the profile cannot back, leave it out rather than implying it.

Output ONLY a JSON object matching this schema:
{
  "company_name": "string",
  "job_title": "string",
  "company_location": "string",
  "detected_language": "de | en",
  "title": "string (CV header specialization, e.g. 'Applied Machine Learning & Predictive Modeling')",
  "profile_summary": "string (3-4 sentence paragraph)",
  "skills": [
    {"category": "string", "items": ["string", "..."]}
  ],
  "experience": [
    {"role": "string", "duration": "string", "company": "string", "bullets": ["string", "..."]}
  ],
  "projects": [
    {"title": "string", "duration": "string", "grade": "string or null", "bullets": ["string", "..."]}
  ],
  "cover_letter_greeting": "string",
  "cover_letter_paragraphs": ["string", "string", "string"]
}
"""

def extract_json_from_response(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
        
    match = re.search(r'```(?:json)?(.*?)```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
            
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        try:
            return json.loads(text[start:end+1])
        except json.JSONDecodeError:
            pass
            
    raise ValueError("Could not parse JSON from LLM response")

def generate_tailored_content(job_description: str, master_profile: Dict[str, Any]) -> Dict[str, Any]:
    prompt = f"Master Profile:\n{json.dumps(master_profile, indent=2)}\n\nJob Description:\n{job_description}"
    
    if GEMINI_API_KEY:
        client = genai.Client(
            api_key=GEMINI_API_KEY,
            # SDK takes milliseconds here.
            http_options=genai.types.HttpOptions(timeout=LLM_TIMEOUT_SECONDS * 1000),
        )
        # PRIMARY_GEMINI_MODEL (settable via .env) goes first, then the rest of
        # the chain. dict.fromkeys dedupes while preserving order.
        models = list(dict.fromkeys([PRIMARY_GEMINI_MODEL] + GEMINI_FALLBACK_MODELS))
        for model in models:
            try:
                logger.info(f"Attempting generation with Gemini ({model})...")
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        response_mime_type="application/json"
                    )
                )
                result = extract_json_from_response(response.text)
                # Which model actually won the fallback race — used to tag the
                # output filenames so generations stay comparable.
                result["_model"] = model
                return result
            except Exception as e:
                logger.warning(f"Gemini model {model} failed: {e}")
        logger.warning("All Gemini models failed. Falling back to OpenRouter...")
    else:
        logger.warning("GEMINI_API_KEY not set. Falling back to OpenRouter...")

    if not OPENROUTER_API_KEY:
        raise ValueError("Neither GEMINI_API_KEY nor OPENROUTER_API_KEY are configured.")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        timeout=LLM_TIMEOUT_SECONDS,
    )

    for model in OPENROUTER_FALLBACK_MODELS:
        try:
            logger.info(f"Attempting generation with OpenRouter ({model})...")
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )
            result = extract_json_from_response(completion.choices[0].message.content)
            result["_model"] = model
            return result
        except Exception as e:
            logger.warning(f"OpenRouter model {model} failed: {e}")

    raise RuntimeError("All LLM providers failed to generate content.")
