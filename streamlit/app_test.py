import uuid

from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage

from main import *
from preprocessing_uploadfile import *
import streamlit as st
import uuid

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
session_id = st.session_state.session_id

if 'vector_store' not in st.session_state:
    st.session_state.vector_store = load_vector_store()

if 'is_first_question' not in st.session_state:
    st.session_state.is_first_question = True

if 'summary_text' not in st.session_state:
    st.session_state.summary_text = None

if 'all_memory' not in st.session_state:
    st.session_state.all_memory = {}

if session_id not in st.session_state.all_memory:
    st.session_state.all_memory[session_id] = ConversationBufferMemory(return_messages=True)

user_memory = st.session_state.all_memory[session_id]

st.title("📑 이력서 기반 채용공고 추천 챗봇")

uploaded_file = st.file_uploader("📄 이력서 또는 포트폴리오를 업로드하세요", type=['pdf'])

for message in user_memory.chat_memory.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message('user'):
            st.write(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message('assistant'):
            st.write(message.content)

if uploaded_file is not None:
    with st.spinner("⏳ 이력서를 분석하는 중입니다..."):
        extracted_text = extract_text_from_file(uploaded_file)
        st.session_state.summary_text = summary_uploadfile_text(extracted_text)
    #st.subheader("📄 이력서 요약")
    #st.markdown(summary_text['학력'])
    if 'chain' not in st.session_state:
        st.session_state.chain, st.session_state.retriever = create_chain(
            st.session_state.vector_store,
            is_first=True
        )

    user_input = st.chat_input("💬 궁금한 내용을 입력해 주세요")
    if user_input:
        with st.chat_message('user'):
            st.write(user_input)
        user_memory.chat_memory.add_user_message(user_input)
        history = user_memory.load_memory_variables({})['history']

        if st.session_state.is_first_question:
            ai_response = get_answer(
                st.session_state.chain,
                st.session_state.retriever,
                user_input,
                history,
                st.session_state.summary_text
            )
            st.session_state.is_first_question = False

            st.session_state.chain, st.session_state.retriever = create_chain(
                st.session_state.vector_store, is_first=False
            )
        else:
            ai_response = get_answer(
                st.session_state.chain,
                st.session_state.retriever,
                user_input,
                history
            )
        with st.chat_message('assistant'):
            st.write(ai_response)
        user_memory.chat_memory.add_ai_message(ai_response)
else:
    st.info("📂 파일을 업로드해 주세요.")
    st.text_input("💬 궁금한 내용을 입력해 주세요", disabled=True)

