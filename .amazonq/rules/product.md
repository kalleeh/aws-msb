# AWS Minimum Security Baseline (MSB) - Product Overview

## Purpose

AWS MSB provides a **simple, cost-optimized security baseline** for small AWS environments, proof-of-concept accounts, and startups. It automates the deployment of essential security controls aligned with industry standards (CIS v5.0, FSBP) using AWS CDK.

## Target Users

- **Small AWS environments** (1-5 accounts)
- **Proof-of-Concept environments** requiring security controls
- **Startups** establishing initial security posture
- **Development/test accounts** needing baseline security

**Not for:** Multi-account enterprises (use AWS Control Tower or AWS Deployment Framework instead)

## Key Features

### Tiered Security Approach

**Essential Tier (~$50/month)**
- Preventative controls (account-level S3 block + EBS encryption by default)
- Security Hub CSPM with CIS v5.0 + AWS FSBP
- AWS Config with service-linked role
- CloudTrail (multi-region, 90-day retention)
- S3 encryption + public access blocks
- KMS with automatic key rotation
- SNS notifications

**Standard Tier (~$150/month)**
- Everything in Essential
- GuardDuty threat detection
- IAM Access Analyzer
- Security Hub cross-region aggregation (all regions)

**Enhanced Tier (~$300/month)**
- Everything in Standard
- Automated remediation (Config auto-remediation with AWS-managed SSM documents)
- Extended log retention (365 days)

### Post-Deployment Configuration
- Security contact information (CIS Account.1)
- AWS Support role (CIS IAM.18)
- Expired SSL certificate cleanup (CIS IAM.26)
- IAM password policy (CIS IAM.15, IAM.16)

## Business Objectives

1. **Simplicity First** - Deploy secure infrastructure in 5 minutes with minimal configuration
2. **Cost Optimization** - Designed for budget-conscious small teams
3. **Compliance Ready** - 80% CIS v5.0 automation (32/40 controls)
4. **No Custom Lambda** - Use AWS-managed services and SSM automation documents
5. **Single Stack** - Avoid complex multi-stack orchestration

## Technical Philosophy

- **Security Hub CSPM as primary interface** - Not Config Conformance Packs
- **AWS-managed remediation** - Config auto-remediation with SSM documents, not custom Lambda
- **Preventative + Detective** - Account-level blocks + Security Hub detection
- **Multi-region by default** - CloudTrail captures all regions (zero extra cost)
- **Service-linked roles** - Use AWS-managed roles (no custom IAM management)
- **Modern AWS patterns** - Use latest AWS services and best practices (2024-2025)

## Key Constraints

- Single AWS account focus (not multi-account Organizations)
- Cost-optimized defaults (90-day logs for Essential tier)
- Regional deployment for most services (CloudTrail and Security Hub are multi-region)
- No custom Lambda for security controls (use AWS-managed solutions)

## Compliance Coverage

- **CIS AWS Foundations Benchmark v5.0**: 32/40 controls (80%) automated
  - 28 controls via CDK (IaC)
  - 4 controls via post-deployment script (CLI)
- **AWS Foundational Security Best Practices**: Full coverage for automated controls
- **Remaining 8 manual controls**: Require root MFA, user MFA, or human judgment
