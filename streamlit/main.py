from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache
import os

api_key = os.environ.get("OPENAI_API_KEY")
os.makedirs('sqlite_cache', exist_ok=True)
set_llm_cache(SQLiteCache(database_path = '../sqlite_cache/sqlite_cache.db'))

def load_vector_store():
    embeddings = OpenAIEmbeddings(model = 'text-embedding-3-large')
    vector_store = Chroma(
        persist_directory='../vectors/parent_db',
        embeddings_function = embeddings,
        collection_name='parent_db'
    )
    return vector_store

def create_chain(vector_store):
    llm = ChatOpenAI(model = 'gpt-4.1')
    ouput_parser = StrOutputParser()
    retriever = vector_store.as_retriever()

