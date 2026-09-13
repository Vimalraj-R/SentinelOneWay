"""
Test script for SentinelOneWay simulation API.

This script demonstrates how to use the simulation endpoints
to generate synthetic network traffic for testing detection algorithms.

IMPORTANT: This only generates synthetic flow metadata - no real
network packets are sent. Safe for development and testing.
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000/api/simulation"


def test_simulation_workflow():
    """Test complete simulation workflow."""

    print("=== SentinelOneWay Traffic Simulation Test ===\n")

    # 1. Check initial status
    print("1. Checking initial status...")
    response = requests.get(f"{BASE_URL}/status")
    print(f"   Status: {response.json()}\n")

    # 2. Start SYN flood simulation
    print("2. Starting SYN flood simulation (intensity 0.8)...")
    start_request = {
        "scenario": "syn_flood",
        "intensity": 0.8
    }
    response = requests.post(f"{BASE_URL}/start", json=start_request)
    print(f"   Response: {response.json()}\n")

    # 3. Wait and check status
    print("3. Waiting 5 seconds for flow generation...")
    time.sleep(5)

    response = requests.get(f"{BASE_URL}/status")
    status = response.json()
    print(f"   Running status: {status}")
    print(f"   Flows generated: {status['total_flows_generated']}")
    print(f"   Generation rate: {status.get('flows_per_second', 0):.2f} flows/sec\n")

    # 4. Get sample flows
    print("4. Retrieving 3 sample flows...")
    response = requests.get(f"{BASE_URL}/flows?limit=3")
    flows_data = response.json()
    print(f"   Total flows available: {flows_data['total']}")

    for i, flow in enumerate(flows_data['flows'], 1):
        print(f"\n   Flow {i}:")
        print(f"     ID: {flow['flow_id']}")
        print(f"     {flow['src_ip']}:{flow['src_port']} -> {flow['dst_ip']}:{flow['dst_port']}")
        print(f"     Protocol: {flow['protocol']}, Packets: {flow['packet_count']}")
        print(f"     SYN: {flow['syn_count']}, ACK: {flow['ack_count']}")
        print(f"     SYN/ACK ratio: {flow['syn_count'] / max(flow['ack_count'], 1):.1f}")

    print("\n5. Stopping simulation...")
    response = requests.post(f"{BASE_URL}/stop")
    stop_data = response.json()
    print(f"   Result: {stop_data}")
    print(f"   Duration: {stop_data['duration_seconds']:.2f} seconds")
    print(f"   Total flows: {stop_data['total_flows_generated']}\n")

    # 6. Test other scenarios
    print("6. Testing other scenarios...")
    scenarios = ["normal", "port_scan", "c2_beacon", "dns_tunnel", "data_exfiltration"]

    for scenario in scenarios:
        print(f"\n   Starting {scenario} simulation...")
        response = requests.post(f"{BASE_URL}/start", json={
            "scenario": scenario,
            "intensity": 0.5
        })
        print(f"   Started: {response.json()['status']}")

        time.sleep(3)

        response = requests.get(f"{BASE_URL}/status")
        status = response.json()
        print(f"   Generated {status['total_flows_generated']} flows")

        response = requests.post(f"{BASE_URL}/stop")
        print(f"   Stopped: {response.json()['status']}")

    # 7. Clear flows
    print("\n7. Clearing flows from memory...")
    response = requests.delete(f"{BASE_URL}/flows")
    print(f"   Result: {response.json()}\n")

    print("=== All tests completed successfully ===")


def demonstrate_scenario_characteristics():
    """Show characteristics of each scenario."""

    print("\n=== Traffic Scenario Characteristics ===\n")

    scenarios = {
        "normal": "Benign traffic with balanced ratios and varied destinations",
        "syn_flood": "High SYN count, few ACKs, diverse sources to single target",
        "port_scan": "Single source scanning many ports on target",
        "c2_beacon": "Regular periodic connections to same external server",
        "dns_tunnel": "High-entropy long DNS queries for covert data transfer",
        "data_exfiltration": "Large outbound data transfers with high out/in ratio"
    }

    for scenario, description in scenarios.items():
        print(f"{scenario:20s} - {description}")

    print("\nIntensity values:")
    print("  0.0 - Minimal traffic generation")
    print("  0.5 - Moderate traffic (default)")
    print("  1.0 - Maximum traffic generation")


if __name__ == "__main__":
    try:
        print("SentinelOneWay Simulation API Test\n")
        print("Make sure the backend server is running on port 8000")
        print("Start it with: python -m uvicorn main:app --reload\n")

        input("Press Enter to continue...")

        test_simulation_workflow()
        demonstrate_scenario_characteristics()

    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to backend server.")
        print("Please start the server first:")
        print("  cd backend")
        print("  python -m uvicorn main:app --reload")

    except Exception as e:
        print(f"\nError: {e}")
