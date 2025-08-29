import requests
import json
from fastapi.concurrency import run_in_threadpool
from openai import OpenAI

from api.core.config import settings
from api.models.chat_models import ChatRequest

openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)


class SalesforceChatService:
    def __init__(self):


        self.SALESFORCE_SCHEMA = {
            "Solicitacao__c": {
                "description": "Usado para gerenciar oportunidades de negócio, também conhecidas como OP.",
                "fields": {
                    "Id": {"type": "id", "description": "O ID único do registro."},
                    "Name": {"type": "string",
                             "description": "O identificador principal da Oportunidade, como 'OP-10000'."},
                    "Status_da_OP__c": {"type": "picklist",
                                        "description": "O status atual da oportunidade (ex: Em Negociação, Ganho, Perdido)."},
                    "Total_da_Oportunidade_Valor_Estimado__c": {"type": "currency",
                                                                "description": "O valor monetário estimado da oportunidade."},
                    "Prioridade_da_Oportunidade__c": {"type": "picklist",
                                                      "description": "A prioridade da oportunidade (ex: Alta, Média, Baixa)."}
                }
            },
            "Contact": {
                "description": "Representa uma pessoa de contato de um cliente.",
                "fields": {
                    "Id": {"type": "id", "description": "O ID único do contato."},
                    "FirstName": {"type": "string", "description": "O primeiro nome do contato."},
                    "LastName": {"type": "string", "description": "O sobrenome do contato."},
                    "Email": {"type": "email", "description": "O endereço de e-mail do contato."},
                    "Phone": {"type": "phone", "description": "O número de telefone do contato."}
                }
            }

        }
        self.termos_objetos = {
            "Contact": "contato", "Solicitacao__c": "solicitação"
        }

    def _plan_soql_query(self, pergunta: str) -> dict:
        """
        Passo 2: Pede ao LLM para criar um plano de consulta em JSON.
        """
        schema_json_string = json.dumps(self.SALESFORCE_SCHEMA, indent=2)

        prompt = f"""
            Você é um assistente de dados especialista em Salesforce. Sua tarefa é converter uma pergunta em linguagem natural em um plano de consulta JSON estruturado.

            Analise o schema de dados do Salesforce fornecido abaixo:
            ```json
            {schema_json_string}
            ```

            Agora, analise a seguinte pergunta do usuário:
            "{pergunta}"

            Com base na pergunta e no schema, gere um objeto JSON que descreve o plano de consulta. O objeto JSON deve ter a seguinte estrutura:
            {{
              "object": "Nome do objeto a ser consultado",
              "fields": ["lista de campos para incluir no SELECT"],
              "filters": [
                {{
                  "field": "Campo a ser usado no WHERE",
                  "operator": "operador de comparação, como '=', '>', '<', 'LIKE'",
                  "value": "valor a ser comparado"
                }}
              ]
            }}

            Se o usuário não especificar campos, selecione os campos mais importantes com base na pergunta e na descrição do schema. Se não houver filtros claros na pergunta, retorne uma lista de filtros vazia.
            Responda APENAS com o objeto JSON.
        """

        response = openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )

        try:
            query_plan = json.loads(response.choices[0].message.content)
            print(f"Plano de Consulta JSON gerado: {query_plan}")
            return query_plan
        except (json.JSONDecodeError, KeyError) as e:
            print(f"ERRO ao decodificar o plano JSON do LLM: {e}")
            raise ValueError("Não foi possível gerar um plano de consulta válido.")

    def _build_soql_from_plan(self, plan: dict) -> str:
        """
        Passo 3: Constrói a string SOQL a partir do plano JSON.
        Esta função não tem IA, é 100% determinística e segura.
        """
        object_name = plan.get("object")
        fields = plan.get("fields", ["Id"])
        filters = plan.get("filters", [])

        if not object_name or not fields:
            raise ValueError("O plano de consulta é inválido. Faltam 'object' ou 'fields'.")

        soql = f"SELECT {', '.join(fields)} FROM {object_name}"

        if filters:
            where_clauses = []
            for f in filters:

                value = str(f['value']).replace("'", "\\'")
                where_clauses.append(f"{f['field']} {f['operator']} '{value}'")
            soql += " WHERE " + " AND ".join(where_clauses)

        soql += " LIMIT 10"
        return soql

    def _formatar_resposta(self, records: list, plan: dict) -> str:
        """
        Formata os registros do Salesforce em uma resposta amigável para o usuário.
        """
        object_name = plan.get("object")

        if not records:
            return f"Nenhum registro correspondente foi encontrado para o objeto {object_name} no Salesforce."

        termo_amigavel = self.termos_objetos.get(object_name, "registro")


        resposta_final = f"Encontrei {len(records)} {termo_amigavel}(s) para sua consulta.\n\n"


        for i, record in enumerate(records):
            nome_principal = record.get("Name", f"Registro {i + 1}")
            resposta_final += f"--- **{nome_principal}** ---\n"

            detalhes = []

            for campo, valor in record.items():
                if campo.lower() != 'attributes':
                    campo_formatado = campo.replace('__c', '').replace('_', ' ')
                    detalhes.append(f"- **{campo_formatado}:** {valor}")

            resposta_final += "\n".join(detalhes) + "\n\n"

        return resposta_final.strip()

    def _process_query_sync(self, request: ChatRequest) -> dict:
        """Função SÍNCRONA que executa a lógica e retorna um dicionário com a resposta e a SOQL."""
        try:
            query_plan = self._plan_soql_query(request.question)
            soql = self._build_soql_from_plan(query_plan)
            print(f"SOQL Construída: {soql}")

            headers = {"Authorization": f"Bearer {settings.SF_ACCESS_TOKEN}", "Content-Type": "application/json"}
            url = f"{settings.SF_INSTANCE_URL}/services/data/v59.0/query/"

            response = requests.get(url, headers=headers, params={'q': soql})
            response.raise_for_status()

            records = response.json().get("records", [])


            answer_formatada = self._formatar_resposta(records, query_plan)


            return {"answer": answer_formatada, "soql_query": soql}

        except Exception as e:
            print(f"ERRO no serviço Salesforce: {e}")
            error_message = "Desculpe, ocorreu um erro ao tentar consultar o Salesforce."
            return {"answer": error_message, "soql_query": "ERRO"}

    async def query(self, request: ChatRequest) -> dict:
        """Função ASSÍNCRONA que o endpoint chama."""
        result = await run_in_threadpool(self._process_query_sync, request)
        return result


salesforce_chat_service = SalesforceChatService()