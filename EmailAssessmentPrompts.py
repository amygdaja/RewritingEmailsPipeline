import json

# -------------------------------------------------------------
# Persuasion
# -------------------------------------------------------------

def evaluate_persuasion(email, pipe):
    combined = {
        "email": email
    }

    messages = [
        {
            "role": "system",
            "content": [
                {"type": "text", "text": f"""
                    You are an expert in persuasion psychology. Your task is to identify the persuasion principles used in the attached email.
                    
                    Persuasion principles:
                    - Reciprocity: The email offers something and asks for a favor, click or confirmation in return.
                    - Scarcity: The email creates urgency by implying limited time, quantity or opportunity.
                    - Authority: The email claims or displays credibility through a recognized institution, title or role.
                    - Commitment/Consistency: The email references prior behavior of choices to push further action.
                    - Liking: The email uses familiarity, flattery or personalization to build trust or rapport.
                    - Social proof: The email references other people's participation or endorsement.
                 
                    Mention how the persuasion principle is used in the explanation. If a principle is not present in the email, put "Not present" in the explanation.
                    """
                    
                    + "Respond STRICTLY in valid JSON only, in this exact format (no extra text before or after):" +
                    """
                    {
                        "Reciprocity": {"Explanation": "explanation"},
                        "Scarcity": {"Explanation": "explanation"},
                        "Authority": {"Explanation": "explanation"},
                        "Commitment/Consistency": {"Explanation": "explanation"},
                        "Liking": {"Explanation": "explanation"},
                        "Social proof": {"Explanation": "explanation"}
                    } """
                    + """Do *NOT* output anything other than this JSON."""
                 }
            ]
        },
        {
            "role": "user",
            "content": json.dumps(combined, indent=2)
        }

    ]
    output = pipe(text_inputs=messages, max_new_tokens=400)

    return output[0]["generated_text"][-1]["content"]


# -------------------------------------------------------------
# Detection
# -------------------------------------------------------------

def evaluate_phishing(email, pipe):
    combined = {
        "email": email
    }

    messages = [
        {
            "role": "system",
            "content": [
                {"type": "text", "text": """
                    You are an email security analyst. Your task is to determine whether an email is phishing or benign.  
                 
                    Use the indicators as defined below as guidance in your assessment. Do NOT assume missing information.
                 
                    Phishing indicators:
                    - Sender inconsistency: The sender’s name, email address, or domain is inconsistent with the claimed source.
                    - Lack of personalization: The email is generic and not personalized to the recipient.
                    - Suspicious call to action: The email urges the recipient to perform an unusual or suspicious action (e.g., clicking on a link or opening an attachment).
                    - Sensitive information request: The email asks for sensitive information (e.g., credentials, financial data or login information).
                    - Link legitimacy: If a link is present, the link appears illegitimate or misleading.
                    - Attachment legitimacy: If an attachment is present, the attachment does not have a benign-looking file extension (e.g., .exe, .zip, .html).
                    - Tone: The tone of the email is inappropriate for the given context and request (e.g., overly urgent, formal or informal).
                    - Spelling and grammar: The email contains noticeable spelling or grammar mistakes.
                 
                    Return exactly one of the following labels:
                    - "Phishing Email"
                    - "Benign Email"
                    Show your reasoning in the justification.

                    Respond STRICTLY in valid JSON only, in this exact format (no extra text before or after):
                    {"Assessment": "<Phishing Email or Benign Email>", "Justification": "<Justification on the assessment>"}
                    Rules:
                    - The justification must be a maximum of 5 sentences.
                    - do NOT use bullet points, markdown, line breaks, or quotation marks within the justification.
                    - Do NOT add any text outside the JSON."""
                 }
            ]
        },
        {
            "role": "user",
            "content": json.dumps(combined, indent=2)
        }

    ]
    output = pipe(text_inputs=messages, max_new_tokens=300)

    return output[0]["generated_text"][-1]["content"]


