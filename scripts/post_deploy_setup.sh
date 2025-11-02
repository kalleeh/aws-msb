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

# 1. Set Security Contact (CIS Account.1)
echo -e "${YELLOW}[1/2] Setting Security Contact Information...${NC}"
echo "AWS will use this contact for security notifications."
echo ""

read -p "Enter security contact email: " SECURITY_EMAIL
read -p "Enter security contact name: " SECURITY_NAME
read -p "Enter security contact phone (e.g., +1-555-0100): " SECURITY_PHONE

if [[ -n "$SECURITY_EMAIL" && -n "$SECURITY_NAME" && -n "$SECURITY_PHONE" ]]; then
    aws account put-alternate-contact \
        --alternate-contact-type SECURITY \
        --email-address "$SECURITY_EMAIL" \
        --name "$SECURITY_NAME" \
        --phone-number "$SECURITY_PHONE" \
        --title "Security Contact" \
        2>/dev/null && echo -e "${GREEN}✓ Security contact configured${NC}" || echo -e "${YELLOW}⚠ Failed to set security contact (may need account permissions)${NC}"
else
    echo -e "${YELLOW}⊘ Skipped security contact (missing information)${NC}"
fi

echo ""

# 2. Create AWS Support Role (CIS IAM.18)
echo -e "${YELLOW}[2/4] Creating AWS Support Role...${NC}"
echo "This allows AWS Support to access your account when you create support cases."
echo ""

read -p "Create AWS Support role? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Check if role already exists
    if aws iam get-role --role-name AWSSupportAccess &>/dev/null; then
        echo -e "${YELLOW}⊘ AWSSupportAccess role already exists${NC}"
    else
        # Create trust policy
        TRUST_POLICY='{
          "Version": "2012-10-17",
          "Statement": [{
            "Effect": "Allow",
            "Principal": {"AWS": "arn:aws:iam::'$ACCOUNT_ID':root"},
            "Action": "sts:AssumeRole"
          }]
        }'
        
        aws iam create-role \
            --role-name AWSSupportAccess \
            --assume-role-policy-document "$TRUST_POLICY" \
            --description "Allows AWS Support to access account for support cases" \
            &>/dev/null && \
        aws iam attach-role-policy \
            --role-name AWSSupportAccess \
            --policy-arn arn:aws:iam::aws:policy/AWSSupportAccess \
            &>/dev/null && \
        echo -e "${GREEN}✓ AWS Support role created${NC}" || \
        echo -e "${RED}✗ Failed to create support role${NC}"
    fi
else
    echo -e "${YELLOW}⊘ Skipped AWS Support role${NC}"
fi

echo ""

# 3. Delete Expired SSL Certificates (CIS IAM.26)
echo -e "${YELLOW}[3/4] Checking for Expired SSL Certificates...${NC}"

EXPIRED_CERTS=$(aws iam list-server-certificates --query 'ServerCertificateMetadataList[?Expiration<`'$(date -u +%Y-%m-%d)'`].ServerCertificateName' --output text 2>/dev/null)

if [[ -n "$EXPIRED_CERTS" ]]; then
    echo "Found expired certificates:"
    echo "$EXPIRED_CERTS" | tr '\t' '\n' | sed 's/^/  - /'
    echo ""
    read -p "Delete expired certificates? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        for cert in $EXPIRED_CERTS; do
            aws iam delete-server-certificate --server-certificate-name "$cert" 2>/dev/null && \
            echo -e "${GREEN}✓ Deleted $cert${NC}" || \
            echo -e "${RED}✗ Failed to delete $cert${NC}"
        done
    else
        echo -e "${YELLOW}⊘ Skipped certificate deletion${NC}"
    fi
else
    echo -e "${GREEN}✓ No expired certificates found${NC}"
fi

echo ""

# 4. Set IAM Password Policy (CIS IAM.15, IAM.16)
echo -e "${YELLOW}[4/4] Setting IAM Password Policy...${NC}"
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
echo "Security controls configured:"
echo "  ✓ Security contact information (CIS Account.1)"
echo "  ✓ AWS Support role (CIS IAM.18)"
echo "  ✓ Expired certificate cleanup (CIS IAM.26)"
echo "  ✓ IAM password policy (CIS IAM.15, IAM.16)"
echo ""
echo "Note: IAM password policy only applies to IAM users."
echo "If you use AWS SSO/IAM Identity Center, this policy doesn't apply."
