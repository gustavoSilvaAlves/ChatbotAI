import asyncio
import time
import httpx

# --- Configurações do Teste ---
NUM_REQUISICOES = 15
# Usamos um URL que força uma espera de 1 segundo no servidor
URL_TESTE = "https://httpbin.org/delay/1"


# =======================================================================
# ABORDAGEM 1: Sequencial (Uma de cada vez) 🐢
# =======================================================================
def fazer_requisicoes_sequenciais():
    """Faz 15 requisições usando um loop for simples e a biblioteca 'requests'."""
    print(f"--- INICIANDO TESTE SEQUENCIAL COM {NUM_REQUISICOES} REQUISIÇÕES ---")
    print("Cada requisição vai esperar a anterior terminar...")

    start_time = time.perf_counter()

    # Usamos um cliente síncrono que faz uma requisição por vez
    with httpx.Client() as client:
        for i in range(1, NUM_REQUISICOES + 1):
            print(f"🐢 Sequencial: Enviando requisição {i}...")
            try:
                client.get(URL_TESTE, timeout=10.0)
                print(f"🐢 Sequencial: Resposta da requisição {i} recebida.")
            except httpx.ReadTimeout:
                print(f"🐢 Sequencial: Requisição {i} falhou (timeout).")

    end_time = time.perf_counter()
    total_time = end_time - start_time

    print("\n--- RESULTADO SEQUENCIAL ---")
    print(f"Tempo total: {total_time:.2f} segundos")
    print("----------------------------\n")
    return total_time


# =======================================================================
# ABORDAGEM 2: Concorrente ("Todas ao mesmo tempo") 🚀
# =======================================================================
async def fazer_requisicao_unitaria(client: httpx.AsyncClient, numero: int):
    """Função auxiliar que executa uma única requisição assíncrona."""
    print(f"🚀 Concorrente: Enviando requisição {numero}...")
    try:
        await client.get(URL_TESTE, timeout=10.0)
        print(f"🚀 Concorrente: Resposta da requisição {numero} recebida.")
    except httpx.ReadTimeout:
        print(f"🚀 Concorrente: Requisição {numero} falhou (timeout).")


async def fazer_requisicoes_concorrentes():
    """Dispara 15 requisições de forma concorrente usando asyncio e httpx."""
    print(f"--- INICIANDO TESTE CONCORRENTE COM {NUM_REQUISICOES} REQUISIÇÕES ---")
    print("Todas as requisições serão disparadas quase simultaneamente...")

    start_time = time.perf_counter()

    # Usamos um cliente assíncrono para permitir múltiplas chamadas
    async with httpx.AsyncClient() as client:
        # Criamos uma lista de "tarefas" a serem executadas
        tarefas = []
        for i in range(1, NUM_REQUISICOES + 1):
            tarefas.append(fazer_requisicao_unitaria(client, i))

        # asyncio.gather é o comando mágico que executa todas as tarefas concorrentemente
        await asyncio.gather(*tarefas)

    end_time = time.perf_counter()
    total_time = end_time - start_time

    print("\n--- RESULTADO CONCORRENTE ---")
    print(f"Tempo total: {total_time:.2f} segundos")
    print("-----------------------------\n")
    return total_time


# =======================================================================
# EXECUÇÃO PRINCIPAL
# =======================================================================
async def main():
    tempo_sequencial = fazer_requisicoes_sequenciais()
    tempo_concorrente = await fazer_requisicoes_concorrentes()

    print("================= COMPARAÇÃO FINAL =================")
    print(f"🐢 Tempo Sequencial (1 por 1):   {tempo_sequencial:.2f} segundos")
    print(f"🚀 Tempo Concorrente (todas de uma vez): {tempo_concorrente:.2f} segundos")

    try:
        ganho = (tempo_sequencial / tempo_concorrente)
        print(f"\n✨ A abordagem concorrente foi {ganho:.1f} vezes mais rápida! ✨")
    except ZeroDivisionError:
        print("\nNão foi possível calcular o ganho de performance.")
    print("====================================================")


if __name__ == "__main__":
    # Para rodar uma função async, precisamos do asyncio.run()
    asyncio.run(main())