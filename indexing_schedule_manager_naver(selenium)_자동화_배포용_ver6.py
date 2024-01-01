# -*- coding: utf-8 -*-

import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import platform
import datetime
import undetected_chromedriver as uc
from tqdm import tqdm
import requests
import json
import re
import advertools as adv
from pprint import pprint as pp
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import random
from urllib import parse
from pathlib import Path
import subprocess
import pandas as pd
from tabulate import tabulate
import feedparser
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import schedule
import os
import urllib3

urllib3.disable_warnings()

osName = platform.system()  # window 인지 mac 인지 알아내기 위한
# print(osName)

# # 필요한 패키지들을 리스트에 저장합니다.
# import subprocess
# packages = [
#     "chromedriver-autoinstaller",
#     "openai",
#     "selenium",
#     "chardet",
#     "beautifulsoup4",
#     "emoji",
#     "requests",
#     "pyperclip",
#     "schedule",
#     "bs4",
#     "pandas",
#     "tabulate",
#     "httplib2",
#     "ServiceAccountCredentials",
#     "undetected_chromedriver",
#     "fake_useragent",
#     "advertools",
#     "lxml",
#     "oauth2client"
# ]
#
# # 각 패키지를 설치합니다.
# for package in packages:
#     try:
#         # pip를 통해 패키지를 설치합니다.
#         subprocess.check_call(["pip", "install", package])
#         print(f"{package} installed successfully!")
#     except subprocess.CalledProcessError:
#         # 패키지 설치 실패 메시지 출력
#         print(f"Failed to install {package}.")
#     # 설치가 완료되었으면 코드블럭 아래에 설치 완료 메시지를 출력합니다.
#     print("\nAll packages installed successfully!")


# TODO: github는 sitemap으로 가져왔을때 순서가 최신순으로 정렬이 되는게 아니라 반대로 되어있어 수정해 줘야 함
# TODO: owshopping 에 왜 ree31206.mycafe24.com 데이터가 써졌는지 확인
# TODO: 워드프레스 한번 확인해 보기

C_END = "\033[0m"
C_BOLD = "\033[1m"
C_INVERSE = "\033[7m"
C_BLACK = "\033[30m"
C_RED = "\033[31m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"
C_BLUE = "\033[34m"
C_PURPLE = "\033[35m"
C_CYAN = "\033[36m"
C_WHITE = "\033[37m"
C_BGBLACK = "\033[40m"
C_BGRED = "\033[41m"
C_BGGREEN = "\033[42m"
C_BGYELLOW = "\033[43m"
C_BGBLUE = "\033[44m"
C_BGPURPLE = "\033[45m"
C_BGCYAN = "\033[46m"
C_BGWHITE = "\033[47m"

# TODO: 사이트들이 많을 경우 리스트화해서 전부 기지고 올수 있도록 해야함(일단 사이트 200개 목표)
# TODO: 기존에 wordpress 의 경우 wordpress API 를 사용하여 리스트를 업데이트 하였으나 속도가 매우 느림(그땐 sitemap 을 이용하면 리스트가 최신 업데이트 순서가 아닌 거꾸로 있는 경우 대부분)
# 따라서 기본적으로 sitemap에 의해 리스트를 가져오고 최신 데이터는 wordpress API를 통해 업데이트 되도록 변경(왜 다시 wordpress API 추가적으로 하냐면? sitemap 업데이트가 너무 느림)
# TODO: 기존에는 txt 로 관리하던것을 엑셀로 리스트가 업데이트 되도록 변경(추후 google app script와 연동을 위한 이유와 색인 여부 필드 추가 및 기타)
# TODO: 각 사이트별로 여러개의 주소가 존재할때 리스트 형태로 처리가 되도록 수정

# [사용자 입력 정보]
# ======================================================================================================== START

# 업로드 대상이 되는 티스토리 블로그 주소(본인들의 주소를 적어주시면 됩니다.)
tistory_address_lists = ['https://theface71.tistory.com/', '']

# 업로드 대상이 되는 본인 사이트의 rss 정보
rss_blog_address = 'https://todaynews.kr/rss_view.php'  # sample - rss full 주소
rss_site_address = 'https://todaynews.kr'  # sample - rss 사이트의 original 주소w
rss_blog_address_lists = ['https://todaynews.kr/rss_view.php']

# 워드프레스 정보
wordpress_blog_address_lists = ['',
                                '']  # 업로드 대상이 되는 워드프레스 블로그 주소 리스트
WP_ID = ['', '']  # 자신의 워드프레스 ID 정보 리스트
WP_BASIC_TOKEN = ['xxxx xxxx xxxx xxxx xxxx xxxx', 'xxxx xxxx xxxx xxxx xxxx xxxx']  # BASIC 토큰 정보 리스트
WP_JWT_TOKEN = ['', '']

# 최근 포스팅된 포스팅 리스트를 몇개까지 가져올 것인지 결정
# 해당 리스트는 sitemap 으로 리스트를 가져온 후 wordpress API 로 최근 데이터 업데이트 할때 사용
# 0을 입력하면 모둔 posting 정보를 가져오게 합니다. sitemap 업데이트 주기가 늦기 때문에 200 ~ 250개 사이로 해야함 개인마다 다름
available_max_post_list_num = 300

# 네이버 indexnow를 사용하기 때문에 한번 reqeuest에 1만개까지 요청 가능하며. 구글의 경우는 하루에 200개, 빙의 경우 250개
# 하지만 현재 indexnow 는 잘 색인이 안되어 본 프로그램에서는 내용 삭제, 현재 네이버서치어드바이져에 의한 requests 방법을 사용하여 50개
available_indexing_list_num = 50

