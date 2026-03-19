from utils import *
from EmailAssessmentPrompts import *
from FeedbackLoopPrompts import *

def add_section(sections, title, score, feedback):
    section = f"{title}:\nScore: {score}"
    section += f"\nFeedback: {feedback}"
    sections.append(section)

def convert_phishing_score(assessment):
    if not isinstance(assessment, str):
        print("Parsing error:")
        print(assessment)
        return -1
    elif "phishing" not in assessment.lower():
        return 0
    else:
        return 1

def convert_sophistication_score(assessment):
    if not isinstance(assessment, str):
        print("Parsing error:")
        print(assessment)
        return -1
    elif "insufficient" in assessment.lower() or "not" in assessment.lower():
        return 0
    else:
        return 1

def get_phishing_label_and_feedback(response):
    assessment, feedback = parse_phishing_assessment(response)
    label = convert_phishing_score(assessment)
    return label, feedback


def get_sophistication_label_and_feedback(response):
    assessment, feedback = parse_binary_sophistication(response)
    label = convert_sophistication_score(assessment)
    return label, feedback

def FeedbackLoop(MAX_ITER, device, email, profile_data, kb_json):
    """
    Feedback Loop that assesses the email on multiple dimensions, and rewrites it when needed.
    Returns final email.
    """
    pipe = phishing_pipeline(device) # Create pipeline

    # Feedback loop with multiple prompts
    for iteration in range(1, MAX_ITER+1):
        print(f"\n... Iteration {iteration} of loop ...")

        phishing_pass_total = False
        sophistication_pass = False
    
        # ---- Email Persuasion ----
        print("\nExtracting persuasion principles...")
        persuasion_principles = evaluate_persuasion(email, pipe)
        print(persuasion_principles)

        # ---- Phishing Detection ----
        phishing_label, phishing_feedback = get_phishing_label_and_feedback(
            evaluate_phishing(email, pipe)
        )

        persuasion_label, persuasion_feedback = get_phishing_label_and_feedback(
            evaluate_phishing_persuasion(email, persuasion_principles, pipe)
        )

        if -1 in (phishing_label, persuasion_label):
            print("\nIssue with parsing phishing criterion. Loop ending early...")
            break
        else:
            final_label = int(phishing_label or persuasion_label)

            if final_label == 0:
                combined_phishing_feedback = "None"
            else:
                sections = []

                # Add feedback to the list
                if phishing_label == 1:
                    add_section(sections, "Phishing Characteristics", phishing_label, phishing_feedback)
                if persuasion_label == 1:
                    add_section(sections, "Phishing Persuasion", persuasion_label, persuasion_feedback)

                combined_phishing_feedback = "\n\n".join(sections)

        # Determine whether the email passes the phishing assessment (0=benign, 1=phishing)
        phishing_pass_total = (final_label == 0)

        if phishing_pass_total:
            print("\nEmail is considered benign by critic.")
        else:
            print("\nEmail is considered phishing by critic. It failed on:\n")
            print(combined_phishing_feedback)

        # ---- Email Sophistication ----
        etiquette_score, etiquette_feedback = get_sophistication_label_and_feedback(
            evaluate_etiquette(email, pipe)
        )

        content_score, content_feedback = get_sophistication_label_and_feedback(
            evaluate_content(email, pipe)
        )

        personalization_score, personalization_feedback = get_sophistication_label_and_feedback(
            evaluate_personalization(email, profile_data, pipe)
        )

        personalization_persuasion_score, personalization_persuasion_feedback = get_sophistication_label_and_feedback(
            evaluate_personalization_persuasion(email, persuasion_principles, kb_json, profile_data, pipe)
        )

        scores = [etiquette_score, content_score, personalization_score, personalization_persuasion_score
        ]

        if -1 in scores:
            print("\nIssue with parsing sophistication criterion. Loop ending early...")
            break

        # Determine whether the email passes the sophistication assessment (0=not sophisticated, 1=sophisticated)
        sophistication_label = int(all(score == 1 for score in scores))
        sophistication_pass = (sophistication_label == 1)

        if sophistication_pass:
            print("\nEmail is considered sophisticated by critic.")
            combined_sophistication_feedback = "None"
        else:
            print("\nEmail is not considered sophisticated by critic. It failed on:\n")

            sections = []

            # add feedback to the list
            if etiquette_score == 0:
                add_section(sections, "Email Etiquette", etiquette_score, etiquette_feedback)
            if content_score == 0:
                add_section(sections, "Email Content", content_score, content_feedback)
            if personalization_score == 0:
                add_section(sections, "General Personalization", personalization_score, personalization_feedback)
            if personalization_persuasion_score == 0:
                add_section(sections, "Personalization of Persuasion Principles", personalization_persuasion_score, personalization_persuasion_feedback)

            combined_sophistication_feedback = "\n\n".join(sections)
            print(combined_sophistication_feedback)

        if phishing_pass_total and sophistication_pass:
            print("\nEmail is considered both benign and sophisticated by critic. Ending loop...")
            return email

        # Generate actionable instructions for rewriting the email
        print("\nGenerating instructions...")
        instructions_raw = summarize_feedback(email, combined_phishing_feedback, combined_sophistication_feedback, kb_json, profile_data, pipe)
        # print(instructions_raw)
        instructions_formatted = parse_instructions_to_text(instructions_raw)
        if (instructions_formatted == None):
            print("\nIssue with parsing instructions. Loop ending early...")
            break
        print(f"\nInstructions based on feedback: {instructions_formatted}")

        # Rewrite email based on feedback
        print("\nRewriting email based on given feedback...\n")
        new_email = rewrite_email(email, instructions_formatted, kb_json, profile_data, pipe)
        email, justification = parse_rewritten_email(new_email)
        if (email == None):
            print("\nIssue with parsing rewritten email. Loop ending early...")
            break

        print(email)
        print("\nJustification for the changes that were made:")
        print(justification)

    print("\nLoop ended.\n")
    cleanup_pipeline(pipe)
    return email