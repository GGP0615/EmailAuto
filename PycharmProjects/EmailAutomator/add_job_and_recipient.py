import yaml
import os

JOBS_FILE = 'jobs_and_recipients.yaml'

def load_yaml():
    if not os.path.exists(JOBS_FILE):
        return {'jobs': [], 'recipients': []}
    with open(JOBS_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {'jobs': [], 'recipients': []}

def save_yaml(data):
    with open(JOBS_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)

def get_next_job_id(jobs):
    if not jobs:
        return 1
    return max(job['id'] for job in jobs) + 1

def main():
    data = load_yaml()
    jobs = data.get('jobs', [])
    recipients = data.get('recipients', [])

    print('--- Add a New Job and Recipient ---')
    company = input('Company name: ').strip()
    job_title = input('Job title: ').strip()
    print('Enter job description (end with a blank line):')
    lines = []
    while True:
        line = input()
        if line.strip() == '':
            break
        lines.append(line)
    job_description = '\n'.join(lines)

    # Check if job already exists
    job = next((j for j in jobs if j['company'].lower() == company.lower() and j['job_title'].lower() == job_title.lower()), None)
    if job:
        job_id = job['id']
        print(f"Job already exists with ID {job_id}. Adding recipient to this job.")
    else:
        job_id = get_next_job_id(jobs)
        job = {
            'id': job_id,
            'company': company,
            'job_title': job_title,
            'job_description': job_description
        }
        jobs.append(job)
        print(f"Added new job with ID {job_id}.")

    name = input('Contact name: ').strip()
    email = input('Contact email: ').strip()

    # Check if recipient already exists
    recipient = next((r for r in recipients if r['email'].lower() == email.lower()), None)
    if recipient:
        print(f"Recipient {email} already exists. Not adding again.")
    else:
        recipients.append({'name': name, 'email': email, 'job_id': job_id})
        print(f"Added recipient {name} <{email}> for job ID {job_id}.")

    data['jobs'] = jobs
    data['recipients'] = recipients
    save_yaml(data)
    print('Done!')

if __name__ == '__main__':
    main() 