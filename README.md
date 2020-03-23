# Minimum Security Baseline (MSB)

This reference architecture provides a set of YAML templates for deploying a Minimum Security Baseline in a stand-alone AWS Account with [AWS CloudFormation](https://aws.amazon.com/cloudformation/).

This is useful for AWS environments with a small amount of AWS Accounts or a Proof-of-Concept environment.
If you have a multi-account setup that you are looking to baseline you should probably look at solutions such as [AWS Deployment Framework](https://github.com/awslabs/aws-deployment-framework) or [AWS Control Tower](https://aws.amazon.com/controltower/) instead.

## Template details

The templates below are included in this repository and reference architecture:

| Template | Description |
| --- | --- |
| [cfn/iam.yaml](cfn/iam.yaml) | This template deploys IAM Groups, Roles and policies in the account. Create IAM Users and assign them to groups to give access to users. |
| [cfn/logging.yaml](cfn/logging.yaml) | This template deploys a multi-region CloudTrail Trail, an S3 Bucket used to store logs from the other services and an IAM Role used for AWS Config. |
| [cfn/logging-regional.yaml](cfn/logging-regional.yaml) | This template deploys AWS Config in the region and sends logs to an S3 Bucket. |
| [cfn/security-regional.yaml](cfn/security-regional.yaml) | This template deploys AWS GuardDuty and AWS Security Hub with CIS Foundations Benchmark enabled. It also provisions CloudWatch Event Rules to automatically notify the Notification E-Mail of events that happen. Note: This uses a custom resource to enable the CIS Foundations Benchmark. |
| [cfn/vpc-regional.yaml](cfn/vpc-regional.yaml) | This template deploys a VPC with a pair of public and private subnets spread across two or three Availability Zones. It deploys an [Internet gateway](http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/VPC_Internet_Gateway.html), with a default route on the public subnets. It deploys a pair of NAT gateways (one in each zone), and default routes for them in the private subnets. |

After the CloudFormation templates have been deployed, the [stack outputs](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html) contain a series of parameters useful for accessing your resources and logs.

## Deployment Instructions

### Prerequisites

#### Client Requirements

- AWS CLI installed and configured to the AWS Account you want to secure.
- Terminal/Shell for the `deploy` script.

#### AWS Services

This template sets up a number of logging and security services in your account. If you already have enabled these services they need to be disabled beforehand.

- AWS Config
- AWS GuardDuty
- AWS IAM Access Analyzer
- AWS Security Hub

### Setup

Run the below command to package all the deployment artifacts, upload them to the S3 bucket and create the CloudFormation stacks.

1. First modify the msb.config file with your settings.
2. Run the deployment script in Global deployment mode to deploy account level pre-requisites.

    ```sh
    ./deploy.sh
    ```

3. Run the deployment script in Regional deployment mode for every region you want to protect.
4. Done.

#### Multi-Region

If you are operating in multiple regions you need to deploy the regional templates in each region since some security and logging services operate on a regional level.
Run the deploy script for each region you want to enable and choose the regional deployment mode and then specify the new region.

### (Slightly) Advanced Topics

#### Federated Users from a SAML 2.0 Provider

The IAM template provides support for integrating with a SAML 2.0 IdP to authenticate your users.

1. Create the IdP manually in your AWS Account and specify a name.
2. Update the iam.yaml template and set the default value for parameter IdentityProvider to the name of the IdP you just created.

For detailed instructions on setting up federation you can read more on this [blog post](https://aws.amazon.com/blogs/security/aws-federated-authentication-with-active-directory-federation-services-ad-fs/).

#### Security Logging

The baseline configures CloudWatch Events that listen and alerts on several types of events.

- [GuardDuty Findings with severity Medium or Higher (Above 4)](https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_findings.html)
- [IAM Access Analyzer Findings](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-findings.html)

The following events are disabled by default but to avoid too much noise but can be enabled by setting the `SecurityHubEvents` parameter to true in the `security-regional` template.

- Security Hub Findings - Imported
- Security Hub Insight Results

[List of Security Hub Types](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-cloudwatch-events.html#securityhub-cwe-integration-types)

Note: It is recommended that you regularly view the status in the [Security Hub Dashboard](console.aws.amazon.com/securityhub/home) in relevant regions for an overview of your security status.

### Cleanup

In order to clean up the MSB delete CloudFormation stacks starting from regional stacks and then the global ones, like in the example below:

```sh
aws cloudformation delete-stack msb-security-eu-west-1 [ --profile yourawsprofile ]
aws cloudformation delete-stack msb-vpc-eu-west-1 [ --profile yourawsprofile ]
aws cloudformation delete-stack msb-logging-eu-west-1 [ --profile yourawsprofile ]
aws cloudformation delete-stack msb-logging-global [ --profile yourawsprofile ]
aws cloudformation delete-stack msb-iam-global [ --profile yourawsprofile ]
```