# 네이버에 로그인을 이미 했는지 안했는지 저장하는 부분
already_naver_login = False

# 업로드 대상이 되는 github 블로그 주소(본인들의 주소를 적어주시면 됩니다.)
github_blog_address_lists = ['', '']

# 포스팅된 리스트들을 저장할 txt 파일의 path
csv_submit_urls_path = "./"

# time 정보
PAUSE_TIME = 1  # 셀레니움 수행도중 중간중간 wait time
LOADING_WAIT_TIME = 5  # 페이지의 로딩 시간
LOGIN_WAIT_TIME = 180  # 로그인시 기다리는 시간
SEARCHADVISOR_RESPONSE_WATE_TIME = 10  # (naver) 서치어드바이저에 url을 넣고 수집요청을 눌렀을때 응답을 기다리는 시간
INDEXING_WAIT_TIME = 10  # indexing request 사이의 시간 간격 (고정)
# INDEXING_WAIT_TIME = random.randint(20, 60)  # indexing request 사이의 시간 간격 (랜덤)

# user agent 랜덤화
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
]
user_agent = random.choice(user_agents)
fixed_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Whale/3.19.166.16 Safari/537.36'


# [사용자 입력 정보]
# ======================================================================================================== END

# [시스템 공통 입력 정보]
# ======================================================================================================== START

# [시스템 공통 입력 정보]
# ======================================================================================================== END


# def init_driver():  # google과 같이 로봇에 의해 검증을 요청할 때
#     # "This version of ChromeDriver only supports Chrome version 114" 만약에 이런 에러가 발생하면
#     # C:\Users\ree31\AppData\Local\Programs\Python\Python311\python.exe -m pip uninstall undetected_chromedriver
#     # C:\Users\ree31\AppData\Local\Programs\Python\Python311\python.exe -m pip install undetected_chromedriver
#     # 위와 같이 undetected_chromedriver를 제설치하면 됩니다.
#     # driver = uc.Chrome(version_main=104)
#     driver = uc.Chrome()
#     driver.maximize_window()  # 창 최대화
#     return driver

# def init_driver():  # 일반적인 driver init
#     options = webdriver.ChromeOptions()
#     options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
#
#     _driver = webdriver.Chrome(service=ChromeService(
#         ChromeDriverManager().install(), options=options))
#     _driver.maximize_window()  # 창 최대화
#     return _driver

def init_driver():  # 인증정보들을 chrometemp 에 저장하고 그것을 유지하고 싶을때
    # try :
    #     shutil.rmtree(r"C:\chrometemp")  #쿠키 / 캐쉬파일 삭제(캐쉬파일 삭제시 로그인 정보 사라짐)
    # except FileNotFoundError :
    #     pass

    if osName not in "Windows":
        try:
            subprocess.Popen([
                '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9232 --user-data-dir="~/Desktop/crawling/chromeTemp32"'],
                shell=True, stdout=subprocess.PIPE)  # 디버거 크롬 구동
        except FileNotFoundError:
            subprocess.Popen([
                '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9232 --user-data-dir="~/Desktop/crawling/chromeTemp32"'],
                shell=True, stdout=subprocess.PIPE)
    else:
        try:
            subprocess.Popen(r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9232 '
                             r'--user-data-dir="C:\chromeTemp32"')  # 디버거 크롬 구동
        except FileNotFoundError:
            subprocess.Popen(
                r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9232 '
                r'--user-data-dir="C:\chromeTemp32"')

    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9232")

    # 아래의 코드는 현재 사용하고 싶은 크롬드라이버의 위치를 나타낸다 최근 드라이버의 위치를 아래와 같이 절대 주소로 적어줘야 한다.
    # 이것을 위해 한번 실행을 하면 C:\\Users\\xxx\\.wdm\\drivers\\chromedriver\\win64 아래에 최신 크롬 드라이버가 받아진다
    # 바로 아래에 있는 형태로 절대주소 패스를 적어주면 된다.

    service = ChromeService('C:\\Users\\ree31\\.wdm\\drivers\\chromedriver\\win64\\118.0.5993.71\\chromedriver.exe')
    # service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(LOADING_WAIT_TIME)
    return driver


