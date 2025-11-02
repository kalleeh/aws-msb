# Testing Guide

## Overview

AWS MSB includes comprehensive testing to ensure security, reliability, and compliance before deployment.

## Test Suites

### 1. Unit Tests (`test_security_baseline_stack.py`)

Basic resource validation for each tier.

```bash
pytest tests/test_security_baseline_stack.py -v
```

**Tests:**
- Essential tier resources (4 tests)
- Standard tier additions
- Enhanced tier auto-remediation
- SNS notifications

**Coverage:** Basic resource counts and tier logic

### 2. CDK Nag Security Validation (`test_cdk_nag.py`)

AWS Solutions best practices validation using CDK Nag.

```bash
pytest tests/test_cdk_nag.py -v
```

**Tests:**
- Essential tier security (AwsSolutions checks)
- Standard tier security
- Enhanced tier security
- No unsuppressed errors

**Validates:**
- IAM policies follow least privilege
- Encryption enabled on all resources
- Logging and monitoring configured
- No security anti-patterns

**Suppressions:**
- `AwsSolutions-IAM4`: AWS managed policies (required for Config)
- `AwsSolutions-IAM5`: Wildcard permissions (required for service operations)
- `AwsSolutions-S1`: S3 access logging (would create circular dependency)

### 3. Snapshot Tests (`test_snapshots.py`)

Infrastructure validation and security property checks.

```bash
pytest tests/test_snapshots.py -v
```

**Tests (10):**
- KMS key rotation enabled
- S3 encryption enabled
- S3 public access blocked
- CloudTrail encryption enabled
- CloudTrail log validation enabled
- Config all-supported enabled
- SNS encryption enabled

**Purpose:** Detect unintended infrastructure changes

### 4. Integration Tests (`test_integration.py`)

Tier transitions and resource dependencies.

```bash
pytest tests/test_integration.py -v
```

**Tests (9):**
- Tier upgrades (Essential → Standard → Enhanced)
- Multi-region CloudTrail (Standard/Enhanced)
- Single-region CloudTrail (Essential)
- Log retention (90 days vs 365 days)
- Auto-remediation only in Enhanced
- GuardDuty only in Standard/Enhanced
- Optional email notifications

**Purpose:** Validate tier-based conditional logic

## Running All Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=aws_msb_cdk --cov-report=html

# Run specific test file
pytest tests/test_cdk_nag.py -v

# Run specific test
pytest tests/test_cdk_nag.py::test_cdk_nag_aws_solutions_essential -v
```

## Pre-Deployment Validation

Run comprehensive pre-deployment checks:

```bash
./scripts/pre_deploy_check.sh [tier] [email]

# Examples
./scripts/pre_deploy_check.sh essential security@company.com
./scripts/pre_deploy_check.sh standard ops@company.com
./scripts/pre_deploy_check.sh enhanced security@company.com
```

**Checks:**
1. Unit tests (4 tests)
2. CDK Nag security validation (4 tests)
3. Snapshot tests (10 tests)
4. Integration tests (9 tests)
5. CloudFormation synthesis
6. Cost estimation

**Total:** 27 tests

## Test Results

```
✓ 27/27 tests passing (100%)
✓ CDK Nag validation passed
✓ No security violations
✓ All tiers validated
```

## CDK Nag Rules

### Suppressed Rules

| Rule | Reason | Acceptable? |
|------|--------|-------------|
| AwsSolutions-IAM4 | AWS managed policies required for Config service role | ✅ Yes |
| AwsSolutions-IAM5 | Wildcard permissions required for Config/CloudTrail operations | ✅ Yes |
| AwsSolutions-S1 | S3 access logging would create circular dependency | ✅ Yes |

### Enforced Rules

All other AwsSolutions rules are enforced:
- IAM password policies
- Encryption at rest
- Encryption in transit
- Logging and monitoring
- Network security
- Data protection

## Security Validation

### Encryption Checks

```bash
# Verify all S3 buckets encrypted
pytest tests/test_snapshots.py::test_s3_encryption_enabled -v

# Verify KMS key rotation
pytest tests/test_snapshots.py::test_kms_key_rotation_enabled -v

# Verify CloudTrail encryption
pytest tests/test_snapshots.py::test_cloudtrail_encryption_enabled -v
```

### Access Control Checks

```bash
# Verify S3 public access blocked
pytest tests/test_snapshots.py::test_s3_public_access_blocked -v

# Verify Config all-supported
pytest tests/test_snapshots.py::test_config_all_supported_enabled -v
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest tests/ -v --cov=aws_msb_cdk
      - run: ./scripts/pre_deploy_check.sh essential test@example.com
```

## Troubleshooting

### CDK Version Mismatch

**Error:** "Cloud assembly schema version mismatch"

**Solution:**
```bash
npm install -g aws-cdk@latest
```

### Test Failures

**Check test output:**
```bash
pytest tests/ -v --tb=short
```

**Run specific failing test:**
```bash
pytest tests/test_cdk_nag.py::test_cdk_nag_aws_solutions_essential -v
```

### CDK Nag Errors

**View detailed CDK Nag output:**
```bash
pytest tests/test_cdk_nag.py -v -s
```

**Common issues:**
- Missing encryption
- Overly permissive IAM policies
- Missing logging

## Best Practices

1. **Run tests before every deployment**
   ```bash
   ./scripts/pre_deploy_check.sh standard security@company.com
   ```

2. **Run CDK Nag on code changes**
   ```bash
   pytest tests/test_cdk_nag.py -v
   ```

3. **Check snapshot tests for infrastructure changes**
   ```bash
   pytest tests/test_snapshots.py -v
   ```

4. **Validate tier transitions**
   ```bash
   pytest tests/test_integration.py -v
   ```

## Test Coverage

Current coverage: **27 tests, 100% pass rate**

| Test Suite | Tests | Status |
|------------|-------|--------|
| Unit Tests | 4 | ✅ 100% |
| CDK Nag | 4 | ✅ 100% |
| Snapshot Tests | 10 | ✅ 100% |
| Integration Tests | 9 | ✅ 100% |
| **Total** | **27** | **✅ 100%** |

## References

- [CDK Nag Documentation](https://github.com/cdklabs/cdk-nag)
- [AWS Solutions Constructs](https://docs.aws.amazon.com/solutions/latest/constructs/)
- [CDK Testing Best Practices](https://docs.aws.amazon.com/cdk/v2/guide/testing.html)
