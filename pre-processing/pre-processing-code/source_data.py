import os
import boto3
import urllib.request

def source_dataset(s3_bucket, new_s3_key):

	county_title = 'county-predictions.xlsx'
	county_url = 'https://docs.google.com/spreadsheets/d/1ZLev2pRIPXvP-qNnvAtO53-bCrAGTAhB_w0w7bZKAWw/export?format=xlsx'

	severity_title = 'severity-index.xlsx'
	severity_url = 'https://docs.google.com/spreadsheets/d/1ZSG7o4cV-G0Zg3wlgJpB2Zvg-vEN1i_76n2I-djL0Dk/export?format=xlsx'

	urllib.request.urlretrieve(
		county_url, '/tmp/' + county_title)
	urllib.request.urlretrieve(
		severity_url, '/tmp/' + severity_title)

	s3 = boto3.client('s3')
	folder = '/tmp'

	asset_list = []

	for filename in os.listdir(folder):
		print(filename)
		
		s3.upload_file('/tmp/' + filename, s3_bucket, new_s3_key + filename)

		asset_list.append({'Bucket': s3_bucket, 'Key': new_s3_key + filename})

	return asset_list