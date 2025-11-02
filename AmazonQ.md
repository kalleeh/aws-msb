# Amazon Q Implementation Tasks

## Phase 1: Modernize Architecture

### Task 1.1: Create Single Stack Implementation
**Priority**: High  
**Status**: ✅ Completed

Consolidate existing multi-stack architecture into a single `SecurityBaselineStack` with tiered feature flags.

**Requirements**:
- Single stack with Essential/Standard/Enhanced tiers
- Feature flags for conditional resource creation
- Backward compatible with existing deployments

**References**:
- [Architecture Doc](docs/architecture.md)
- [Product Overview](.amazonq/rules/product.md)
- [Tech Stack](.amazonq/rules/tech.md)

**Acceptance Criteria**:
- [ ] `SecurityBaselineStack` class created
- [ ] Tier-based conditional logic implemented
- [ ] All Essential tier resources deployed
- [ ] Tests pass for single stack deployment

---

### Task 1.2: Implement Security Hub CSPM Integration
**Priority**: High  
**Status**: ✅ Completed (CIS v5.0)

Replace Config Conformance Packs with Security Hub CSPM as primary interface.

**Requirements**:
- Enable Security Hub with `CfnHub`
- Enable standards (CIS v3.0, FSBP) with `CfnStandard`
- Configure AWS Config as backend
- Security Hub creates Config rules automatically (service-linked)

**References**:
- [Security Hub CloudFormation Docs](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-securityhub-hub.html)
- [Tech Stack](.amazonq/rules/tech.md) - Standard ARN formats

**Code Example**:
```python
# Enable Security Hub
hub = securityhub.CfnHub(self, "SecurityHub",
    enable_default_standards=False,
    auto_enable_controls=True
)

# Enable CIS v3.0
cis = securityhub.CfnStandard(self, "CIS",
    standards_arn=f"arn:aws:securityhub:{self.region}::standards/cis-aws-foundations-benchmark/v/3.0.0"
)
cis.add_dependency(hub)
```

**Acceptance Criteria**:
- [ ] Security Hub enabled via CloudFormation
- [ ] CIS v3.0 and FSBP standards enabled
- [ ] Config recorder configured for Security Hub
- [ ] Standards visible in Security Hub console

---

### Task 1.3: Implement Config Auto-Remediation
**Priority**: High  
**Status**: ✅ Completed

Add automated remediation using Config auto-remediation with AWS-managed SSM documents.

**Requirements**:
- Map Security Hub controls to Config rules
- Configure auto-remediation for safe controls
- Use AWS-managed SSM automation documents (no custom Lambda)
- Enhanced tier only

