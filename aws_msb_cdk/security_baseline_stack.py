"""AWS Minimum Security Baseline Stack - Single unified stack with tiered features"""
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    custom_resources as cr,
    aws_securityhub as securityhub,
    aws_config as config,
    aws_guardduty as guardduty,
    aws_cloudtrail as cloudtrail,
    aws_kms as kms,
    aws_s3 as s3,
    aws_iam as iam,
    aws_sns as sns,
    aws_accessanalyzer as accessanalyzer,
)
from constructs import Construct


class SecurityBaselineStack(Stack):
    """Single stack implementing AWS security baseline with Essential/Standard/Enhanced tiers"""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        tier: str = "essential",
        notification_email: str = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.tier = tier
        self.notification_email = notification_email

        # Essential tier - core security controls
        self._setup_preventative_controls()
        self._setup_kms()
        self._setup_cloudtrail()
        self._setup_config()
        self._setup_security_hub()
        if notification_email:
            self._setup_notifications()

        # Standard tier - enhanced detection
        if tier in ["standard", "enhanced"]:
            self._setup_guardduty()
            self._setup_access_analyzer()

        # Enhanced tier - automated remediation
        if tier == "enhanced":
            self._setup_auto_remediation()

    def _setup_preventative_controls(self):
        """Configure account-wide preventative security controls"""
        # Account-level S3 Block Public Access (CIS S3.8)
        cr.AwsCustomResource(
            self,
            "S3AccountPublicAccessBlock",
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
            ),
            on_create=cr.AwsSdkCall(
                service="S3Control",
                action="putPublicAccessBlock",
                parameters={
                    "AccountId": self.account,
                    "PublicAccessBlockConfiguration": {
                        "BlockPublicAcls": True,
                        "IgnorePublicAcls": True,
                        "BlockPublicPolicy": True,
                        "RestrictPublicBuckets": True,
                    },
                },
                physical_resource_id=cr.PhysicalResourceId.of("S3AccountBlock"),
            ),
            on_update=cr.AwsSdkCall(
                service="S3Control",
                action="putPublicAccessBlock",
                parameters={
                    "AccountId": self.account,
                    "PublicAccessBlockConfiguration": {
                        "BlockPublicAcls": True,
                        "IgnorePublicAcls": True,
                        "BlockPublicPolicy": True,
                        "RestrictPublicBuckets": True,
                    },
                },
                physical_resource_id=cr.PhysicalResourceId.of("S3AccountBlock"),
            ),
        )
        
        # EBS Encryption by Default (CIS EC2.7)
        cr.AwsCustomResource(
            self,
            "EBSEncryptionByDefault",
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
            ),
            on_create=cr.AwsSdkCall(
                service="EC2",
                action="enableEbsEncryptionByDefault",
                physical_resource_id=cr.PhysicalResourceId.of("EBSEncryption"),
            ),
        )

    def _setup_kms(self):
        """Create KMS key for encryption"""
        self.kms_key = kms.Key(
            self,
            "SecurityKey",
            description="MSB encryption key",
            enable_key_rotation=True,
            removal_policy=RemovalPolicy.RETAIN,
        )
        
        # Grant CloudTrail permissions to use the key
        self.kms_key.add_to_resource_policy(
            iam.PolicyStatement(
                sid="Allow CloudTrail to encrypt logs",
                principals=[iam.ServicePrincipal("cloudtrail.amazonaws.com")],
                actions=["kms:GenerateDataKey*"],
                resources=["*"],
                conditions={
                    "StringLike": {
                        "kms:EncryptionContext:aws:cloudtrail:arn": [
                            f"arn:aws:cloudtrail:*:{self.account}:trail/*"
                        ]
                    }
                },
            )
        )
        
        self.kms_key.add_to_resource_policy(
            iam.PolicyStatement(
                sid="Allow CloudTrail to describe key",
                principals=[iam.ServicePrincipal("cloudtrail.amazonaws.com")],
                actions=["kms:DescribeKey"],
                resources=["*"],
            )
        )

    def _setup_cloudtrail(self):
        """Configure CloudTrail with encryption and multi-region support"""
        retention = Duration.days(90 if self.tier == "essential" else 365)

        # CloudTrail bucket
        trail_bucket = s3.Bucket(
            self,
            "CloudTrailBucket",
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.kms_key,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            versioned=True,
            lifecycle_rules=[
                s3.LifecycleRule(
                    enabled=True,
                    expiration=retention,
                    noncurrent_version_expiration=Duration.days(30),
                )
            ],
            removal_policy=RemovalPolicy.RETAIN,
        )

        # CloudTrail - always multi-region for comprehensive coverage
        # Single trail in home region captures events from all regions
        self.trail = cloudtrail.Trail(
            self,
            "CloudTrail",
            bucket=trail_bucket,
            encryption_key=self.kms_key,
            enable_file_validation=True,
            include_global_service_events=True,
            is_multi_region_trail=True,  # Always multi-region
            management_events=cloudtrail.ReadWriteType.ALL,
        )

    def _setup_config(self):
        """Configure AWS Config with service-linked role"""
        # Config bucket
        config_bucket = s3.Bucket(
            self,
            "ConfigBucket",
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.kms_key,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            versioned=True,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # Use service-linked role (AWS best practice)
        # AWS Config automatically creates AWSServiceRoleForConfig
        service_linked_role_arn = f"arn:aws:iam::{self.account}:role/aws-service-role/config.amazonaws.com/AWSServiceRoleForConfig"

        # Grant bucket permissions to service-linked role
        config_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="AWSConfigBucketPermissionsCheck",
                principals=[iam.ServicePrincipal("config.amazonaws.com")],
                actions=["s3:GetBucketAcl"],
                resources=[config_bucket.bucket_arn],
            )
        )
        
        config_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="AWSConfigBucketExistenceCheck",
                principals=[iam.ServicePrincipal("config.amazonaws.com")],
                actions=["s3:ListBucket"],
                resources=[config_bucket.bucket_arn],
            )
        )
        
        config_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="AWSConfigBucketPutObject",
                principals=[iam.ServicePrincipal("config.amazonaws.com")],
                actions=["s3:PutObject"],
                resources=[f"{config_bucket.bucket_arn}/*"],
                conditions={
                    "StringEquals": {
                        "s3:x-amz-acl": "bucket-owner-full-control"
                    }
                },
            )
        )

        # Config delivery channel
        self.config_channel = config.CfnDeliveryChannel(
            self,
            "ConfigChannel",
            s3_bucket_name=config_bucket.bucket_name,
        )

        # Config recorder using service-linked role
        self.config_recorder = config.CfnConfigurationRecorder(
            self,
            "ConfigRecorder",
            role_arn=service_linked_role_arn,
            recording_group=config.CfnConfigurationRecorder.RecordingGroupProperty(
                all_supported=True,
                include_global_resource_types=True,
            ),
        )

    def _setup_security_hub(self):
        """Enable Security Hub with CIS v5.0 and FSBP standards"""
        # Enable Security Hub
        hub = securityhub.CfnHub(
            self,
            "SecurityHub",
            enable_default_standards=False,
            auto_enable_controls=True,
        )

        # Enable CIS v5.0
        cis = securityhub.CfnStandard(
            self,
            "CISStandard",
            standards_arn=f"arn:aws:securityhub:{self.region}::standards/cis-aws-foundations-benchmark/v/5.0.0",
        )
        cis.add_dependency(hub)

        # Enable AWS FSBP
        fsbp = securityhub.CfnStandard(
            self,
            "FSBPStandard",
            standards_arn=f"arn:aws:securityhub:{self.region}::standards/aws-foundational-security-best-practices/v/1.0.0",
        )
        fsbp.add_dependency(hub)
        
        # Enable cross-region aggregation (Standard+ tier)
        # This allows viewing findings from all regions in one home region
        if self.tier in ["standard", "enhanced"]:
            aggregator = securityhub.CfnFindingAggregator(
                self,
                "FindingAggregator",
                region_linking_mode="ALL_REGIONS",  # Aggregate from all enabled regions
            )
            aggregator.add_dependency(hub)

    def _setup_notifications(self):
        """Configure SNS notifications for security events"""
        self.notification_topic = sns.Topic(
            self,
            "SecurityNotifications",
            display_name="MSB Security Notifications",
            master_key=self.kms_key,
        )

        if self.notification_email:
            sns.Subscription(
                self,
                "EmailSubscription",
                topic=self.notification_topic,
                endpoint=self.notification_email,
                protocol=sns.SubscriptionProtocol.EMAIL,
            )

    def _setup_guardduty(self):
        """Enable GuardDuty threat detection (Standard tier)"""
        guardduty.CfnDetector(
            self,
            "GuardDuty",
            enable=True,
            finding_publishing_frequency="FIFTEEN_MINUTES",
        )

    def _setup_access_analyzer(self):
        """Enable IAM Access Analyzer (Standard tier)"""
        accessanalyzer.CfnAnalyzer(
            self,
            "AccessAnalyzer",
            type="ACCOUNT",
        )

    def _setup_auto_remediation(self):
        """Configure auto-remediation for safe controls (Enhanced tier)"""
        remediation_role = self._create_remediation_role()

        # S3 public access remediation
        config.CfnRemediationConfiguration(
            self,
            "S3PublicAccessRemediation",
            config_rule_name="securityhub-s3-bucket-public-read-prohibited",
            target_type="SSM_DOCUMENT",
            target_id="AWS-ConfigureS3BucketPublicAccessBlock",
            automatic=True,
            maximum_automatic_attempts=5,
            retry_attempt_seconds=60,
            parameters={
                "AutomationAssumeRole": {
                    "StaticValue": {
                        "Values": [remediation_role.role_arn]
                    }
                },
                "BucketName": {"ResourceValue": {"Value": "RESOURCE_ID"}},
            },
        )

        # Security group remediation
        config.CfnRemediationConfiguration(
            self,
            "SecurityGroupRemediation",
            config_rule_name="securityhub-vpc-default-security-group-closed",
            target_type="SSM_DOCUMENT",
            target_id="AWS-DisablePublicAccessForSecurityGroup",
            automatic=True,
            maximum_automatic_attempts=5,
            retry_attempt_seconds=60,
            parameters={
                "AutomationAssumeRole": {
                    "StaticValue": {
                        "Values": [remediation_role.role_arn]
                    }
                },
                "GroupId": {"ResourceValue": {"Value": "RESOURCE_ID"}},
            },
        )

    def _create_remediation_role(self):
        """Create IAM role for Config auto-remediation"""
        if hasattr(self, "remediation_role"):
            return self.remediation_role

        self.remediation_role = iam.Role(
            self,
            "RemediationRole",
            assumed_by=iam.ServicePrincipal("ssm.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMAutomationRole")
            ],
        )

        # Grant permissions for S3 and EC2 remediation
        self.remediation_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "s3:PutBucketPublicAccessBlock",
                    "ec2:RevokeSecurityGroupIngress",
                    "ec2:RevokeSecurityGroupEgress",
                ],
                resources=["*"],
            )
        )

        return self.remediation_role
