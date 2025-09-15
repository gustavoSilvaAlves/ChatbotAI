from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
from jose import jwt, JWTError

from api.core.config import settings


KEYCLOAK_CERTS_URL = f"{settings.KEYCLOAK_BASE_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/certs"
oauth2_scheme = HTTPBearer()



async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas, token expirado ou não autorizado para esta aplicação",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:

        jwks_client = requests.get(KEYCLOAK_CERTS_URL)
        jwks_client.raise_for_status()
        jwks = jwks_client.json()




        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {"kty": key["kty"], "kid": key["kid"], "use": key["use"], "n": key["n"], "e": key["e"]}
                break

        if not rsa_key:

            raise credentials_exception

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            issuer=f"{settings.KEYCLOAK_BASE_URL}/realms/{settings.KEYCLOAK_REALM}",
            options={"verify_aud": False}
        )
        authorized_party = payload.get("azp")

        allowed_clients = [settings.KEYCLOAK_CLIENT_ID, "streamlit-frontend"]

        if authorized_party not in allowed_clients:

            raise credentials_exception

        username: str = payload.get("preferred_username")
        if username is None:
            raise credentials_exception

        return payload

    except (JWTError, requests.exceptions.RequestException, KeyError) as e:

        raise credentials_exception