def get_tistory_post_lists_indexing_naver(driver):
    for tistory_blog_address in tistory_address_lists:
        modified_tistory_blog_address = tistory_blog_address.replace('https://', '').replace('http://', '').replace(
            '.', '_')
        csv_save_path = f'{csv_submit_urls_path}naver_{modified_tistory_blog_address}_submit_urls.csv'

        submit_urls = []
        tistory_sitemap_address = f'{tistory_blog_address}/sitemap.xml'  # 사이트맵 URL

        res = requests.get(tistory_sitemap_address)
        pattern = f'(?<={tistory_blog_address}/)+[^\s]*(?=</loc>)'
        url_info_lists = re.findall(pattern, res.text)
        # print(url_info_lists)

        print
        count = 1
        for url_info in url_info_lists:
            temp_dict = {}
            if url_info.isdigit() or url_info.find('entry/') == 0:  # ex) entry/%EC%98%A4%ED%94%BC%EC 이라서 0값을 반환한 것들만 처리
                url = f'{tistory_blog_address}/{url_info}'
                temp_dict['url'] = f'{url}'
                temp_dict['indexed'] = 'X'
                # print(f'{count}. {tistory_blog_address}/{url_info}')
                submit_urls.append(temp_dict)  # 새로운 데이터를 아래에 쌓는다 그러면 중복된 데이터를 첵크할때 first 명령어를 통해 위쪽 데이터를 남기게 된다.
                count = count + 1

        columns = ['url', 'indexed']
        df = pd.DataFrame(submit_urls, columns=columns)
        print(df.head(5))
        print(df.tail(5))

        # print(tabulate(df, headers='keys', tablefmt='grid'))
        if not os.path.exists(csv_save_path):
            df.to_csv(csv_save_path, mode='w', sep=',', na_rep='NaN', encoding='utf-8-sig', index=False)
        else:
            df.to_csv(csv_save_path, mode='a', sep=',', na_rep='NaN', encoding='utf-8-sig', index=False, header=False)

        print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}({csv_save_path})에서 중복된 행을 제거 시작{C_END}')
        data = pd.read_csv(csv_save_path)
        data = data.drop_duplicates(subset=['url'],
                                    keep="first")  # 중복제거를할때 남길 행입니다. first면 위에서부터 첫값을 남기고 last면 행의 마지막 값을 남깁
        data.to_csv(csv_save_path, index=False, encoding="utf-8-sig")
        print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}({csv_save_path})에서 중복된 행을 제거 완료{C_END}')

        print(f'\ntistory sitemap 정보를 이용하여 ({csv_save_path})로 ({len(submit_urls)})개의 포스팅 url을 저장하는데 성공하였습니다.')

        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[네이버써치어드바이저 로그인 후 쿠키값 저장 및 세션 리턴 시작]', C_END)
        naver_searchadvisor_session = get_cookies_session(driver,
                                                          f'https://searchadvisor.naver.com/console/site/request/crawl?site={tistory_blog_address}')
        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[네이버써치어드바이저 로그인 후 쿠키값 저장 및 세션 리턴 완료]', C_END)

        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[네이버에 requests로 색인 시작]', C_END)
        indexing_naver(driver, naver_searchadvisor_session, tistory_blog_address, csv_save_path)
        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[네이버에 requests로 색인 완료]', C_END)


