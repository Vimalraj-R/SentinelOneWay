"""
WebSocket API endpoints for real-time alert streaming.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from websocket.manager import manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/alerts")
async def websocket_alerts(
    websocket: WebSocket,
    client_id: str = Query(None, description="Optional client identifier")
):
    """
    WebSocket endpoint for real-time alert streaming.

    Clients connect to this endpoint to receive:
    - Real-time threat alerts
    - Statistics updates
    - System status changes
    - Heartbeat messages

    Args:
        websocket: WebSocket connection
        client_id: Optional client identifier for tracking
    """
    await manager.connect(websocket, client_id)

    try:
        # Keep connection alive and process any incoming messages
        while True:
            # Wait for messages from client (ping, subscribe, etc.)
            data = await websocket.receive_text()

            # Handle client messages
            if data == "ping":
                await websocket.send_json({
                    'type': 'pong',
                    'message': 'Connection alive'
                })

            elif data == "stats":
                # Send connection stats
                stats = manager.get_stats()
                await websocket.send_json({
                    'type': 'stats_response',
                    'data': stats
                })

    except WebSocketDisconnect:
        logger.info("Client disconnected normally")
        manager.disconnect(websocket)

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.get("/ws/status")
async def websocket_status():
    """
    Get WebSocket connection status and statistics.

    Returns:
        Dictionary with connection information
    """
    return manager.get_stats()
