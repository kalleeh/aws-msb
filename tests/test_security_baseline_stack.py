"""Tests for SecurityBaselineStack"""
import pytest
from aws_cdk import App
from aws_cdk.assertions import Template
from aws_msb_cdk.security_baseline_stack import SecurityBaselineStack


@pytest.fixture
def app():
    return App()


def test_essential_tier(app):
    """Test Essential tier has core security controls"""
    stack = SecurityBaselineStack(app, "TestStack", tier="essential")
    template = Template.from_stack(stack)

    # Security Hub enabled
    template.resource_count_is("AWS::SecurityHub::Hub", 1)

    # 2 standards enabled (CIS + FSBP)
    template.resource_count_is("AWS::SecurityHub::Standard", 2)

    # Config enabled
    template.resource_count_is("AWS::Config::ConfigurationRecorder", 1)

    # CloudTrail enabled
    template.resource_count_is("AWS::CloudTrail::Trail", 1)

    # GuardDuty NOT enabled in essential tier
    template.resource_count_is("AWS::GuardDuty::Detector", 0)


def test_standard_tier(app):
    """Test Standard tier includes GuardDuty and Access Analyzer"""
    stack = SecurityBaselineStack(app, "TestStack", tier="standard")
    template = Template.from_stack(stack)

    # GuardDuty enabled
    template.resource_count_is("AWS::GuardDuty::Detector", 1)

    # Access Analyzer enabled
    template.resource_count_is("AWS::AccessAnalyzer::Analyzer", 1)

    # No auto-remediation in standard tier
    template.resource_count_is("AWS::Config::RemediationConfiguration", 0)


def test_enhanced_tier(app):
    """Test Enhanced tier includes auto-remediation"""
    stack = SecurityBaselineStack(app, "TestStack", tier="enhanced")
    template = Template.from_stack(stack)

    # Auto-remediation configured (2 rules)
    template.resource_count_is("AWS::Config::RemediationConfiguration", 2)


def test_notifications(app):
    """Test SNS notifications when email provided"""
    stack = SecurityBaselineStack(
        app, "TestStack", tier="essential", notification_email="test@example.com"
    )
    template = Template.from_stack(stack)

    # SNS topic created
    template.resource_count_is("AWS::SNS::Topic", 1)

    # Email subscription created
    template.resource_count_is("AWS::SNS::Subscription", 1)
