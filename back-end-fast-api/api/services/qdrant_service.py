from fastapi.concurrency import run_in_threadpool
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from typing import Optional

from ..models.chat_models import DocumentSource
from ..core.config import settings

# Prompt para a IA reformular a pergunta do usuário com base no histórico.
_template = """Dada a seguinte conversa e uma pergunta de acompanhamento, reformule a pergunta de acompanhamento para ser uma pergunta independente, em seu idioma original.

Histórico do Chat:
{chat_history}
Pergunta de Acompanhamento: {question}
Pergunta Independente:"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)


class QdrantChatService:
    def __init__(self):
        print("[DEBUG] Iniciando __init__ do QdrantChatService...")
        self.qdrant_client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=settings.OPENAI_API_KEY)
        self.llm = ChatOpenAI(temperature=0.7, openai_api_key=settings.OPENAI_API_KEY)

        self.vector_store = Qdrant(
            client=self.qdrant_client,
            collection_name=settings.QDRANT_COLLECTION_NAME,
            embeddings=self.embeddings
        )

        PROMPT_TEMPLATE = """
        Você é um assistente de IA. Você recebeu um histórico de conversa e alguns documentos de contexto para responder à pergunta final do usuário.
        Sua tarefa é sintetizar uma resposta útil com base nessas informações.

        Aqui está o histórico da conversa para te dar contexto sobre o que foi discutido anteriormente:
        {chat_history}

        Aqui estão os documentos de contexto recuperados de uma base de conhecimento que podem conter a resposta:
        {context}

        Com base em TODAS as informações acima, responda à seguinte pergunta. Dê prioridade às informações dos documentos de contexto. Se a resposta não estiver nos documentos, diga que não sabe. Formate a resposta como um guia passo a passo.

        Pergunta: {question}
        Resposta útil:
        """
        self.QA_PROMPT = PromptTemplate(template=PROMPT_TEMPLATE,
                                        input_variables=["chat_history", "context", "question"])
        print("[DEBUG] __init__ do QdrantChatService concluído.")

    def _get_retriever(self, department: Optional[str]):
        """Cria o retriever com filtro de departamento, se aplicável."""
        search_kwargs = {'k': 3}
        if department:
            qdrant_filter = Filter(must=[FieldCondition(key="Departamento", match=MatchValue(value=department))])
            search_kwargs['filter'] = qdrant_filter


        return self.vector_store.as_retriever(search_kwargs=search_kwargs)

    def _process_query_sync(self, question: str, history: list, department: str | None):
        retriever = self._get_retriever(department)




        memory = ConversationBufferMemory(
            chat_memory=ChatMessageHistory(),
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        for user_msg, ai_msg in history:
            memory.chat_memory.add_user_message(user_msg)
            memory.chat_memory.add_ai_message(ai_msg)

        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
            condense_question_prompt=CONDENSE_QUESTION_PROMPT,
            combine_docs_chain_kwargs={"prompt": self.QA_PROMPT},
            return_source_documents=True,
            output_key="answer"
        )



        result = qa_chain.invoke({"question": question})


        return result

    async def query(self, question: str, history: list, filtro_departamento: str | None) -> dict:
        result = await run_in_threadpool(self._process_query_sync, question, history, filtro_departamento)

        source_docs = [
            DocumentSource(page_content=doc.page_content, metadata=doc.metadata)
            for doc in result.get("source_documents", [])
        ]

        return {
            "answer": result.get("answer", "Não foi possível gerar uma resposta."),
            "source_documents": source_docs
        }


qdrant_chat_service = QdrantChatService()
