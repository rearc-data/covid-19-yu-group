import os
import boto3
from urllib.request import urlopen

def source_dataset(s3_bucket, new_s3_key):

    county_title = 'county-predictions.xlsx'

    county_url = urlopen(
        'https://docs.google.com/spreadsheets/d/1ZLev2pRIPXvP-qNnvAtO53-bCrAGTAhB_w0w7bZKAWw/export?format=xlsx')
    county_output = open('/tmp/' + county_title, 'wb')
    county_output.write(county_url.read())
    county_output.close()

    severity_title = 'severity-index.xlsx'

    severity_url = urlopen(
        'https://docs.google.com/spreadsheets/d/1ZSG7o4cV-G0Zg3wlgJpB2Zvg-vEN1i_76n2I-djL0Dk/export?format=xlsx')
    severity_output = open('/tmp/' + severity_title, 'wb')
    severity_output.write(severity_url.read())
    severity_output.close()

    s3 = boto3.client('s3')
    folder = '/tmp'

    for filename in os.listdir(folder):
        print(filename)
        s3.upload_file('/tmp/' + filename, s3_bucket, new_s3_key + filename)