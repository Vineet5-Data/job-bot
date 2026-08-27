import os
import json
import logging
from src.llm_engine import generate_tailored_content
from src.config import MASTER_PROFILE_PATH

logging.basicConfig(level=logging.DEBUG)

def test():
    with open(MASTER_PROFILE_PATH, "r") as f:
        profile = json.load(f)
        
    jd = "We are looking for a Data Science Intern with experience in Python, PyTorch, and Deep Learning."
    
    try:
        result = generate_tailored_content(jd, profile)
        print("SUCCESS:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test()