def get_wordpress_post_lists_indexing_naver(driver):
    pre_df = pd.DataFrame()

    for address_idx, wordpress_blog_address in enumerate(wordpress_blog_address_lists):
        modified_wordpress_blog_address = wordpress_blog_address.replace('https://', '').replace('http://', '').replace(
            '.', '_')
        csv_save_path = f'{csv_submit_urls_path}naver_{modified_wordpress_blog_address}_submit_urls.csv'

        if not os.path.exists(csv_save_path):
            Path(csv_save_path).touch(exist_ok=True)
        else:
            pre_df = pd.read_csv(csv_save_path)

        """ sitemap 을 이용한 빠른 리스트 업데이트 (업그레이드 방법) """
        # 참고자료: https://www.nadeem.tech/automate-your-seo-indexing-strategy-with-python-and-wordpress/
        submit_urls = []
        # TODO: Rank Math sitemap_index.xml(post-sitemap1.xml, post-sitemap2.xml,...)
        # TODO: 워드프레스 자체 제공, wp-sitemap.xml, 웹호스팅 서버에 SimpleXML PHP 익스텐션이 설치되어 있어야 하고 info.php 파일을 루트 폴더에 올려야 합니다. 이미지, 비디오, 뉴스 사이트맵 기능이 없습니다.
        # TODO: Jetpack sitemap.xml(sitemap-1.xml, sitemap-2.xml,...), news-sitemap.xml
        # TODO: All in One SEO
        # TODO: Yoast SEO, sitemap_index.xml

        # Jetpack sitemap 플러그인이 설치된 환경에서만 구동 가능
        post_count = 0
        for idx in range(100):  # sitemap-1,... 당 2000개 max로 저장되어 100x2000=200000 까지 저장할수 있음, 100이라는 숫자는 조절가능
            # print("test1")
            wordpress_sitemap_address = f"{wordpress_blog_address}/sitemap-{idx + 1}.xml"
            # print(wordpress_sitemap_address)

            res = requests.get(wordpress_sitemap_address)
            if res.status_code != 200:
                break
            # pattern = '(?<=<loc>)[a-zA-z]+://[^\s]*(?=</loc>)'
            pattern = '<loc>(.*?)</loc>'
            url_info_lists = re.findall(pattern, res.text)

            print
            for url_info in url_info_lists:
                temp_dict = {}
                post_count = post_count + 1
                temp_dict['url'] = f'{url_info}'
                temp_dict['indexed'] = 'X'
                # print(f'{post_count}. {url_info}')
                submit_urls.insert(0,
                                   temp_dict)  # 앞쪽에 계속 추가 왜냐면 sitemap 순서가 최근순서가 아님 맨아래가 최신 포스팅, insert는 삽입 위치까지 넣어주어야함 맨앞에
                # submit_urls.append(f'{url_info}')

        print(f'\nwordpress sitemap 정보를 이용하여 ({csv_save_path})로 ({len(submit_urls)})개의 포스팅 url을 저장하는데 성공하였습니다.')

        columns = ['url', 'indexed']
        df1 = pd.DataFrame(submit_urls, columns=columns)

        print(f'\ndf1 = >')
        print(df1.head(5))
        print(df1.tail(5))

        total = pre_df._append(df1)  # pre_df 에 하단으로 df1을 붙여준다.

        print(f'\total(pre_df + df1) = >')
        print(total.head(5))
        print(total.tail(5))

        # print(tabulate(df, headers='keys', tablefmt='grid'))
        print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}(total dataFrame)에서 중복된 행을 제거 시작{C_END}')
        total = total.drop_duplicates(subset=['url'], keep="first")
        print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}(total dataFrame)에서 중복된 행을 제거 완료{C_END}')

        """ +wordpress API를 이용한 최근 리스트 받아오는 방법(앞선 sitemap 리스트 + 최근 리스트는 wordpress API를 사용하여 업데이트) """
        submit_urls = []

        def page_numbers():
            # Infinite generate of page numbers
            num = 1
            while True:
                yield num
                num += 1

        # # ===============================================================
        # basic token 을 이용할 때
        # # ===============================================================

        # keys = {
        #     'wp_key': WP_BASIC_TOKEN[address_idx],
        #     'user': WP_ID[address_idx]
        # }
        #
        # # Define WP Keys
        # user = keys['user']
        # password = keys['wp_key']
        #
        # # Create WP Connection
        # creds = user + ':' + password
        #
        # # Encode the connection of your website
        # token = base64.b64encode(creds.encode())
        #
        # # Prepare the header of our request
        # headers = {'Authorization': 'Basic ' + token.decode('utf-8')}

        # # ===============================================================
        # jwt token 을 이용할 때
        # # ===============================================================

        headers = {
            "Authorization": f"Bearer {WP_JWT_TOKEN[address_idx]}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if available_max_post_list_num == 0:  # 전체 포스팅 항목을 모두 가져오는 경우
            print(f'\n전체 포스팅 정보를 가져오려면 페이지당 request를 해야하므로 시간이 오래 걸릴 수 있습니다.')
            posts = []
            for page in tqdm(page_numbers()):
                # print(page)
                # Fetch the next [pagesize=10] posts
                posts_page = requests.get(f'{wordpress_blog_address}/wp-json/wp/v2/posts',
                                          params={"page": page, "per_page": 100},
                                          headers=headers).json()
                # print(posts_page)
                # sleep(PAUSE_TIME)
                # Check for "last page" error code
                if isinstance(posts_page, dict) and posts_page[
                    "code"] == "rest_post_invalid_page_number":  # Found last page
                    break
                # No error code -> add posts
                posts += posts_page
                # print(len(posts))
        else:  # 포스팅 항목중 원하는 갯수만 가져오는 경우
            if available_max_post_list_num % 100 > 0:
                calculate_page = available_max_post_list_num // 100 + 1  # 전체 페이지 수
                calculate_per_page = available_max_post_list_num % 100
            else:
                calculate_page = available_max_post_list_num // 100
                calculate_per_page = 100

            posts = []
            for page in tqdm(page_numbers()):
                if calculate_page < page:
                    break
                print(
                    f'\n{C_BOLD}{C_YELLOW}{C_BGRED}{page}, {calculate_page}, {calculate_per_page}, {calculate_per_page if calculate_page == page else 100}{C_END}')
                # print("page = ", page)
                # Fetch the next [pagesize=10] posts
                posts_page = requests.get(f'{wordpress_blog_address}/wp-json/wp/v2/posts',
                                          params={"page": page,
                                                  "per_page": calculate_per_page if calculate_page == page else 100},
                                          headers=headers).json()

                # Check for "last page" error code
                # print(f'\n{posts_page}')
                if isinstance(posts_page, dict) and posts_page[
                    "code"] == "rest_post_invalid_page_number":  # Found last page
                    break
                # No error code -> add posts
                posts += posts_page
                # print(len(posts))
                if page == 1 and len(posts) < 100:
                    break
                # pp(posts_page)
                # print(f'\n{posts_page}')

        # print(posts)
        post_count = 0
        # for post in reversed(posts):
        for post in posts:
            temp_dict = {}
            post_count = post_count + 1
            temp_dict['url'] = f'{post["link"]}'
            temp_dict['indexed'] = 'X'
            # print(f'{post_count}. {post["link"]}')
            submit_urls.append(temp_dict)  # sitemap 데이터와는 다르게 wordpress API는 상단이 최신데이터기 때문에 그대로 append 시켜줌
            # submit_urls.insert(0, temp_dict)  # 위쪽에 추가를 계속 해준다. 그런데 wordpress API 최신데이터가 위에 오기 때문에 reversed 된 리스트 순으로 위로 올려준다.

        print(f'\nwordpress API 정보를 이용하여 ({csv_save_path})로 ({len(posts)})개의 포스팅 url을 저장하는데 성공하였습니다.')

        columns = ['url', 'indexed']
        df2 = pd.DataFrame(submit_urls, columns=columns)

        print(f'\ndf2 = >')
        print(df2.head(5))
        print(df2.tail(5))

        total = df2._append(total)

        print(f'\total(df2 + total) = >')
        print(total.head(5))
        print(total.tail(5))

        # print(tabulate(df, headers='keys', tablefmt='grid'))
        print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}(total dataFrame)에서 중복된 행을 제거 시작{C_END}')
        total = total.drop_duplicates(subset=['url'],
                                      keep="last")  # 중복제거를할때 남길 행입니다. first면 위에서부터 첫값을 남기고 last면 행의 마지막 값을 남깁
        print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}(total dataFrame)에서 중복된 행을 제거 완료{C_END}')

        print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}({csv_save_path})에 데이터 저장 시작{C_END}')
        total.to_csv(csv_save_path, mode='w', sep=',', na_rep='NaN', encoding='utf-8-sig', index=False)
        print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}({csv_save_path})에 데이터 저장 완료{C_END}')

        print(
            f'\nwordpress API 를 사용하여 포스팅 리스트를 가져와 ({csv_save_path})로 ({available_max_post_list_num})개 이하의 포스팅 url을 저장하는데 성공하였습니다.')

        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[네이버써치어드바이저 로그인 후 쿠키값 저장 및 세션 리턴 시작]', C_END)
        naver_searchadvisor_session = get_cookies_session(driver,
                                                          f'https://searchadvisor.naver.com/console/site/request/crawl?site={wordpress_blog_address}')
        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[네이버써치어드바이저 로그인 후 쿠키값 저장 및 세션 리턴 완료]', C_END)

        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[네이버에 requests로 색인 시작]', C_END)
        indexing_naver(driver, naver_searchadvisor_session, wordpress_blog_address, csv_save_path)
        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[네이버에 requests로 색인 완료]', C_END)


