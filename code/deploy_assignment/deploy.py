import paramiko
from os.path import expanduser
from user_definition import *


# ## Assumption : Anaconda, Git (configured)

def ssh_client():
    """Return ssh client object"""
    return paramiko.SSHClient()


def ssh_connection(ssh, ec2_address, user, key_file):
    """
    Set up SSH connection
    """
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ec2_address, username=user,
                key_filename=expanduser("~") + key_file)
    return ssh


def create_or_update_environment(ssh):
    # Create environment
    git_create_env_command = "conda env create -f ~/" \
                             + git_repo_name + "/environment.yml"
    stdin, stdout, stderr = ssh.exec_command(git_create_env_command)

    # If already exists
    if (b'already exists' in stderr.read()):

        # Update environment
        git_update_env_command = "conda env update -f ~/" + git_repo_owner \
                                 + "/environment.yml"
        ssh.exec_command(git_update_env_command)


def git_clone(ssh):
    """Clone from the repo if it doesn't exist or pull from it if it does"""
    # Clone
    git_clone_command = "git clone https://" + git_user_id + "@github.com/" + \
        git_repo_owner + '/' + git_repo_name + ".git"
    stdin, stdout, stderr = ssh.exec_command(git_clone_command)

    # If already exists
    if (b"already exists" in stderr.read()):
        # Pull
        git_pull_command = "cd " + git_repo_name + ";" + "git pull"
        ssh.exec_command(git_pull_command)


def connect_to_crontab(ssh):
    """Launch Cron Jobs for scraping the daily results"""

    # set CronJob for 10 PM PST, or 5 AM UTC
    ssh.exec_command("echo '0 5 * * * ~/.conda/envs/msds603/bin/python " +
                     "/home/ec2-user/product-analytics-group-project-" +
                     "sportsexclamation/code/backend/scrapers/" +
                     "daily_scrape.py\n' > crontab_file")
    ssh.exec_command('crontab crontab_file')


def launch_application(ssh):
    """Run the application in the background"""
    stdin, stdout, stderr = ssh.exec_command('source activate msds603\n' +
                                             'cd product-analytics-group' +
                                             '-project-sportsexclamation/' +
                                             'code/frontend/app \nscreen ' +
                                             "-dm bash -c 'python routes.py'")


def main():
    ssh = ssh_client()
    ssh_connection(ssh, ec2_address, user, key_file)
    git_clone(ssh)
    create_or_update_environment(ssh)
    connect_to_crontab(ssh)

    # halt previous app instances
    ssh.exec_command('pkill -9 python')
    # print('Application running on port 8080')
    launch_application(ssh)
    ssh.exec_command('exit')


if __name__ == '__main__':
    main()