def evaluate_phishing_persuasion(email, persuasion_output, pipe):
    combined = {
        "email": email,
        "persuasion_principles": persuasion_output
    }

    messages = [
        {
            "role": "system",
            "content": [
                {"type": "text", "text": """
                    You are an email security analyst. Your task is to determine whether an email is phishing or benign based on the persuasion principles that are used within the email.
                    An email is considered phishing if the persuasion principles used in the email are inconsistent with the sender’s claimed purpose and appear manipulative, deceptive, or inappropriate for legitimate communication.

                    Task:
                    1. Review the attached email.
                    2. Review the attached list of persuasion principles that have already been identified. Do NOT identify any additional persuasion principles.
                    3. Examine the sender’s claimed purpose as stated or implied in the email.
                    4. Assess whether the identified persuasion principles are appropriate for a legitimate email with that purpose.

                    Return exactly one of the following labels:
                    - "Phishing Email"
                    - "Benign Email"
                    Show your reasoning in the justification.
                    
                    Respond STRICTLY in valid JSON only, in this exact format (no extra text before or after):
                    {"Assessment": "<Phishing Email or Benign Email>", "Justification": "<Justification on the assessment>"}
                    Rules:
                    - The justification must be a maximum of 5 sentences.
                    - do NOT use bullet points, markdown, line breaks, or quotation marks within the justification.
                    - Do NOT add any text outside the JSON."""
                 }
            ]
        },
        {
            "role": "user",
            "content": json.dumps(combined, indent=2)
        }

    ]
    output = pipe(text_inputs=messages, max_new_tokens=300)

    return output[0]["generated_text"][-1]["content"]


# -------------------------------------------------------------
# Sophistication
# -------------------------------------------------------------

def evaluate_etiquette(email, pipe):
    combined = {
        "email": email
    }

    messages = [
        {
            "role": "system",
            "content": [
                {"type": "text", "text": """
                    You are a professional email communication analyst. Your task is to evaluate the etiquette of an email, which refers to the structure and writing quality of the email.
                    
                    Evaluate the attached email based on the indicators below. Do NOT assume missing information.
                 
                    Etiquette indicators:
                    - Subject line: The subject line is less than 50 characters.
                    - Salutation: The email includes a salutation with the name of the recipient.
                    - Coherent structure: The email follows a coherent structure (greeting → introduction → body paragraph(s) → closing).
                    - Paragraphs: The email is structured with clear paragraphs (one idea per paragraph) and one blank line between paragraphs.
                    - Brevity: The email is brief and to the point.
                    - Spelling and grammar: The email does not contain spelling or grammar mistakes.
                    - Punctuation: The email does not use excessive punctuation.
                    - Closure phrases: The email includes appropriate closure phrases and a signature.
                 
                    An email is Sufficient if its structure and writing quality would be considered acceptable in a typical workplace. Otherwise, it is Insufficient.
                    
                    Return exactly one of the following labels:
                    - "Sufficient"
                    - "Insufficient"
                    Show your reasoning in the justification.

                    Respond STRICTLY in valid JSON only, in this exact format (no extra text before or after):
                    {"Assessment": "<Sufficient or Insufficient>", "Justification": "<Justification on the assessment>"}
                    Rules:
                    - The justification must be a maximum of 5 sentences.
                    - do NOT use bullet points, markdown, line breaks, or quotation marks within the justification.
                    - Do NOT add any text outside the JSON."""
                 }
            ]
        },
        {
            "role": "user",
            "content": json.dumps(combined, indent=2)
        }

    ]
    output = pipe(text_inputs=messages, max_new_tokens=300)

    return output[0]["generated_text"][-1]["content"]

def evaluate_content(email, pipe):
    combined = {
        "email": email
    }

    messages = [
        {
            "role": "system",
            "content": [
                {"type": "text", "text": """
                    You are a professional email communication analyst. Your task is to evaluate the content of an email, which refers to the accuracy, relevance and clarity of the email.
                    
                    Evaluate the attached email based on the indicators below. Do NOT assume missing information.
                 
                    Content indicators:
                    - Single-topic message: The email focuses on a single topic.
                    - Subject line: The subject line accurately reflects the content and purpose of the email.
                    - Sender context: The sender provides relevant information about themselves (e.g., their role, organization, or reason for contacting the recipient).
                    - Specific details: The email includes realistic and specific details (e.g., company name, dates or projects).
                    - Amount of information: The email provides enough information for the recipient to understand and act on the message.
                    - Consistency: The email does not contain conflicting or contradictory details.
                    - Tone appropriateness: The tone of the email is consistent and appropriate for the sender and context.
                                 
                   An email is Sufficient if a recipient could clearly understand the message without needing additional clarification. Otherwise, it is Insufficient.
                                 
                   Return exactly one of the following labels:
                    - "Sufficient"
                    - "Insufficient"
                    Show your reasoning in the justification.

                    Respond STRICTLY in valid JSON only, in this exact format (no extra text before or after):
                    {"Assessment": "<Sufficient or Insufficient>", "Justification": "<Justification on the assessment>"}
                    Rules:
                    - The justification must be a maximum of 5 sentences.
                    - do NOT use bullet points, markdown, line breaks, or quotation marks within the justification.
                    - Do NOT add any text outside the JSON."""
                 }
            ]
        },
        {
            "role": "user",
            "content": json.dumps(combined, indent=2)
        }

    ]
    output = pipe(text_inputs=messages, max_new_tokens=300)

    return output[0]["generated_text"][-1]["content"]


