import mysql.connector

# def insert_data_to_db(posted, company_data):
#     try:
#         conn = mysql.connector.connect(
#             host='localhost',
#             user='root',
#             password='0000',
#             database='job_matcher'
#         )
#         cursor = conn.cursor()
#
#         # 1️⃣ 회사 중복 확인
#         select_query = "SELECT id FROM company WHERE company_name = %s"
#         cursor.execute(select_query, (company_data['company_name'],))
#         result = cursor.fetchone()
#
#         if result:
#             # 회사가 이미 있을 경우 → 기존 id 사용
#             company_id = result[0]
#         else:
#             # 회사가 없을 경우 → INSERT
#             insert_company_query = """
#             INSERT INTO company (
#                 company_name, industry, company_type, capital, ceo, insurance, address,
#                 employees, founded_date, sales, business_desc, homepage
#             ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """
#
#             company_values = (
#                 company_data['company_name'],
#                 company_data['industry'],
#                 company_data['company_type'],
#                 company_data['capital'],
#                 company_data['ceo'],
#                 company_data['insurance'],
#                 company_data['address'],
#                 company_data['employees'],
#                 company_data['founded_date'],
#                 company_data['sales'],
#                 company_data['business_desc'],
#                 company_data['homepage']
#             )
#
#             cursor.execute(insert_company_query, company_values)
#             company_id = cursor.lastrowid
#
#         # 2️⃣ 채용공고 데이터 INSERT
#         insert_posted_query = """
#         INSERT INTO posted (
#             company_id, title, career, education, skill, preferred,
#             contract_type, salary, location, working_time,
#             position_level, position_role, content, url, due_date
#         ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
#
#         posted_values = (
#             company_id,
#             posted['title'],
#             posted['career'],
#             posted['education'],
#             posted['skill'],
#             posted['preferred'],
#             posted['contract_type'],
#             posted['salary'],
#             posted['location'],
#             posted['working_time'],
#             posted['position_level'],
#             posted['position_role'],
#             posted['content'],
#             posted['url'],
#             posted['due_date']
#         )
#
#         cursor.execute(insert_posted_query, posted_values)
#
#         conn.commit()
#
#     except mysql.connector.Error as e:
#         print('MySQL 에러:', e)
#         conn.rollback()
#
#     finally:
#         cursor.close()
#         conn.close()

# 채용공고를 중복해서 스크래핑 방지

def is_posted_url_exist(cursor, url):
    check_query = "SELECT id FROM job_postings WHERE url = %s"
    cursor.execute(check_query, (url,))
    return cursor.fetchone() is not None

def insert_job_posting(cursor, conn, data):
    sql = """
    INSERT INTO job_postings (
        title, company_name, career, education, skill, preferred, contract_type,
        salary, location, working_time, position_level, position_role, content,
        url, due_date, industry, employees, founded, company_type, homepage
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    """

    params = (
        data.get('title'),
        data.get('company_name'),
        data.get('career'),
        data.get('education'),
        data.get('skill'),
        data.get('preferred'),
        ', '.join(data.get('contract_type', [])) if isinstance(data.get('contract_type'), list) else data.get('contract_type'),
        data.get('salary'),
        data.get('location'),
        data.get('working_time'),
        data.get('position_level'),
        data.get('position_role'),
        data.get('content'),
        data.get('url'),
        data.get('due_date'),  # 날짜 파싱 필요시 datetime.strptime() 사용
        data.get('industry'),
        data.get('employees'),
        data.get('founded'),
        data.get('company_type'),
        data.get('homepage')
    )
    #   print('execute 전')
    cursor.execute(sql, params)
    print(f"Inserted ID: {cursor.lastrowid}")

