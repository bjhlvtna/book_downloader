#_*_ coding:utf8 _*_
'''
    파 일 명 : bookcrawler.py
    작 성 자 : 변 진 호 (Loading)
    목    적 : zenisoft book download
    사용 방식 : python bookcrawler.py ( 저장될 디렉토리에서 )
    사용 파일 : BeautifulSoup Lib : 웹 페이지 파싱 라이브러리
    제한 사항 : 1. html에 의존적
    오류 처리 : 1.
    이력 사항 : 1. 2013 년 04월 17 일 최초 작성
                2. 2013 년 04월 25 일 기본 기능 완성
                3. 2013 년 04월 26일 다운로드 이력및 이어받기 기능 구현
                4. 2013 년 04월 27일 마이너 버그 수정
    미구현내용: 1. 저장 디렉토리 지정
                2. 선택 다운 로드
'''
import os
import sys
import urllib2
from bs4 import BeautifulSoup

down_num = 0

def write_down_book_list(title):
    """
        docstring for write_down_book_list
    """
    global down_num
    down_num += 1
    message = '{0} : {1}\n'.format(down_num, title)
    with open('Book_List.txt', 'a') as book_list:
        book_list.write(message)
        
def make_url():
    """
        다운 받을 도서리스트 page url 만들기 
    """
    url = ''
    start_book_num = ''
    global down_num
    html = urllib2.urlopen(url).read().encode('utf8')
    soup = BeautifulSoup(html)
    
    if os.path.isfile('./Book_List.txt')==True:
        down_num = sum(1 for line in open('Book_List.txt'))
        start_book_num = str(down_num+1)
    else:
        start_book_num = '1'
    max_book_num = soup.find('span').text.split(' ')[-1]
    url = ''.format(max_book_num,start_book_num)

    return url

def classify_element(soup):
    """
        필요하지 않은 element 삭제하여
        필요한 부분만 남긴다.
    """
    # extract class=thumbnail in td_element
    for tmp in soup.findAll('td','thumbnail'):
        tmp.extract()
    for tmp in soup.findAll('div','navigation'):
        tmp.extract()
        
    return soup.find_all('td')

def extract_book_list(url):
    """
        해당 페이지에서 도서관련 정보 추출 
    """
    html = urllib2.urlopen(url).read().encode('utf8')
    soup = BeautifulSoup(html)
    book_list = classify_element(soup)
    
    book_info_list = []
    base_url = ''

    for book_data in book_list:
        book_info = {}
        if book_data.find('a')==None:
            continue
        file_type = book_data.find('a').text
        # 파일이름이 252자 이상이면 에러 발생 따라서 250으로 고정 
        file_name = book_data.find('span','first-line').text.strip()[0:250].replace('/','')
        book_url = base_url + book_data.find('a')['href']
        book_info['title'] = file_name+'.'+file_type
        book_info['url'] = book_url

        book_info_list.append(book_info)

    return book_info_list 

def update_progress(file_size, total_size):
    """
        도서 다운로드 상태 표시

    """
    percent = (float(file_size)/total_size)*100
    sys.stdout.flush()
    sys.stdout.write('\r[{0:100}] : {1:.2f}%'.format('#'*(int(percent)), round(percent,2)))
    if file_size >= total_size:
        sys.stdout.write('\n')

def download_file(book_info, block_size=1024, progress=None):
    """ 
        1024 씩 다운 로드
    """
    try:
        response = urllib2.urlopen(book_info['url'])
        total_size = response.info().getheader('Content-Length').strip()
        total_size = int(total_size)

        print 'Downloading : ' + book_info['title'] 
        down_file_size = 0
        with open(book_info['title'], 'wb') as local_file:
            while True:
                block = response.read(block_size)
                if block =='':
                    break
                down_file_size += len(block)
                local_file.write(block)
                update_progress(down_file_size, total_size)
        print '-'*110
        response.close()
        write_down_book_list(book_info['title'])

    except urllib2.HTTPError, e:
        print 'Http Error : ', e.code
    except urllib2.URLError, e:
            print 'Url Error : ', e.reason


if __name__ == '__main__':
    """
        url에 start 와 num의 값을 바꿔서 다운 로드 가능
        나중에 추가...
    """
    print 'Book Downloader Start - By Loading'

    url = make_url()
    book_list = extract_book_list(url)
    
    for book in book_list:
        download_file(book, progress=update_progress)

    print 'Download Complete : %d'%(down_num)