def get_github_post_lists_indexing_naver(driver):
    for github_blog_address in github_blog_address_lists:
        modified_tistory_blog_address = github_blog_address.replace('https://', '').replace('http://', '').replace('.',
                                                                                                                   '_')
        csv_save_path = f'{csv_submit_urls_path}naver_{modified_tistory_blog_address}_submit_urls.csv'

        submit_urls = []
        github_sitemap_address = f'{github_blog_address}/sitemap.xml'  # 사이트맵 URL

        res = requests.get(github_sitemap_address)
        pattern = f'(?<={github_blog_address}/)+[^\s]*(?=</loc>)'
        url_info_lists = re.findall(pattern, res.text)
        # print(url_info_lists)

        print
        count = 1
        for url_info in url_info_lists:
            temp_dict = {}
            if url_info.isdigit() or url_info.find('posts/') == 0 or url_info.find(
                    '2023/') == 0:  # ex) entry/%EC%98%A4%ED%94%BC%EC 이라서 0값을 반환한 것들만 처리
                # TODO: github 의 경우 어떤 테마를 쓰느냐에 따라 정화한 색인 대상 url 을 구분하기 힘들다 따라서 어떤 github는 2023/ 이라는 특징을 가진 url 로 필터링을 한다 (현 하드코딩, 추후 다른 방법 필요)
                url = f'{github_blog_address}/{url_info}'
                temp_dict['url'] = f'{url}'
                temp_dict['indexed'] = 'X'
                # print(f'{count}. {github_blog_address}/{url_info}')
                # submit_urls.append(temp_dict)  # 새로운 데이터를 아래에 쌓는다 그러면 중복된 데이터를 첵크할때 first 명령어를 통해 위쪽 데이터를 남기게 된다.
                submit_urls.insert(0, temp_dict)  # github는 sitemap 에서 가져오는 데이터가 거꾸로 쌓여있음 즉 최신것이 아래에 있음
                count = count + 1

        columns = ['url', 'indexed']
        df = pd.DataFrame(submit_urls, columns=columns)

        print(df.head(5))
        print(df.tail(5))

        # print(tabulate(df, headers='keys', tablefmt='grid'))
        if not os.path.exists(csv_save_path):
            df.to_csv(csv_save_path, mode='w', sep=',', na_rep='NaN', encoding='utf-8-sig', index=False)
        else:
            df.to_csv(csv_save_path, mode='a', sep=',', na_rep='NaN', encoding='utf-8-sig', index=False, header=False)

        print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}({csv_save_path})에서 중복된 행을 제거 시작{C_END}')
        data = pd.read_csv(csv_save_path)
        data = data.drop_duplicates(subset=['url'],
                                    keep="first")  # 중복제거를할때 남길 행입니다. first면 위에서부터 첫값을 남기고 last면 행의 마지막 값을 남깁
        data.to_csv(csv_save_path, index=False, encoding="utf-8-sig")
        print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}({csv_save_path})에서 중복된 행을 제거 완료{C_END}')

        print(f'\ngithub sitemap 정보를 이용하여 ({csv_save_path})로 ({len(submit_urls)})개의 포스팅 url을 저장하는데 성공하였습니다.')

        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[네이버써치어드바이저 로그인 후 쿠키값 저장 및 세션 리턴 시작]', C_END)
        naver_searchadvisor_session = get_cookies_session(driver,
                                                          f'https://searchadvisor.naver.com/console/site/request/crawl?site={github_blog_address}')
        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[네이버써치어드바이저 로그인 후 쿠키값 저장 및 세션 리턴 완료]', C_END)

        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[네이버에 requests로 색인 시작]', C_END)
        indexing_naver(driver, naver_searchadvisor_session, github_blog_address, csv_save_path)
        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[네이버에 requests로 색인 완료]', C_END)


def get_rss_post_lists_indexing_naver(driver):
    for rss_blog_address in rss_blog_address_lists:
        modified_tistory_blog_address = rss_blog_address.replace('https://', '').replace('http://', '').replace('.',
                                                                                                                '_')
        csv_save_path = f'{csv_submit_urls_path}{modified_tistory_blog_address}_submit_urls.csv'

        submit_urls = []
        rss = rss_blog_address
        parse_rss = feedparser.parse(rss)
        # pp(parse_rss)

        print()
        for idx, entry in enumerate(parse_rss.entries):
            try:
                temp_dict = {}
                temp_dict['url'] = f'{entry.link}'
                temp_dict['indexed'] = 'X'
                # print(f'{idx + 1}. {entry.link}')
                submit_urls.append(temp_dict)  # 새로운 데이터를 아래에 쌓는다 그러면 중복된 데이터를 첵크할때 first 명령어를 통해 위쪽 데이터를 남기게 된다.
            except:
                print(f'\nUNKNOWN ISSUE')

        columns = ['url', 'indexed']
        df = pd.DataFrame(submit_urls, columns=columns)

        print(df.head(5))
        print(df.tail(5))

        # print(tabulate(df, headers='keys', tablefmt='grid'))
        if not os.path.exists(csv_save_path):
            df.to_csv(csv_save_path, mode='w', sep=',', na_rep='NaN', encoding='utf-8-sig', index=False)
        else:
            df.to_csv(csv_save_path, mode='a', sep=',', na_rep='NaN', encoding='utf-8-sig', index=False, header=False)

        print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}({csv_save_path})에서 중복된 행을 제거 시작{C_END}')
        data = pd.read_csv(csv_save_path)
        data = data.drop_duplicates(subset=['url'],
                                    keep="first")  # 중복제거를할때 남길 행입니다. first면 위에서부터 첫값을 남기고 last면 행의 마지막 값을 남깁
        data.to_csv(csv_save_path, index=False, encoding="utf-8-sig")
        print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}({csv_save_path})에서 중복된 행을 제거 완료{C_END}')

        print(f'\ntistory sitemap 정보를 이용하여 ({csv_save_path})로 ({len(submit_urls)})개의 포스팅 url을 저장하는데 성공하였습니다.')

        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[네이버써치어드바이저 로그인 후 쿠키값 저장 및 세션 리턴 시작]', C_END)
        naver_searchadvisor_session = get_cookies_session(driver,
                                                          f'https://searchadvisor.naver.com/console/site/request/crawl?site={rss_blog_address}')
        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[네이버써치어드바이저 로그인 후 쿠키값 저장 및 세션 리턴 완료]', C_END)

        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[네이버에 requests로 색인 시작]', C_END)
        indexing_naver(driver, naver_searchadvisor_session, rss_blog_address, csv_save_path)
        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[네이버에 requests로 색인 완료]', C_END)


