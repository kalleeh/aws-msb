# AWS MSB Deployment Guide

> **Stability**: This guide is maintained with the code and reflects current deployment procedures.

## Prerequisites

- AWS Account with administrative access
- AWS CLI configured with credentials
- Node.js 18+ and Python 3.9+
- AWS CDK CLI installed: `npm install -g aws-cdk`

## Quick Start

### 1. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Validate AWS Account

**Important:** Run this before deployment to check for conflicts:

```bash
python scripts/check_aws_account.py
```

This checks for:
- Existing Security Hub configuration
- Existing AWS Config recorders
- Existing GuardDuty detectors
- Conflicting CloudFormation stacks

If conflicts are found, follow the remediation steps provided by the script.

### 3. Choose Your Tier

| Tier | Monthly Cost | Use Case |
|------|--------------|----------|
| **Essential** | ~$50 | POC accounts, minimal security |
| **Standard** | ~$150 | Development/test accounts |
| **Enhanced** | ~$300 | Production accounts with auto-remediation |

### 4. Deploy

**Essential Tier:**
```bash
cdk deploy --context tier=essential --context email=security@company.com
```

**Standard Tier:**
```bash
cdk deploy --context tier=standard --context email=security@company.com
```

**Enhanced Tier:**
```bash
cdk deploy --context tier=enhanced --context email=security@company.com
```

### 5. Post-Deployment Configuration

Some security controls cannot be configured via CloudFormation and require manual setup:

```bash
# Run post-deployment setup script
./scripts/post_deploy_setup.sh
```

This configures:
- **Security Contact Information** (CIS Account.1) - AWS can reach you for security issues
- **IAM Password Policy** (CIS IAM.15, IAM.16) - Enforces strong passwords for IAM users

**Note**: If you use AWS SSO/IAM Identity Center for authentication, the password policy doesn't apply.

---

## What Gets Deployed

### Essential Tier (~$50/month)

**Security Controls:**
- ✅ Security Hub with CIS v5.0 + AWS FSBP
- ✅ AWS Config with service-linked role
- ✅ CloudTrail (multi-region, 90-day retention)
- ✅ S3 encryption + public access blocks
- ✅ KMS with automatic key rotation
- ✅ SNS notifications

**Multi-Region Coverage:**
- CloudTrail: ✅ ALL regions (no extra cost)
- Security Hub: Home region only
- Config: Home region only

**Cost Breakdown:**
- Security Hub: ~$25
- Config: ~$15
- CloudTrail (multi-region): ~$5
- S3 storage: ~$3
- KMS: ~$2
- **Total: ~$50/month**

### Standard Tier (~$150/month)

**Everything in Essential, plus:**
- ✅ GuardDuty threat detection
- ✅ IAM Access Analyzer
- ✅ Security Hub cross-region aggregation

**Multi-Region Coverage:**
- CloudTrail: ✅ ALL regions
- Security Hub: ✅ ALL regions (aggregated to home region, no extra cost)
- Config: Home region only
- GuardDuty: Home region only

**Additional Costs:**
- GuardDuty: ~$80/month
- IAM Access Analyzer: ~$10/month
- Security Hub aggregation: $0 (free)
- **Total: ~$150/month**

### Enhanced Tier (~$300/month)

**Everything in Standard, plus:**
- ✅ Config auto-remediation (2 AWS-managed SSM documents)
- ✅ Extended log retention (365 days)

**Additional Costs:**
- Auto-remediation: ~$50/month
- Extended storage: ~$100/month
- **Total: ~$300/month**

## Configuration Options

### Using Context Parameters

```bash
cdk deploy \
  --context tier=standard \
  --context email=security@company.com \
  --context region=us-east-1
```

### Using Environment Variables

```bash
export CDK_DEFAULT_REGION=us-east-1
export CDK_DEFAULT_ACCOUNT=123456789012
cdk deploy --context tier=standard --context email=security@company.com
```

## Post-Deployment

### 1. Confirm SNS Subscription

Check your email for SNS subscription confirmation and click the link.

### 2. Verify Security Hub

```bash
aws securityhub get-enabled-standards --region us-east-1
```

Expected output shows CIS v5.0 and FSBP enabled.

### 3. Check Compliance Score

