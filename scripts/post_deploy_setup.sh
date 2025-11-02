#!/bin/bash
# Post-deployment setup script for configurations not supported by CloudFormation
# Run this AFTER deploying the CDK stack

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}AWS MSB Post-Deployment Setup${NC}"
echo "================================"
echo ""

# Check AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI not found. Please install it first.${NC}"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured.${NC}"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "AWS Account: ${GREEN}${ACCOUNT_ID}${NC}"
echo ""

# 1. Set IAM Password Policy (CIS IAM.15, IAM.16)
echo -e "${YELLOW}[1/1] Setting IAM Password Policy...${NC}"
echo "  - Minimum length: 14 characters"
echo "  - Requires: uppercase, lowercase, numbers, symbols"
echo "  - Password reuse prevention: 24 passwords"
echo "  - Max password age: 90 days"
echo ""

read -p "Apply IAM password policy? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    aws iam update-account-password-policy \
        --minimum-password-length 14 \
        --require-symbols \
        --require-numbers \
        --require-uppercase-characters \
        --require-lowercase-characters \
        --allow-users-to-change-password \
        --max-password-age 90 \
        --password-reuse-prevention 24 \
        2>/dev/null && echo -e "${GREEN}✓ IAM password policy configured${NC}" || echo -e "${YELLOW}⚠ Password policy may already be set${NC}"
else
    echo -e "${YELLOW}⊘ Skipped IAM password policy${NC}"
fi

echo ""
echo -e "${GREEN}Post-deployment setup complete!${NC}"
echo ""
echo "Note: IAM password policy only applies to IAM users."
echo "If you use AWS SSO/IAM Identity Center, this policy doesn't apply."
