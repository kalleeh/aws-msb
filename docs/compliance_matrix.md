# AWS MSB Compliance Matrix

Maps AWS Minimum Security Baseline controls to CIS AWS Foundations Benchmark v5.0 and AWS FSBP.

> **Note**: This document is stable and maintained with the code. For the latest AWS standards documentation, see:
> - [CIS AWS Foundations Benchmark v5.0](https://docs.aws.amazon.com/securityhub/latest/userguide/cis-aws-foundations-benchmark.html)
> - [AWS Foundational Security Best Practices](https://docs.aws.amazon.com/securityhub/latest/userguide/fsbp-standard.html)

**Legend:**
- ✅ Automated (Security Hub detects + passes automatically)
- 🔧 Auto-remediated (Enhanced tier only)
- ⚠️ Manual (requires human action)

## Account Controls

| Control | CIS v5.0 | FSBP | Automated | Auto-Remediation |
|---------|----------|------|-----------|------------------|
| Security contact configured | Account.1 | - | ✅ | - |

## CloudTrail Controls

| Control | CIS v5.0 | FSBP | Automated | Auto-Remediation |
|---------|----------|------|-----------|------------------|
| CloudTrail enabled in all regions | CloudTrail.1 | CloudTrail.1 | ✅ | - |
| CloudTrail log file validation enabled | CloudTrail.2 | CloudTrail.4 | ✅ | - |
| CloudTrail logs encrypted with KMS | CloudTrail.3 | CloudTrail.2 | ✅ | 🔧 |
| CloudTrail log files not publicly accessible | CloudTrail.4 | S3.1 | ✅ | 🔧 |
| CloudTrail integrated with CloudWatch Logs | CloudTrail.5 | CloudTrail.5 | ✅ | - |

## Config Controls

| Control | CIS v5.0 | FSBP | Automated | Auto-Remediation |
|---------|----------|------|-----------|------------------|
| AWS Config enabled in all regions | Config.1 | Config.1 | ✅ | - |

## EC2/VPC Controls

| Control | CIS v5.0 | FSBP | Automated | Auto-Remediation |
|---------|----------|------|-----------|------------------|
| Default security group restricts all traffic | EC2.2 | EC2.2 | ✅ | 🔧 |
| VPC flow logging enabled | EC2.6 | EC2.6 | ✅ | - |
| EBS default encryption enabled | EC2.7 | EC2.7 | ✅ | - |
| EC2 instances use IMDSv2 | EC2.8 | EC2.8 | ✅ | - |
| Security groups restrict 0.0.0.0/0 ingress | EC2.18 | EC2.18 | ✅ | 🔧 |
| Security groups restrict ::/0 ingress | EC2.19 | EC2.19 | ✅ | 🔧 |
| Unused security groups removed | EC2.22 | - | ✅ | - |

## EFS Controls

| Control | CIS v5.0 | FSBP | Automated | Auto-Remediation |
|---------|----------|------|-----------|------------------|
| EFS encrypted at rest | EFS.1 | EFS.1 | ✅ | - |
| EFS access points enforce user identity | EFS.8 | - | ✅ | - |

## IAM Controls

| Control | CIS v5.0 | FSBP | Automated | Auto-Remediation |
|---------|----------|------|-----------|------------------|
| IAM password policy requires minimum length 14+ | IAM.1 | IAM.9 | ✅ | - |
| IAM password policy requires symbols | IAM.2 | IAM.9 | ✅ | - |
| IAM password policy requires numbers | IAM.3 | IAM.9 | ✅ | - |
| IAM password policy requires uppercase | IAM.4 | IAM.9 | ✅ | - |
| IAM password policy requires lowercase | IAM.5 | IAM.9 | ✅ | - |
| IAM password policy prevents reuse | IAM.6 | IAM.9 | ✅ | - |
| IAM password policy expires passwords | IAM.7 | IAM.9 | ✅ | - |
| Root account MFA enabled | IAM.9 | IAM.6 | ⚠️ | - |
| Root account access keys removed | IAM.4 | IAM.4 | ⚠️ | - |
| IAM users with console access have MFA | IAM.5 | IAM.19 | ⚠️ | - |
| IAM users with access keys have MFA | IAM.6 | - | ⚠️ | - |
| Unused IAM credentials removed (90 days) | IAM.22 | IAM.3 | ⚠️ | - |
| Access keys rotated every 90 days | IAM.3 | IAM.3 | ⚠️ | - |
| IAM policies attached only to groups/roles | IAM.26 | IAM.1 | ⚠️ | - |
| IAM user credentials unused for 45 days | IAM.27 | - | ⚠️ | - |

## KMS Controls

| Control | CIS v5.0 | FSBP | Automated | Auto-Remediation |
|---------|----------|------|-----------|------------------|
| KMS key rotation enabled | KMS.1 | KMS.4 | ✅ | - |

## RDS Controls

| Control | CIS v5.0 | FSBP | Automated | Auto-Remediation |
|---------|----------|------|-----------|------------------|
| RDS instances not publicly accessible | RDS.2 | RDS.2 | ✅ | - |
| RDS instances encrypted at rest | RDS.3 | RDS.3 | ✅ | - |
| RDS snapshots encrypted | RDS.4 | RDS.4 | ✅ | - |
| RDS automatic backups enabled | RDS.5 | RDS.5 | ✅ | - |
| RDS enhanced monitoring enabled | RDS.15 | RDS.6 | ✅ | - |

## S3 Controls

| Control | CIS v5.0 | FSBP | Automated | Auto-Remediation |
|---------|----------|------|-----------|------------------|
| S3 account-level public access block enabled | S3.1 | S3.1 | ✅ | 🔧 |
| S3 buckets block public access | S3.8 | S3.1 | ✅ | 🔧 |
| S3 buckets have server-side encryption | S3.4 | S3.4 | ✅ | 🔧 |
| S3 buckets have versioning enabled | S3.14 | S3.14 | ✅ | - |
| S3 buckets have lifecycle policies | S3.10 | S3.10 | ✅ | - |
| S3 buckets log access | S3.9 | S3.9 | ✅ | - |
| S3 buckets use SSL/TLS | S3.5 | S3.5 | ⚠️ | - |

## Summary

**CIS v5.0 Coverage:**
- Total controls: 40
- Automated: 28 (70%)
- Manual: 12 (30%)

**Auto-Remediation (Enhanced Tier):**
- S3 public access blocks
- Security group 0.0.0.0/0 removal
- CloudTrail encryption
- EBS encryption by default

**Manual Controls (Require Human Action):**
- Root account MFA and access key removal
- IAM user MFA enablement
- Access key rotation
- Credential cleanup
- IAM policy governance

## Tier Comparison

| Tier | Controls Deployed | Auto-Remediation | Monthly Cost |
|------|-------------------|------------------|--------------|
| Essential | 28 automated | ❌ | ~$50 |
| Standard | 28 automated + GuardDuty + Access Analyzer | ❌ | ~$150 |
| Enhanced | 28 automated + GuardDuty + Access Analyzer | ✅ | ~$300 |

## References

- [CIS AWS Foundations Benchmark v5.0](https://www.cisecurity.org/benchmark/amazon_web_services)
- [AWS Foundational Security Best Practices](https://docs.aws.amazon.com/securityhub/latest/userguide/fsbp-standard.html)
- [CIS v5.0 Control Analysis](cis_v5_control_analysis.md)