def evaluate_personalization(email, profile_data, pipe):

    combined = {
        "email": email,
        "user_profile": profile_data
    }

    messages = [
        {
            "role": "system",
            "content": [
                {"type": "text", "text": """
                    You are a professional email communication analyst. Your task is to evaluate how appropriately personalized an email is, according to the attached user profile. 
                    
                    Task:
                    1. Review the attached email.
                    2. Review the attached user profile.
                    3. Based on the list of personalization indicators below, evaluate how well the email is personalized for the recipient in the user profile. Do NOT assume missing information.
               
                    Personalization indicators:
                    - Alignment with profile: All personal information in the email accurately matches the given profile (e.g., name, workplace, role).
                    - Greeting: The email includes a personalized greeting using the correct name of the recipient.
                    - Relevance to role: The message is appropriate for the recipient’s job, interests, or responsibilities.
                    - Logical connection: The sender’s reason for contact aligns logically with their role and the recipient’s context.
                    - Appropriate personalization level: The amount of personal information included is appropriate for the purpose of the email.
                                
                    An email is Sufficient if it demonstrates appropriate personalization for the recipient in the attached profile. Otherwise, it is Insufficient.
                                
                    Return exactly one of the following labels:
                    - "Sufficient"
                    - "Insufficient"
                    Show your reasoning in the justification.

                    Respond STRICTLY in valid JSON only, in this exact format (no extra text before or after):
                    {"Assessment": "<Sufficient or Insufficient>", "Justification": "<Justification on the assessment>"}
                    Rules:
                    - The justification must be a maximum of 5 sentences.
                    - do NOT use bullet points, markdown, line breaks, or quotation marks within the justification.
                    - Do NOT add any text outside the JSON."""
                 }
            ]
        },
        {
            "role": "user",
            "content": json.dumps(combined, indent=2)
        }

    ]
    output = pipe(text_inputs=messages, max_new_tokens=300)

    return output[0]["generated_text"][-1]["content"]


def evaluate_personalization_persuasion(email, persuasion_principles, kb, profile_data, pipe):

    combined = {
        "email": email,
        "user_profile": profile_data,
        "knowledge_base": kb,
        "persuasion_principles": persuasion_principles
    }

    messages = [
        {
            "role": "system",
            "content": [
                {"type": "text", "text": """
                    You are an expert in persuasion psychology. Your task is to determine whether the persuasion techniques used in an email are appropriate for the attached recipient's profile.

                    Task:
                    1. Review the attached email.
                    2. Review the attached list of persuasion principles that have already been identified. Do NOT identify any additional persuasion principles.
                    3. Review the attached knowledge base which contains information on what persuasion techniques are effective for specific recipients (e.g., based on job role and nationality).
                    4. Review the attached profile that belongs to the recipient.
                    5. Assess the alignment of the chosen persuasion principles with the knowledge base's recommendations.
                 
                    An email is Sufficient if the identified persuasion techniques are appropriate for the recipient profile and context. Otherwise, it is Insufficient.

                    Return exactly one of the following labels:
                    - "Sufficient"
                    - "Insufficient"
                    Show your reasoning in the justification.

                    Respond STRICTLY in valid JSON only, in this exact format (no extra text before or after):
                    {"Assessment": "<Sufficient or Insufficient>", "Justification": "<Justification on the assessment>"}
                    Rules:
                    - The justification must be a maximum of 5 sentences.
                    - do NOT use bullet points, markdown, line breaks, or quotation marks within the justification.
                    - Do NOT add any text outside the JSON."""
                 }
            ]
        },
        {
            "role": "user",
            "content": json.dumps(combined, indent=2)
        }

    ]
    output = pipe(text_inputs=messages, max_new_tokens=300)

    return output[0]["generated_text"][-1]["content"]