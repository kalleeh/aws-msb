"""Snapshot tests to detect unintended infrastructure changes"""
import json
import pytest
from aws_cdk import App
from aws_cdk.assertions import Template
from aws_msb_cdk.security_baseline_stack import SecurityBaselineStack


@pytest.fixture
def app():
    return App()


def test_essential_tier_snapshot(app):
    """Snapshot test for Essential tier infrastructure"""
    stack = SecurityBaselineStack(app, "TestStack", tier="essential")
    template = Template.from_stack(stack)
    
    # Verify critical resources exist
    assert template.find_resources("AWS::SecurityHub::Hub")
    assert template.find_resources("AWS::SecurityHub::Standard")
    assert template.find_resources("AWS::Config::ConfigurationRecorder")
    assert template.find_resources("AWS::CloudTrail::Trail")
    assert template.find_resources("AWS::KMS::Key")
    assert template.find_resources("AWS::S3::Bucket")


def test_standard_tier_snapshot(app):
    """Snapshot test for Standard tier infrastructure"""
    stack = SecurityBaselineStack(app, "TestStack", tier="standard")
    template = Template.from_stack(stack)
    
    # Verify Standard tier additions
    assert template.find_resources("AWS::GuardDuty::Detector")
    assert template.find_resources("AWS::AccessAnalyzer::Analyzer")


def test_enhanced_tier_snapshot(app):
    """Snapshot test for Enhanced tier infrastructure"""
    stack = SecurityBaselineStack(app, "TestStack", tier="enhanced")
    template = Template.from_stack(stack)
    
    # Verify Enhanced tier additions
    remediation_configs = template.find_resources("AWS::Config::RemediationConfiguration")
    assert len(remediation_configs) == 2, "Should have 2 auto-remediation rules"


def test_kms_key_rotation_enabled(app):
    """Verify KMS key rotation is enabled"""
    stack = SecurityBaselineStack(app, "TestStack", tier="essential")
    template = Template.from_stack(stack)
    
    template.has_resource_properties(
        "AWS::KMS::Key",
        {"EnableKeyRotation": True}
    )


def test_s3_encryption_enabled(app):
    """Verify S3 buckets have encryption"""
    stack = SecurityBaselineStack(app, "TestStack", tier="essential")
    template = Template.from_stack(stack)
    
    buckets = template.find_resources("AWS::S3::Bucket")
    for bucket_id, bucket in buckets.items():
        assert "BucketEncryption" in bucket["Properties"], f"Bucket {bucket_id} missing encryption"


def test_s3_public_access_blocked(app):
    """Verify S3 buckets block public access"""
    stack = SecurityBaselineStack(app, "TestStack", tier="essential")
    template = Template.from_stack(stack)
    
    buckets = template.find_resources("AWS::S3::Bucket")
    for bucket_id, bucket in buckets.items():
        public_access = bucket["Properties"].get("PublicAccessBlockConfiguration", {})
        assert public_access.get("BlockPublicAcls") == True
        assert public_access.get("BlockPublicPolicy") == True
        assert public_access.get("IgnorePublicAcls") == True
        assert public_access.get("RestrictPublicBuckets") == True


def test_cloudtrail_encryption_enabled(app):
    """Verify CloudTrail has KMS encryption"""
    stack = SecurityBaselineStack(app, "TestStack", tier="essential")
    template = Template.from_stack(stack)
    
    trails = template.find_resources("AWS::CloudTrail::Trail")
    for trail_id, trail in trails.items():
        assert "KMSKeyId" in trail["Properties"], f"Trail {trail_id} missing KMS encryption"


def test_cloudtrail_log_validation_enabled(app):
    """Verify CloudTrail log file validation is enabled"""
    stack = SecurityBaselineStack(app, "TestStack", tier="essential")
    template = Template.from_stack(stack)
    
    template.has_resource_properties(
        "AWS::CloudTrail::Trail",
        {"EnableLogFileValidation": True}
    )


def test_config_all_supported_enabled(app):
    """Verify Config records all supported resources"""
    stack = SecurityBaselineStack(app, "TestStack", tier="essential")
    template = Template.from_stack(stack)
    
    template.has_resource_properties(
        "AWS::Config::ConfigurationRecorder",
        {
            "RecordingGroup": {
                "AllSupported": True,
                "IncludeGlobalResourceTypes": True,
            }
        }
    )


def test_sns_encryption_enabled(app):
    """Verify SNS topics have KMS encryption"""
    stack = SecurityBaselineStack(
        app, "TestStack", tier="essential", notification_email="test@example.com"
    )
    template = Template.from_stack(stack)
    
    topics = template.find_resources("AWS::SNS::Topic")
    for topic_id, topic in topics.items():
        assert "KmsMasterKeyId" in topic["Properties"], f"Topic {topic_id} missing KMS encryption"