def naver_searchadvisor_login(driver):
    driver.get('https://searchadvisor.naver.com/')
    sleep(LOADING_WAIT_TIME)

    # 로그인 버튼 클릭
    try:
        driver.find_element(By.CLASS_NAME,
                            'ma-0.px-4.v-btn.v-btn--depressed.theme--light.v-size--default.white.accent--text').click()
        sleep(PAUSE_TIME)
    except:
        print("\n로그인 버튼을 찾을 수 없습니다. 로그인 버튼을 직접 눌러 다음 로그인 과정을 수행해 주세요!!!")

    global already_naver_login

    # 로그인 과정을 기다려주는 부분
    print(f'\n{C_BOLD}{C_RED}{C_BGBLACK}주의: 3분안에 로그인을 완료해주세요!!!{C_END}')
    pbar = tqdm(total=LOGIN_WAIT_TIME)
    for x in range(LOGIN_WAIT_TIME):
        sleep(1)
        try:
            driver.find_element(By.CLASS_NAME, 'toolbar_nickname_33K75')  # 해당 element 가 존재하는지 확인
            global already_naver_login
            already_naver_login = True
            break
        except:
            pass
        pbar.update(1)
    pbar.close()

    sleep(PAUSE_TIME)


def indexing_naver(_driver, _session, _url_address, csv_save_path):
    df = pd.read_csv(csv_save_path)

    if len(df) == 0:
        print(f'\n색인할 url 존재하지 않습니다. ({csv_save_path}) 에 색인할 url 항목이 존재해야 합니다.')
        return

    # # ===============================================================
    # 순수 requests를 사용해서 인덱싱 할때 (로그인 세션 이용)
    # # ===============================================================

    sleep(PAUSE_TIME)
    count = 0
    # for url in submit_urls:
    for index_count in range(len(df)):

        if df["indexed"].values[index_count] == 'O':
            print(f'[SKIP] 해당 ({df["url"].values[index_count]})은 이미 색인 요청이 완료된 상태입니다. 다음으로 넘어가겠습니다.')
            continue

        if available_indexing_list_num == count:
            print(f"\n원하는 인덱스 수 ({available_indexing_list_num}) 만큼 색인이 완료 되었습니다.")
            # print(tabulate(df, headers='keys', tablefmt='grid'))
            df.to_csv(csv_save_path, mode='w', sep=',', na_rep='NaN', encoding='utf-8-sig', index=False)
            break

        url = df["url"].values[index_count]
        print(f'\n{count + 1}. {url}')

        # csrf <script> 에서 파싱해오기
        html = _driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        string = soup.select_one("body > script")
        # string = """<script>window.__NUXT__=(function(a,b,c,d,e){return {layout:"layout_sitecheck",data:[{}],fetch:[],error:b,state:{authUser:{id:"6199319",enc_id:"bc4ba5e84d121c26b6bc91d1972cb328ba43ca29ed41c20cfd08dbd701fe27f9",profile_image:"https:\u002F\u002Fphinf.pstatic.net\u002Fcontact\u002F20221012_20\u002F1665552880947TvTgB_JPEG\u002FShop_Poto_Moonbird_Word_ver12.jpg",age:"40-49",gender:"M",nickname:"달새",email:"ree31206@naver.com",birthday:"07-10",token:{access_token:"AAAAONSS0bWNLIjtAvqVhTFYVjbJnG1Sae3jSmvYULt3r2tMR0B5xta5GHTo-bpCAtN0OtDE6l60gh_9PJm7_eldmV0",refresh_token:"4pLoSKNxXxtiiCipnDoN8vOYuHxYoMxEa7B30r4N2M0ATisYxJbf2DjHLgSxn5IFis1KlesQgxTPQfipqyLIAdiiLgboIp0CSXJe7p3zFcbb8uFuis97UHWUulCg9rleY3nkNON",token_type:"bearer",expires_in:"315360000"},policy:{siteCheck:{lastDateTime:"2021-04-26 05:45:55",count:1},alarm:{verifySiteExpire:c},syndication:{allyStatus:a,maxPing:d},agree:{terms:c,oldUser:a},tag:{manualWhite:a,black:a},crawlRequest:{allyStatus:a,maxRequest:d,type:b}}},callerUrl:e,isOldBrowser:a,guideCurrent:{menuItemName:b,postTitle:b},topDrawer:a,hasMobile:a,appBarUrl:e,consoleMenuItemCurrent:{},consoleMenuItems:{site:b,setting:b},consoleMenuSiteBreadCrumbs:[],sorryComment:{},adminOpt:{oldscreen:a},csrfToken:"lqIfEgw9-9n3-SnAqYNPwoRCa165pnGl2CAI",diagnosisItems:b,clientHeaders:"header host:127.0.0.1:10080\nheader sec-ch-ua:\"Not.A\u002FBrand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"\nheader sec-ch-ua-mobile:?0\nheader sec-ch-ua-platform:\"macOS\"\nheader upgrade-insecure-requests:1\nheader user-agent:Mozilla\u002F5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit\u002F537.36 (KHTML, like Gecko) Chrome\u002F114.0.0.0 Safari\u002F537.36\nheader accept:text\u002Fhtml,application\u002Fxhtml+xml,application\u002Fxml;q=0.9,image\u002Favif,image\u002Fwebp,image\u002Fapng,*\u002F*;q=0.8,application\u002Fsigned-exchange;v=b3;q=0.7\nheader sec-fetch-site:same-site\nheader sec-fetch-mode:navigate\nheader sec-fetch-dest:document\nheader referer:https:\u002F\u002Fnid.naver.com\u002F\nheader accept-encoding:gzip, deflate, br\nheader accept-language:ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7\nheader cookie:SADV=s%3AiOnth-EqWn_MqM2mq4urvM8ApdijxOxs.0SPklabZZsPMHwaGGk1nMRUCQDP46HhdJnbkHQm%2BYpI; NNB=HOK3YQR3DZ6WI; nid_inf=-1264427168; NID_AUT=uu61lGOvp3+rzE4+HBUOXTYrT5671MKscVhk7bUMn7KE+ChP\u002F6isULi0FN3RCdbC; NID_SES=AAABxtGm9BVDey4XviTC61y4yLPDtnGEYugLc\u002F5M2VZjd0DF1sahSptc3y33NRBisALeBom0KJ1w\u002FlacgmlOb8lMW42kbskdvx2VT\u002FXAx\u002FRXm6NkHCs4bNLSbr1TRBrnkQcRLxNXM+wZIsx6i1q\u002F0nTY220edBdl5tC0awDslZZToaEE\u002FKBAuWpr7ze6zfU1LikGbcliaGezj+YFcL2\u002Folzfzw++\u002FTC6t+iGNwSNeo3x89YYfCgeHMlYp4bjmXYwVDXMQvZf0Be5R9GLOQOByrCqd1ZmLr4dUcIhwrCfIVgccJz6g4qM3Dv6Q+1f29ZXEAO05MjjxNztksyQG4NTxLrWu\u002FahV53m+EiIqTwdm3NeRYYfH5YLwYXKHEdx1pe44mqh3JHmfJZu7XEdz\u002FhVovvJi+edRfJyQxGF89Svd+ejymoYl4uGoGO91nd6LS0GSu2PSV+T3LVI9MF8lpozrJ\u002FpkRpSfHJahUGqKAPdnV2\u002FsTDgobjuzEqnBk1ML9lZ2yqixCy3y\u002F64IQtnov+vNDxA+kKX+31idLWr6ICTcc+j6MN\u002FOyXNrS9RjSoqY5drPdLLk5ZbtL7K8iecC1du2umxnNwGuXLBz09rYNG6M2t0xu5f; NID_JKL=8I1k0Bx8B\u002Fb3BbPlc2UbSZ28Coi5vVB7mWQJByppvOw=\nheader n-client-ip:211.51.160.200\nheader n-forwarded-proto:https\nheader n-proto:h2\nheader x-forwarded-for:10.107.57.91\nheader x-forwarded-host:searchadvisor.naver.com\nheader x-forwarded-server:searchadvisor.naver.com\nheader connection:Keep-Alive\nremoteAddress : 10.107.57.91"},serverRendered:c,routePath:"\u002Fauth\u002Fcallback"}}(false,null,true,0,""));</script>"""
        # print(string)
        # print(type(string))
        csrf_token = str(string).split("csrfToken:\"")[-1].split("\",")[0]
        enc_id = str(string).split("enc_id:\"")[-1].split("\",")[0]
        # print(f'csrfToken >>> {csrf_token}')
        # print(f'enc_id >>> {enc_id}')

        # 참고자료 중요 'https://iwantadmin.tistory.com/250'

        headers = {
            'authority': 'searchadvisor.naver.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://searchadvisor.naver.com',
            'pragma': 'no-cache',
            'referer': f'https://searchadvisor.naver.com/console/site/request/crawl?site=https%3A%2F%2F{_url_address.replace("https://", "")}',
            'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': fixed_user_agent,
        }

        json_data = {
            'user_enc_id': enc_id,
            'site': f'{_url_address}',
            'document': f'{url.replace(f"{_url_address}/", "")}',
            # 'document': 'entry/%EA%B3%84%EC%95%BD%EC%B7%A8%EC%86%8C%EC%A3%BC%ED%83%9D-%EB%B6%84%EC%96%91-%EC%A0%95%EB%B3%B4-%ED%8F%89%ED%83%9D-%EC%A7%80%EC%A0%9C%EC%97%AD-%EC%9E%90%EC%9D%B4%EA%B3%84%EC%95%BD%EC%B7%A8%EC%86%8C%EC%A3%BC%ED%83%9D',
            '_csrf': csrf_token,
        }

        # print(f'site >>> {_url_address}')
        # print(f'document >>> {url.replace(f"{_url_address}/", "")}')

        with _session as s:
            response = s.post('https://searchadvisor.naver.com/api-console/request/crawl', headers=headers,
                              json=json_data, verify=False).json()

        if response["message"] == 'SUCCESS':
            print(f'>> NOTICE: 색인 요청 성공!!')
            df["indexed"].values[index_count] = 'O'
            df.to_csv(csv_save_path, mode='w', sep=',', na_rep='NaN', encoding='utf-8-sig', index=False)
            count = count + 1
        elif response["message"] == 'FAIL_MAX_DOCUMENT_COUNT':
            print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '>> NOTICE: NAVER 최대 인덱싱 수(50개)를 넘었습니다. 루프를 종료합니다.', C_END)
            df["indexed"].values[index_count] = 'X'
            # print(tabulate(df, headers='keys', tablefmt='grid'))
            df.to_csv(csv_save_path, mode='w', sep=',', na_rep='NaN', encoding='utf-8-sig', index=False)
            return -1
        else:
            print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}NOTICE: 색인 요청 실패!! [{response["message"]}] {C_END}')
            df["indexed"].values[index_count] = 'X'
            df.to_csv(csv_save_path, mode='w', sep=',', na_rep='NaN', encoding='utf-8-sig', index=False)
            count = count + 1  # TODO: 추후 ERROR 에 따라 count 수정

        if count != available_indexing_list_num:
            sleep(INDEXING_WAIT_TIME)


