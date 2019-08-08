import boto3
import pandas as pd
import re

re_ = '(?<=[,])(?=[^\s])'


def load_file(target_file):
    s3 = boto3.client('s3')
    data = s3.get_object(Bucket='sportsextreme', Key=target_file)
    contents = str(data['Body'].read())[2:-1]
    data = [re.split(re_, line)[:-1] for line in contents.split('\\n')][:-2]
    data = [[d[:-1] for d in d_] for d_ in data]
    df_data = pd.DataFrame(data=data[1:], columns=data[0])

    df_data['player'] = df_data['player'].apply(lambda x: x.strip('"'))

    return df_data
