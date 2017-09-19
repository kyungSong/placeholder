from selenium import webdriver
from bs4 import BeautifulSoup
from urllib import parse
import datetime
import copy
import os

def num_of_posts(soup):
    total_post_num = soup.find('span', {'class':'title_num'})
    result_page_num = 0

    if total_post_num:
        total_post_num = int(total_post_num.text.split(' ')[-1].replace(',','')[:-1])

        if total_post_num < 10:
            result_page_num = 1
        else:
            if total_post_num%10 == 0:
                result_page_num = int(total_post_num/10)
            else:
                result_page_num = int(total_post_num/10) + 1
    else:
        total_post_num = 0
        result_page_num = 0

    return total_post_num, result_page_num

def generate_url(query, mode, page_num = ""):

    day = "2"
    week = "3"
    month = "4"
    halfYear = "5"

    word = query.replace(query, parse.quote(query))
    url = "https://search.naver.com/search.naver?where=post&query="+word+ \
            "&ie=utf8&st=sim&sm=tab_opt&date_from=20030520&date_to=20170724&date_option="+mode+ \
            "&srchby=title&dup_remove=1&post_blogurl=&post_blogurl_without=&nso=so%3Ar%2Ca%3Aall%2Cp%3A1d&mson=0"

    if page_num:
        url += "&start=" + page_num
    return url

def get_buzz(query, soup):

    post_num, page_num = num_of_posts(soup)

    return [query, post_num, page_num, datetime.date.today()]

def source_extractor(url, driver):

    driver.get(url)
    s = (driver.page_source).encode('utf-8')
    soup = BeautifulSoup(s, "lxml", from_encoding='utf-8')

    return soup

def href_extractor(soup):
    hrefs = []
    for post in soup.find_all('a', attrs={'class':'sh_blog_title _sp_each_url _sp_each_title'}):
        hrefs.append(post['href'])

    return hrefs

def naver_blog_scraper(copy_list, driver):
    current_url = copy_list[1]
    current_url = current_url.replace('?Redirect=Log&logNo=', '/')
    current_url = current_url.replace('http://', 'http://m.')
    try:
        soup = source_extractor(current_url, driver)
        contents = ''
        contents_holder = soup.find_all('div', class_='se_component_wrap sect_dsc __se_component_area')
        contents_holder += soup.find_all('div', class_='post_ct ')
        contents_holder += soup.find_all('div', class_='post_ct   se3_view ')
        if contents_holder:
            for paragraph_soup in contents_holder:
                sentences_soup = paragraph_soup.find_all('div')
                sentences_soup += paragraph_soup.find_all('p')
                sentences_soup += paragraph_soup.find_all('span')
            if sentences_soup:
                for text_soup in sentences_soup:
                    if text_soup.text:
                        temp_line = ' '.join(text_soup.text.split())
                        if temp_line not in contents:
                            contents += ' ' + temp_line + ' '
    except:
        print("Loading the following page has failed : " + current_url)

    if contents:
        copy_list.append(contents)
        copy_list[1] = current_url
    else:
        print("No Content retrieved from the following URL : " + current_url)

def content_scraper(list_of_posts, driver):
    #driver.set_page_load_timeout(50)
    copy_list = copy.deepcopy(list_of_posts)
    for i in range(len(copy_list)):
        for j in range(len(copy_list[i])):
            if 'naver' in copy_list[i][j][1]:
                naver_blog_scraper(copy_list[i][j], driver)

    return copy_list

def all_post_list(queries, mode, driver):
    buzz_per_query = []
    post_list = []

    for query in queries:
        current_url = generate_url(query, mode)
        soup = source_extractor(current_url, driver)
        post_num, page_num = num_of_posts(soup)
        posts_per_query = []

        for i in range(page_num):
            #naver search result url moves up by 10 when you move between pages (i.e. first page = 1, second page = 11, third = 31...)
            current_page = str(10*i + 1)
            current_page_url = generate_url(query, mode, current_page)
            soup = source_extractor(current_page_url, driver)
            each_post = soup.find_all('li', attrs={'class':'sh_blog_top'})

            for post in each_post:
                href = href_extractor(post)
                posts_per_query.append([query, href[0]])
        post_list.append(posts_per_query)
        buzz_per_query.append([query,mode,post_num])

    return buzz_per_query, post_list

def run_scraper(query_list, mode, driver):
    buzz_per_query, post_list = all_post_list(query_list, mode, driver)

    post_list = content_scraper(post_list, driver)

    return buzz_per_query, post_list

def main():
    path = os.getcwd() + "\\phantomjs\\bin\\phantomjs"
    driver = webdriver.PhantomJS(path)
    test = run_scraper(["리니지m"], "2", driver)
    print(test)
main()
