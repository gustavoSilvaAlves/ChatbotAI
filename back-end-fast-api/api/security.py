# api/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
from jose import jwt, JWTError

from api.core.config import settings

# --- Configuração ---
KEYCLOAK_CERTS_URL = f"{settings.KEYCLOAK_BASE_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/certs"
oauth2_scheme = HTTPBearer()


# --- Lógica de Validação Segura ---
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas, token expirado ou não autorizado para esta aplicação",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # ETAPA 1: Buscar as chaves públicas do Keycloak
        print("\n[DEBUG 1] Buscando chaves de segurança do Keycloak...")
        jwks_client = requests.get(KEYCLOAK_CERTS_URL)
        jwks_client.raise_for_status()
        jwks = jwks_client.json()
        print("[DEBUG 2] Chaves obtidas com sucesso.")

        # ETAPA 2: Encontrar a chave correta para este token
        print("[DEBUG 3] Lendo o cabeçalho do token para encontrar o Key ID (kid)...")
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {"kty": key["kty"], "kid": key["kid"], "use": key["use"], "n": key["n"], "e": key["e"]}
                break

        if not rsa_key:
            print("[ERRO FATAL] Key ID (kid) do token não encontrado nas chaves do Keycloak!")
            raise credentials_exception
        print("[DEBUG 4] Chave de assinatura encontrada no JWKS.")

        # ETAPA 3: Decodificar e validar o token (assinatura, expiração, emissor)
        print("[DEBUG 5] Tentando decodificar e validar o token (assinatura, issuer)...")
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            issuer=f"{settings.KEYCLOAK_BASE_URL}/realms/{settings.KEYCLOAK_REALM}",
            # Esta opção diz à biblioteca para NÃO verificar a audiência.
            options={"verify_aud": False}
        )
        authorized_party = payload.get("azp")
        # Lista de clientes que têm permissão para usar esta API
        allowed_clients = [settings.KEYCLOAK_CLIENT_ID, "streamlit-frontend"]

        if authorized_party not in allowed_clients:
            print(f"[ERRO DE AUTORIZAÇÃO] O cliente '{authorized_party}' não tem permissão para usar esta API.")
            raise credentials_exception

        username: str = payload.get("preferred_username")
        if username is None:
            raise credentials_exception

        return payload

    except (JWTError, requests.exceptions.RequestException, KeyError) as e:
        # Remova os prints de debug se quiser deixar o código mais limpo
        print(f"\n[ERRO DE VALIDAÇÃO] A exceção foi: {e}\n")
        raise credentials_exception