from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError, PyJWKClientError

from app.core.config import Settings, get_settings

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True, slots=True)
class AdminPrincipal:
    subject: str
    roles: frozenset[str]


@lru_cache(maxsize=8)
def _jwks_client(url: str) -> PyJWKClient:
    return PyJWKClient(url, cache_jwk_set=True, lifespan=300, timeout=5)


async def get_admin_principal(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AdminPrincipal:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Administrator access token required.")

    if not settings.oidc_issuer or not settings.oidc_audience or not settings.oidc_jwks_url:
        raise HTTPException(status_code=503, detail="Administrator identity provider is not configured.")

    try:
        client = _jwks_client(settings.oidc_jwks_url)
        signing_key = client.get_signing_key_from_jwt(credentials.credentials)
        claims = jwt.decode(
            credentials.credentials,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.oidc_audience,
            issuer=settings.oidc_issuer,
            options={"require": ["exp", "iat", "sub", "iss", "aud"]},
            leeway=30,
        )
    except (InvalidTokenError, PyJWKClientError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid administrator access token.") from exc

    subject = claims.get("sub")
    raw_roles = claims.get(settings.oidc_roles_claim, [])
    if not isinstance(subject, str) or not subject.strip():
        raise HTTPException(status_code=401, detail="Token subject is missing.")
    if isinstance(raw_roles, str):
        raw_roles = [raw_roles]
    if not isinstance(raw_roles, list) or not all(
        isinstance(role, str) for role in raw_roles
    ):
        raise HTTPException(status_code=403, detail="Administrator roles claim is invalid.")

    return AdminPrincipal(subject=subject, roles=frozenset(raw_roles))


def require_roles(*allowed_roles: str) -> Callable:
    async def dependency(
        principal: Annotated[AdminPrincipal, Depends(get_admin_principal)],
    ) -> AdminPrincipal:
        if not (principal.roles & set(allowed_roles)) and "admin" not in principal.roles:
            raise HTTPException(status_code=403, detail="Insufficient administrator permissions.")
        return principal

    return dependency
