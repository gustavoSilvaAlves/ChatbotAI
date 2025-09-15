import httpx
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from api.core.config import settings
import re


# ===================================================================
# FUNÇÕES-FERRAMENTA
# ===================================================================

async def run_soql(soql: str, object_name: str = None) -> dict:
    """
    Executa uma query SOQL no Salesforce, retorna registros já com labels
    amigáveis e traduz valores de picklist automaticamente.
    """
    url = f"{settings.SF_INSTANCE_URL}/services/data/v59.0/query"
    headers = {
        "Authorization": f"Bearer {settings.SF_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    params = {"q": soql}


    async with httpx.AsyncClient() as client:
        try:
            # PRIMEIRA CHAMADA NÃO-BLOQUEANTE
            resp = await client.get(url, headers=headers, params=params, timeout=30.0)
            resp.raise_for_status()
            data = resp.json()

            # Se precisarmos dos metadados, fazemos a segunda chamada
            if "records" in data and data["records"] and object_name:
                meta_url = f"{settings.SF_INSTANCE_URL}/services/data/v59.0/sobjects/{object_name}/describe"
                # SEGUNDA CHAMADA NÃO-BLOQUEANTE
                meta_resp = await client.get(meta_url, headers=headers, timeout=30.0)
                meta_resp.raise_for_status()
                meta = meta_resp.json()
            else:
                # Se não precisar de metadados, retorna os dados brutos
                return data

        except httpx.HTTPStatusError as e:

            return {"error": f"Erro na API do Salesforce: {e.response.status_code}", "details": e.response.text}
        except httpx.RequestError as e: # Captura erros de rede, timeout, etc.
            return {"error": "Falha na comunicação com a API do Salesforce.", "details": str(e)}

    labels = {f["name"]: f["label"] for f in meta.get("fields", [])}
    picklists = {
        f["name"]: {v["value"]: v["label"] for v in f.get("picklistValues", [])}
        for f in meta.get("fields", []) if f.get("picklistValues")
    }

    # Formata registros com labels e picklists traduzidos
    formatted_records = []
    for rec in data["records"]:
        clean_rec = {k: v for k, v in rec.items() if k != "attributes"}
        formatted_rec = {}
        for field, value in clean_rec.items():
            label = labels.get(field, field)
            if field in picklists and value in picklists[field]:
                value = picklists[field][value]
            formatted_rec[label] = value if value is not None else "N/D"
        formatted_records.append(formatted_rec)

    return {"records": formatted_records}


async def query_nf(identificador: str) -> dict:
    """
    Consulta uma Nota Fiscal (Nota_Fiscal__c) por Número SAP, DANFE, Chave de Acesso ou Nome(NF-).
    """
    if not identificador or not identificador.strip():
        return {"error": "Nenhum identificador foi fornecido para a busca."}

    identificador_limpo = identificador.strip().replace("'", "\\'")
    where_clause = (
        f"Numero_SAP__c = '{identificador_limpo}' OR "
        f"Danfe__c = '{identificador_limpo}' OR "
        f"Chave_de_Acesso__c = '{identificador_limpo}' OR "
        f"Name = '{identificador_limpo}'"
    )
    soql = f"""
        SELECT 
            Id, Name, Itens_Relacionados__c, Status__c, Indicador_Consumidor_Final__c, Cliente__c,
            Status_Cobranca__c, Observacoes__c, Total_antes_do_Desconto__c,
            Valor_Faturado__c, SOL__c, Cotacao_de_Venda__c, 
            Numero_SAP__c, Danfe__c, Chave_de_Acesso__c, Interacao_Logistica__c,
            Utilizacao_Lista__c, Data_Lancamento_SAP__c, Transportadora_Final_Lista__c,
            Conhec_Transport__c, Valor_da_Cobranca_Frete__c, N_Fatura_Frete__c,
            Status_Processo_Compra_Logistica__c, Observacoes_CV__c, Data_da_Baixa__c,
            NF_de_Devolucao__c, CNPJ_CPF__c, Raz_o_Social__c, Data_Recebimento_Empenho__c,
            Data_Limite_Entrega__c, Data_Coleta__c, Data_Entrega__c,
            Data_Entrega_Prorrogada__c, Data_Lancamento__c,
            Data_Inicial_da_Previsao_de_Recebimento__c,
            Data_Inicio_Cobranca_Interna_Mais_Recent__c, Filial_CV__c,
            Status_Processo_NF__c, Fonte_do_Recurso__c, Indicador_IE__c,
            Hoje_menos_Entrega__c, Dados_bancarios__c, Cliente_de_Risco__c,
            Segmento_de_Mercado_do_PN__c
        FROM Nota_Fiscal__c
        WHERE {where_clause}
        LIMIT 10
    """
    resultado_api = await run_soql(soql, object_name="Nota_Fiscal__c")

    if "error" in resultado_api:
        return resultado_api
    records = resultado_api.get("records", [])

    if not records:
        return {"message": f"Nenhuma nota fiscal foi encontrada com o identificador '{identificador}'."}
    if len(records) == 1:
        return records[0]

    lista_de_opcoes = []
    for rec in records:
        # Usamos .get() para segurança, caso algum campo esteja vazio
        nome_nf = rec.get('Nome de Nota Fiscal', 'N/A')
        razao_social = rec.get('Razão Social', 'N/A')
        cnpj_cpf = rec.get('CNPJ/CPF', 'N/A')

        # Criamos a string formatada para cada opção
        opcao_formatada = f"{nome_nf} (Cliente: {razao_social} - Doc: {cnpj_cpf})"
        lista_de_opcoes.append(opcao_formatada)

    return {
        "message": "Foram encontradas várias notas fiscais com o identificador fornecido. Por favor, especifique qual delas você deseja consultar:",
        "options": lista_de_opcoes
    }


async def query_cv(id: str) -> dict:
    """Consulta uma CV (Cotação de venda) pelo ID."""
    soql = f"SELECT Id, Name, Fase_cotacao_venda__c, Prioridade__c, Utilizacao__c FROM Cotacao_de_Venda__c WHERE Id = '{id}' OR Name = '{id}' LIMIT 1"
    return await run_soql(soql, object_name="Cotacao_de_Venda__c")


async def query_ivs(iv_names: list[str]) -> dict:
    """Consulta um ou mais Itens de Venda (Item_venda__c) pelo Nome."""
    if not iv_names:
        return {"error": "Nenhum IV informado"}
    names_str = ','.join([f"'{name}'" for name in iv_names])
    soql = f"SELECT Id, Name, Status__c, Status_Logistica__c, Status_Processo_IV__c FROM Item_venda__c WHERE Name IN ({names_str})"
    return await run_soql(soql, object_name="Item_venda__c")


async def query_op(name: str) -> dict:
    """Consulta uma Oportunidade (Solicitacao__c) pelo Nome."""
    soql = f"SELECT Id, Name, Status_da_OP__c, Total_da_Oportunidade_Valor_Estimado__c FROM Solicitacao__c WHERE Name = '{name}' LIMIT 1"
    return await run_soql(soql, object_name="Solicitacao__c")


# ===================================================================
# CLASSE DO SERVIÇO
# ===================================================================

class SalesforceChatService:
    def __init__(self):
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=settings.OPENAI_API_KEY)
        tools = [query_ivs, query_pn, query_nf, query_op, query_cv]

        # Agente é criado de forma simples, sem prompt na inicialização
        self.agent_executor = create_react_agent(llm, tools)

    async def query(self, question: str, history: list) -> dict:
        """Executa a consulta usando o agente LangGraph."""
        system_prompt = (
            "Você é um assistente especialista em Salesforce. "
            "Quando escolher as tools se atente ao padrão do salesforce para consulta como: "
            "OP-{Número da OP} (ex: OP-10000), "
            "Name do IV(Item de Venda) (ex: IV-123456)."
            "ou CV(Cotação de venda) (ex: CV-123456)."
            "Quando o usuário solicitar todas as 'informações', 'informação completa' ou perguntas similares se atente aos objeto que estão sendo referenciados na consulta e realiza consultas nesses objetos para retornar as informações completas."
            "Se atente as informações já retornadas anteriormente. "
            "Analise o histórico e a pergunta atual para fornecer a melhor resposta."

        )

        messages = [("system", system_prompt)]

        for user_msg, ai_msg in history:
            messages.append(("user", user_msg))
            messages.append(("ai", ai_msg))

        messages.append(("user", question))


        final_answer = ""
        try:
            # Usando astream_events para capturar a saída
            async for event in self.agent_executor.astream_events({"messages": messages}, version="v1"):
                kind = event["event"]
                if kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        final_answer += content
        except Exception as e:

            final_answer = "Ocorreu um erro ao processar sua solicitação com o agente V2."

        if not final_answer:
            final_answer = "Não consegui gerar uma resposta. Verifique os logs do back-end para mais detalhes."

        return {"answer": final_answer.strip()}