def get_cookies_session(driver, url):
    driver.get(url)
    sleep(LOADING_WAIT_TIME)

    _cookies = driver.get_cookies()
    cookie_dict = {}
    for cookie in _cookies:
        cookie_dict[cookie['name']] = cookie['value']
        print(f"\n{cookie['name']} = {cookie['value']}")

    _session = requests.Session()
    headers = {
        'User-Agent': fixed_user_agent,
    }
    print(f'{_session.headers}')
    print(f'{_session.cookies}')

    _session.headers.update(headers)  # User-Agent 변경
    print(f'{_session.headers}')

    _session.cookies.update(cookie_dict)  # 응답받은 cookies로  변경
    print(f'{_session.cookies}')

    # global nid_ses
    _cookies = driver.get_cookies()
    for cookie in _cookies:
        cookie_dict[cookie['name']] = cookie['value']
        print(f"\n{cookie['name']} = {cookie['value']}")
        # if cookie['name'] == 'NID_SES':
        #     nid_ses = cookie['value']
        # if cookie['name'] == 'SADV':
        #     sadv = cookie['value']

    # 셀레니움 웹 드라이버를 종료(drivet.quit())
    # print('세션 정보를 얻어왔습니다. 셀레니움 웹 드리이버를 종료하겠습니다.')

    # # if url == 'https://searchadvisor.naver.com/console/site/request/crawl?site=https://pemtinfo1.tistory.com':
    # driver.close()
    # driver.quit()

    return _session


