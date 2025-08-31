"""
Utility functions for the attendance system.
"""
import socket
import uuid
import logging

logger = logging.getLogger(__name__)

def get_device_id() -> str:
    """
    Get a unique device identifier (MAC address or hostname).
    
    Returns:
        str: Device identifier
    """
    try:
        # Try to get MAC address
        mac = uuid.getnode()
        if (mac >> 40) % 2 == 0:  # Valid MAC address
            return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))
    except:
        pass
    
    # Fallback to hostname
    try:
        return socket.gethostname()
    except:
        return "unknown_device"