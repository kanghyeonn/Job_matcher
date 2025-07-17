from PyPDF2 import PdfReader
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.schema.runnable import RunnableLambda
api_key = os.environ.get("OPENAI_API_KEY")

# pdf 파일에서 파일을 읽어 text를 추출하는 함수
def extract_text_from_file(uploaded_file):
    if uploaded_file.name.endswith('.pdf'):
        reader = PdfReader(uploaded_file)
        text = '\n'.join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text
    else:
        return uploaded_file.read().decode('utf8')

# 업로드한 파일을 요약하는 함수
def summary_uploadfile_text(uploaded_file):
    model = ChatOpenAI(
        model='gpt-4.1',
        temperature=0.1,
    )

    response_schemas = [
        ResponseSchema(name="학력", description="최종 학력과 졸업 여부를 포함한 정보 (예: 전문학사 졸업)"),
        ResponseSchema(name="학력수치", description="학력을 숫자로 표현 (전문학사=0, 학사=1, 석사=2, 박사=3, 무관=-1, 고졸=-2)"),
        ResponseSchema(name="학과", description="전공한 학과명 (예: 컴퓨터공학과)"),
        ResponseSchema(name="경력", description="경력 요약 (예: 3년차, 대리, 5년차, 신입) 및 인턴·대외활동 여부 명시"),
        ResponseSchema(name="경력수치", description="경력을 숫자로 표현. 신입=0, 1년차=1, 2년차=2, …, 대리=3, 과장=5, 차장=8, 무관=-1"),
        ResponseSchema(name="자격증", description="보유 자격증명과 취득 시기 (예: 정보처리산업기사 2024.09)"),
        ResponseSchema(name="보유스킬", description="보유 기술 스택 목록 (예: Java, Spring Boot, JPA, MySQL 등)"),
        ResponseSchema(name="자기소개서", description="자기소개서 전체 내용")
    ]

    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()


    prompt = ChatPromptTemplate.from_template(
        """
        너는 이력서에서 경력, 학과, 학력, 자격증, 보유스킬, 자기소개서 내용을 추출하는 전문가야.
    
        경력수치는 아래 기준으로 변환해.
        - 신입은 0
        - 1년차는 1
        - 2년차는 2
        - 3년차는 3
        - 4년차는 4 … 경력 연차에 맞춰 숫자를 그대로 사용해
        - 직급으로 표현된 경우 (대리=3, 과장=5, 차장=8)
        - 무관은 -1로 처리해
    
        숫자화된 학력과 경력 정보를 포함해서 JSON으로 변환해줘.
    
        {format_instructions}
    
        이력서 본문:
        \"\"\"
        {content}
        \"\"\"
        """
    )

    chain = (
        prompt
        | model
        | RunnableLambda(lambda x: output_parser.parse(x.content))
    )

    result = chain.invoke({
        "format_instructions" : format_instructions,
        "content" : uploaded_file
    })

    return result