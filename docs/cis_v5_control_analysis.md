# CIS AWS Foundations Benchmark v5.0 - Control Analysis

> **Note**: This document reflects the controls implemented in this codebase. For the latest CIS benchmark specification, see:
> - [Official CIS AWS Foundations Benchmark v5.0](https://docs.aws.amazon.com/securityhub/latest/userguide/cis-aws-foundations-benchmark.html)
> - [CIS Benchmark Download](https://www.cisecurity.org/benchmark/amazon_web_services)

## Automated Controls (28/40 = 70%)

### Account (1/1 = 100%)
| Control | Status | Reason |
|---------|--------|--------|
| Account.1 | ✅ Automated | Security contact set via Account Management API (PutAlternateContact) |

### CloudTrail (5/5 = 100%)
| Control | Status | Reason |
|---------|--------|--------|
| CloudTrail.1 | ✅ Automated | Security Hub detects multi-region trail configuration |
| CloudTrail.2 | ✅ Automated | Security Hub detects encryption + auto-remediation via SSM |
| CloudTrail.4 | ✅ Automated | Security Hub detects log file validation |
| CloudTrail.7 | ✅ Automated | Security Hub detects S3 bucket access logging |

### Config (1/1 = 100%)
| Control | Status | Reason |
|---------|--------|--------|
| Config.1 | ✅ Automated | Security Hub detects Config recorder with service-linked role |

### EC2/VPC/Networking (5/5 = 100%)
| Control | Status | Reason |
|---------|--------|--------|
| EC2.2 | ✅ Automated | Security Hub detects default SG rules + auto-remediation via SSM |
| EC2.6 | ✅ Automated | Security Hub detects VPC flow logs |
| EC2.7 | ✅ Automated | Security Hub detects EBS encryption + preventative control |
| EC2.8 | ✅ Automated | Security Hub detects IMDSv2 + preventative control |
| EC2.21 | ✅ Automated | Security Hub detects NACL ingress rules |
| EC2.53 | ✅ Automated | Security Hub detects SG IPv4 rules + auto-remediation via SSM |
| EC2.54 | ✅ Automated | Security Hub detects SG IPv6 rules + auto-remediation via SSM |

### EFS (2/2 = 100%)
| Control | Status | Reason |
|---------|--------|--------|
| EFS.1 | ✅ Automated | Security Hub detects EFS KMS encryption |
| EFS.8 | ✅ Automated | Security Hub detects EFS encryption at rest |

### IAM (3/13 = 23%)
| Control | Status | Reason |
|---------|--------|--------|
| IAM.2 | ❌ Manual | Detectable but requires manual policy removal |
| IAM.3 | ❌ Manual | Detectable but requires user to rotate keys |
| IAM.4 | ❌ Manual | Detectable but requires root user to delete keys |
| IAM.5 | ❌ Manual | Detectable but requires each user to enable MFA |
| IAM.6 | ❌ Manual | Detectable but requires root user to configure hardware MFA |
| IAM.9 | ❌ Manual | Detectable but requires root user to enable MFA |
| IAM.15 | ✅ Automated | Preventative control sets password length policy |
| IAM.16 | ✅ Automated | Preventative control sets password reuse policy |
| IAM.18 | ❌ Manual | Detectable but requires manual support role creation |
| IAM.22 | ❌ Manual | Detectable but requires manual credential removal |
| IAM.26 | ❌ Manual | Detectable but requires manual certificate removal |
| IAM.27 | ❌ Manual | Detectable but requires manual policy detachment |
| IAM.28 | ✅ Automated | IAM Access Analyzer enabled in Standard tier |

### KMS (1/1 = 100%)
| Control | Status | Reason |
|---------|--------|--------|
| KMS.4 | ✅ Automated | Security Hub detects KMS key rotation |

### RDS (5/5 = 100%)
| Control | Status | Reason |
|---------|--------|--------|
| RDS.2 | ✅ Automated | Security Hub detects public accessibility |
| RDS.3 | ✅ Automated | Security Hub detects encryption at rest |
| RDS.5 | ✅ Automated | Security Hub detects multi-AZ configuration |
| RDS.13 | ✅ Automated | Security Hub detects auto minor version upgrades |
| RDS.15 | ✅ Automated | Security Hub detects cluster multi-AZ configuration |

### S3 (6/7 = 86%)
| Control | Status | Reason |
|---------|--------|--------|
| S3.1 | ✅ Automated | Security Hub detects block public access + auto-remediation via SSM |
| S3.5 | ✅ Automated | Security Hub detects SSL requirement |
| S3.8 | ✅ Automated | Security Hub detects block public access + preventative control |
| S3.20 | ❌ Manual | Detectable but requires root user to enable MFA delete |
| S3.22 | ✅ Automated | Security Hub detects object-level write logging |
| S3.23 | ✅ Automated | Security Hub detects object-level read logging |

---

## Manual Controls (12/40 = 30%)

### Why These Cannot Be Automated

**IAM User Actions (11 controls)**
- IAM.2, IAM.3, IAM.4, IAM.5, IAM.6, IAM.9: Require individual user or root user action
- IAM.18: Requires organizational decision on support role design
- IAM.22, IAM.26, IAM.27: Require manual review and cleanup decisions

**Root User Actions (1 control)**
- S3.20: MFA delete requires root user credentials

### Detection vs Remediation

All 12 manual controls are **detectable** by Security Hub - they will show as FAILED findings. However, remediation requires human action because:

1. **Authentication**: MFA setup requires physical devices or authenticator apps
2. **Authorization**: Root account actions cannot be automated for security
3. **Business Logic**: Support roles and policy attachments require organizational decisions
4. **User Interaction**: Individual users must rotate their own credentials

---

## Summary by Category

| Category | Automated | Manual | % Automated |
|----------|-----------|--------|-------------|
| Account | 1 | 0 | 100% |
| CloudTrail | 5 | 0 | 100% |
| Config | 1 | 0 | 100% |
| EC2/VPC | 7 | 0 | 100% |
| EFS | 2 | 0 | 100% |
| IAM | 3 | 10 | 23% |
| KMS | 1 | 0 | 100% |
| RDS | 5 | 0 | 100% |
| S3 | 6 | 1 | 86% |
| **Total** | **28** | **12** | **70%** |

---

## Implementation Coverage

### Preventative Controls (5 controls)
- Account.1: Security contact via Account Management API
- EC2.7: EBS encryption by default
- EC2.8: IMDSv2 required by default
- IAM.15: Password length policy
- IAM.16: Password reuse policy
- S3.8: S3 account public access block

### Detective Controls (28 controls)
All 40 controls are detectable via Security Hub CSPM

### Responsive Controls (5 controls)
- CloudTrail.2: Encrypt CloudTrail logs
- EC2.2: Close default security groups
- EC2.53/54: Remediate security group rules
- S3.1: Enable S3 bucket public access block

---

## Compliance Impact

**Initial Deployment**: 70% of controls automatically compliant  
**After Manual Work**: 95%+ compliance achievable

**Manual effort required**:
- Week 1: Enable root MFA (1 hour)
- Week 2: Enable user MFA, rotate access keys (4-8 hours depending on user count)
- Ongoing: 90-day access key rotation, credential cleanup (1 hour/quarter)
