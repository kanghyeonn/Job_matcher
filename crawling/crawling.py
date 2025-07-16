import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

# 페이지를 순회해서 리스트 정보를 가져옴
def get_page_soup(page):
    url = 'https://www.jobkorea.co.kr/Recruit/Home/_GI_List/'
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Referer": "https://www.jobkorea.co.kr/recruit/joblist?menucode=local&localorder=1",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.jobkorea.co.kr"
    }

    payload = {
      "page": page,
      "order": 2,
      "direct": 0,
      "pagesize": 40,
      "tabindex": 0,
      "onePick": 0,
      "confirm": 0,
      "profile": 0
    }
    response = requests.post(url, headers=headers, data=payload)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup

# 채용공고리스트에서 채용공고를 가져오는 함수
def extract_announcement(soup):
    BASE_URL = 'https://www.jobkorea.co.kr'
    announcement = []
    job_list = soup.select('tbody > tr.devloopArea')
    for job in job_list:
        company_tag = job.select_one('td.tplCo a')
        title_tag = job.select_one('td.tplTit strong a')
        area_tag = job.select_one('td.tplTit p.etc span.cell:nth-of-type(3)')
        career_tag = job.select_one('td.tplTit p.etc span.cell:nth-of-type(1)')
        deadline_tag = job.select_one('td.odd span.date span.tahoma')

        company = company_tag.get_text(strip=True) if company_tag else None
        company_link = company_tag['href'] if company_tag and company_tag.has_attr('href') else '링크없음'

        title = title_tag.get_text(strip=True) if title_tag else None
        title_link = title_tag['href'] if title_tag and title_tag.has_attr('href') else '링크없음'

        area = area_tag.get_text(strip=True) if area_tag else None
        career = career_tag.get_text(strip=True) if career_tag else None
        deadline = deadline_tag.get_text(strip=True) if deadline_tag else None
        if deadline:
            deadline = deadline.replace('~', '')
            year = datetime.today().year
            deadline_date = datetime.strptime(f"{year}/{deadline}", "%Y/%m/%d")
            deadline = deadline_date.strftime("%Y-%m-%d")

        announcement.append({
            'company': company,
            'company_link': BASE_URL + company_link,
            'title': title,
            'title_link': BASE_URL+title_link,
            'area': area,
            'career': career,
            'deadline': deadline,
        })
    return announcement

# 채용공고의 정보를 가져오는 함수
def extract_posted_info(url, headers, title, deadline):

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    BASE_URL = 'https://www.jobkorea.co.kr'
    def get_text_or_none(tag):
        return tag.get_text(strip=True) if tag else None

    def get_all_texts(tags):
        return [t.get_text(strip=True) for t in tags] if tags else None

    def get_next_dd_by_dt(text):
        dt = soup.select_one(f'dt:-soup-contains("{text}")')
        return dt.find_next_sibling('dd') if dt else None

    def get_homepage_url():
        dt = soup.select_one('dt:-soup-contains("홈페이지")')
        if dt:
            dd = dt.find_next_sibling('dd')
            if dd:
                a = dd.select_one('a[href]')
                if a:
                    return a['href']
        return None

    result = {}

    # 채용공고 제목 → title
    # title_tag = soup.select_one('article.artReadJobSum h3.hd_3')
    # result['title'] = title_tag.get_text(strip=True) if title_tag else None
    result['title'] = title

    # 회사이름
    company_name = soup.select_one('span.coName')
    result['company_name'] = get_text_or_none(company_name)

    # 경력 → career
    career = get_next_dd_by_dt('경력')
    result['career'] = get_text_or_none(career)

    # 학력 → education
    education = get_next_dd_by_dt('학력')
    result['education'] = get_text_or_none(education)

    # 스킬 → skill
    skill = get_next_dd_by_dt('스킬')
    if skill:
        skills = [s.strip() for s in skill.get_text(strip=True).split(',')]
    else:
        skills = None
    result['skill'] = skills

    # 우대 → preferred
    preference_spans = soup.select('dl#dlPref dd span.pref')
    result['preferred'] = get_all_texts(preference_spans)

    # 고용형태 → contract_type
    employment_list = []
    employment_lis = soup.select('dt:-soup-contains("고용형태") + dd li')
    for li in employment_lis:
        employment_list.append(li.get_text(strip=True))
    result['contract_type'] = employment_list if employment_list else None

    # 급여 → salary
    salary = get_next_dd_by_dt('급여')
    result['salary'] = get_text_or_none(salary)

    # 지역 → location
    location = soup.select_one('dt:-soup-contains("지역") + dd a')
    result['location'] = get_text_or_none(location)

    # 시간 → working_time
    working_time = get_next_dd_by_dt('시간')
    result['working_time'] = get_text_or_none(working_time)

    # 직급 → position_level
    position = get_next_dd_by_dt('직급')
    result['position_level'] = get_text_or_none(position)

    # 직책 → position_role
    role = get_next_dd_by_dt('직책')
    result['position_role'] = get_text_or_none(role)

    # 상세요강 content
    iframe_tag = soup.select_one('article.artReadDetail iframe')
    content_url = BASE_URL + iframe_tag['src'] if iframe_tag and iframe_tag.has_attr('src') else None

    result['content'] = extract_posted_content_info(content_url, headers)

    # url
    result['url'] = url

    # 마감일 → due_date
    result['due_date'] = deadline
    # 기업정보 추가
    result['industry'] = get_text_or_none(get_next_dd_by_dt('산업(업종)'))
    result['employees'] = get_text_or_none(get_next_dd_by_dt('사원수'))
    result['founded'] = get_text_or_none(get_next_dd_by_dt('설립년도'))
    result['company_type'] = get_text_or_none(get_next_dd_by_dt('기업형태'))
    result['homepage'] = get_homepage_url()

    return result

# 채용공고의 본문내용을 가져오는 함수
def extract_posted_content_info(url, headers):
    if not url:
        return None
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    body_text = soup.body.get_text(separator='\n', strip=True)
    return body_text

def extract_posted_company_info(url, headers):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    company_name_div = soup.select_one('.company-header-branding-body .name')
    company_name = company_name_div.get_text(strip=True) if company_name_div else None

    def get_value(label):
        ths = soup.find_all('th', class_='field-label')
        for th in ths:
            if th.get_text(strip=True) == label:
                td = th.find_next_sibling('td')
                return td.get_text(strip=True) if td else None
        return None

    return {
        'company_name': company_name,
        'industry': get_value('산업'),
        'company_type': get_value('기업구분'),
        'capital': get_value('자본금'),
        'ceo': get_value('대표자'),
        'insurance': get_value('4대보험'),
        'address': get_value('주소'),
        'employees': get_value('사원수'),
        'founded_date': get_value('설립일'),
        'sales': get_value('매출액'),
        'business_desc': get_value('주요사업'),
        'homepage': get_value('홈페이지'),
    }

# mysql에 넣기 위한 데이터 전처리
def preprocess_data_for_mysql(data):
    processed_data = {}
    for key, value in data.items():
        if value is None:
            processed_data[key] = None
        elif isinstance(value, list):
            # 리스트는 JSON 문자열로 변환 (권장)
            processed_data[key] = json.dumps(value, ensure_ascii=False)
        elif isinstance(value, str):
            processed_data[key] = value.strip()
        else:
            processed_data[key] = str(value).strip()
    return processed_data

