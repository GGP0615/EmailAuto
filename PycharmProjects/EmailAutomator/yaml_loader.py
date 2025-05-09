import yaml

class YamlJobRecipientLoader:
    def __init__(self, yaml_path='jobs_and_recipients.yaml'):
        self.yaml_path = yaml_path
        self.jobs = {}
        self.recipients = []
        self._load()

    def _load(self):
        with open(self.yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            for job in data.get('jobs', []):
                self.jobs[job['id']] = job
            self.recipients = data.get('recipients', [])

    def get_job_for_recipient(self, recipient):
        job_id = recipient.get('job_id')
        return self.jobs.get(job_id)

    def get_all_recipients(self):
        return self.recipients

    def get_all_jobs(self):
        return list(self.jobs.values()) 