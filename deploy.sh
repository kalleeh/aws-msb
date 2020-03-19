#!/bin/bash
. msb.config

# If user didn't set the e-mail they probably didn't look in the config file.
if [ -z "$NOTIFICATION_EMAIL" ]; then
    echo "ERROR: Please update 'msb.config' with your desired configuration."
    exit
fi

echo -e "\033[0;32m>>> CONFIGURATION"
echo "> Notification Email: $NOTIFICATION_EMAIL"
echo "> AWS CLI Profile: $AWS_PROFILE"
ACCOUNT_ID=$(aws sts get-caller-identity --profile $AWS_PROFILE --output text --query 'Account')
echo "> AWS Account ID: $ACCOUNT_ID"
REGION=$(aws configure get region --profile $AWS_PROFILE)
echo "> AWS Region: $REGION"
echo ""

echo -e "\033[0;34m>>> DEPLOYMENT MODE"
echo "> Deploy Global once per account and Regional once for every region you want to operate in."
read -p "Choose Deployment Mode. (g/r) " mode && [[ $mode == [gG] || $mode == [rR] ]] || exit 1

# Global Deployment Mode
if [[ $mode == 'g' || $mode == 'G' ]] ; then
    echo -e "\033[0m>>> GLOBAL DEPLOYMENT MODE"

    # CLOUDFORMATION PACKAGE: Uncomment this section if any of your templates need to use `aws cloudformation package` first.
    # S3_BUCKET="msb-artifacts-$ACCOUNT_ID-$REGION"
    # echo "> Artifact S3 Bucket: $S3_BUCKET"
    # # Only create the artifacts bucket if one does not exist.
    # if aws s3 ls --profile $AWS_PROFILE "s3://$S3_BUCKET" 2>&1 | grep -q 'NoSuchBucket'; then
    #     echo "Creating deployment artifacts bucket"
    #     aws s3 mb --profile $AWS_PROFILE "s3://$S3_BUCKET"
    # fi
    
    # if ! aws cloudformation package --template-file cfn/template-name.yaml --s3-bucket $S3_BUCKET --output-template-file template-deploy.yaml --profile $AWS_PROFILE > /dev/null ; then
    #     echo -e "\033[0;31mERROR: Unable to package template $STACK_NAME"
    #     exit 1
    # fi
    # CLOUDFORMATION PACKAGE:END

    read -p "Deploy Global resources with these settings? (Y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1

    # Deploy Global IAM
    STACK_NAME="$STACK_PREFIX-iam-global"
    echo "> Deploying IAM template in: $REGION"
    aws cloudformation deploy --template-file cfn/iam.yaml --stack-name $STACK_NAME --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND --profile $AWS_PROFILE

    # Deploy Global Logging
    STACK_NAME="$STACK_PREFIX-logging-global"
    echo "> Deploying Global Logging template in: $REGION"
    aws cloudformation deploy --template-file cfn/logging.yaml --stack-name $STACK_NAME --parameter-overrides NotificationEmail=$NOTIFICATION_EMAIL --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND --profile $AWS_PROFILE

    echo "> Configuring IAM password policy"
    aws iam update-account-password-policy --profile $AWS_PROFILE --minimum-password-length 14 --require-symbols --require-numbers --require-uppercase-characters --require-lowercase-characters --allow-users-to-change-password --max-password-age 90 --password-reuse-prevention 24
    echo -e "\033[0;32m> Finished."
    echo -e "\033[0;31mNOTE: Remember to deploy regional resources in every region you want to run resources in."
fi

# Regional Deployment Mode
if [[ $mode == 'r' || $mode == 'R' ]] ; then
    echo -e "\033[0m>>> REGIONAL DEPLOYMENT MODE"

    echo "> Enter Region using Region Code format, i.e. 'eu-west-1'"
    echo "> List of regions: https://docs.aws.amazon.com/general/latest/gr/rande.html#regional-endpoints"
    read -p "Region Code: " REGION
    echo "> Deploying Regional MSB to: $REGION"

    read -p "Continue? (Y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1

    # CLOUDFORMATION PACKAGE: Uncomment this section if any of your templates need to use `aws cloudformation package` first.
    # S3_BUCKET="msb-artifacts-$ACCOUNT_ID-$REGION"
    # echo "> Artifact S3 Bucket: $S3_BUCKET"
    # # Only create the artifacts bucket if one does not exist.
    # if aws s3 ls --profile $AWS_PROFILE "s3://$S3_BUCKET" 2>&1 | grep -q 'NoSuchBucket'; then
    #     echo "Creating deployment artifacts bucket"
    #     aws s3 mb --profile $AWS_PROFILE --region $REGION "s3://$S3_BUCKET"
    # fi
    
    # if ! aws cloudformation package --template-file cfn/template-name.yaml --s3-bucket $S3_BUCKET --output-template-file template-deploy.yaml --profile $AWS_PROFILE > /dev/null ; then
    #     echo -e "\033[0;31mERROR: Unable to package template $STACK_NAME"
    #     exit 1
    # fi
    # CLOUDFORMATION PACKAGE:END

    # Deploy Regional Logging
    STACK_NAME="$STACK_PREFIX-logging-$REGION"
    echo "> Deploying Regional Logging template in: $REGION"
    aws cloudformation deploy --template-file cfn/logging-regional.yaml --stack-name $STACK_NAME --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND --region $REGION --profile $AWS_PROFILE

    # Deploy Regional Security
    STACK_NAME="$STACK_PREFIX-security-$REGION"
    echo "> Deploying Regional Security template in: $REGION"
    aws cloudformation deploy --template-file cfn/security-regional.yaml --stack-name $STACK_NAME --parameter-overrides NotificationEmail=$NOTIFICATION_EMAIL --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND --region $REGION --profile $AWS_PROFILE

    # Deploy Regional VPC
    STACK_NAME="$STACK_PREFIX-vpc-$REGION"
    echo "> Deploying Regional VPC template in: $REGION"
    aws cloudformation deploy --template-file cfn/vpc-regional.yaml --stack-name $STACK_NAME --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND --region $REGION --profile $AWS_PROFILE

    echo "> Finished."
fi