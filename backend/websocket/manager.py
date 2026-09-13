"""
WebSocket connection manager for real-time alert streaming.

Manages connections to dashboard clients and broadcasts alerts.
"""
from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time alert streaming.

    Handles:
    - Client connections/disconnections
    - Broadcasting alerts to all clients
    - Connection health monitoring
    """

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: List[WebSocket] = []
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, client_id: str = None):
        """
        Accept a new WebSocket connection.

        Args:
            websocket: WebSocket connection
            client_id: Optional client identifier
        """
        await websocket.accept()
        self.active_connections.append(websocket)

        # Store metadata
        self.connection_metadata[websocket] = {
            'client_id': client_id or f"client_{len(self.active_connections)}",
            'connected_at': datetime.utcnow().isoformat(),
            'alerts_sent': 0
        }

        logger.info(
            f"WebSocket connected: {self.connection_metadata[websocket]['client_id']} "
            f"(total: {len(self.active_connections)})"
        )

        # Send welcome message
        await self._send_personal_message(websocket, {
            'type': 'connection',
            'status': 'connected',
            'client_id': self.connection_metadata[websocket]['client_id'],
            'timestamp': datetime.utcnow().isoformat()
        })

    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection to remove
        """
        if websocket in self.active_connections:
            client_id = self.connection_metadata.get(websocket, {}).get('client_id', 'unknown')
            self.active_connections.remove(websocket)

            if websocket in self.connection_metadata:
                del self.connection_metadata[websocket]

            logger.info(
                f"WebSocket disconnected: {client_id} "
                f"(remaining: {len(self.active_connections)})"
            )

    async def _send_personal_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """
        Send message to specific client.

        Args:
            websocket: Target WebSocket
            message: Message dictionary
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast_alert(self, alert: Dict[str, Any]):
        """
        Broadcast alert to all connected clients.

        Args:
            alert: Alert dictionary to broadcast
        """
        if not self.active_connections:
            logger.debug("No active connections to broadcast to")
            return

        # Prepare broadcast message
        message = {
            'type': 'alert',
            'data': alert,
            'timestamp': datetime.utcnow().isoformat()
        }

        # Track disconnected clients
        disconnected = []

        # Broadcast to all clients
        for websocket in self.active_connections:
            try:
                await websocket.send_json(message)

                # Update metadata
                if websocket in self.connection_metadata:
                    self.connection_metadata[websocket]['alerts_sent'] += 1

            except WebSocketDisconnect:
                logger.warning("Client disconnected during broadcast")
                disconnected.append(websocket)

            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(websocket)

        # Clean up disconnected clients
        for websocket in disconnected:
            self.disconnect(websocket)

        logger.info(
            f"Alert broadcast to {len(self.active_connections)} clients "
            f"({len(disconnected)} disconnected)"
        )

    async def broadcast_stats(self, stats: Dict[str, Any]):
        """
        Broadcast statistics update to all clients.

        Args:
            stats: Statistics dictionary
        """
        message = {
            'type': 'stats',
            'data': stats,
            'timestamp': datetime.utcnow().isoformat()
        }

        disconnected = []

        for websocket in self.active_connections:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting stats: {e}")
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(websocket)

    async def send_heartbeat(self):
        """Send heartbeat to all clients to keep connections alive."""
        message = {
            'type': 'heartbeat',
            'timestamp': datetime.utcnow().isoformat()
        }

        disconnected = []

        for websocket in self.active_connections:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(websocket)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get connection manager statistics.

        Returns:
            Dictionary with connection stats
        """
        return {
            'active_connections': len(self.active_connections),
            'total_alerts_sent': sum(
                meta.get('alerts_sent', 0)
                for meta in self.connection_metadata.values()
            ),
            'clients': [
                {
                    'client_id': meta.get('client_id'),
                    'connected_at': meta.get('connected_at'),
                    'alerts_sent': meta.get('alerts_sent', 0)
                }
                for meta in self.connection_metadata.values()
            ]
        }


# Global connection manager instance
manager = ConnectionManager()


async def heartbeat_loop():
    """Background task to send periodic heartbeats."""
    while True:
        await asyncio.sleep(30)  # Send heartbeat every 30 seconds
        if manager.active_connections:
            await manager.send_heartbeat()
