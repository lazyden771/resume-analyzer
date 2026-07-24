"""
AI Resume Analyzer - Backend
Single-file Flask app. Run with: python app.py
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

SKILL_DB = {
    'Programming Languages': ['python', 'java', 'javascript', 'c++', 'go', 'rust', 'typescript', 'php', 'ruby'],
    'Machine Learning': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'nlp', 'computer vision'],
    'Cloud Platforms': ['aws', 'azure', 'gcp', 'kubernetes', 'docker', 'lambda', 'ec2', 's3'],
    'Web Development': ['react', 'angular', 'vue', 'node.js', 'django', 'flask', 'fastapi', 'rest api', 'html', 'css'],
    'Database': ['sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'nosql'],
    'DevOps': ['ci/cd', 'jenkins', 'terraform', 'ansible', 'git', 'github'],
    'Soft Skills': ['leadership', 'communication', 'project management', 'agile', 'scrum', 'mentoring'],
}


def extract_skills(text):
    text_lower = text.lower()
    found = set()
    for skills in SKILL_DB.values():
        for skill in skills:
            if skill in text_lower:
                found.add(skill.title())
    return found


def calculate_ats_score(resume_text, job_description):
    resume_lower = resume_text.lower()
    job_lower = job_description.lower()

    sections = ['experience', 'education', 'skills']
    section_score = sum(8 for s in sections if s in resume_lower)

    job_words = set(w for w in re.findall(r'[a-z]+', job_lower) if len(w) > 3)
    resume_words = set(w for w in re.findall(r'[a-z]+', resume_lower) if len(w) > 3)
    overlap = len(job_words & resume_words) / len(job_words) if job_words else 0
    keyword_score = int(overlap * 40)

    job_skills = extract_skills(job_description)
    resume_skills = extract_skills(resume_text)
    skill_overlap = len(job_skills & resume_skills) / len(job_skills) if job_skills else 0.5
    skill_score = int(skill_overlap * 36)

    total = min(100, section_score + keyword_score + skill_score)
    return max(total, 15)


def calculate_match_score(resume_text, job_description):
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)
    if not job_skills:
        return 50
    overlap = len(resume_skills & job_skills) / len(job_skills)
    return min(100, max(20, int(overlap * 100)))


def identify_missing_skills(resume_text, job_description):
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)
    missing = sorted(job_skills - resume_skills)
    return missing[:6]


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/api/v1/analyze', methods=['POST'])
def analyze():
    data = request.get_json(force=True, silent=True) or {}
    resume_text = (data.get('resume_text') or '').strip()
    job_description = (data.get('job_description') or '').strip()

    if not resume_text or not job_description:
        return jsonify({'error': 'resume_text and job_description are both required'}), 400

    ats_score = calculate_ats_score(resume_text, job_description)
    match_score = calculate_match_score(resume_text, job_description)
    missing_skills = identify_missing_skills(resume_text, job_description)
    resume_skills = list(extract_skills(resume_text))

    strengths = []
    if resume_skills:
        strengths.append(f"{len(resume_skills)} relevant skills detected: {', '.join(resume_skills[:5])}")
    if 'experience' in resume_text.lower():
        strengths.append("Experience section clearly present")
    if not strengths:
        strengths.append("Resume submitted successfully")

    recommendations = [
        "Add measurable outcomes to your bullet points (e.g. reduced load time by 30%)",
        "Mirror 3-5 exact keywords from the job description in your skills section",
    ]
    if missing_skills:
        recommendations.append(f"Consider adding or highlighting: {', '.join(missing_skills[:3])}")
    recommendations.append("Keep formatting simple - avoid tables/columns that confuse ATS parsers")

    roadmap = {
        'phase_1_foundation': [
            {'skill': s, 'duration': '3-4 weeks', 'resource': 'Coursera / official docs', 'priority': 'High'}
            for s in missing_skills[:2]
        ],
        'phase_2_advanced': [
            {'skill': s, 'duration': '5-6 weeks', 'resource': 'Udemy / hands-on project', 'priority': 'Medium'}
            for s in missing_skills[2:4]
        ],
        'phase_3_specialization': [
            {'skill': s, 'duration': '6-8 weeks', 'resource': 'Certification track', 'priority': 'Medium'}
            for s in missing_skills[4:6]
        ],
    }

    job_matches = [
        {'title': 'Software Engineer', 'company': 'Market sample', 'match': match_score},
        {'title': 'Backend Developer', 'company': 'Market sample', 'match': max(0, match_score - 8)},
        {'title': 'Senior Engineer', 'company': 'Market sample', 'match': max(0, match_score - 15)},
    ]
    job_matches.sort(key=lambda j: j['match'], reverse=True)

    salary_range = {'min': 70000, 'max': 130000, 'median': 100000}

    interview_questions = [
        "Walk me through a project you are most proud of and your specific role in it.",
        "How do you approach debugging a production issue under time pressure?",
        "Tell me about a time you disagreed with a technical decision. What did you do?",
        "How do you decide what to learn next in your field?",
        "Describe how you would design a system to handle rapid growth in usage.",
    ]

    return jsonify({
        'ats_score': ats_score,
        'match_score': match_score,
        'strengths': strengths,
        'missing_skills': missing_skills,
        'weak_keywords': [],
        'recommendations': recommendations,
        'roadmap': roadmap,
        'job_matches': job_matches,
        'salary_range': salary_range,
        'interview_questions': interview_questions,
    }), 200


if __name__ == '__main__':
    print("Backend running at http://localhost:5000")
    app.run(debug=False, port=5000, host='0.0.0.0')
