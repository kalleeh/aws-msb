# Technology Stack

## Core Framework

- **AWS CDK v2** - Infrastructure as Code
- **Python 3.9+** - Primary language
- **CloudFormation** - Underlying deployment engine

## AWS Services (Primary)

### Security & Compliance
- **AWS Security Hub CSPM** - Primary security posture management interface
  - Enables standards: CIS AWS Foundations v3.0, AWS FSBP, NIST 800-53, PCI-DSS
  - Uses AWS Config rules under the hood (service-linked)
- **AWS Config** - Backend for Security Hub CSPM
  - Auto-remediation with SSM automation documents
  - NOT using Conformance Packs directly (let Security Hub create rules)
- **Amazon GuardDuty** - Threat detection
- **IAM Access Analyzer** - External access detection

### Logging & Monitoring
- **AWS CloudTrail** - API activity logging
- **Amazon CloudWatch Logs** - Centralized logging
- **VPC Flow Logs** - Network traffic logging
- **Amazon SNS** - Security event notifications
- **Amazon EventBridge** - Event-driven automation

### Encryption & Key Management
- **AWS KMS** - Encryption key management with automatic rotation
- **S3 Server-Side Encryption** - Default encryption for all buckets

### Networking
- **Amazon VPC** - Network isolation
- **VPC Endpoints** - Private AWS service access
- **NAT Gateway** - Single gateway for cost optimization
- **Security Groups** - Stateful firewall rules
- **Network ACLs** - Stateless firewall rules

## AWS Services (Remediation)

- **AWS Systems Manager Automation** - Pre-built remediation documents
  - `AWS-ConfigureS3BucketPublicAccessBlock`
  - `AWS-DisablePublicAccessForSecurityGroup`
  - `AWS-EnableS3BucketEncryption`
  - 100+ managed documents available

## CDK Constructs

### L1 Constructs (CfnXxx) - Primary Usage
```python
from aws_cdk import (
    aws_securityhub as securityhub,
    aws_config as config,
    aws_guardduty as guardduty,
    aws_cloudtrail as cloudtrail,
    aws_kms as kms,
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_sns as sns,
    aws_events as events,
    aws_events_targets as targets,
)
```

### Key CDK Resources
- `securityhub.CfnHub` - Enable Security Hub
- `securityhub.CfnStandard` - Enable security standards
- `config.CfnConfigurationRecorder` - Enable Config
- `config.CfnRemediationConfiguration` - Auto-remediation
- `guardduty.CfnDetector` - Enable GuardDuty
- `cloudtrail.Trail` - L2 construct for CloudTrail
- `ec2.Vpc` - L2 construct for VPC

## Development Tools

- **pytest** - Testing framework
- **pytest-cov** - Code coverage
- **black** - Code formatting
- **pylint** - Linting
- **pre-commit** - Git hooks

## Technical Constraints

1. **No Custom Lambda for Security Controls** - Use AWS-managed SSM documents
2. **Single Stack Architecture** - Avoid multi-stack dependencies
3. **L1 Constructs Preferred** - Security Hub/Config don't have L2 constructs
4. **Cost-First Design** - Single NAT gateway, 90-day log retention by default
5. **Regional Deployment** - Single region by default, multi-region optional

## Standard ARN Formats

```python
# Security Hub Standards
f"arn:aws:securityhub:{region}::standards/cis-aws-foundations-benchmark/v/3.0.0"
f"arn:aws:securityhub:{region}::standards/aws-foundational-security-best-practices/v/1.0.0"
f"arn:aws:securityhub:{region}::standards/nist-800-53/v/5.0.0"
f"arn:aws:securityhub:{region}::standards/pci-dss/v/3.2.1"

# Config Rules (created by Security Hub)
"securityhub-s3-bucket-public-read-prohibited"
"securityhub-vpc-default-security-group-closed"
"securityhub-iam-password-policy"
```

## Deployment Pattern

```bash
# Simple deployment
cdk deploy --context tier=standard --context email=security@company.com

# Or via config file
cat > config.yaml <<EOF
tier: standard
email: security@company.com
region: us-east-1
EOF
./deploy.sh
```

## Version Requirements

- AWS CDK: >=2.100.0
- Python: >=3.9
- boto3: >=1.34.0
- constructs: >=10.3.0
