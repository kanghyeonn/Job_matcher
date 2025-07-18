from langchain.chains.query_constructor.schema import AttributeInfo

metadata_field_info = [
    AttributeInfo(
        name="location",
        description="채용공고의 근무지역명 (예: 서울, 경기, 부산 등)",
        type="string"
    ),
    AttributeInfo(
        name="industry",
        description="채용공고의 산업 또는 업종명 (예: 외식업, IT, 금융, 제조업 등)",
        type="string"
    ),
    AttributeInfo(
        name="career",
        description="채용공고에서 요구하는 경력 조건 (예: 경력, 신입, 무관)",
        type="string"
    ),
    AttributeInfo(
        name="education",
        description="채용공고에서 요구하는 학력 조건 (예: 대졸, 고졸, 무관)",
        type="string"
    ),
    AttributeInfo(
        name="contract_type",
        description="채용공고의 고용 형태 (예: 정규직, 계약직, 아르바이트)",
        type="string"
    ),
]
