#!/usr/bin/env bash

# Exit on error. Append "|| true" if you expect an error.
set -o errexit
# Exit on error inside any functions or subshells.
set -o errtrace
# Do not allow use of undefined vars. Use ${VAR:-} to use an undefined VAR
#set -o nounset
# Catch the error in case mysqldump fails (but gzip succeeds) in `mysqldump |gzip`
set -o pipefail
# Turn on traces, useful while debugging but commented out by default
# set -o xtrace

while [[ $# -gt 0 ]]
do
  opt="${1}"
  shift;
  current_arg="$1"
  case ${opt} in
    "-s"|"--s3-bucket") export S3_BUCKET="$1"; shift;;
    "-d"|"--dataset-name") export DATASET_NAME="$1"; shift;;
    "-p"|"--product-name") export PRODUCT_NAME="$1"; shift;;
    "-i"|"--product-id") export PRODUCT_ID="$1"; shift;;
    "-r"|"--region") export REGION="$1"; shift;;
    *) echo "ERROR: Invalid option: \""$opt"\"" >&2
        exit 1;;
  esac
done

#creating a pre-processing zip package
(cd pre-processing/pre-processing-code && zip -r pre-processing-code.zip .)

#upload pre-preprocessing.zip to s3
echo "uploading pre-preprocessing.zip to s3"
aws s3 cp pre-processing/pre-processing-code/pre-processing-code.zip s3://$S3_BUCKET/$DATASET_NAME/automation/pre-processing-code.zip --region $REGION

#creating dataset on ADX
echo "creating dataset on ADX"
DATASET_COMMAND="aws dataexchange create-data-set --asset-type "S3_SNAPSHOT" --description file://dataset-description.md --name \"${PRODUCT_NAME}\" --region $REGION --output json"
DATASET_OUTPUT=$(eval $DATASET_COMMAND)
DATASET_ARN=$(echo $DATASET_OUTPUT | tr '\r\n' ' ' | jq -r '.Arn')
DATASET_ID=$(echo $DATASET_OUTPUT | tr '\r\n' ' ' | jq -r '.Id')

#creating pre-processing cloudformation stack
echo "creating pre-processing cloudformation stack"
CFN_STACK_NAME="producer-${DATASET_NAME}-preprocessing"
aws cloudformation create-stack --stack-name $CFN_STACK_NAME --template-body file://pre-processing/pre-processing-cfn.yaml --parameters ParameterKey=S3Bucket,ParameterValue=$S3_BUCKET ParameterKey=DataSetName,ParameterValue=$DATASET_NAME ParameterKey=DataSetArn,ParameterValue=$DATASET_ARN ParameterKey=ProductId,ParameterValue=$PRODUCT_ID ParameterKey=Region,ParameterValue=$REGION --region $REGION --capabilities "CAPABILITY_AUTO_EXPAND" "CAPABILITY_NAMED_IAM" "CAPABILITY_IAM"

echo "waiting for cloudformation stack to complete"
aws cloudformation wait stack-create-complete --stack-name $CFN_STACK_NAME --region $REGION

if [[ $? -ne 0 ]]
then
  # Cloudformation stack created
  echo "Cloudformation stack creation failed"
  exit 1
fi

#invoking the pre-processing lambda function to create first dataset revision
echo "invoking the pre-processing lambda function to create first dataset revision"
LAMBDA_FUNCTION_NAME="source-revision-updates-for-${DATASET_NAME}"
LAMBDA_FUNCTION_STATUS_CODE=$(aws lambda invoke --function-name $LAMBDA_FUNCTION_NAME --invocation-type "RequestResponse" --payload '{ "test": "event" }' response.json --region $REGION --query 'StatusCode' --output text --cli-binary-format raw-in-base64-out)

#grabbing dataset revision status
echo "grabbing dataset revision status"
DATASET_REVISION_STATUS=$(aws dataexchange list-data-set-revisions --data-set-id $DATASET_ID --region $REGION --query "sort_by(Revisions, &CreatedAt)[-1].Finalized")

if [[ $DATASET_REVISION_STATUS == "true" ]]
then
  echo "Dataset revision completed successfully"
  echo "Destroying the Cloudformation stack"
  aws cloudformation delete-stack --stack-name $CFN_STACK_NAME --region $REGION

  #check status of cloudformation stack delete action
  aws cloudformation wait stack-delete-complete --stack-name $CFN_STACK_NAME --region $REGION
  if [[ $? -eq 0 ]]
  then
    # Cloudformation stack deleted
    echo "Cloudformation stack successfully deleted"
    echo "Please create the ADX product manually and re-run the pre-processing cloudformation template with the right product id"
  else
    # Cloudformation stack deletion failed
    echo "Cloudformation stack deletion failed"
    exit 1
  fi
else
  echo "Dataset revision failed"
  cat response.json
fi