from utils import *
from FeedbackLoop import *
import json
import sys

MAX_ITER = 5

PATHS = {
    "profile": "Files/Profiles/1EleanorVance.json", # LLM-generated profile with a fake user
    "email": "Files/example.eml", # Example email
    "kb": "Files/Knowledge Base/kb.json", # Knowledge base extracted from picture
}

def load_json(path, label):
    """
    Function for loading content from a json file.
    """
    print(f"Loading {label}...\n")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"{label} loaded successfully:")
        print(data)
        return data
    except FileNotFoundError:
        sys.exit(f"File not found: {path}")
    except json.JSONDecodeError as e:
        sys.exit(f"Invalid JSON in {path}: {e}")
    except Exception as e:
        sys.exit(f"Unexpected error loading {path}: {e}")


def load_text(path, label):
    """
    Function for loading content from a text file.
    """
    print(f"Loading {label}...\n")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = f.read()
        print(f"{label} loaded successfully.")
        return data
    except FileNotFoundError:
        sys.exit(f"File not found: {path}")
    except Exception as e:
        sys.exit(f"Unexpected error loading {path}: {e}")


if __name__ == "__main__":
    device = device_selection()

    # Load user profile and knowledge base
    profile_data = load_json(PATHS["profile"], "profile")
    kb_json = load_json(PATHS["kb"], "knowledge base")

    # Load an email
    email = load_text(PATHS["email"], "email")

    print("\nPerforming feedback loop on existing email...\n")

    new_email = FeedbackLoop(MAX_ITER, device, email, profile_data, kb_json)

    print("\nFinal email output:\n")
    print(new_email)