**References**:
- [Config Remediation Docs](https://docs.aws.amazon.com/config/latest/developerguide/remediation.html)
- [Tech Stack](.amazonq/rules/tech.md) - SSM document list

**Code Example**:
```python
# Auto-remediate S3 public access
config.CfnRemediationConfiguration(self, "S3PublicAccessRemediation",
    config_rule_name="securityhub-s3-bucket-public-read-prohibited",
    target_type="SSM_DOCUMENT",
    target_identifier="AWS-ConfigureS3BucketPublicAccessBlock",
    automatic=True,
    maximum_automatic_attempts=5,
    retry_attempt_seconds=60
)
```

**Safe Controls for Auto-Remediation**:
- S3 public access blocks
- Security group 0.0.0.0/0 removal
- CloudTrail encryption
- EBS encryption by default

**Acceptance Criteria**:
- [ ] Auto-remediation configured for 5+ controls
- [ ] Only AWS-managed SSM documents used
- [ ] Remediation tested in non-prod environment
- [ ] Documentation updated with remediated controls

---

## Phase 2: Cost Optimization

### Task 2.1: Implement Cost-Optimized Defaults
**Priority**: Medium  
**Status**: ✅ Completed

Configure cost-optimized defaults for small accounts.

**Requirements**:
- Single NAT gateway (not per-AZ)
- 90-day log retention (not 1 year)
- Single region by default
- Optional GuardDuty (parameter-driven)

**References**:
- [Product Overview](.amazonq/rules/product.md) - Cost constraints
- [Architecture Doc](docs/architecture.md) - Cost breakdown

**Acceptance Criteria**:
- [ ] Single NAT gateway deployed
- [ ] CloudWatch Logs retention set to 90 days
- [ ] GuardDuty optional via parameter
- [ ] Cost estimation documented

---

### Task 2.2: Create Cost Estimation Tool
**Priority**: Low  
**Status**: ✅ Completed

Build tool to estimate monthly costs based on tier selection.

**Requirements**:
- Calculate costs for Essential/Standard/Enhanced tiers
- Include AWS service pricing
- Output cost breakdown

**Acceptance Criteria**:
- [ ] Cost calculator script created
- [ ] Costs documented in README
- [ ] Tier comparison table added

---

## Phase 3: Testing & Documentation

### Task 3.1: Update Test Suite for Single Stack
**Priority**: High  
**Status**: ✅ Completed

Refactor tests to validate single stack architecture.

**Requirements**:
- Test Security Hub enablement
- Test standard enablement (CIS, FSBP)
- Test auto-remediation configuration
- Test tier-based conditional logic

**References**:
- [Project Structure](.amazonq/rules/structure.md) - Testing patterns

**Acceptance Criteria**:
- [ ] All tests pass for single stack
- [ ] Coverage >80%
- [ ] Tests for each tier

---

### Task 3.2: Create Deployment Guide
**Priority**: Medium  
**Status**: ✅ Completed

Write comprehensive deployment guide for end users.

**Requirements**:
- Prerequisites
- Step-by-step deployment
- Configuration options
- Troubleshooting

**Acceptance Criteria**:
- [ ] Deployment guide created in docs/
- [ ] Includes tier selection guidance
- [ ] Includes cost estimates
- [ ] Includes troubleshooting section

---

### Task 3.3: Update Compliance Matrix
**Priority**: Medium  
**Status**: ✅ Completed (CIS v5.0)

Update compliance matrix to reflect Security Hub CSPM controls.

**Requirements**:
- Map Security Hub controls to CIS, FSBP, NIST
- Document auto-remediated controls
- Document manual controls

**References**:
- [Existing Compliance Matrix](docs/compliance_matrix.md)

**Acceptance Criteria**:
- [ ] Compliance matrix updated
- [ ] Auto-remediation column added
- [ ] Control coverage documented

---

## Phase 4: Migration & Cleanup

### Task 4.1: Create Migration Guide
**Priority**: Low  
**Status**: ✅ Completed

Document migration path from multi-stack to single stack.

**Requirements**:
- Identify breaking changes
- Provide migration steps
- Include rollback procedure

**Acceptance Criteria**:
- [ ] Migration guide created
- [ ] Tested in non-prod environment
- [ ] Rollback procedure documented

---

### Task 4.2: Deprecate Legacy Stacks
**Priority**: Low  
**Status**: ✅ Completed

Mark legacy multi-stack implementation as deprecated.

**Requirements**:
- Add deprecation notices
- Update README
- Maintain backward compatibility for 1 release

**Acceptance Criteria**:
- [ ] Deprecation notices added
- [ ] README updated
- [ ] Legacy code moved to `legacy/` directory

---

## Quick Reference

### Key Files
- [Product Overview](.amazonq/rules/product.md) - Purpose, users, objectives
- [Tech Stack](.amazonq/rules/tech.md) - AWS services, CDK constructs
- [Project Structure](.amazonq/rules/structure.md) - File organization, patterns
- [Architecture](docs/architecture.md) - System design
- [Compliance Matrix](docs/compliance_matrix.md) - Control mappings

### Key Decisions
1. **Security Hub CSPM** as primary interface (not Config Conformance Packs)
2. **Single stack** architecture (not multi-stack)
3. **AWS-managed SSM documents** for remediation (not custom Lambda)
4. **Cost-first design** for small accounts
5. **Tiered approach** (Essential/Standard/Enhanced)

### Standard ARNs
```python
# CIS v3.0
f"arn:aws:securityhub:{region}::standards/cis-aws-foundations-benchmark/v/3.0.0"

# AWS FSBP
f"arn:aws:securityhub:{region}::standards/aws-foundational-security-best-practices/v/1.0.0"

# NIST 800-53
f"arn:aws:securityhub:{region}::standards/nist-800-53/v/5.0.0"
```
