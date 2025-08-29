
import asyncio
import time
import httpx


# --- Configurações do Teste ---

ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJVQzJiVzJROGxCRGhOd1RuLVRPYk9keWpMaG5OMzRzOXZQWE5JQk9yOGJJIn0.eyJleHAiOjE3NTQ5NTk2ODcsImlhdCI6MTc1NDk1OTM4NywianRpIjoib25ydHJvOjQ3YTI0OTU0LTMyOGUtMDBiOC1kYzVmLTIxMTgzNDA1NmFjMiIsImlzcyI6Imh0dHA6Ly8xMjcuMC4wLjE6ODA4MC9yZWFsbXMvZGV2IiwiYXVkIjoiYWNjb3VudCIsInN1YiI6ImQ3OWYwNzA3LTIzNjItNGM2ZS1hODE1LWFjZDFiNTM1MTBmMCIsInR5cCI6IkJlYXJlciIsImF6cCI6ImFwaS1iYWNrZW5kLWNsaWVudCIsInNpZCI6IjYwNTAwOGNlLTUyZTktNDMwOS04YTlmLWFhOTQ1OWU2OTBjNiIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiLyoiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbImRlZmF1bHQtcm9sZXMtZGV2Iiwib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoiZW1haWwgcHJvZmlsZSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJuYW1lIjoidGVzdGVuYW1lIHRlc3Rlc29icmVuYW1lIiwicHJlZmVycmVkX3VzZXJuYW1lIjoidGVzdGUiLCJnaXZlbl9uYW1lIjoidGVzdGVuYW1lIiwiZmFtaWx5X25hbWUiOiJ0ZXN0ZXNvYnJlbmFtZSIsImVtYWlsIjoidGVzdGFuZG9AZ21haWwuY29tIn0.CoJY0ph4n5Npumil3GFdYr9_nZ5ugQd4lVbjUKrl3tmhuy5-8iIJ8MwcQ0YDgh1nSQGVUqqOBRpJhInkwwtSTvmI771SqbB8r9zdKy0Ia9GvQSERZ2HSGMudkuvchfX6ITvJK6dRuiI08VIMwaHgCybBFmtzenh6d_YGE5nerRIqUyu_yVeUq17hpJ4IgMSpSS96r6FnGT-mAIOKOES99hN95mlQr4X-ciSajKpdFaHzxXWEtTHVF_v6NsV74XiFzwM61kripfX3Ps6b2nFBuR9xp0OZg-s1RU_P_1cdTix19DfoeN4ElBP4t5eXjTz7oylbqdshHskBwz9PmACMRQ"

# 2. Defina o endpoint que você quer testar
# URL = "http://127.0.0.1:8000/chat/knowledge_base"
URL = "http://127.0.0.1:8000/chat/knowledge_base" # Ou o endpoint do Salesforce

NUM_REQUESTS = 1  # Quantas requisições simultâneas vamos fazer

# 3. Defina os cabeçalhos (Headers), incluindo a autorização
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

# 4. Defina o corpo (Payload) da requisição
PAYLOAD = {
  "chat_id": "4e9ab30c-b6b4-4e88-acaa-329dbc084e7a",    # Use um chat_id válido
  "usuario_id": "d79f0707-2362-4c6e-a815-acd1b53510f0",  # Use um usuario_id válido
  "question": "Qual a prioridade da OP-10000?",
  "department": "TI"
}
# -----------------------------

async def make_post_request(client: httpx.AsyncClient, request_num: int):
    """Função que faz uma única requisição POST autenticada."""
    print(f"-> Iniciando requisição {request_num}...")
    try:
        # A chamada agora inclui o cabeçalho de autorização
        response = await client.post(URL, headers=HEADERS, json=PAYLOAD)
        response.raise_for_status()
        print(f"<- Requisição {request_num} finalizada com status: {response.status_code}")
        return response.json()
    except httpx.RequestError as e:
        print(f"!! Erro na requisição {request_num}: {e}")
        return None
    except httpx.HTTPStatusError as e:
        # Isso vai nos mostrar o corpo do erro se for um 401, 403, etc.
        print(f"!! Erro de status HTTP na requisição {request_num}: {e.response.status_code} - {e.response.text}")
        return None


async def main():
    """Função principal que orquestra os testes."""
    if "COLE_SEU_TOKEN" in ACCESS_TOKEN:
        print("!!! ERRO: Por favor, edite o script e insira um Access Token válido na variável ACCESS_TOKEN.")
        return

    print(f"Testando o endpoint seguro: {URL}")
    print(f"Enviando {NUM_REQUESTS} requisições POST simultâneas...")

    start_time = time.perf_counter()

    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [make_post_request(client, i + 1) for i in range(NUM_REQUESTS)]
        results = await asyncio.gather(*tasks)

    end_time = time.perf_counter()
    total_time = end_time - start_time

    print("\n" + "="*20 + " RESULTADO FINAL " + "="*20)
    success_count = len([res for res in results if res is not None])
    print(f"Tempo total para {success_count}/{NUM_REQUESTS} requisições: {total_time:.2f} segundos")
    print("="*57)

if __name__ == "__main__":
    asyncio.run(main())