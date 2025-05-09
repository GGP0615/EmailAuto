from openai import OpenAI
from config import OPENAI_API_KEY
from resume_parser import ResumeParser
import os
import re

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.resume_parser = ResumeParser(os.path.join(os.path.dirname(__file__), "resume.pdf"))

    def generate_ai_message(self, job_desc, recipient_info):
        # Use recipient's name if available, else fallback to 'Hiring Manager'
        recipient_name = recipient_info.get('name') or 'Hiring Manager'
        if not recipient_name or recipient_name.strip().lower() in ['','n/a','none','null']:
            recipient_name = 'Hiring Manager'

        # Get relevant experience and skills from resume
        relevant_experience = self.resume_parser.get_relevant_experience(job_desc)
        matching_skills = self.resume_parser.get_matching_skills(job_desc)

        # Format a brief summary for the prompt
        brief_achievements = []
        for exp in relevant_experience[:1]:  # Only the most relevant experience
            if exp['description']:
                brief_achievements.append(exp['description'].split('.')[0])  # First sentence only
        if matching_skills:
            brief_achievements.append(f"Key skills: {', '.join(matching_skills[:2])}")
        achievements_text = ' '.join(brief_achievements)

        prompt = f"""
Write a concise, professional, and warm outreach email in HTML format.

- Start with a greeting using this name: {recipient_name}
- Mention the specific position (<span style=\"color: #2B579A\">{recipient_info['job_title']}</span>) and company (<span style=\"color: #2B579A\">{recipient_info['company']}</span>).
- Briefly introduce me (Gnanendra Prasad Gopi) and state why I am interested in this role and company.
- Add a section header using <p style=\"font-weight: bold; color: #2B579A; margin: 12px 0 4px 0; font-size: 16px;\"> for both 'Why I'm Interested' and 'My Fit for the Role' (do NOT use <h3> or large headers). Keep spacing tight and the look consistent with the rest of the email.
- Under each header, write a short, relevant paragraph.
- In the 'My Fit for the Role' section, summarize in 1-2 sentences why I am a strong fit, referencing only the most relevant skills or achievements from my resume (do not list my full experience or make it a mini-resume). Use <strong> and <span style=\"color: #2B579A\"> to highlight 1-2 key skills/achievements. Here is a brief summary for reference: {achievements_text}
- Express genuine enthusiasm and a desire to connect or learn more.
- If the recipient is not the hiring manager, politely ask if they could forward this email to the appropriate person.
- End with a courteous thank you and a wish for a great day, but do NOT include a closing or sign-off (like "Best regards")—the signature will be added automatically.
- Keep the tone warm, approachable, and professional.
- Do NOT include any contact details, as these will be in the signature.
- Use clear HTML formatting for readability (styled <p> headers, short paragraphs, and bold/color for key points). Do NOT use <h3> or large headers.

Here is the job description for context:
{job_desc}
"""
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700,
            temperature=0.7,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        # Remove any trailing sign-off phrases
        content = re.sub(r'<p>\s*(Best regards|Sincerely|Kind regards|Regards|Yours truly|Yours sincerely)[^<]*</p>\s*$', '', content, flags=re.IGNORECASE)
        content = re.sub(r'(Best regards|Sincerely|Kind regards|Regards|Yours truly|Yours sincerely)[,.!\s]*$', '', content, flags=re.IGNORECASE)
        return content
