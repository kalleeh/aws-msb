# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-02

### Added
- Single-stack architecture with Essential/Standard/Enhanced tiers
- Security Hub CSPM integration with CIS v5.0 controls (39 controls enabled)
- Multi-region CloudTrail for all tiers (zero additional cost)
- Cross-region Security Hub aggregation for Standard+ tiers
- Service-linked role for AWS Config (AWS best practice)
- Account-level S3 Block Public Access (preventative control)
- EBS encryption by default (preventative control)
- Post-deployment setup script for manual configurations
- Security contact configuration (CIS Account.1)
- AWS Support role creation (CIS IAM.18)
- Expired SSL certificate cleanup (CIS IAM.26)
- IAM password policy enforcement (CIS IAM.15, IAM.16)
- Comprehensive documentation suite (8 core documents)
- Pre-deployment validation script (`scripts/check_aws_account.py`)
- Post-deployment setup script (`scripts/post_deploy_setup.sh`)
- Cost estimation tool (`scripts/estimate_costs.py`)
- CDK Nag integration for security validation
- 80% CIS control automation (32/40 controls)

### Changed
- Migrated from multi-stack to single-stack architecture
- Replaced Config Conformance Packs with Security Hub CSPM
- CloudTrail now multi-region for all tiers (previously Essential was single-region)
- Config uses service-linked role instead of custom IAM role
- Updated to CIS AWS Foundations Benchmark v5.0

### Security
- Implemented account-level S3 public access block (CIS S3.8)
- Enabled EBS encryption by default (CIS EC2.7)
- Added KMS encryption for CloudTrail logs
- Configured Security Hub with SECURITY_CONTROL mode (CSPM)
- Auto-remediation for S3 public access and security groups (Enhanced tier)

### Fixed
- Resolved CloudTrail KMS key policy permissions
- Fixed Config recorder circular dependency with service-linked role
- Corrected Config role policy naming convention
- Fixed pre-commit hook reference to deleted test file

## [Unreleased]

### Planned
- Auto-remediation for common security findings (Enhanced tier)
- Additional compliance frameworks (NIST 800-53, PCI-DSS)
- Multi-account deployment via AWS Organizations
