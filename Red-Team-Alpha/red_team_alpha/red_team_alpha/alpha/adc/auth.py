import jwt
import hmac
import hashlib
import base64
import json
from datetime import datetime, timedelta, UTC
from data.users import USERS

PRIVATE_KEY = open("keys/pdcp_2026_private.pem","rb").read()
PUBLIC_KEY = open("keys/pdcp_2026_public.pem","rb").read().replace(b"\r\n", b"\n")

ISSUER = "http://127.0.0.1:8080/auth"

def create_token(username):
    now = int(datetime.now(UTC).timestamp())

    payload = {
        "user": username,
        "role": USERS[username]["role"],
        "iss": ISSUER,
        "iat": now,
        "exp": now + 7200
    }

    headers = {
        "alg":"RS256",
        "kid":"pdcp-2026",
        "typ":"JWT"
    }

    return jwt.encode(
        payload,
        PRIVATE_KEY,
        algorithm="RS256",
        headers=headers
    )

def b64decode(data):
    data += "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data)

def verify_token(token):
    unverified_header = jwt.get_unverified_header(token)
    alg = unverified_header.get("alg")
    kid = unverified_header.get("kid")

    if kid != "pdcp-2026":
        raise jwt.InvalidTokenError("Unknown key ID")

    if alg == "RS256":
        return jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            issuer=ISSUER
        ) 

    elif alg == "HS256":
        header_b64, payload_b64, sig_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}".encode()

        expected_with_newline = base64.urlsafe_b64encode(
            hmac.new(PUBLIC_KEY, signing_input, hashlib.sha256).digest()
        ).rstrip(b"=").decode()

        expected_without_newline = base64.urlsafe_b64encode(
            hmac.new(PUBLIC_KEY.rstrip(b"\n"), signing_input, hashlib.sha256).digest()
        ).rstrip(b"=").decode()

        if sig_b64 not in (expected_with_newline, expected_without_newline):
            raise jwt.InvalidTokenError("Invalid signature")

        payload = json.loads(b64decode(payload_b64).decode())

        if payload.get("iss") != ISSUER:
            raise jwt.InvalidTokenError("Invalid issuer")

        if payload.get("exp", 0) < int(datetime.now(UTC).timestamp()):
            raise jwt.InvalidTokenError("Token expired")

        if payload.get("user") not in USERS:
            raise jwt.InvalidTokenError("Unknown user")

        return payload
    
    raise jwt.InvalidTokenError("Unsupported algorithm")