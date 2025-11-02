#!/usr/bin/env python3
"""
Pre-deployment AWS account validation script.
Checks for existing resources that would conflict with MSB deployment.
"""
import boto3
import sys
from botocore.exceptions import ClientError

# ANSI colors
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
GREEN = '\033[0;32m'
NC = '\033[0m'  # No Color

def check_security_hub(region):
    """Check if Security Hub is already enabled"""
    client = boto3.client('securityhub', region_name=region)
    try:
        hub = client.describe_hub()
        standards = client.get_enabled_standards()
        
        print(f"{YELLOW}⚠ Security Hub already enabled{NC}")
        print(f"  Subscribed: {hub['SubscribedAt']}")
        print(f"  Standards enabled: {len(standards['StandardsSubscriptions'])}")
        
        standard_arns = []
        for std in standards['StandardsSubscriptions']:
            std_name = std['StandardsArn'].split('/')[-2]
            print(f"    - {std_name}")
            standard_arns.append(std['StandardsSubscriptionArn'])
        
        print(f"\n  {YELLOW}Cleanup Process (DESTRUCTIVE - deletes all findings):{NC}")
        print(f"  # Step 1: Disable each standard")
        for i, arn in enumerate(standard_arns, 1):
            print(f"  aws securityhub batch-disable-standards --standards-subscription-arns {arn} --region {region}")
        print(f"\n  # Step 2: Wait for standards to disable (check status)")
        print(f"  aws securityhub get-enabled-standards --region {region}")
        print(f"\n  # Step 3: Disable Security Hub")
        print(f"  aws securityhub disable-security-hub --region {region}")
        
        print(f"\n  {GREEN}Recommended: Import existing hub into CDK (preserves data){NC}")
        print(f"  See: https://docs.aws.amazon.com/cdk/v2/guide/resources.html#resources_import")
        return False
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidAccessException':
            print(f"{GREEN}✓ Security Hub not enabled{NC}")
            return True
        raise

def check_config(region):
    """Check if Config is already enabled"""
    client = boto3.client('config', region_name=region)
    try:
        recorder = client.describe_configuration_recorders()
        if recorder['ConfigurationRecorders']:
            recorder_name = recorder['ConfigurationRecorders'][0]['name']
            
            # Check for delivery channel
            try:
                channels = client.describe_delivery_channels()
                channel_name = channels['DeliveryChannels'][0]['name'] if channels['DeliveryChannels'] else None
            except:
                channel_name = None
            
            print(f"{YELLOW}⚠ AWS Config already enabled{NC}")
            print(f"  Recorder: {recorder_name}")
            if channel_name:
                print(f"  Delivery channel: {channel_name}")
            
            print(f"\n  {YELLOW}Cleanup Process (DESTRUCTIVE - loses compliance history):{NC}")
            print(f"  # Step 1: Stop the recorder")
            print(f"  aws configservice stop-configuration-recorder --configuration-recorder-name {recorder_name} --region {region}")
            if channel_name:
                print(f"\n  # Step 2: Delete delivery channel")
                print(f"  aws configservice delete-delivery-channel --delivery-channel-name {channel_name} --region {region}")
            print(f"\n  # Step 3: Delete recorder")
            print(f"  aws configservice delete-configuration-recorder --configuration-recorder-name {recorder_name} --region {region}")
            
            print(f"\n  {RED}WARNING: Must disable Security Hub standards first (they create Config rules){NC}")
            print(f"\n  {GREEN}Recommended: Import existing Config into CDK (preserves data){NC}")
            return False
        else:
            print(f"{GREEN}✓ AWS Config not enabled{NC}")
            return True
    except ClientError:
        print(f"{GREEN}✓ AWS Config not enabled{NC}")
        return True

def check_guardduty(region):
    """Check if GuardDuty is already enabled"""
    client = boto3.client('guardduty', region_name=region)
    try:
        detectors = client.list_detectors()
        if detectors['DetectorIds']:
            detector_id = detectors['DetectorIds'][0]
            print(f"{YELLOW}⚠ GuardDuty already enabled{NC}")
            print(f"  Detector ID: {detector_id}")
            
            print(f"\n  {YELLOW}Cleanup Process (DESTRUCTIVE - deletes threat findings):{NC}")
            print(f"  aws guardduty delete-detector --detector-id {detector_id} --region {region}")
            
            print(f"\n  {GREEN}Recommended: Import existing detector into CDK (preserves findings){NC}")
            return False
        else:
            print(f"{GREEN}✓ GuardDuty not enabled{NC}")
            return True
    except ClientError:
        print(f"{GREEN}✓ GuardDuty not enabled{NC}")
        return True

