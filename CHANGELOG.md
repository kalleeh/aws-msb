# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-02

### Added
- Single-stack architecture with Essential/Standard/Enhanced tiers
- Security Hub CSPM integration with CIS v5.0 controls
- Multi-region CloudTrail for all tiers (zero additional cost)
- Cross-region Security Hub aggregation for Standard+ tiers
- Service-linked role for AWS Config (AWS best practice)
- Comprehensive documentation suite (8 core documents)
- Pre-deployment validation script (`scripts/check_aws_account.py`)
- Cost estimation tool (`scripts/estimate_costs.py`)
- CDK Nag integration for security validation

### Changed
- Migrated from multi-stack to single-stack architecture
- Replaced Config Conformance Packs with Security Hub CSPM
- CloudTrail now multi-region for all tiers (previously Essential was single-region)
- Config uses service-linked role instead of custom IAM role
- Updated to CIS AWS Foundations Benchmark v5.0

### Security
- Implemented account-level S3 public access block
- Added KMS encryption for CloudTrail logs
- Configured Security Hub with SECURITY_CONTROL mode (CSPM)
- Enabled 39 CIS v5.0 controls automatically

### Fixed
- Resolved CloudTrail KMS key policy permissions
- Fixed Config recorder circular dependency with service-linked role
- Corrected Config role policy naming convention

## [Unreleased]

### Planned
- Auto-remediation for common security findings (Enhanced tier)
- Additional compliance frameworks (NIST 800-53, PCI-DSS)
- Multi-account deployment via AWS Organizations
