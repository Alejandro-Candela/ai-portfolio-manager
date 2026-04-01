from __future__ import annotations

import logging
from functools import lru_cache
from typing import Annotated

import jwt
import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.config.settings import get_settings

logger = logging.getLogger(__name__)

_bearer = HTTPBearer(auto_error=False)


@lru_cache(maxsize=1)
def _fetch_jwks() -> dict:
    settings = get_settings()
    url = f"https://login.microsoftonline.com/{settings.azure_ad_tenant_id}/discovery/v2.0/keys"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _decode_token(token: str) -> dict:
    settings = get_settings()

    if settings.dev_auth_bypass:
        # In dev mode, accept an unsigned token with tenant/user info
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except jwt.DecodeError:
            return {}

    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        jwks = _fetch_jwks()
        key = None
        for k in jwks.get("keys", []):
            if k.get("kid") == kid:
                key = jwt.algorithms.RSAAlgorithm.from_jwk(k)
                break

        if key is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown signing key"
            )

        return jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            issuer=f"https://login.microsoftonline.com/{settings.azure_ad_tenant_id}/v2.0",
            audience=settings.azure_ad_audience,
        )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {exc}"
        ) from exc


class CurrentUser:
    def __init__(
        self,
        user_id: str,
        tenant_id: str,
        email: str,
        roles: list[str],
    ) -> None:
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.email = email
        self.roles = roles

    def require_role(self, *roles: str) -> None:
        if not any(r in self.roles for r in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> CurrentUser:
    settings = get_settings()

    if credentials is None:
        if settings.dev_auth_bypass:
            return CurrentUser(
                user_id="dev-user-001",
                tenant_id=settings.dev_tenant_id,
                email="dev@localhost",
                roles=["admin"],
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
        )

    claims = _decode_token(credentials.credentials)

    if settings.dev_auth_bypass and not claims:
        return CurrentUser(
            user_id="dev-user-001",
            tenant_id=settings.dev_tenant_id,
            email="dev@localhost",
            roles=["admin"],
        )

    return CurrentUser(
        user_id=claims.get("oid", claims.get("sub", "unknown")),
        tenant_id=claims.get("tid", settings.dev_tenant_id),
        email=claims.get("preferred_username", claims.get("email", "")),
        roles=(claims.get("roles") or []),
    )
