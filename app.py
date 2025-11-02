#!/usr/bin/env python3
"""AWS Minimum Security Baseline (MSB) CDK Application"""
import os
from aws_cdk import App, Environment
from aws_msb_cdk.security_baseline_stack import SecurityBaselineStack

app = App()

# Get configuration from context
tier = app.node.try_get_context("tier") or "essential"
notification_email = app.node.try_get_context("email")
region = app.node.try_get_context("region") or os.environ.get("CDK_DEFAULT_REGION", "us-east-1")
account = os.environ.get("CDK_DEFAULT_ACCOUNT")

if not notification_email:
    print("WARNING: notification_email not provided. Use --context email=your.email@example.com")

# Deploy SecurityBaselineStack
SecurityBaselineStack(
    app,
    "MSB-SecurityBaseline",
    tier=tier,
    notification_email=notification_email,
    env=Environment(account=account, region=region),
)

app.synth()
