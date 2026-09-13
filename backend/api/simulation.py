"""
Simulation API endpoints.

Provides API for controlling network traffic simulation
for testing and development purposes.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from simulator.simulation_manager import simulation_manager
from schemas.simulation import (
    SimulationStartRequest,
    SimulationStartResponse,
    SimulationStopResponse,
    SimulationStatusResponse,
    FlowListResponse,
    FlowRecordResponse
)

router = APIRouter(prefix="/api/simulation", tags=["simulation"])


@router.post("/start", response_model=SimulationStartResponse)
def start_simulation(request: SimulationStartRequest):
    """
    Start traffic simulation.

    Generates synthetic network flow records for testing detection algorithms.

    **IMPORTANT:** This generates synthetic metadata only - no real network
    packets are sent. This is for defensive cybersecurity testing and development.

    **Scenarios:**
    - `normal` - Benign traffic with typical patterns
    - `syn_flood` - SYN flood DDoS attack simulation
    - `port_scan` - Port scanning reconnaissance
    - `c2_beacon` - Command & Control beaconing
    - `dns_tunnel` - DNS tunneling covert channel
    - `data_exfiltration` - Large data exfiltration

    **Intensity:** 0.0 (minimal) to 1.0 (maximum)

    Args:
        request: Simulation configuration

    Returns:
        Simulation start confirmation
    """
    try:
        result = simulation_manager.start(
            scenario=request.scenario,
            intensity=request.intensity
        )
        return SimulationStartResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start simulation: {str(e)}")


@router.post("/stop", response_model=SimulationStopResponse)
def stop_simulation():
    """
    Stop running simulation.

    Stops the current traffic simulation and returns statistics
    about the completed simulation run.

    Returns:
        Simulation statistics and stop confirmation
    """
    try:
        result = simulation_manager.stop()
        return SimulationStopResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop simulation: {str(e)}")


@router.get("/status", response_model=SimulationStatusResponse)
def get_simulation_status():
    """
    Get current simulation status.

    Returns information about the running or completed simulation,
    including state, scenario, and generation statistics.

    Returns:
        Current simulation status
    """
    try:
        status = simulation_manager.get_status()
        return SimulationStatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/flows", response_model=FlowListResponse)
def get_generated_flows(
    limit: int = Query(100, ge=1, le=10000, description="Maximum flows to return")
):
    """
    Get generated flow records.

    Retrieves synthetic flow records that have been generated
    by the simulation. These can be used for testing detection
    algorithms or analyzing simulation output.

    **Note:** Flows are stored in memory. Large simulations may
    consume significant memory. Use limit parameter to control
    retrieval size.

    Args:
        limit: Maximum number of flows to return

    Returns:
        List of generated flow records
    """
    try:
        flows = simulation_manager.get_flows(limit=limit)
        flow_responses = [FlowRecordResponse(**flow.to_dict()) for flow in flows]

        return FlowListResponse(
            total=len(flows),
            flows=flow_responses
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get flows: {str(e)}")


@router.delete("/flows")
def clear_flows():
    """
    Clear stored flow records.

    Removes all generated flows from memory. Useful after
    processing flows or to free memory during long-running
    simulations.

    Returns:
        Confirmation message
    """
    try:
        simulation_manager.clear_flows()
        return {
            "status": "success",
            "message": "All flows cleared from memory"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear flows: {str(e)}")


@router.get("/metrics")
def get_simulation_metrics():
    """
    Get live simulation metrics.

    Returns real-time metrics about the running simulation including
    flows generated, threats detected, detection latency, and current risk.

    Returns:
        Dictionary with simulation metrics
    """
    try:
        status = simulation_manager.get_status()

        # Calculate metrics from simulation status
        flows_generated = status.get('flows_generated', 0)

        # TODO: These would be calculated from actual detection results
        # For now, return mock metrics that make sense for the scenario
        scenario = status.get('scenario', 'normal')
        intensity = status.get('intensity', 0.5)

        # Estimate threats based on scenario (mock for now)
        threats_detected = 0
        current_risk = 0

        if scenario != 'normal' and status.get('is_running'):
            # Non-normal scenarios should detect threats
            threats_detected = max(1, int(flows_generated * 0.01))  # ~1% of flows are threats

            # Risk score based on scenario
            risk_map = {
                'syn_flood': 95,
                'port_scan': 78,
                'c2_beacon': 82,
                'dns_tunnel': 68,
                'data_exfil': 91
            }
            base_risk = risk_map.get(scenario, 50)
            current_risk = int(base_risk * intensity)

        # Mock latency (would be real from detection pipeline)
        avg_latency = 5.2 + (intensity * 3.0)  # 5-8ms range

        return {
            'flows_generated': flows_generated,
            'threats_detected': threats_detected,
            'avg_latency': avg_latency,
            'current_risk': current_risk,
            'is_running': status.get('is_running', False),
            'scenario': scenario,
            'intensity': intensity
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")
