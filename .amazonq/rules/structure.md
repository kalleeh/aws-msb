# Project Structure

## Directory Layout

```
aws-msb-cdk/
├── .amazonq/
│   └── rules/              # Amazon Q context rules
├── app.py                  # CDK app entry point
├── aws_msb_cdk/           # Main package
│   ├── __init__.py
│   ├── security_baseline_stack.py    # Single unified stack
│   ├── iam_stack.py                  # IAM controls (legacy)
│   ├── s3_security_stack.py          # S3 controls (legacy)
│   ├── logging_stack.py              # CloudTrail/CloudWatch (legacy)
│   ├── vpc_stack.py                  # VPC with flow logs (legacy)
│   ├── kms_stack.py                  # KMS encryption (legacy)
│   └── ...                           # Other legacy stacks
├── lambda/                # Lambda functions (if needed)
│   ├── access_analyzer_monitor/
│   └── iam_policy_checker/
├── tests/                 # Test suite
│   ├── unit/
│   ├── test_*.py
│   └── conftest.py
├── docs/                  # Documentation
│   ├── compliance_matrix.md
│   ├── architecture.md
│   └── deployment_guide.md
├── cdk.json              # CDK configuration
├── requirements.txt      # Python dependencies
└── README.md            # Project overview
```

## Naming Conventions

### Stack Names
```python
# Pattern: MSB-{Service}-{Scope}
"MSB-SecurityBaseline"           # New unified stack
"MSB-IAM-Global"                 # Legacy: Global resources
"MSB-VPC-Regional-us-east-1"     # Legacy: Regional resources
```

### Resource Names
```python
# Pattern: msb-{service}-{region}
f"msb-security-hub-{self.region}"
f"msb-cloudtrail-{self.region}"
f"msb-config-recorder-{self.region}"
```

### CDK Construct IDs
```python
# Pattern: PascalCase descriptive names
securityhub.CfnHub(self, "SecurityHub")
securityhub.CfnStandard(self, "CISStandard")
config.CfnRemediationConfiguration(self, "S3PublicAccessRemediation")
```

## File Organization

### Single Stack Pattern (Preferred)
```python
# aws_msb_cdk/security_baseline_stack.py
class SecurityBaselineStack(Stack):
    def __init__(self, scope, id, tier="standard", email=None):
        super().__init__(scope, id)
        
        # Core (Essential tier)
        self._setup_security_hub()
        self._setup_cloudtrail()
        self._setup_config()
        self._setup_s3_security()
        self._setup_iam_policy()
        
        # Standard tier
        if tier in ["standard", "enhanced"]:
            self._setup_guardduty()
            self._setup_access_analyzer()
            self._setup_vpc_flow_logs()
        
        # Enhanced tier
        if tier == "enhanced":
            self._setup_auto_remediation()
```

### Multi-Stack Pattern (Legacy)
```python
# app.py - Legacy approach
iam_stack = IAMStack(app, "MSB-IAM-Global")
kms_stack = KMSStack(app, "MSB-KMS-Global")
logging_stack = LoggingStack(app, "MSB-Logging-Global", kms_stack=kms_stack)
```

## Import Patterns

### Standard Imports
```python
from aws_cdk import (
    Stack,
    aws_securityhub as securityhub,
    aws_config as config,
    aws_guardduty as guardduty,
    aws_cloudtrail as cloudtrail,
    aws_kms as kms,
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_sns as sns,
    aws_events as events,
    aws_events_targets as targets,
    Duration,
    RemovalPolicy,
)
from constructs import Construct
```

### Avoid
```python
# Don't use wildcard imports
from aws_cdk import *

# Don't use custom resources unless absolutely necessary
from aws_cdk import custom_resources as cr
```

## Architectural Decisions

### 1. Single Stack vs Multi-Stack
**Decision:** Migrate to single stack for simplicity
- **Old:** 7+ separate stacks with complex dependencies
- **New:** Single `SecurityBaselineStack` with feature flags

### 2. Security Hub CSPM vs Config Conformance Packs
**Decision:** Use Security Hub CSPM as primary interface
- Security Hub creates Config rules automatically (service-linked)
- Don't deploy Conformance Packs directly
- Add auto-remediation to Security Hub-created rules

### 3. Custom Lambda vs AWS-Managed Solutions
**Decision:** Prefer AWS-managed SSM automation documents
- Use `AWS-ConfigureS3BucketPublicAccessBlock` instead of custom Lambda
- Only use Lambda for complex logic not available in SSM

### 4. L1 vs L2 Constructs
**Decision:** Use L1 (CfnXxx) for Security Hub/Config
- Security Hub and Config don't have L2 constructs
- Use L2 for VPC, CloudTrail where available

### 5. Cost Optimization
**Decision:** Cost-first design for small accounts
- Single NAT gateway (not per-AZ)
- 90-day log retention (not 1 year)
- Single region by default
- Optional GuardDuty (can be expensive)

## Configuration Pattern

### Context-Based Configuration
```python
# app.py
tier = app.node.try_get_context("tier") or "essential"
email = app.node.try_get_context("email")
region = app.node.try_get_context("region") or "us-east-1"

SecurityBaselineStack(app, "MSB", 
    tier=tier,
    notification_email=email,
    env=Environment(region=region)
)
```

### YAML Configuration (Alternative)
```yaml
# config.yaml
tier: standard
email: security@company.com
region: us-east-1
enable_guardduty: true
enable_vpc_flow_logs: true
```

## Testing Structure

```python
# tests/test_security_baseline_stack.py
def test_security_hub_enabled(stack):
    template = Template.from_stack(stack)
    template.has_resource_properties("AWS::SecurityHub::Hub", {
        "EnableDefaultStandards": False
    })

def test_cis_standard_enabled(stack):
    template = Template.from_stack(stack)
    template.has_resource_properties("AWS::SecurityHub::Standard", {
        "StandardsArn": Match.string_like_regexp(".*cis-aws-foundations-benchmark.*")
    })
```

## Documentation Structure

```
docs/
├── architecture.md           # System design and architecture
├── deployment_guide.md       # How to deploy
├── compliance_matrix.md      # Control mappings
├── cost_estimation.md        # Cost breakdown by tier
└── troubleshooting.md        # Common issues
```

## Code Style

- **Line length:** 120 characters
- **Formatting:** Black
- **Linting:** Pylint
- **Type hints:** Preferred but not required
- **Docstrings:** Google style for public methods
