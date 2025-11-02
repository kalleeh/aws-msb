#!/usr/bin/env python3
"""Cost estimation tool for AWS MSB tiers"""

COSTS = {
    "essential": {
        "Security Hub": 25,
        "AWS Config": 15,
        "CloudTrail": 5,
        "S3 Storage": 3,
        "KMS": 2,
        "Total": 50,
    },
    "standard": {
        "Security Hub": 25,
        "AWS Config": 15,
        "CloudTrail": 5,
        "S3 Storage": 3,
        "KMS": 2,
        "GuardDuty": 80,
        "Access Analyzer": 10,
        "Multi-region CloudTrail": 10,
        "Total": 150,
    },
    "enhanced": {
        "Security Hub": 25,
        "AWS Config": 15,
        "CloudTrail": 5,
        "S3 Storage": 3,
        "KMS": 2,
        "GuardDuty": 80,
        "Access Analyzer": 10,
        "Multi-region CloudTrail": 10,
        "Auto-remediation": 50,
        "Extended Storage": 100,
        "Total": 300,
    },
}


def estimate_tier(tier: str) -> dict:
    """Estimate monthly costs for a tier"""
    return COSTS.get(tier.lower(), COSTS["essential"])


def print_estimate(tier: str):
    """Print cost estimate for a tier"""
    costs = estimate_tier(tier)
    print(f"\n{tier.upper()} Tier - Monthly Cost Estimate")
    print("=" * 50)
    for service, cost in costs.items():
        if service != "Total":
            print(f"{service:.<40} ${cost:>6}")
    print("-" * 50)
    print(f"{'TOTAL':.<40} ${costs['Total']:>6}/month")


def compare_tiers():
    """Compare all tiers"""
    print("\nAWS MSB Cost Comparison")
    print("=" * 70)
    print(f"{'Tier':<12} {'Monthly Cost':<15} {'Use Case'}")
    print("-" * 70)
    print(f"{'Essential':<12} {'~$50':<15} POC accounts, minimal security")
    print(f"{'Standard':<12} {'~$150':<15} Development/test accounts")
    print(f"{'Enhanced':<12} {'~$300':<15} Production with auto-remediation")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        tier = sys.argv[1]
        print_estimate(tier)
    else:
        compare_tiers()
        print("\nUsage: python estimate_costs.py [essential|standard|enhanced]")
