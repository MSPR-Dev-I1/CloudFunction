import base64
import json
import functions_framework
import git
import os
import shutil
from ruamel.yaml import YAML

@functions_framework.http
def detect_new_image(cloud_event):
    data = cloud_event.data.decode('UTF-8')
    data = json.loads(data)

    encoded_jwt = data["message"]["data"]
    decoded_jwt = base64.urlsafe_b64decode(encoded_jwt + '=' * (4 - len(encoded_jwt) % 4)).decode('utf-8')
    decoded_message = json.loads(decoded_jwt)

    github_token = os.getenv('Github_token')
    github_user = os.getenv('Github_user')
    github_user_email = os.getenv('Github_user_email')
    source_branch = 'develop'
    repo_path = '/tmp/repo'

    api = decoded_message["digest"].split('/')
    if api[2] == "api-client":
        clone_url = 'https://github.com/MSPR-Dev-I1/RepoVersion-API-Client.git'
        repo_url = f'https://{github_user}:{github_token}@github.com/MSPR-Dev-I1/RepoVersion-API-Client.git'

        return push_new_version(repo_path, clone_url, source_branch, github_user, github_user_email, decoded_message, repo_url, api[2])

    if api[2] == "api-commande":
        clone_url = 'https://github.com/MSPR-Dev-I1/RepoVersion-API-Commande.git'
        repo_url = f'https://{github_user}:{github_token}@github.com/MSPR-Dev-I1/RepoVersion-API-Commande.git'

        return push_new_version(repo_path, clone_url, source_branch, github_user, github_user_email, decoded_message, repo_url, api[2])
    return f"Rien Push"


def update_version_in_yaml(file_path, new_sha256):
    yaml = YAML()

    with open(file_path, 'r') as file:
        data = yaml.load(file)

    data['jobs']['deploy']['steps'][2]['env']['VERSION'] = new_sha256

    with open(file_path, 'w') as file:
        yaml.dump(data, file)

    print(f"La valeur de VERSION a été mise à jour à {new_sha256}")


def delete_repo(repo_path):
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)


def clone_repo(clone_url, repo_path, source_branch, github_user,github_user_email):
    repo = git.Repo.clone_from(clone_url, repo_path, branch=source_branch)
    with repo.config_writer() as git_config:
        git_config.set_value("user", "name", github_user)
        git_config.set_value("user", "email", github_user_email)

    repo.git.checkout(source_branch)
    return repo


def get_new_sha(digest):
    sha = digest.split('@')[-1]
    sha = sha.split(':')[-1]
    return sha


def push_commit(repo, sha, repo_url, source_branch):
    repo.git.add(all=True)

    repo.index.commit(f'feat: nouvelle version sha:{sha}')

    repo.remote().set_url(repo_url)
    repo.git.push('origin', source_branch)


def push_new_version(repo_path, clone_url, source_branch, github_user, github_user_email, decoded_message, repo_url, name_api):
    file_path = os.path.join(repo_path, '.github/workflows/deploy.yml')

    delete_repo(repo_path)
    repo = clone_repo(clone_url, repo_path, source_branch, github_user, github_user_email)

    sha = get_new_sha(decoded_message['digest'])
    update_version_in_yaml(file_path, sha)

    push_commit(repo, sha, repo_url, source_branch)
    return f"Version push {name_api} : {sha}"
