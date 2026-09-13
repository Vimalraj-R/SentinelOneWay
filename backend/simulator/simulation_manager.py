"""
Simulation manager for controlling traffic generation.

Manages simulation lifecycle, state, and flow persistence.
"""
import asyncio
import threading
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from .traffic_generator import TrafficGenerator
from .flow_record import FlowRecord


class SimulationState(str, Enum):
    """Simulation states."""
    IDLE = "idle"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"


class SimulationManager:
    """
    Manages network traffic simulation.

    Controls simulation lifecycle and provides interface for
    detection engines to consume generated flows.
    """

    def __init__(self):
        self.generator = TrafficGenerator()
        self.state = SimulationState.IDLE
        self.current_scenario: Optional[str] = None
        self.current_intensity: float = 0.5
        self.generated_flows: List[FlowRecord] = []
        self.flow_callback: Optional[callable] = None
        self.simulation_thread: Optional[threading.Thread] = None
        self.stop_flag = threading.Event()
        self.start_time: Optional[datetime] = None
        self.total_flows_generated = 0

    def set_flow_callback(self, callback: callable):
        """
        Set callback for flow processing.

        The callback will be invoked for each generated flow record,
        allowing detection engines to process flows in real-time.

        Args:
            callback: Function that accepts a FlowRecord
        """
        self.flow_callback = callback

    def start(self, scenario: str, intensity: float = 0.5) -> Dict[str, Any]:
        """
        Start traffic simulation.

        Args:
            scenario: Traffic scenario to simulate
            intensity: Simulation intensity (0.0 to 1.0)

        Returns:
            Status dict

        Raises:
            ValueError: If simulation already running or invalid scenario
        """
        if self.state == SimulationState.RUNNING:
            raise ValueError("Simulation already running")

        valid_scenarios = ['normal', 'syn_flood', 'port_scan', 'c2_beacon', 'dns_tunnel', 'data_exfiltration']
        if scenario not in valid_scenarios:
            raise ValueError(f"Invalid scenario. Valid: {valid_scenarios}")

        self.current_scenario = scenario
        self.current_intensity = max(0.0, min(1.0, intensity))
        self.state = SimulationState.RUNNING
        self.start_time = datetime.now()
        self.generated_flows = []
        self.total_flows_generated = 0
        self.stop_flag.clear()

        # Start generation in background thread
        self.simulation_thread = threading.Thread(
            target=self._generation_loop,
            daemon=True
        )
        self.simulation_thread.start()

        return {
            "status": "started",
            "scenario": self.current_scenario,
            "intensity": self.current_intensity,
            "start_time": self.start_time.isoformat()
        }

    def _generation_loop(self):
        """
        Background loop for continuous flow generation.

        Generates flows periodically until stopped.
        """
        while not self.stop_flag.is_set():
            try:
                # Generate batch of flows
                flows = self.generator.generate_traffic(
                    self.current_scenario,
                    self.current_intensity
                )

                # Store flows
                self.generated_flows.extend(flows)
                self.total_flows_generated += len(flows)

                # Process flows through callback if set
                if self.flow_callback:
                    for flow in flows:
                        try:
                            self.flow_callback(flow)
                        except Exception as e:
                            print(f"Flow callback error: {e}")

                # Sleep between batches (simulate real-time generation)
                if not self.stop_flag.wait(timeout=2.0):
                    continue
                else:
                    break

            except Exception as e:
                print(f"Generation loop error: {e}")
                break

        self.state = SimulationState.STOPPED

    def stop(self) -> Dict[str, Any]:
        """
        Stop running simulation.

        Returns:
            Status dict with statistics
        """
        if self.state != SimulationState.RUNNING:
            return {
                "status": "not_running",
                "message": "No simulation is currently running"
            }

        self.state = SimulationState.STOPPING
        self.stop_flag.set()

        # Wait for thread to finish (max 5 seconds)
        if self.simulation_thread:
            self.simulation_thread.join(timeout=5.0)

        duration = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0

        result = {
            "status": "stopped",
            "scenario": self.current_scenario,
            "duration_seconds": duration,
            "total_flows_generated": self.total_flows_generated,
            "flows_available": len(self.generated_flows)
        }

        self.state = SimulationState.STOPPED
        return result

    def get_status(self) -> Dict[str, Any]:
        """
        Get current simulation status.

        Returns:
            Status dict
        """
        status = {
            "state": self.state.value,
            "scenario": self.current_scenario,
            "intensity": self.current_intensity,
            "total_flows_generated": self.total_flows_generated,
            "flows_in_memory": len(self.generated_flows)
        }

        if self.start_time and self.state == SimulationState.RUNNING:
            duration = (datetime.now() - self.start_time).total_seconds()
            status["duration_seconds"] = duration
            status["flows_per_second"] = self.total_flows_generated / duration if duration > 0 else 0

        return status

    def get_flows(self, limit: Optional[int] = None) -> List[FlowRecord]:
        """
        Get generated flows.

        Args:
            limit: Maximum number of flows to return

        Returns:
            List of flow records
        """
        if limit:
            return self.generated_flows[-limit:]
        return self.generated_flows.copy()

    def clear_flows(self):
        """Clear stored flows from memory."""
        self.generated_flows = []


# Global simulation manager instance
simulation_manager = SimulationManager()
