from yaml_loader import YamlJobRecipientLoader

def import_yaml_to_db(yaml_path, add_recipient_func):
    loader = YamlJobRecipientLoader(yaml_path)
    for recipient in loader.get_all_recipients():
        job = loader.get_job_for_recipient(recipient)
        job_url = job.get('job_url', None)
        add_recipient_func(
            recipient['name'],
            recipient['email'],
            job['company'],
            job['job_title'],
            job['job_description'],
            job_url
        )
    print("[YAML IMPORT] Completed.")
