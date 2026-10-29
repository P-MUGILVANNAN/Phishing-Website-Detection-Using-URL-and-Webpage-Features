import ipaddress
import socket
from typing import List, Tuple
from fastapi import Header, HTTPException, status
from app.config import settings

CLOUD_METADATA_IPS = {
    "169.254.169.254", # AWS, GCP, Azure, DigitalOcean
    "169.254.169.253",
    "100.100.100.200", # Alibaba Cloud
}

def is_ip_prohibited(ip_str: str) -> Tuple[bool, str]:
    """
    Evaluates whether an IP address belongs to loopback, private, link-local,
    multicast, reserved, or cloud metadata ranges.
    Returns (is_prohibited, reason).
    """
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return True, f"Invalid IP address format: {ip_str}"

    if ip_str in CLOUD_METADATA_IPS:
        return True, "Cloud metadata endpoint is strictly prohibited"
        
    if ip.is_loopback:
        return True, "Loopback address is strictly prohibited"
        
    if ip.is_private:
        return True, "Private RFC-1918 / RFC-4193 address is prohibited"
        
    if ip.is_link_local:
        return True, "Link-local address is prohibited"
        
    if ip.is_multicast:
        return True, "Multicast address is prohibited"
        
    if ip.is_reserved:
        return True, "Reserved IETF address range is prohibited"
        
    if ip.is_unspecified:
        return True, "Unspecified address (0.0.0.0 or ::) is prohibited"

    return False, "Allowed"

def resolve_and_validate_host(hostname: str) -> Tuple[bool, List[str], str]:
    """
    Resolves hostname to IP addresses and validates all resolved IPs.
    Returns (is_safe, resolved_ips, error_message).
    """
    # Reject localhost explicitly
    if hostname.lower() in {"localhost", "127.0.0.1", "::1", "metadata.google.internal"}:
        return False, [], "Localhost or metadata domain is strictly prohibited"

    # Direct IP check
    try:
        ip = ipaddress.ip_address(hostname)
        prohibited, reason = is_ip_prohibited(str(ip))
        if prohibited:
            return False, [str(ip)], reason
        return True, [str(ip)], "OK"
    except ValueError:
        pass

    # Resolve via DNS
    try:
        addr_infos = socket.getaddrinfo(hostname, None)
        resolved_ips = list({addr[4][0] for addr in addr_infos})
    except socket.gaierror as e:
        return False, [], f"DNS resolution failed: {e}"
    except Exception as e:
        return False, [], f"Resolution error: {str(e)}"

    if not resolved_ips:
        return False, [], "No IP addresses resolved for host"

    for ip_str in resolved_ips:
        prohibited, reason = is_ip_prohibited(ip_str)
        if prohibited:
            return False, resolved_ips, f"Resolved IP {ip_str} is prohibited: {reason}"

    return True, resolved_ips, "OK"

def verify_admin_access(x_api_key: str = Header(None)) -> bool:
    """
    Admin verification. In development mode with default key, access is permitted,
    otherwise requires matching ADMIN_API_KEY.
    """
    if settings.ENVIRONMENT == "development" and not x_api_key:
        return True
    if x_api_key and x_api_key == settings.ADMIN_API_KEY:
        return True
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Administrative access required. Provide valid X-API-Key."
    )

