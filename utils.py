import torch
import re
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import gc
import json5

# -------------------------------------------------------------
# Device selection
# -------------------------------------------------------------

def device_selection():
    if torch.cuda.is_available():
        return "cuda:0"
    elif torch.mps.is_available():
        return "mps"
    else:
        return "cpu"

def phishing_pipeline(device="cuda"):
    torch.backends.cuda.enable_flash_sdp(True)
    torch.backends.cuda.enable_mem_efficient_sdp(True)
    torch.backends.cuda.enable_math_sdp(True)

    MODEL_ID = "google/gemma-3-4b-it"
    #MODEL_ID = "meta-llama/Llama-3.2-3B-Instruct"

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"  

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        device_map=device,
        torch_dtype=torch.bfloat16
    )

    model.config.pad_token_id = tokenizer.pad_token_id
    model.config.eos_token_id = tokenizer.eos_token_id

    model.config.use_cache = True
    model.eval()
    torch.set_grad_enabled(False)

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        batch_size=1
    )
    return pipe


def cleanup_pipeline(pipe):
    del pipe
    gc.collect()
    torch.cuda.empty_cache()

# -------------------------------------------------------------
# Parsers
# -------------------------------------------------------------

def parse_binary_sophistication(text):
    """
    Parse AI-generated JSON of the form:
    { "Assessment": "Insufficient" or "Sufficient", "Justification": "<text>" }

    Returns:
        (assessment, justification)  # on success
        (-1, "Parsing error")        # on failure
    """
    # Normalize quotes
    text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'").strip()

    # Try json5 first
    try:
        data = json5.loads(text)
        assessment = data.get("Assessment")
        justification = str(data.get("Justification", "")).strip()
        if assessment not in ["Sufficient", "Insufficient", "Not sufficient"]:
            return -1, "Parsing error"
        return assessment, justification
    except Exception:
        pass  # fallback to regex if JSON parsing fails

    # Extract Assessment
    assessment_match = re.search(r'"Assessment"\s*:\s*"([^"]+)"', text)
    if not assessment_match:
        return -1, "Parsing error"
    assessment = assessment_match.group(1).strip()
    if assessment not in ["Sufficient", "Insufficient", "Not sufficient"]:
        return -1, "Parsing error"

    # Extract Justification (everything after "Justification":)
    justification_match = re.search(r'"Justification"\s*:\s*"?(.*)', text, re.DOTALL)
    if not justification_match:
        return -1, "Parsing error"
    justification = justification_match.group(1).strip()

    # Remove trailing braces or quotes if present
    justification = re.sub(r'["}]\s*$', '', justification).strip()

    return assessment, justification


def parse_phishing_assessment(text):
    """
    Parse AI-generated JSON of the form:
    { "Assessment": "Phishing Email" or "Benign Email", "Justification": "<text>" }

    Returns:
        (assessment, justification)  # on success
        (-1, "Parsing error")        # on failure
    """
    # Normalize quotes
    text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'").strip()

    # Try json5 first
    try:
        data = json5.loads(text)
        assessment = data.get("Assessment")
        justification = str(data.get("Justification", "")).strip()
        if assessment not in ["Phishing Email", "Benign Email"]:
            return -1, "Parsing error"
        return assessment, justification
    except Exception:
        pass  # fallback to regex if JSON parsing fails

    # Regex fallback: extract Assessment
    assessment_match = re.search(r'"Assessment"\s*:\s*"([^"]+)"', text)
    if not assessment_match:
        return -1, "Parsing error"
    assessment = assessment_match.group(1).strip()
    if assessment not in ["Phishing Email", "Benign Email"]:
        return -1, "Parsing error"

    # Regex fallback: extract Justification (everything after "Justification":)
    justification_match = re.search(r'"Justification"\s*:\s*"?(.*)', text, re.DOTALL)
    if not justification_match:
        return -1, "Parsing error"
    justification = justification_match.group(1).strip()

    # Remove trailing braces or quotes if present
    justification = re.sub(r'["}]\s*$', '', justification).strip()

    return assessment, justification

def parse_rewritten_email(text):
    """
    Parse a model's JSON output of the form:
    {"Email": <rewritten email>, "Justification": <reasoning>}

    Returns:
        (email_text, justification) or ("Parsing error", "Parsing error") on failure.
    """

    # Pre-cleaning
    text = text.strip()
    text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    
    # Remove Markdown fences (```json ... ```), BOMs, zero-width chars
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE)
    text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)

    # Handle multiple JSON blocks
    all_blocks = re.findall(r'\{[\s\S]*?\}', text)
    data = {}
    if all_blocks:
        for block in all_blocks:
            block = block.strip()
            # Fix unbalanced braces
            if block.count("{") > block.count("}"):
                block += "}" * (block.count("{") - block.count("}"))
            elif block.count("}") > block.count("{"):
                block = "{" * (block.count("}") - block.count("{")) + block

            # Fix missing comma between fields like Email and Justification
            block = re.sub(
                r'("Email"\s*:\s*[^,]+)\s*("Justification")',
                r'\1, \2',
                block
            )

            try:
                obj = json5.loads(block)
                data.update(obj)
            except Exception:
                continue  # skip invalid block

    if not data:
        return "Parsing error", "Parsing error"

    # Extract fields
    email = str(data.get("Email", "")).strip()
    justification = str(data.get("Justification", "")).strip()

    if not email:
        return "Parsing error", "Parsing error"
    if not justification:
        justification = "Parsing error"

    return email, justification


def parse_instructions_to_text(model_output):
    """
    Parses a model's JSON output containing 'Improvement instructions'
    and returns a single formatted text string:
    '1. Instruction 1. 2. Instruction 2. ...'
    """
    try:
        # Pre-cleaning
        text = model_output.strip()
        text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
        text = re.sub(r"[\u200B-\u200D\uFEFF]", "", text)  # remove zero-width/BOM chars

        # Extract JSON block
        start = text.find("{")
        end = text.rfind("}")
        if start == -1:
            return model_output  # fallback to raw output

        if end == -1 or end < start:
            json_str = text[start:] + "}"
        else:
            json_str = text[start:end+1]

        try:
            data = json5.loads(json_str)
        except Exception:
            return model_output  # fallback to raw output

        # Extract instructions
        instructions = (
            data.get("Improvement instructions")
            or data.get("ImprovementInstructions")
            or []
        )

        if not isinstance(instructions, list) or not all(isinstance(i, str) for i in instructions):
            return model_output  # invalid format, return original

        # Format as numbered text
        numbered_text = " ".join(f"{i+1}. {instr.strip()}" for i, instr in enumerate(instructions))
        return numbered_text

    except Exception:
        return model_output # fallback to raw output