1. Open AWS Console → Security Hub
2. Navigate to "Security standards"
3. View CIS v5.0 compliance score (expect 70% automated controls passing)

### 4. Review Findings

Security Hub will start generating findings within 24 hours. Initial compliance:
- **28/40 controls (70%)** automated and passing
- **12/40 controls (30%)** require manual action (IAM MFA, access keys, etc.)

## Troubleshooting

### "Public Preview" Banner in Security Hub Console

**What you see**: Banner about "Security Hub CSPM public preview"

**What it means**: 
- Security Hub IS enabled and working ✅
- You're using the newer CSPM mode (SECURITY_CONTROL) ✅
- The banner is about optional preview features, not your enrollment status

**Verify it's working**:
```bash
aws securityhub describe-hub --region eu-west-1
aws securityhub get-enabled-standards --region eu-west-1
```

Expected: Hub ARN and standards (CIS v5.0, FSBP) shown.

### Issue: "Security Hub is not enabled"

**Solution:** Security Hub must be enabled in the region. The stack enables it automatically, but if you see this error:

```bash
aws securityhub enable-security-hub --region us-east-1
cdk deploy --context tier=standard --context email=security@company.com
```

### Issue: "Config recorder already exists"

**Solution:** Delete existing Config recorder:

```bash
aws configservice delete-configuration-recorder --configuration-recorder-name default
cdk deploy --context tier=standard --context email=security@company.com
```

### Issue: "CloudTrail already exists"

**Solution:** Use a different stack name or delete existing trail:

```bash
aws cloudtrail delete-trail --name existing-trail-name
cdk deploy --context tier=standard --context email=security@company.com
```

### Issue: High costs

**Solution:** Start with Essential tier and upgrade:

```bash
# Deploy Essential first
cdk deploy --context tier=essential --context email=security@company.com

# Upgrade to Standard after validating
cdk deploy --context tier=standard --context email=security@company.com
```

## Upgrading Tiers

To upgrade from Essential → Standard → Enhanced:

```bash
# Current: Essential
cdk deploy --context tier=standard --context email=security@company.com

# Current: Standard
cdk deploy --context tier=enhanced --context email=security@company.com
```

CDK will add new resources without destroying existing ones.

## Downgrading Tiers

To downgrade, you must destroy and redeploy:

```bash
cdk destroy
cdk deploy --context tier=essential --context email=security@company.com
```

**Warning:** This will delete all security logs and findings. Export data first if needed.

## Multi-Region Architecture

### Home Region Deployment

Deploy the stack once in your "home region" to get multi-region coverage:

```bash
# Deploy to us-east-1 (home region)
cdk deploy --context tier=standard --context email=security@company.com
```

**What You Get:**
- **CloudTrail**: Captures events from ALL AWS regions (all tiers)
- **Security Hub**: Aggregates findings from all regions (Standard+ tiers)
- **Config**: Records resources in home region only

### Multi-Region Coverage by Tier

| Service | Essential | Standard | Enhanced |
|---------|-----------|----------|----------|
| CloudTrail | ✅ All regions | ✅ All regions | ✅ All regions |
| Security Hub | Home region | ✅ All regions* | ✅ All regions* |
| Config | Home region | Home region | Home region |
| GuardDuty | N/A | Home region | Home region |

*Findings aggregated to home region (no additional cost)

### Benefits
- **Single Deployment**: Deploy once, get multi-region coverage
- **No Extra Cost**: CloudTrail multi-region and Security Hub aggregation are free
- **Simplified Management**: View all findings from home region console
- **Automatic**: New regions automatically included

## Uninstalling

```bash
cdk destroy
```

This removes all resources except:
- S3 buckets (retained for compliance)
- KMS keys (retained for 30 days)

To force delete S3 buckets:

```bash
aws s3 rb s3://msb-cloudtrail-bucket-* --force
aws s3 rb s3://msb-config-bucket-* --force
```

## Next Steps

1. Review [Compliance Matrix](compliance_matrix.md) for control coverage
2. Configure [manual controls](cis_v5_control_analysis.md) (IAM MFA, access keys)
3. Set up [automated remediation](preventative_controls.md) for Enhanced tier
4. Review [architecture](architecture.md) for customization options