# main start
def main():
    try:
        start_time = time.time()  # 시작 시간 체크
        now = datetime.datetime.now()
        print("START TIME : ", now.strftime('%Y-%m-%d %H:%M:%S'))
        print("\nSTART...")

        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[크롬 드라이버 초기화 시작]', C_END)
        driver = init_driver()
        sleep(PAUSE_TIME)
        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[크롬 드라이버 초기화 완료]', C_END)

        global already_naver_login
        if not already_naver_login:  # driver init 시 debug 모드로 chrometemp 에 인증 정보들을 저장할 경우에 처리가 가능
            print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[네이버서치어드바이저 로그인 과정 시작]', C_END)
            naver_searchadvisor_login(driver)
            sleep(PAUSE_TIME)
            print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[네이버서치어드바이저 로그인 과정 완료]', C_END)

        print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}[tistory 색인을 시작]{C_END}')
        get_tistory_post_lists_indexing_naver(driver)
        print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}[tistory 색인을 완료]{C_END}')

        print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}[wordpress 색인을 시작]{C_END}')
        get_wordpress_post_lists_indexing_naver(driver)
        print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}[wordpress 색인을 완료]{C_END}')

        print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}[github 색인을 시작]{C_END}')
        get_github_post_lists_indexing_naver(driver)
        print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}[github 색인을 완료]{C_END}')

        # print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}[rss 색인을 시작]{C_END}')
        # get_rss_post_lists_indexing_naver(driver)
        # print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}[rss 색인을 완료]{C_END}')

    finally:
        driver.close()
        driver.quit()
        end_time = time.time()  # 종료 시간 체크
        ctime = end_time - start_time
        time_list = str(datetime.timedelta(seconds=ctime)).split(".")
        print("실행시간 (시:분:초)", time_list)
        now = datetime.datetime.now()
        print("END TIME : ", now.strftime('%Y-%m-%d %H:%M:%S'))
        print("\nEND...")


# main end


if __name__ == '__main__':
    main()
    # schedule.every(12).hours.do(main)  # 12시간에 한번씩
    # schedule.every().hour.at(":15").do(main)  # 매시간 42분에 작업 실행
    # schedule.every(10).minutes.do(main)  # 10분에 한번씩
    # schedule.every().day.at('02:00:00').do(get_tistory_post_lists)
    # schedule.every().day.at('03:00:00').do(get_wordpress_post_lists)
    # schedule.every().day.at('04:00:00').do(get_github_post_lists)
    # schedule.every().day.at('05:00:00').do(get_rss_post_lists)
    # schedule.every().day.at('09:00:00').do(main)
    # schedule.every().day.at('12:00:00').do(main)
    # schedule.every().day.at('15:00:00').do(main)
    # schedule.every().day.at('18:00:00').do(main)
    # schedule.every().day.at('21:00:00').do(main)
    # schedule.every().day.at('00:00:00').do(main)
    # schedule.every().day.at('03:00:00').do(main)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)