import PyPDF2
import re
from typing import Dict, List, Optional

class ResumeParser:
    def __init__(self, resume_path: str):
        self.resume_path = resume_path
        self.content = self._extract_text()
        self.experience = self._extract_experience()
        self.skills = self._extract_skills()
        self.education = self._extract_education()

    def _extract_text(self) -> str:
        """Extract text from PDF resume."""
        try:
            with open(self.resume_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"Error reading resume: {e}")
            return ""

    def _extract_experience(self) -> List[Dict]:
        """Extract work experience sections."""
        experience_sections = []
        # Look for experience sections (this pattern might need adjustment based on your resume format)
        experience_pattern = r"(?i)(.*?)\s*(\d{4}\s*-\s*(?:Present|\d{4}))\s*(.*?)(?=\n\s*\n|\Z)"
        matches = re.finditer(experience_pattern, self.content, re.DOTALL)
        
        for match in matches:
            if match:
                title_company = match.group(1).strip()
                period = match.group(2).strip()
                description = match.group(3).strip()
                
                # Split title and company
                title_company_parts = title_company.split(" at ", 1)
                title = title_company_parts[0].strip()
                company = title_company_parts[1].strip() if len(title_company_parts) > 1 else ""
                
                experience_sections.append({
                    "title": title,
                    "company": company,
                    "period": period,
                    "description": description
                })
        
        return experience_sections

    def _extract_skills(self) -> List[str]:
        """Extract skills section."""
        skills = []
        # Look for skills section (adjust pattern based on your resume format)
        skills_pattern = r"(?i)skills:?\s*(.*?)(?=\n\s*\n|\Z)"
        match = re.search(skills_pattern, self.content, re.DOTALL)
        
        if match:
            skills_text = match.group(1)
            # Split skills by common delimiters
            skills = [skill.strip() for skill in re.split(r'[,•|\n]', skills_text) if skill.strip()]
        
        return skills

    def _extract_education(self) -> List[Dict]:
        """Extract education section."""
        education = []
        # Look for education section (adjust pattern based on your resume format)
        education_pattern = r"(?i)(.*?)\s*(\d{4}\s*-\s*\d{4})\s*(.*?)(?=\n\s*\n|\Z)"
        matches = re.finditer(education_pattern, self.content, re.DOTALL)
        
        for match in matches:
            if match:
                degree = match.group(1).strip()
                years = match.group(2).strip()
                institution = match.group(3).strip()
                
                education.append({
                    "degree": degree,
                    "years": years,
                    "institution": institution
                })
        
        return education

    def get_relevant_experience(self, job_description: Optional[str]) -> List[Dict]:
        """Get experience sections most relevant to the job description."""
        relevant_experience = []
        job_keywords = self._extract_keywords(job_description or "")
        
        for exp in self.experience:
            relevance_score = self._calculate_relevance(exp, job_keywords)
            if relevance_score > 0:
                exp['relevance_score'] = relevance_score
                relevant_experience.append(exp)
        
        # Sort by relevance score
        relevant_experience.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_experience

    def _extract_keywords(self, text: Optional[str]) -> List[str]:
        """Extract important keywords from text."""
        if not text:
            return []
        # Remove common words and split into keywords
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by'}
        words = re.findall(r'\b\w+\b', text.lower())
        return [word for word in words if word not in common_words and len(word) > 3]

    def _calculate_relevance(self, experience: Dict, keywords: List[str]) -> float:
        """Calculate how relevant an experience is to the job description."""
        text = f"{experience['title']} {experience['description']}".lower()
        return sum(1 for keyword in keywords if keyword in text)

    def get_matching_skills(self, job_description: Optional[str]) -> List[str]:
        """Get skills that match the job description."""
        job_keywords = self._extract_keywords(job_description or "")
        return [skill for skill in self.skills if any(keyword in skill.lower() for keyword in job_keywords)] 