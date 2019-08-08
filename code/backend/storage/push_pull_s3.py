import os


def push(target_file, target_dest):
    os.system('aws s3 cp ' + target_file + ' s3://sportsextreme/' +
              target_dest + target_file)


def pull(target_file, target_dest):
    os.system('aws s3 cp s3://sportsextreme/' +
              target_file + ' ' + target_dest)


def remove_local(target_file):
    os.system('rm ' + target_file)
