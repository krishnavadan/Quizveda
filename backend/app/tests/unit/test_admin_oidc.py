from datetime import UTC, datetime, timedelta

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.config import Settings
from app.modules.admin import security


@pytest.mark.asyncio
async def test_oidc_token_verifies_issuer_audience_signature_and_roles(monkeypatch) -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": "reviewer-42",
            "iss": "https://identity.example.test/",
            "aud": "quizveda-admin",
            "iat": now,
            "exp": now + timedelta(minutes=5),
            "roles": ["content_reviewer"],
        },
        private_key,
        algorithm="RS256",
        headers={"kid": "test-key"},
    )

    class FakeSigningKey:
        key = public_key

    class FakeJwksClient:
        def get_signing_key_from_jwt(self, supplied_token):
            assert supplied_token == token
            return FakeSigningKey()

    monkeypatch.setattr(security, "_jwks_client", lambda _url: FakeJwksClient())
    settings = Settings(
        oidc_issuer="https://identity.example.test/",
        oidc_audience="quizveda-admin",
        oidc_jwks_url="https://identity.example.test/.well-known/jwks.json",
    )
    principal = await security.get_admin_principal(
        HTTPAuthorizationCredentials(scheme="Bearer", credentials=token),
        settings,
    )
    assert principal.subject == "reviewer-42"
    assert principal.roles == frozenset({"content_reviewer"})


@pytest.mark.asyncio
async def test_oidc_token_with_wrong_issuer_is_rejected(monkeypatch) -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": "reviewer-42",
            "iss": "https://attacker.example.test/",
            "aud": "quizveda-admin",
            "iat": now,
            "exp": now + timedelta(minutes=5),
            "roles": ["admin"],
        },
        private_key,
        algorithm="RS256",
        headers={"kid": "test-key"},
    )

    class FakeSigningKey:
        key = private_key.public_key()

    class FakeJwksClient:
        def get_signing_key_from_jwt(self, _token):
            return FakeSigningKey()

    monkeypatch.setattr(security, "_jwks_client", lambda _url: FakeJwksClient())
    settings = Settings(
        oidc_issuer="https://identity.example.test/",
        oidc_audience="quizveda-admin",
        oidc_jwks_url="https://identity.example.test/.well-known/jwks.json",
    )
    with pytest.raises(HTTPException) as exc:
        await security.get_admin_principal(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials=token),
            settings,
        )
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_admin_api_fails_closed_when_identity_provider_is_unconfigured() -> None:
    settings = Settings()
    with pytest.raises(HTTPException) as exc:
        await security.get_admin_principal(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials="untrusted-token"),
            settings,
        )
    assert exc.value.status_code == 503


@pytest.mark.asyncio
async def test_admin_api_rejects_missing_bearer_token() -> None:
    with pytest.raises(HTTPException) as exc:
        await security.get_admin_principal(None, Settings())
    assert exc.value.status_code == 401
