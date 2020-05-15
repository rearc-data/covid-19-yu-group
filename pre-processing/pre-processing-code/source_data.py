import os
import boto3
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from multiprocessing.dummy import Pool

def data_to_s3(data):

	# throws error occured if there was a problem accessing data
	# otherwise downloads and uploads to s3

	try:
		response = urlopen(data['url'])

	except HTTPError as e:
		raise Exception('HTTPError: ', e.code, data['filename'])

	except URLError as e:
		raise Exception('URLError: ', e.reason, data['filename'])

	else:
		
		file_location = '/tmp/' + data['filename']

		if file_location.endswith('.csv'):
			csv = response.read().decode().split('\n')

			with open(file_location, 'w', encoding='utf-8') as f:
				f.write(csv[2].lower().replace(' ', '_') + '\n')
				f.write('\n'.join(csv[3:]))
		
		if file_location.endswith('.xlsx'):
			with open(file_location, 'wb') as f:
				f.write(response.read())

		# variables/resources used to upload to s3
		s3_bucket = os.environ['S3_BUCKET']
		data_set_name = os.environ['DATA_SET_NAME']
		new_s3_key = data_set_name + '/dataset/'
		s3 = boto3.client('s3')

		s3.upload_file(file_location, s3_bucket, new_s3_key + data['filename'])
		
		print('Uploaded: ' + data['filename'])

		# deletes to preserve limited space in aws lamdba
		os.remove(file_location)

		# dicts to be used to add assets to the dataset revision
		return {'Bucket': s3_bucket, 'Key': new_s3_key + data['filename']}

def source_dataset():

	county_url = 'https://docs.google.com/spreadsheets/d/1ZSG7o4cV-G0Zg3wlgJpB2Zvg-vEN1i_76n2I-djL0Dk/export?format='
	severity_url = 'https://docs.google.com/spreadsheets/d/1ZLev2pRIPXvP-qNnvAtO53-bCrAGTAhB_w0w7bZKAWw/export?format='

	county_title = 'county-predictions.'
	severity_title = 'severity-index.'

	# list of enpoints to be used to access data included with product
	endpoints = [
		{'url': county_url + 'csv', 'filename': county_title + 'csv'},
		{'url': county_url + 'xlsx', 'filename': county_title + 'xlsx'},
		{'url': severity_url + 'csv', 'filename': severity_title + 'csv'},
		{'url': severity_url + 'xlsx', 'filename': severity_title + 'xlsx'}

	]

	# multithreading speed up accessing data, making lambda run quicker
	with (Pool(4)) as p:
		asset_list = p.map(data_to_s3, endpoints)

	# asset_list is returned to be used in lamdba_handler function
	return asset_list