def check_cloudtrail(region):
    """Check for existing CloudTrail trails"""
    client = boto3.client('cloudtrail', region_name=region)
    try:
        trails = client.describe_trails()
        if trails['trailList']:
            print(f"{YELLOW}⚠ CloudTrail trails exist ({len(trails['trailList'])}){NC}")
            for trail in trails['trailList']:
                print(f"  - {trail['Name']} (multi-region: {trail.get('IsMultiRegionTrail', False)})")
            
            print(f"\n  {YELLOW}Note:{NC} Existing trails won't conflict but may duplicate logging")
            return True
        else:
            print(f"{GREEN}✓ No CloudTrail trails{NC}")
            return True
    except ClientError:
        print(f"{GREEN}✓ No CloudTrail trails{NC}")
        return True

def check_iam_access_analyzer(region):
    """Check if IAM Access Analyzer exists"""
    client = boto3.client('accessanalyzer', region_name=region)
    try:
        analyzers = client.list_analyzers()
        if analyzers['analyzers']:
            print(f"{YELLOW}⚠ IAM Access Analyzer already exists{NC}")
            for analyzer in analyzers['analyzers']:
                print(f"  - {analyzer['name']} (status: {analyzer['status']})")
            
            print(f"\n  {YELLOW}Note:{NC} Existing analyzer won't conflict but may duplicate findings")
            return True
        else:
            print(f"{GREEN}✓ No IAM Access Analyzer{NC}")
            return True
    except ClientError:
        print(f"{GREEN}✓ No IAM Access Analyzer{NC}")
        return True

def check_existing_stacks(region):
    """Check for existing MSB CloudFormation stacks"""
    client = boto3.client('cloudformation', region_name=region)
    try:
        stacks = client.list_stacks(
            StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE', 'ROLLBACK_COMPLETE']
        )
        msb_stacks = [s for s in stacks['StackSummaries'] if 'MSB' in s['StackName']]
        
        if msb_stacks:
            print(f"{YELLOW}⚠ Existing MSB stacks found{NC}")
            for stack in msb_stacks:
                print(f"  - {stack['StackName']} ({stack['StackStatus']})")
            
            print(f"\n  {YELLOW}Cleanup Process:{NC}")
            for stack in msb_stacks:
                print(f"  aws cloudformation delete-stack --stack-name {stack['StackName']} --region {region}")
            print(f"\n  # Wait for deletion to complete")
            print(f"  aws cloudformation wait stack-delete-complete --stack-name <name> --region {region}")
            return False
        else:
            print(f"{GREEN}✓ No existing MSB stacks{NC}")
            return True
    except ClientError:
        print(f"{GREEN}✓ No existing MSB stacks{NC}")
        return True

def main():
    # Get current region
    session = boto3.Session()
    region = session.region_name or 'us-east-1'
    
    print("=" * 60)
    print("AWS Account Pre-Deployment Validation")
    print("=" * 60)
    print(f"Region: {region}")
    print(f"Account: {boto3.client('sts').get_caller_identity()['Account']}")
    print()
    
    checks = [
        ("Security Hub", check_security_hub),
        ("AWS Config", check_config),
        ("GuardDuty", check_guardduty),
        ("CloudTrail", check_cloudtrail),
        ("IAM Access Analyzer", check_iam_access_analyzer),
        ("Existing Stacks", check_existing_stacks),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\nChecking {name}...")
        try:
            results.append(check_func(region))
        except Exception as e:
            print(f"{RED}✗ Error checking {name}: {e}{NC}")
            results.append(False)
    
    print("\n" + "=" * 60)
    if all(results):
        print(f"{GREEN}✓ Account ready for deployment{NC}")
        print("\nDeploy with:")
        print(f"  cdk deploy --context tier=essential --context email=your@email.com")
        sys.exit(0)
    else:
        print(f"{RED}✗ Account has conflicts{NC}")
        print("\n" + "=" * 60)
        print("DEPLOYMENT OPTIONS:")
        print("=" * 60)
        print(f"\n{YELLOW}Option 1: Clean Account (DESTRUCTIVE){NC}")
        print("  - Follow cleanup steps above (deletes all security data)")
        print("  - Correct order: Stack → Security Hub → Config")
        print("  - Time: 15-30 minutes")
        print("  - Risk: Loses all findings, compliance history")
        
        print(f"\n{GREEN}Option 2: Import Resources (RECOMMENDED){NC}")
        print("  - Import existing resources into CDK stack")
        print("  - Preserves all data and findings")
        print("  - Requires CDK resource import process")
        print("  - See: https://docs.aws.amazon.com/cdk/v2/guide/resources.html#resources_import")
        
        print(f"\n{YELLOW}Option 3: Fresh Account{NC}")
        print("  - Deploy to a new/clean AWS account instead")
        print("  - Recommended for testing MSB")
        
        print("\n" + "=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
