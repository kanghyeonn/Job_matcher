from crawling import *
from database import *
from header import *
import mysql.connector
import time
import random
import os

mysql_pw = os.environ['MYSQL']

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='0000',
    database='job_matcher'
)

cursor = conn.cursor()


for page in range(3,5):
    try:
        page_soup = get_page_soup(page)
        #print("page soup")
        # 채용공고 리스트
        announcements = extract_announcement(page_soup)
        #print("extract announcements")
        for announcement in announcements:
            header = get_random_headers(headers_list)
            try:
                title = announcement['title']
                posted_url = announcement['title_link']
                if is_posted_url_exist(cursor, posted_url):
                    print(f"중복 공고로 건너뜀: {posted_url}")
                    continue
                posted_url = announcement['title_link']
                # company_url = announcement['company_link']
                deadline = announcement['deadline']
                # 공고 정보 추출
                posted = extract_posted_info(posted_url, header, title, deadline)
                #print("extract posted")

                # 회사 정보 추출
                #company = extract_posted_company_info(company_url, headers)

                # 데이터 전처리
                posted = preprocess_data_for_mysql(posted)
                print(posted)
                #company = preprocess_data_for_mysql(company)
                #company_name = company['company_name']

                # db 삽입
                insert_job_posting(cursor, conn, posted)

                print(f'{title} db에 추가')
                conn.commit()
                time.sleep(random.uniform(5, 10))
            except Exception as e:
                print(header)
                print(f"에러발생 : {e}")
        print(f'{page} 작업 완료')
        time.sleep(random.uniform(3, 6))
    except Exception as e:
        print(f"에러 발생 : {e}")

cursor.close()
conn.close()
print('프로그램 종료')