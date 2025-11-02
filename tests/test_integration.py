"""Integration tests for tier transitions and resource dependencies"""
import pytest
from aws_cdk import App
from aws_cdk.assertions import Template
from aws_msb_cdk.security_baseline_stack import SecurityBaselineStack


def test_tier_upgrade_essential_to_standard():
    """Test upgrading from Essential to Standard tier"""
    # Each tier needs its own app
    essential_app = App()
    essential_stack = SecurityBaselineStack(essential_app, "EssentialStack", tier="essential")
    essential_template = Template.from_stack(essential_stack)
    
    standard_app = App()
    standard_stack = SecurityBaselineStack(standard_app, "StandardStack", tier="standard")
    standard_template = Template.from_stack(standard_stack)
    
    # Verify Standard has all Essential resources
    assert standard_template.find_resources("AWS::SecurityHub::Hub")
    assert standard_template.find_resources("AWS::Config::ConfigurationRecorder")
    assert standard_template.find_resources("AWS::CloudTrail::Trail")
    
    # Verify Standard additions
    assert standard_template.find_resources("AWS::GuardDuty::Detector")
    assert standard_template.find_resources("AWS::AccessAnalyzer::Analyzer")


def test_tier_upgrade_standard_to_enhanced():
    """Test upgrading from Standard to Enhanced tier"""
    standard_app = App()
    standard_stack = SecurityBaselineStack(standard_app, "StandardStack", tier="standard")
    standard_template = Template.from_stack(standard_stack)
    
    enhanced_app = App()
    enhanced_stack = SecurityBaselineStack(enhanced_app, "EnhancedStack", tier="enhanced")
    enhanced_template = Template.from_stack(enhanced_stack)
    
    # Verify Enhanced has all Standard resources
    assert enhanced_template.find_resources("AWS::GuardDuty::Detector")
    assert enhanced_template.find_resources("AWS::AccessAnalyzer::Analyzer")
    
    # Verify Enhanced additions
    remediation = enhanced_template.find_resources("AWS::Config::RemediationConfiguration")
    assert len(remediation) == 2


def test_multi_region_cloudtrail_standard_tier():
    """Verify multi-region CloudTrail in Standard tier"""
    app = App()
    stack = SecurityBaselineStack(app, "TestStack", tier="standard")
    template = Template.from_stack(stack)
    
    template.has_resource_properties(
        "AWS::CloudTrail::Trail",
        {"IsMultiRegionTrail": True}
    )


def test_single_region_cloudtrail_essential_tier():
    """Verify multi-region CloudTrail in Essential tier (zero additional cost)"""
    app = App()
    stack = SecurityBaselineStack(app, "TestStack", tier="essential")
    template = Template.from_stack(stack)
    
    template.has_resource_properties(
        "AWS::CloudTrail::Trail",
        {"IsMultiRegionTrail": True}
    )


def test_log_retention_essential_tier():
    """Verify 90-day log retention in Essential tier"""
    app = App()
    stack = SecurityBaselineStack(app, "TestStack", tier="essential")
    template = Template.from_stack(stack)
    
    # Check lifecycle rules exist with 90-day expiration
    buckets = template.find_resources("AWS::S3::Bucket")
    found_90_day = False
    for bucket in buckets.values():
        lifecycle = bucket.get("Properties", {}).get("LifecycleConfiguration", {})
        rules = lifecycle.get("Rules", [])
        if any(rule.get("ExpirationInDays") == 90 for rule in rules):
            found_90_day = True
            break
    assert found_90_day, "No bucket with 90-day retention found"


def test_log_retention_enhanced_tier():
    """Verify 365-day log retention in Enhanced tier"""
    app = App()
    stack = SecurityBaselineStack(app, "TestStack", tier="enhanced")
    template = Template.from_stack(stack)
    
    # Check lifecycle rules exist with 365-day expiration
    buckets = template.find_resources("AWS::S3::Bucket")
    found_365_day = False
    for bucket in buckets.values():
        lifecycle = bucket.get("Properties", {}).get("LifecycleConfiguration", {})
        rules = lifecycle.get("Rules", [])
        if any(rule.get("ExpirationInDays") == 365 for rule in rules):
            found_365_day = True
            break
    assert found_365_day, "No bucket with 365-day retention found"


def test_auto_remediation_only_enhanced():
    """Verify auto-remediation only exists in Enhanced tier"""
    essential_app = App()
    essential = SecurityBaselineStack(essential_app, "Essential", tier="essential")
    
    standard_app = App()
    standard = SecurityBaselineStack(standard_app, "Standard", tier="standard")
    
    enhanced_app = App()
    enhanced = SecurityBaselineStack(enhanced_app, "Enhanced", tier="enhanced")
    
    # Essential and Standard should have no remediation
    Template.from_stack(essential).resource_count_is("AWS::Config::RemediationConfiguration", 0)
    Template.from_stack(standard).resource_count_is("AWS::Config::RemediationConfiguration", 0)
    
    # Enhanced should have 2 remediation rules
    Template.from_stack(enhanced).resource_count_is("AWS::Config::RemediationConfiguration", 2)


def test_guardduty_only_standard_and_enhanced():
    """Verify GuardDuty only in Standard and Enhanced tiers"""
    essential_app = App()
    essential = SecurityBaselineStack(essential_app, "Essential", tier="essential")
    
    standard_app = App()
    standard = SecurityBaselineStack(standard_app, "Standard", tier="standard")
    
    enhanced_app = App()
    enhanced = SecurityBaselineStack(enhanced_app, "Enhanced", tier="enhanced")
    
    # Essential should not have GuardDuty
    Template.from_stack(essential).resource_count_is("AWS::GuardDuty::Detector", 0)
    
    # Standard and Enhanced should have GuardDuty
    Template.from_stack(standard).resource_count_is("AWS::GuardDuty::Detector", 1)
    Template.from_stack(enhanced).resource_count_is("AWS::GuardDuty::Detector", 1)


def test_notification_email_optional():
    """Verify SNS topic only created when email provided"""
    without_app = App()
    without_email = SecurityBaselineStack(without_app, "WithoutEmail", tier="essential")
    
    with_app = App()
    with_email = SecurityBaselineStack(
        with_app, "WithEmail", tier="essential", notification_email="test@example.com"
    )
    
    # Without email should have no SNS resources
    Template.from_stack(without_email).resource_count_is("AWS::SNS::Topic", 0)
    Template.from_stack(without_email).resource_count_is("AWS::SNS::Subscription", 0)
    
    # With email should have SNS resources
    Template.from_stack(with_email).resource_count_is("AWS::SNS::Topic", 1)
    Template.from_stack(with_email).resource_count_is("AWS::SNS::Subscription", 1)
