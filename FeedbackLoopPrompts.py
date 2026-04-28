from transformers import pipeline
import torch
import json
from utils import *

def summarize_feedback(email, phishing_feedback, sophistication_feedback, kb, profile_data, pipe):
    combined = {
        "profile": profile_data,
        "knowledge base": kb,
        "original email": email,
        "likelihood feedback": phishing_feedback,
        "sophistication feedback": sophistication_feedback

    }

    system_instructions = f"""
                    You are a professional email improvement consultant. Your task is to turn reviewer feedback into a concise, actionable set of improvement instructions for an existing email.
                    
                    Context:
                    - Original email draft: {email} 
                    - Reviewer feedback on phishing features: {phishing_feedback} 
                    - Reviewer feedback on email sophistication: {sophistication_feedback} 

                    Goal: Reduce features that make the email appear like phishing while improving email sophistication (etiquette, content and personalization).

                    Task: Based ONLY on the provided feedback, produce 8–10 high-impact improvement instructions. 
                    Include both small refinements and larger structural improvements (e.g., reorganizing sections, adding missing elements, removing suspicious phrasing, adjusting tone).

                    Each instruction must:
                    - Be grounded in the reviewer feedback
                    - Be specific and actionable (e.g., replace X with Y)
                    - Be concise (1-2 sentences) 
                    - Address a distinct issue (no overlap between instructions)

                    Respond STRICTLY in valid JSON only, in this exact format (no extra text before or after):
                    {{"Improvement instructions": ["Instruction 1", "Instruction 2", "Instruction 3", ...]}}
                    Rules:
                    - Output must be valid JSON
                    - Output must contain 8–10 instructions.
                    - Do NOT use bullet points or markdown.
                    - Do NOT add any text outside the JSON."""

    messages = [
        {
        "role": "user",
        "content": system_instructions + "\n\n" + json.dumps(combined, indent=2)
        }
    ]
    output = pipe(text_inputs=messages, max_new_tokens=3000)

    return output[0]["generated_text"][-1]["content"]

def rewrite_email(email, instructions, profile_data, pipe):
    combined = {
        "profile": profile_data,
        "original email": email,
        "instructions": instructions,
    }

    system_instructions = f"""
                    You are a professional email editor. Your task is to rewrite an email based strictly on provided improvement instructions.
                    
                    Context:
                    - Original email: {email} 
                    - Instructions: {instructions} 
                    
                    Task: Rewrite the email by applying ALL instructions.

                    Guidelines:
                    - Follow the instructions precisely
                    - Do not introduce unrelated changes
                    - Ensure the final email reads naturally and professionally

                    Change tracking: For each change, briefly explain what was modified and why, referencing the instruction when possible.

                    Respond STRICTLY in valid JSON only, in this exact format (no extra text before or after):
                    {{"Email": <Rewritten email>, "Justification": ["change 1 explanation", "change 2 explanation", ...]}}
                    Rules:
                    - Output must be valid JSON
                    - do NOT use bullet points, markdown, line breaks within the justification.
                    - Do NOT add any text outside the JSON."""

    messages = [
        {
        "role": "user",
        "content": system_instructions + "\n\n" + json.dumps(combined, indent=2)
        }
    ]
    
    output = pipe(text_inputs=messages, max_new_tokens=3000)

    return output[0]["generated_text"][-1]["content"]