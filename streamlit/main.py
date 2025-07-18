from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache
from example import first_prompt, second_prompt
from metadata_info import metadata_field_info
from langchain.retrievers import SelfQueryRetriever

import os

api_key = os.environ.get("OPENAI_API_KEY")
os.makedirs('sqlite_cache', exist_ok=True)
set_llm_cache(SQLiteCache(database_path = './sqlite_cache/sqlite_cache.db'))

def load_vector_store():
    embeddings = OpenAIEmbeddings(model = 'text-embedding-3-large')
    vector_store = Chroma(
        persist_directory='../vectors/parent_db',
        embedding_function = embeddings,
        collection_name='parent_db'
    )
    return vector_store


def create_chain(vector_store, is_first):
    llm = ChatOpenAI(model = 'gpt-4.1')
    output_parser = StrOutputParser()
    # retriever = SelfQueryRetriever.from_llm(
    #     llm=llm,
    #     vectorstore=vector_store,
    #     document_contents="채용공고 정보",
    #     metadata_field_info=metadata_field_info,
    # )
    retriever = vector_store.as_retriever()
    if is_first:
        prompt = ChatPromptTemplate.from_messages([
            ('system', first_prompt),
            MessagesPlaceholder(variable_name='history'),
            ('human', "질문:{question}\n\n 이력서 요약\n{summary_text} \n\n 참고 문서 \n{context}")
        ])
    else:
        prompt = ChatPromptTemplate.from_messages([
            ('system', second_prompt),
            MessagesPlaceholder(variable_name='history'),
            ('human', "질문:{question} \n\n 참고문서 \n {context}'")
        ])

    chain = prompt | llm | output_parser
    return chain, retriever

def get_answer(chain, retriever, query, history, summary_text=None):
    context_docs = retriever.invoke(query)
    context_list = []
    for doc in context_docs:
        title = doc.metadata.get('title', '제목 없음')
        company = doc.metadata.get('company_name', '회사명 없음')
        url = doc.metadata.get('url', '#')
        content = doc.page_content
        context_list.append(f"제목: {title}\n회사명: {company}\nURL: {url}\n내용: {content}")
        print(context_list)
    if summary_text:
        llm_answer = chain.invoke({
            'question': query,
            'history': history,
            'context': "\n\n---\n\n".join(context_list),
            'summary_text': summary_text
        })
    else:
        llm_answer = chain.invoke({
            'question': query,
            'history': history,
            'context': "\n\n---\n\n".join(context_list)
        })
    return llm_answer