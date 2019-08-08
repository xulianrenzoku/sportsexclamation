Our Code Tutorial
=================

In order to launch this application on an EC2, first one needs to make sure that the paramiko package is installed locally. Once that has been completed, launch an EC2 instance with Anaconda and Git installed. Make sure to initialize the box with your git password and ID. In /code/deploy_assignment/user_definition.py, edit the EC2 address, git_user_id & key_file variables. Once these are updated, execute /code/deploy_assignment/deploy.py, which will create/update the appropriate environment on the EC2, activate this environment, and then launch the website. 
