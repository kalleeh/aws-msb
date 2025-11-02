# AWS Minimum Security Baseline (MSB) - Product Overview

## Purpose

AWS MSB provides a **simple, cost-optimized security baseline** for small AWS environments, proof-of-concept accounts, and startups. It automates the deployment of essential security controls aligned with industry standards (CIS, FSBP, NIST, PCI-DSS) using AWS CDK.

## Target Users

- **Small AWS environments** (1-5 accounts)
- **Proof-of-Concept environments** requiring security controls
- **Startups** establishing initial security posture
- **Development/test accounts** needing baseline security

**Not for:** Multi-account enterprises (use AWS Control Tower or AWS Deployment Framework instead)

## Key Features

### Tiered Security Approach

**Essential Tier (~$50/month)**
- Security Hub CSPM with AWS FSBP standard
- CloudTrail (single region, 90-day retention)
- AWS Config (minimal - only for Security Hub)
- S3 encryption + public access blocks
- IAM password policy
- SNS notifications

**Standard Tier (~$150/month)**
- Everything in Essential
- Security Hub CSPM with CIS AWS Foundations v3.0
- GuardDuty threat detection
- IAM Access Analyzer
- Multi-region CloudTrail
- VPC Flow Logs
- EventBridge automated alerts

**Enhanced Tier (~$300/month)**
- Everything in Standard
- Multi-region deployment
- Security Hub cross-region aggregation
- Automated remediation (Config auto-remediation)
- Extended log retention (1 year)

## Business Objectives

1. **Simplicity First** - Deploy secure infrastructure in 5 minutes with minimal configuration
2. **Cost Optimization** - Designed for budget-conscious small teams
3. **Compliance Ready** - Pass basic security audits (CIS, FSBP, NIST)
4. **No Custom Code** - Use AWS-managed services and SSM automation documents
5. **Single Stack** - Avoid complex multi-stack orchestration

## Technical Philosophy

- **Security Hub CSPM as primary interface** - Not Config Conformance Packs
- **AWS-managed remediation** - Config auto-remediation with SSM documents, not custom Lambda
- **Detection + Remediation** - Security Hub detects, Config remediates
- **Modern AWS patterns** - Use latest AWS services and best practices (2024-2025)

## Key Constraints

- Single AWS account focus (not multi-account Organizations)
- Cost-optimized defaults (single NAT gateway, 90-day logs)
- Regional deployment (not global by default)
- No custom Lambda for security controls (use AWS-managed solutions)
