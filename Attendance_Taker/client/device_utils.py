"""
Device utility functions for getting unique identifiers.
"""
import socket
import uuid
import subprocess
import platform

def get_device_id() -> str:
    """
    Get a unique device identifier (MAC address or hostname).
    
    Returns:
        str: Device identifier
    """
    try:
        # Try to get MAC address
        if platform.system() == "Windows":
            # Windows
            output = subprocess.check_output("ipconfig /all", shell=True).decode()
            for line in output.split('\n'):
                if "Physical Address" in line:
                    mac = line.split(":")[1].strip().replace("-", ":")
                    return mac
        elif platform.system() == "Darwin":
            # macOS
            output = subprocess.check_output("ifconfig", shell=True).decode()
            # Parse MAC address from output
            # This is simplified - would need proper parsing
            import re
            mac_match = re.search(r"ether (([0-9a-fA-F]{2}[:]){5}[0-9a-fA-F]{2})", output)
            if mac_match:
                return mac_match.group(1)
        else:
            # Linux
            with open('/sys/class/net/eth0/address') as f:
                return f.read().strip()
    except:
        pass
    
    # Fallback to hostname
    try:
        return socket.gethostname()
    except:
        return "unknown_device"

if __name__ == "__main__":
    print(f"Device ID: {get_device_id()}")