import json

def rewrite_email(email, instructions, kb, profile_data, pipe):
    combined = {
        "profile": profile_data,
        "knowledge": kb
    }

    messages = [
        {
            "role": "system",
            "content": [
                {"type": "text", "text": f"""
                    You are a professional email editor. Your job is to carefully rewrite emails based on reviewer feedback, ensuring that all instructions are followed precisely.
                    Original draft: {email} \n
                    Instructions for rewriting email: {instructions} \n
                    Rewrite the email according to the given instructions.

                    Do not make any changes that were not suggested in the instructions. Track all the changes you make.

                    Respond strictly in valid JSON with the following format: """+
                    """{"Email": *Rewritten email*,  "Justification": *an explanation of what was changed*}"""

                    +"""Do NOT use any curly braces { }, square brackets [ ], or quotes within the JSON strings."""
                 }
            ]
        },
        {
            "role": "user",
            "content": json.dumps(combined, indent=2)
        }

    ]
    output = pipe(text_inputs=messages, max_new_tokens=2000)

    return output[0]["generated_text"][-1]["content"]

def summarize_feedback(email, likelihood_feedback, sophistication_feedback, kb, profile_data, pipe):
    combined = {
        "profile": profile_data,
        "knowledge base": kb
    }

    messages = [
        {
            "role": "system",
            "content": [
                {"type": "text", "text": f"""
                    You are a professional email improvement consultant. Your task is to turn reviewer feedback into a concise, actionable set of improvement instructions for an existing email.
                    
                    Context:
                    - Original email draft: {email} \n
                    - Reviewer opinion on phishing likelihood: {likelihood_feedback} \n
                    - Reviewer opinion on email sophistication: {sophistication_feedback} \n

                    Goal: Reducing phishing likelihood while increasing email sophistication.

                    Based only on the provided reviews, produce 8–10 high-impact improvement instructions. 
                    These instructions should describe both small refinements and large structural changes, such as reorganizing sections, adding missing elements, removing suspicious phrasing, adjusting the overall tone, etc.

                    Each instruction must be:
                    - Based on the reviewer feedback
                    - Actionable (e.g., replace X with Y)
                    - Specific
                    - Concise (1-2 sentences) 
                    - Distinct (avoid multiple edits covering the same issue)

                    Respond strictly in valid JSON with the following format:"""
                     + 
                    """{"Improvement instructions": ["Instruction 1", "Instruction 2", "Instruction 3", ...]}"""
                    + """Do NOT use any curly braces { }, square brackets [ ], or quotes within the JSON strings."""
                 }
            ]
        },
        {
            "role": "user",
            "content": json.dumps(combined, indent=2)
        }

    ]
    output = pipe(text_inputs=messages, max_new_tokens=2000)

    return output[0]["generated_text"][-1]["content"]
