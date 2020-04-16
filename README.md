# COVID-19 Severity Prediction Models for Counties and Hospitals | Yu Group (UC Berkeley)

## DataSet Desciption
Yu Group at UC Berkeley is working to help forecast the severity of the COVID-19 epidemic both for individual counties and individual hospitals. This release contains datasets for the Prediction and a Severity Index models produced by this team.

## More Information:
- Source: [Yu Group | UC Berkeley](https://www.stat.berkeley.edu/~yugroup/index.html)  
- [Dataset License](https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-03-13/COVID.DATA.LIC.AGMT.pdf)
- [Yu Group | COVID-19 Severity Prediction Homepage](https://pages.semanticscholar.org/coronavirus-research)
- [Yu Group | GitHub Repository for COVID-19 Severity Prediction](https://github.com/Yu-Group/covid19-severity-prediction)
- Frequency: Daily

## What's included?
- County-level Predictions Data (county-predictions.xlsx)
- COVID Severity Index (severity-index.xlsx)

## Contact Information
If you have questions about the source data, please contact a member of [Yu Group](https://www.stat.berkeley.edu/~yugroup/people.html). If you have any questions about the CloudFormation stack, Lambda code or any of the AWS services being used, please contact info@rearc.io.

## About Rearc
Rearc is a cloud, software and services company. We believe that empowering engineers drives innovation. Cloud-native architectures, modern software and data practices, and the ability to safely experiment can enable engineers to realize their full potential. We have partnered with several enterprises and startups to help them achieve agility. Our approach is simple — empower engineers with the best tools possible to make an impact within their industry.

## Refund Policy  
Refunds Not Applicable

## Setup

### Pre-requisites
- Create pre-processing code to acquire source data
- Create pre-processing CloudFormation template
- Create dataset description markdown file (dataset-description.md)
- Create product markdown file (product-description.md)

### Execute init script
Once, you have the pre-processing code written and tested locally, you can run the init shell script to move the pre-processing code to S3, create dataset on ADX, create the first revision etc. The init script requires following parameters to be passed:

- Source S3 Bucket: This is the source S3 bucket where the dataset and pre-processing automation code resides. For Rearc datasets, it's `rearc-data-provider`
- Dataset Name: This is the S3 prefix where the dataset and pre-processing automation code resides. For this e.g., it's `covid-19-sf-bay-area-tracker`
- Product Name: This is the product name on ADX. For this e.g., it's `San Francisco Bay Area COVID-19 Tracker`
- Product ID: Since, ADX does not provide APIs to programmatically create Products, it can be blank for now
- Region: This is the AWS region where the product will be listed on ADX. For this e.g., it's `us-east-1`

#### Here is how you can run the init script  
`./init.sh --s3-bucket "rearc-data-provider" --dataset-name "covid-19-sf-bay-area-tracker" --product-name "San Francisco Bay Area COVID-19 Tracker" --product-id "blank" --region "us-east-1"`

#### At a high-level, init script does following:
- Zips the content of the pre-processing code
- Moves the pre-processing zip file to S3
- Creates a dataset on ADX
- Creates the pre-processing CloudFormation stack
- Executes the pre-processing Lambda function that acquires the source dataset, copies the dataset to S3 and creates the first revision on ADX
- Destroys the CloudFormation stack

### Publishing the product on ADX
At this point, dataset and the first revision is fully created on ADX. You are now ready to create the new product on ADX. Unfortunately, at this point ADX does not provide APIs to programmatically create Products so, you will have to create the product and link the dataset manually using AWS console. Once, the product is created, grab the `Product ID` from ADX console and re-run the pre-processing CloudFormation stack by passing all necessary parameters including the product id. Once the CloudFormation stack is successfully created, based on the CloudWatch scheduled rules, pre-processing Lambda function will automatically create new dataset revisions and publish it to ADX.