import hashlib
import os
import socket
import sys
import tempfile
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

# ─── Configuration ─────────────────────────────────────────────────────────────────

EXPECTED_RELAY_AUTH_TOKEN_SECRET = "uplink-auth-token-01"
EXPECTED_RELAY_AUTH_USERNAME = "station_crew"
STATION_SSH_SSH_CHALLEGE = "536610cb"


# ─── Helper ────────────────────────────────────────────────────────────────────────

def validate_uplink_connection():
    """Test Uplink TCP service connectivity and auth state."""
    with socket.create_connection(("localhost", int(os.getenv("COMMS_TEST_PORT", "5432"))), timeout=5) as sock:
        # Send INFO
        sock.sendall(b"INFO\n")
        resp = sock.recv(4096).decode()
        
        challenge_match = re.search(r"challenge:\s*([a-f0-9]+)", resp)
        challenge = challenge_match.group(1) if challenge_match else None
        
        if not challenge:
            raise AssertionError("Could not extract challenge from INFO response")
        
        # Send AUTH using the challenge as token
        sock.sendall(f"AUTH {EXPECTED_RELAY_AUTH_USERNAME} {challenge}\n".encode())
        result = sock.recv(4096).decode()
        
        assert "authentication accepted" in result or "authentication accepted" in result.lower(), \
            f"Auth test failed: {result}"
        assert "Station SSH" in result, f"Station SSH handoff not received: {result}"
        
        # Verify Station SSH handshake material
        assert STATION_SSH_SSH_CHALLEGE in result, \
            f"Expected station_ssh challenge {STATION_SSH_SSH_CHALLEGE} not found in response"
        
        print("✓ Uplink auth state confirmed: vulnerability present and exploitable")


def test_station_ssh_config():
    """Verify station_ssh configuration file contains expected values."""
    station_ssh_conf = ROOT / "containers/comms/data/handoff.conf"
    assert station_ssh_conf.exists(), "Station SSH config file missing"
    
    content = station_ssh_conf.read_text()
    
    assert EXPECTED_RELAY_AUTH_USERNAME in content, \
        f"Expected station_crew in station_ssh config: {content}"
    assert STATION_SSH_SSH_CHALLEGE in content, \
        f"Expected challenge {STATION_SSH_SSH_CHALLEGE} not found in station_ssh config"
    
    print("✓ Station SSH configuration present with correct values")


def test_docker_services():
    """Verify all services defined in docker-compose.yml are accounted for."""
    compose_path = ROOT / "containers/comms/docker-compose.yml"
    compose_content = compose_path.read_text()
    
    required_services = {
        "webapp": "Slice A service preserved",
        "comms_relay_uplink": "Uplink TCP service",
        "station_ssh": "Station SSH placeholder"
    }
    
    for service_name, description in required_services.items():
        assert f"{service_name}:" in compose_content, \
            f"Required service '{service_name}' missing from compose"
    
    print("✓ All docker-compose services present")


def test_uplink_source_documents_vulnerability():
    """Verify vulnerability is documented in the source and docs."""
    server_path = ROOT / "containers/comms/network_service/auth_server.py"
    source = server_path.read_text()
    
    # The server must contain flawed authentication logic
    assert "flawed" in source.lower() or "RELAY_AUTH_TOKEN_SECRET" in source or "RELAY_AUTH_CHALLENGE_KEY" in source, \
        "Vulnerability logic not found in source"
    
    # Documentation must describe the flaw
    challenge_doc = ROOT / "containers/comms/docs/challenges/comms_relay.md"
    challenge_text = challenge_doc.read_text()
    assert "Flawed Authentication" in challenge_text, \
        "Intended vulnerability not documented"
    assert "challenge" in challenge_text.lower() and "secret" in challenge_text.lower(), \
        "Flaw description incomplete"
    
    solution_doc = ROOT / "containers/comms/docs/solutions/slice-b.md"
    solution_text = solution_doc.read_text()
    assert "vulnerability" in solution_text.lower(), \
        "Solution does not explain the vulnerability"
    
    print("✓ Vulnerability documented and consistent across source, docs, and solution")


# ─── Main ──────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Running Slice B acceptance tests...")
    print()
    
    tests = [
        ("Uplink TCP connectivity & auth state", validate_uplink_connection),
        ("Station SSH config values", test_station_ssh_config),
        ("Docker compose services", test_docker_services),
        ("Vulnerability documentation", test_uplink_source_documents_vulnerability)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, True, "PASS"))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"  ✗ {name}: {e}")
    
    print()
    print("=" * 50)
    print("RESULTS")
    print("=" * 50)
    
    for name, passed, status in results:
        icon = "✓" if passed else "✗"
        print(f"  {icon} {name}: {status}")
    
    failed = [r for r in results if not r[1]]
    if failed:
        print()
        print("FAILURES:")
        for name, passed, status in failed:
            print(f"  ✗ {name}: {status}")
        sys.exit(1)
    else:
        print()
        print("ALL TESTS PASSED ✓")
        print("Slice B is ready for demonstration.")