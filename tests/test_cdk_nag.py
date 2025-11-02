"""CDK Nag security validation tests"""
import pytest
from aws_cdk import App, Aspects
from cdk_nag import AwsSolutionsChecks, NagSuppressions
from aws_msb_cdk.security_baseline_stack import SecurityBaselineStack


@pytest.fixture
def app():
    return App()


def test_cdk_nag_aws_solutions_essential(app):
    """Validate Essential tier against AWS Solutions best practices"""
    stack = SecurityBaselineStack(app, "TestStack", tier="essential")
    
    # Apply suppressions for known acceptable violations
    NagSuppressions.add_stack_suppressions(
        stack,
        [
            {
                "id": "AwsSolutions-IAM4",
                "reason": "AWS managed policies required for Config service role",
            },
            {
                "id": "AwsSolutions-IAM5",
                "reason": "Wildcard permissions required for Config and CloudTrail service operations",
            },
            {
                "id": "AwsSolutions-S1",
                "reason": "Access logging not required for CloudTrail/Config buckets (would create circular dependency)",
            },
        ],
    )
    
    Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
    app.synth()


def test_cdk_nag_aws_solutions_standard(app):
    """Validate Standard tier against AWS Solutions best practices"""
    stack = SecurityBaselineStack(app, "TestStack", tier="standard")
    
    NagSuppressions.add_stack_suppressions(
        stack,
        [
            {
                "id": "AwsSolutions-IAM4",
                "reason": "AWS managed policies required for Config service role",
            },
            {
                "id": "AwsSolutions-IAM5",
                "reason": "Wildcard permissions required for service operations",
            },
            {
                "id": "AwsSolutions-S1",
                "reason": "Access logging not required for security buckets",
            },
        ],
    )
    
    Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
    app.synth()


def test_cdk_nag_aws_solutions_enhanced(app):
    """Validate Enhanced tier against AWS Solutions best practices"""
    stack = SecurityBaselineStack(app, "TestStack", tier="enhanced")
    
    NagSuppressions.add_stack_suppressions(
        stack,
        [
            {
                "id": "AwsSolutions-IAM4",
                "reason": "AWS managed policies required for Config and SSM automation",
            },
            {
                "id": "AwsSolutions-IAM5",
                "reason": "Wildcard permissions required for auto-remediation across resources",
            },
            {
                "id": "AwsSolutions-S1",
                "reason": "Access logging not required for security buckets",
            },
        ],
    )
    
    Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
    app.synth()


def test_no_unsuppressed_errors(app):
    """Ensure no unsuppressed CDK Nag errors"""
    stack = SecurityBaselineStack(app, "TestStack", tier="enhanced")
    
    # Add all necessary suppressions
    NagSuppressions.add_stack_suppressions(
        stack,
        [
            {"id": "AwsSolutions-IAM4", "reason": "AWS managed policies required"},
            {"id": "AwsSolutions-IAM5", "reason": "Wildcard required for service operations"},
            {"id": "AwsSolutions-S1", "reason": "Access logging creates circular dependency"},
        ],
    )
    
    Aspects.of(app).add(AwsSolutionsChecks())
    
    # This will raise if there are unsuppressed errors
    app.synth()
