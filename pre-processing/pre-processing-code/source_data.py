import os
import boto3
from urllib.request import urlretrieve, urlopen

def source_dataset(s3_bucket, new_s3_key):

	severity_url = 'https://docs.google.com/spreadsheets/d/1ZSG7o4cV-G0Zg3wlgJpB2Zvg-vEN1i_76n2I-djL0Dk/export?format='
	county_url = 'https://docs.google.com/spreadsheets/d/1ZLev2pRIPXvP-qNnvAtO53-bCrAGTAhB_w0w7bZKAWw/export?format='

	county_title = 'county-predictions.'
	severity_title = 'severity-index.'

	urlretrieve(
		severity_url + 'xlsx', '/tmp/' + severity_title + 'xlsx')
	urlretrieve(
		county_url + 'xlsx', '/tmp/' + county_title + 'xlsx')

	severity_text = urlopen(severity_url + 'csv').read().decode()
	county_text = urlopen(county_url + 'csv').read().decode()

	severity_list = severity_text.split('\n')
	county_list = county_text.split('\n')

	with open('/tmp/' + severity_title + 'csv', 'w', encoding='utf-8') as s:
		s.write(severity_list[2].lower().replace(' ', '_') + '\n')
		s.write('\n'.join(severity_list[3:]))

	with open('/tmp/' + county_title + 'csv', 'w', encoding='utf-8') as c:
		c.write(county_list[2].lower().replace(' ', '_') + '\n')
		c.write('\n'.join(county_list[3:]))

	s3 = boto3.client('s3')
	folder = '/tmp'

	asset_list = []

	for filename in os.listdir(folder):
		print(filename)
		s3.upload_file('/tmp/' + filename, s3_bucket, new_s3_key + filename)
		asset_list.append({'Bucket': s3_bucket, 'Key': new_s3_key + filename})

	return asset_list