# Architecture

> **Stability**: This document is maintained with the code and reflects the current implementation.
> 
> **External References**: For AWS service documentation, see:
> - [Security Hub Cross-Region Aggregation](https://docs.aws.amazon.com/securityhub/latest/userguide/finding-aggregation.html)
> - [CloudTrail Multi-Region Trails](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/creating-trail-organization.html)
> - [AWS Config Service-Linked Role](https://docs.aws.amazon.com/config/latest/developerguide/using-service-linked-roles.html)

## Design Principles

1. **Security Hub CSPM First** - Primary interface for security posture management
2. **Single Stack Deployment** - One stack, conditional tier logic
3. **Minimal Code** - Use AWS-managed services, avoid custom Lambda
4. **Cost-Optimized** - Tiered pricing from $50-$300/month
5. **Auto-Remediation** - AWS-managed SSM documents only

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Hub CSPM                         │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │ CIS v5.0     │  │ AWS FSBP     │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓ (creates service-linked rules)
┌─────────────────────────────────────────────────────────────┐
│                      AWS Config                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Config Rules (created by Security Hub)              │   │
│  │  - securityhub-s3-bucket-public-read-prohibited      │   │
│  │  - securityhub-vpc-default-security-group-closed     │   │
│  │  - securityhub-iam-password-policy                   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓ (triggers on non-compliance - Enhanced tier only)
┌─────────────────────────────────────────────────────────────┐
│              Config Auto-Remediation (Enhanced)              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  AWS-Managed SSM Automation Documents                │   │
│  │  - AWS-ConfigureS3BucketPublicAccessBlock           │   │
│  │  - AWS-DisablePublicAccessForSecurityGroup          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Tiered Architecture

### Essential Tier (~$50/month)
```
Security Hub (CIS v5.0 + FSBP)
    ↓
AWS Config (service-linked role)
    ↓
CloudTrail (multi-region, 90 days)
    ↓
S3 (encrypted, public access blocked)
    ↓
KMS (automatic key rotation)
    ↓
SNS (security notifications)
```

### Standard Tier (~$150/month)
```
Essential Tier
    +
GuardDuty (threat detection)
    +
IAM Access Analyzer
    +
Security Hub cross-region aggregation
```

### Enhanced Tier (~$300/month)
```
Standard Tier
    +
Config Auto-Remediation (2 rules)
    +
Extended retention (365 days)
```

## Component Details

### Security Hub CSPM
- **Purpose**: Primary security posture management interface
- **Mode**: SECURITY_CONTROL (control-based finding generator)
- **Standards**: CIS v5.0, AWS FSBP (both enabled in all tiers)
- **Cross-Region Aggregation**: Enabled in Standard+ tier - aggregates findings from all regions to home region
- **Findings**: Aggregates from GuardDuty (Standard+), Config
- **Cost**: ~$25/month for typical small account (no additional cost for aggregation)

**Note**: Security Hub has two modes:
- **Classic Mode**: Uses `STANDARD_CONTROL` (older)
- **CSPM Mode**: Uses `SECURITY_CONTROL` (newer, what MSB deploys)

The CSPM mode provides enhanced features like exposure findings and attack path analysis. You may see "public preview" banners in the console for additional CSPM features, but the core functionality is fully available.

### AWS Config
- **Purpose**: Backend for Security Hub CSPM
- **Role**: AWS service-linked role (`AWSServiceRoleForConfig`) - AWS-managed and automatically updated
- **Rules**: Created automatically by Security Hub (service-linked)
- **Remediation**: Auto-remediation in Enhanced tier only (AWS-managed SSM documents)
- **Cost**: ~$15/month (Essential), scales with rules

### GuardDuty (Standard+ only)
- **Purpose**: Threat detection (malicious activity, unauthorized behavior)
- **Data Sources**: VPC Flow Logs, CloudTrail, DNS logs
- **Cost**: ~$80/month for typical small account

### IAM Access Analyzer (Standard+ only)
- **Purpose**: Identifies resources shared with external entities
- **Scope**: Account-level analyzer
- **Cost**: ~$10/month

### CloudTrail
- **Purpose**: API activity logging
- **Configuration**: 
  - All tiers: Multi-region trail (captures events from all AWS regions)
  - Essential/Standard: 90-day retention
  - Enhanced: 365-day retention
- **Cost**: ~$5/month (no additional cost for multi-region)

### Auto-Remediation (Enhanced only)
- **Rules**: 2 AWS-managed SSM documents
  - AWS-ConfigureS3BucketPublicAccessBlock
  - AWS-DisablePublicAccessForSecurityGroup
- **Trigger**: Config rule non-compliance
- **Cost**: Included in Config costs

## Deployment Architecture

### Single Stack Pattern (Current)
```python
SecurityBaselineStack(tier="essential|standard|enhanced")
├── Security Hub
│   ├── Enable Hub
│   ├── Enable CIS v5.0
│   └── Enable AWS FSBP
├── AWS Config
│   ├── Configuration Recorder
│   ├── Delivery Channel
│   └── Remediation (Enhanced only)
├── CloudTrail
│   ├── Single/Multi-region (tier-dependent)
│   ├── S3 Bucket (encrypted)
│   └── 90/365-day retention (tier-dependent)
├── GuardDuty (Standard+ only)
├── IAM Access Analyzer (Standard+ only)
├── KMS (all tiers)
├── IAM Password Policy (all tiers)
└── SNS Topic (all tiers)
```

**Deployment**: Single command
```bash
cdk deploy --context tier=essential
```

### Multi-Stack Pattern (Deprecated)
```
IAM Stack → KMS Stack → S3 Stack → Logging Stack → 
VPC Stack → Monitoring Stack → Compliance Stack
```

**Deployment**: 10+ commands, complex dependencies

See [Migration Guide](migration_guide.md) for transition path.

## Data Flow

### Detection Flow
```
1. Resource created/modified
    ↓
2. Config detects change
    ↓
3. Config evaluates rule
    ↓
4. Finding sent to Security Hub
    ↓
5. Security Hub aggregates finding
    ↓
6. EventBridge receives event
    ↓
7. SNS notification sent
```

### Remediation Flow
```
1. Config rule fails
    ↓
2. Auto-remediation triggered
    ↓
3. SSM Automation Document executes
    ↓
4. Resource fixed
    ↓
5. Config re-evaluates
    ↓
6. Finding updated in Security Hub
```

## Regional vs Global Resources

### Global Resources (us-east-1)
- IAM password policy
- S3 account-level public access blocks (if configured)
- CloudTrail organization trail (if using Organizations)

### Regional Resources (deployment region)
- Security Hub hub
- Security Hub standards (CIS v5.0, FSBP)
- Config recorder and delivery channel
- GuardDuty detector (Standard+ only)
- IAM Access Analyzer (Standard+ only)
- CloudTrail (multi-region trail deployed in home region)
- S3 buckets (CloudTrail, Config)
- KMS keys
- SNS topics

## Multi-Region Architecture

### Home Region Concept
The "home region" is where you deploy the MSB stack. This region becomes the central hub for:

1. **CloudTrail**: Single multi-region trail captures events from ALL regions (all tiers)
2. **Security Hub**: Enabled in home region only, aggregates findings from other regions IF enabled there (Standard+ tier)
3. **Config**: Records resources in home region only

### Security Hub Regional Deployment

**Current Implementation**:
- Security Hub is enabled **only in the home region** (where you deploy)
- Standard+ tier enables cross-region aggregation (collects findings from other regions)
- To get findings from other regions, you must manually enable Security Hub in those regions

**Why Not Auto-Enable All Regions?**
- Cost: Each region incurs Security Hub costs (~$25/month per region)
- Complexity: Most small accounts only use 1-2 regions
- Flexibility: Users can enable only the regions they use

**To Enable Security Hub in Additional Regions**:
```bash
# Enable in us-east-1
aws securityhub enable-security-hub --region us-east-1

# Enable standards
aws securityhub batch-enable-standards \
  --standards-subscription-requests \
    StandardsArn=arn:aws:securityhub:us-east-1::standards/cis-aws-foundations-benchmark/v/5.0.0 \
    StandardsArn=arn:aws:securityhub:us-east-1::standards/aws-foundational-security-best-practices/v/1.0.0 \
  --region us-east-1
```

With Standard+ tier cross-region aggregation, findings from us-east-1 will automatically appear in your home region.

### Multi-Region Coverage by Tier

#### Essential Tier
- **CloudTrail**: ✅ ALL regions (multi-region trail)
- **Security Hub**: Home region only
- **Config**: Home region only
- **Cost**: No additional cost for multi-region CloudTrail

#### Standard Tier
- **CloudTrail**: ✅ ALL regions (multi-region trail)
- **Security Hub**: ✅ ALL regions (cross-region aggregation)
- **Config**: Home region only
- **GuardDuty**: Home region only
- **Cost**: No additional cost for Security Hub aggregation

#### Enhanced Tier
- Same as Standard + auto-remediation and extended retention

### Benefits of Multi-Region Architecture
- **Single Deployment**: Deploy once in home region, get multi-region coverage
- **No Additional Cost**: CloudTrail multi-region and Security Hub aggregation are free
- **Simplified Management**: View all findings from one console
- **Automatic**: New regions automatically included in aggregation

## Cost Breakdown by Tier

### Essential (~$50/month)
- Security Hub: $25
- Config: $15
- CloudTrail (multi-region): $5
- S3 storage: $3
- KMS: $2
- SNS: <$1
- **Total: ~$50/month**

### Standard (~$150/month)
- Essential: $50
- GuardDuty: $80
- IAM Access Analyzer: $10
- Security Hub aggregation: $0 (free)
- **Total: ~$150/month**

### Enhanced (~$300/month)
- Standard: $150
- Auto-remediation: $50
- Extended retention (365 days): $100
- **Total: ~$300/month**

**Note**: Multi-region CloudTrail and Security Hub cross-region aggregation have no additional cost.

**Cost Estimation Tool**: Run `python scripts/estimate_costs.py` for detailed breakdown.

## Security Considerations

### Defense in Depth
1. **Preventative**: IAM policies, S3 blocks, security groups
2. **Detective**: Security Hub, GuardDuty, Config
3. **Responsive**: Auto-remediation, SNS alerts
4. **Forensic**: CloudTrail, VPC Flow Logs

### Least Privilege
- Config role: Only permissions needed for recording
- Remediation role: Only permissions for specific SSM documents
- Lambda roles (if used): Scoped to specific actions

### Encryption
- S3: SSE-KMS with automatic key rotation
- CloudTrail: KMS encryption
- SNS: KMS encryption
- EBS: Encryption by default

## When to Use Security Lake

**Security Lake** is AWS's centralized security data lake service that normalizes and stores security data in OCSF format.

### Security Lake vs Security Hub

| Feature | Security Hub | Security Lake |
|---------|--------------|---------------|
| **Purpose** | Security posture management | Centralized security data lake |
| **Best For** | Single/few accounts | Organizations (multi-account) |
| **Data Format** | ASFF (AWS Security Finding Format) | OCSF (Open Cybersecurity Schema Framework) |
| **Cost** | ~$25/month per account | ~$0.50/GB ingested + storage |
| **Integration** | Built-in AWS service findings | Aggregates from multiple sources |
| **Query** | Console/API | Amazon Athena SQL queries |

### When to Use Security Lake

✅ **Use Security Lake if**:
- You have an AWS Organization with multiple accounts (5+)
- You need to aggregate security data across many accounts
- You want to query security data with SQL (Athena)
- You need long-term security data retention (years)
- You want to integrate with SIEM tools

❌ **Don't use Security Lake if**:
- You have a single account or few accounts (use Security Hub)
- You just need compliance monitoring (Security Hub is sufficient)
- You want simple setup (Security Lake requires Organizations)

### MSB + Security Lake

MSB is designed for **single accounts** and uses Security Hub. If you later grow to an Organization:

1. Keep MSB in each account for Security Hub + Config + CloudTrail
2. Add Security Lake at the Organization level to aggregate data
3. Security Lake will automatically collect Security Hub findings

**Reference**: [Security Hub findings in Security Lake](https://docs.aws.amazon.com/security-lake/latest/userguide/security-hub-findings.html)

## Scalability

### Single Account (Designed For)
- Optimized for 1-5 AWS accounts
- Single region deployment by default
- Essential tier for POC/dev
- Standard tier for production
- Enhanced tier for compliance-heavy workloads

### Multi-Account (Not Recommended)
- Use AWS Control Tower for multi-account
- Or AWS Security Hub with delegated administrator
- MSB is designed for small environments only

## Testing

The architecture includes comprehensive testing:
- **Unit Tests**: 4 tests validating resource counts per tier
- **CDK Nag Tests**: 4 security validation tests
- **Snapshot Tests**: 10 tests for encryption and access control
- **Integration Tests**: 9 tests for tier transitions

Run tests: `pytest tests/`

See [Testing Guide](testing_guide.md) for details.