async def query_pn(identificador: str) -> dict:
    """
    Consulta um Parceiro de Negócio (Account) pelo Identificador do Salesforce, Nome, Nome Fantasia ou CNPJ/CPF.
    """
    if not identificador or not identificador.strip():
        return {"error": "Nenhum identificador foi fornecido para a busca do Parceiro de Negócio."}

    identificador_limpo = identificador.strip().replace("'", "\\'")
    identificador_numerico = re.sub(r'\D', '', identificador)
    # Busca por CNPJ/CPF exato ou por parte do Nome/Nome Fantasia
    where_clause = (
        f"CNPJ_CPF__c = '{identificador_numerico}' OR "
        f"CNPJ_CPF__c = '{identificador_limpo}' OR "
        f"Name LIKE '%{identificador_limpo}%' OR "
        f"Nome_Fantasia_PN__c LIKE '%{identificador_limpo}%'"
    )

    # Selecionamos os campos mais relevantes para uma resposta inicial
    soql = f"""
        SELECT 
        Id, Name, Nome_Fantasia_PN__c, Phone, Telefone_2__c, Email_Integracao__c,
            Grupo_do_PN_Formula__c, Segmento_de_Mercado__c, Esfera__c,
            Cod_IE_Dest__c, Cod_ID_final__c, Sequencia_PN__c, Suframa__c,
            Inscricao_Estadual__c, CNPJ_CPF__c, Endereco_Entrega__c,
            Endereco_Cobranca__c, Score_Automatico__c, Numero_de_Habitantes__c,
            CNPJ_CPF_Formatado__c
        FROM Account
        WHERE {where_clause}
        LIMIT 10
    """

    resultado_api = await run_soql(soql, object_name="Account")

    if "error" in resultado_api:
        return resultado_api
    records = resultado_api.get("records", [])

    if not records:
        return {"message": f"Nenhum Parceiro de Negócio foi encontrado com o identificador '{identificador}'."}

    if len(records) == 1:
        return records[0]

    # Se encontrar múltiplos, formata uma lista para o usuário escolher
    lista_de_opcoes = []
    for rec in records:
        # 'Nome da conta' é o label padrão para o campo 'Name' do objeto Account
        nome_pn = rec.get('Nome da conta', 'N/A')
        cnpj_pn = rec.get('CNPJ/CPF', 'N/A')
        cidade_pn = rec.get('Cidade', 'N/A')
        opcao = f"{nome_pn} (Doc: {cnpj_pn}, Cidade: {cidade_pn})"
        lista_de_opcoes.append(opcao)

    return {
        "message": "Foram encontrados vários Parceiros de Negócio. Por favor, especifique qual deles você deseja consultar:",
        "options": lista_de_opcoes
    }
# ===================================================================
# INSTÂNCIA ÚNICA DO SERVIÇO
# ===================================================================
salesforce_chat_service  = SalesforceChatService()