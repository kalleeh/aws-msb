# AWS Minimum Security Baseline (MSB) CDK

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![AWS](https://img.shields.io/badge/AWS-CDK-orange)

Simple, cost-optimized security baseline for small AWS environments using AWS CDK.

> **⚠️ DEPRECATION NOTICE:** The legacy multi-stack architecture is deprecated. See [DEPRECATION.md](DEPRECATION.md) for details. Use the single-stack architecture below.

---

## Quick Start

```bash
# Install
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Validate AWS account (checks for conflicts)
python scripts/check_aws_account.py

# Deploy Essential tier (~$50/month)
cdk deploy --context tier=essential --context email=security@company.com

# Deploy Standard tier (~$150/month)
cdk deploy --context tier=standard --context email=security@company.com

# Deploy Enhanced tier with auto-remediation (~$300/month)
cdk deploy --context tier=enhanced --context email=security@company.com
```

**See [docs/deployment_guide.md](docs/deployment_guide.md) for detailed instructions.**

---

## Features

✅ **Single Stack Architecture** - Deploy in 5 minutes with one command  
✅ **Security Hub CSPM** - CIS AWS Foundations v5.0 + AWS FSBP standards  
✅ **Multi-Region Coverage** - CloudTrail captures events from all regions (all tiers)  
✅ **Cross-Region Aggregation** - Security Hub aggregates findings from all regions (Standard+)  
✅ **Service-Linked Roles** - Uses AWS-managed roles (no custom IAM management)  
✅ **70% Automated** - 28/40 CIS v5.0 controls automated  
✅ **Auto-Remediation** - Config auto-remediation with AWS-managed SSM documents (Enhanced tier)  
✅ **No Custom Lambda** - Uses AWS-managed services only  

---

## What Gets Deployed

### Essential Tier (~$50/month)
- Security Hub with CIS v5.0 + AWS FSBP
- AWS Config with service-linked role
- CloudTrail (multi-region, 90-day retention)
- S3 encryption + public access blocks
- KMS with automatic key rotation
- SNS notifications

### Standard Tier (~$150/month)
Everything in Essential, plus:
- GuardDuty threat detection
- IAM Access Analyzer
- Security Hub cross-region aggregation

### Enhanced Tier (~$300/month)
Everything in Standard, plus:
- Automated remediation (2 AWS-managed SSM documents)
- Extended log retention (365 days)

---

## Compliance Coverage

**CIS AWS Foundations Benchmark v5.0:**
- 28/40 controls (70%) automated
- 12/40 controls (30%) manual (IAM MFA, access keys, etc.)

**AWS Foundational Security Best Practices:**
- Full coverage for automated controls

**See [docs/compliance_matrix.md](docs/compliance_matrix.md) for details.**

---

## Architecture

**Single Stack** with tiered features and multi-region support:

```
Essential Tier (Core Security)
  ├── Security Hub CSPM (CIS v5.0 + FSBP)
  ├── AWS Config (service-linked role)
  ├── CloudTrail (multi-region, encrypted)
  ├── S3 Security (encrypted, public access blocked)
  ├── KMS (automatic key rotation)
  └── SNS Notifications

Standard Tier (Enhanced Detection + Multi-Region)
  ├── Everything in Essential
  ├── GuardDuty (threat detection)
  ├── IAM Access Analyzer
  └── Security Hub cross-region aggregation

Enhanced Tier (Auto-Remediation)
  ├── Everything in Standard
  ├── Config auto-remediation (2 AWS-managed rules)
  └── Extended log retention (365 days)
```

**Key Features:**
- **Multi-Region CloudTrail**: All tiers capture events from all AWS regions (no extra cost)
- **Cross-Region Aggregation**: Standard+ tiers aggregate Security Hub findings from all regions
- **Service-Linked Roles**: AWS-managed Config role (no custom IAM management)
- **Single Deployment**: Deploy once in home region, get multi-region coverage

**Key Decisions:**
- Security Hub CSPM as primary interface (not Config Conformance Packs)
- AWS-managed SSM documents for remediation (no custom Lambda)
- AWS service-linked roles (no custom IAM roles)
- Single stack deployment (not multi-stack)
- Multi-region by default (CloudTrail all tiers, Security Hub Standard+)

---

## Documentation

### Getting Started
- **[Deployment Guide](docs/deployment_guide.md)** - Step-by-step deployment with tier selection
- **[Architecture](docs/architecture.md)** - System design, multi-region setup, components

### Reference
- **[Compliance Matrix](docs/compliance_matrix.md)** - CIS v5.0 and FSBP control mappings
- **[CIS v5.0 Analysis](docs/cis_v5_control_analysis.md)** - Detailed control breakdown (28 automated, 12 manual)
- **[Testing Guide](docs/testing_guide.md)** - Running tests and validation

### For Contributors
- **[Development Guide](docs/development_guide.md)** - Project structure and contribution workflow
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines

---

## Cost Breakdown

| Tier | Monthly Cost | Use Case |
|------|--------------|----------|
| **Essential** | ~$50 | POC accounts, minimal security |
| **Standard** | ~$150 | Development/test accounts |
| **Enhanced** | ~$300 | Production with auto-remediation |

**Essential Tier Breakdown:**
- Security Hub: ~$25
- Config: ~$15
- CloudTrail: ~$5
- S3 storage: ~$3
- **Total: ~$50/month**

**See [docs/deployment_guide.md](docs/deployment_guide.md) for detailed cost breakdown.**

---

## When NOT to Use This

❌ **Multi-account organizations (>5 accounts)** - Use [AWS Control Tower](https://aws.amazon.com/controltower/)  
❌ **Enterprise deployments** - Use [AWS Deployment Framework](https://github.com/awslabs/aws-deployment-framework)  
❌ **Complex compliance requirements** - Consider custom implementation  

---

## Requirements

- AWS Account with administrative access
- AWS CLI configured
- Node.js 18+ and Python 3.9+
- AWS CDK CLI: `npm install -g aws-cdk`

---

## Development

```bash
# Run all tests (27 tests)
pytest tests/ -v

# Run pre-deployment validation
./scripts/pre_deploy_check.sh essential security@company.com

# Run CDK Nag security validation
pytest tests/test_cdk_nag.py -v

# Run with coverage
pytest --cov=aws_msb_cdk --cov-report=html

# Format code
black aws_msb_cdk tests

# Lint code
pylint aws_msb_cdk
```

**Test Coverage:** 27/27 tests passing (100%)
- 4 unit tests
- 4 CDK Nag security tests
- 10 snapshot tests
- 9 integration tests

See [Testing Guide](docs/testing_guide.md) for details.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License - see [LICENSE](LICENSE) for details.
