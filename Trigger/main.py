import base64
import json
import functions_framework
import git
import os
import re
import shutil

@functions_framework.http
def detect_new_image(cloud_event):
    data = cloud_event.data.decode('UTF-8')
    data = json.loads(data)

    encoded_jwt = data["message"]["data"]
    decoded_jwt = base64.urlsafe_b64decode(encoded_jwt + '=' * (4 - len(encoded_jwt) % 4)).decode('utf-8')
    decoded_message = json.loads(decoded_jwt)

    Github_token = os.getenv('Github_token')
    Github_user = os.getenv('Github_user')
    Github_user_email = os.getenv('Github_user_email')

    api = decoded_message["digest"].split('/')
    if api[2] == "api-client":
        CLONE_URL = 'https://github.com/MSPR-Dev-I1/RepoVersion-API-Client.git'
        SOURCE_BRANCH = 'develop'
        REPO_PATH = '/tmp/repo'
        repo_url = f'https://{Github_user}:{Github_token}@github.com/MSPR-Dev-I1/RepoVersion-API-Client.git'
        file_path = os.path.join(REPO_PATH, '.github/workflows/deploy.yml')

        if os.path.exists(REPO_PATH):
            shutil.rmtree(REPO_PATH)

        repo = git.Repo.clone_from(CLONE_URL, REPO_PATH, branch=SOURCE_BRANCH)
        with repo.config_writer() as git_config:
            git_config.set_value("user", "name", Github_user)
            git_config.set_value("user", "email", Github_user_email)


        repo.git.checkout(SOURCE_BRANCH)

        digest = decoded_message['digest']
        sha = digest.split('@')[-1]
        sha = sha.split(':')[-1]
        find_and_replace_gcloud_command(file_path,sha)

        repo.git.add(all=True)

        repo.index.commit('Modification d\'un fichier existant')

        repo.remote().set_url(repo_url)
        repo.git.push('origin', SOURCE_BRANCH)

    return f"Version push"


def find_and_replace_gcloud_command(file_path, new_sha256):
    gcloud_command_pattern = re.compile(
        r'(gcloud run deploy api-client-develop --image europe-west9-docker.pkg.dev/\$GOOGLE_PROJECT/api-client/image-api-client@sha256:)[0-9a-f]{64}( --set-env-vars DATABASE_HOST=\$DATABASE_HOST --set-env-vars DATABASE_USER=\$DATABASE_USER --set-env-vars DATABASE_PASSWORD=\$DATABASE_PASSWORD --set-env-vars INSTANCE_UNIX_SOCKET=\$INSTANCE_UNIX_SOCKET --add-cloudsql-instances \$CONNECTION_NAME  --region  europe-west9 --platform managed --allow-unauthenticated)'
    )

    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            match = gcloud_command_pattern.search(line)
            if match:
                new_line = gcloud_command_pattern.sub(r'\1' + new_sha256 + r'\2', line)
                file.write(new_line)
            else:
                file.write(line)
