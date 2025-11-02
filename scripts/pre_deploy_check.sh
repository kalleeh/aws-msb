#!/bin/bash
# Pre-deployment validation script

set -e

echo "========================================="
echo "AWS MSB Pre-Deployment Validation"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠ Virtual environment not activated${NC}"
    echo "Activating .venv..."
    source .venv/bin/activate
fi

# 1. Run unit tests
echo "1. Running unit tests..."
if pytest tests/test_security_baseline_stack.py -v --tb=short; then
    echo -e "${GREEN}✓ Unit tests passed${NC}"
else
    echo -e "${RED}✗ Unit tests failed${NC}"
    exit 1
fi
echo ""

# 2. Run CDK Nag security validation
echo "2. Running CDK Nag security validation..."
if pytest tests/test_cdk_nag.py -v --tb=short; then
    echo -e "${GREEN}✓ CDK Nag validation passed${NC}"
else
    echo -e "${RED}✗ CDK Nag validation failed${NC}"
    exit 1
fi
echo ""

# 3. Run snapshot tests
echo "3. Running snapshot tests..."
if pytest tests/test_snapshots.py -v --tb=short; then
    echo -e "${GREEN}✓ Snapshot tests passed${NC}"
else
    echo -e "${RED}✗ Snapshot tests failed${NC}"
    exit 1
fi
echo ""

# 4. Run integration tests
echo "4. Running integration tests..."
if pytest tests/test_integration.py -v --tb=short; then
    echo -e "${GREEN}✓ Integration tests passed${NC}"
else
    echo -e "${RED}✗ Integration tests failed${NC}"
    exit 1
fi
echo ""

# 5. Synthesize CloudFormation template (optional - may fail with CDK version mismatch)
echo "5. Synthesizing CloudFormation template..."
TIER=${1:-essential}
EMAIL=${2:-test@example.com}

if cdk synth --context tier=$TIER --context email=$EMAIL > /tmp/cdk_synth.out 2>&1; then
    echo -e "${GREEN}✓ CDK synthesis successful${NC}"
    SYNTH_SUCCESS=true
else
    if grep -q "schema version mismatch" /tmp/cdk_synth.out; then
        echo -e "${YELLOW}⚠ CDK CLI version mismatch (non-critical)${NC}"
        echo "  Update CDK CLI: npm install -g aws-cdk@latest"
        SYNTH_SUCCESS=false
    else
        echo -e "${RED}✗ CDK synthesis failed${NC}"
        cat /tmp/cdk_synth.out
        exit 1
    fi
fi
echo ""

# 6. Estimate costs
echo "6. Estimating deployment costs..."
python3 scripts/estimate_costs.py $TIER
echo ""

# Summary
echo "========================================="
if [ "$SYNTH_SUCCESS" = true ]; then
    echo -e "${GREEN}✓ All pre-deployment checks passed!${NC}"
else
    echo -e "${YELLOW}⚠ Pre-deployment checks passed with warnings${NC}"
fi
echo "========================================="
echo ""
echo "Ready to deploy with:"
echo "  cdk deploy --context tier=$TIER --context email=$EMAIL"
echo ""
