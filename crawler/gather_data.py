import crawler
from konlpy.tag import Komoran
from collections import defaultdict
import json
import psycopg2

from selenium import webdriver
import os

# create dictionary out of text of posts provided.
# post_list = list of lists. inner list contains [query, url, text of posts aggregated]
def create_dict(post_list):
    dict_list = []
    for query in post_list:
        text = ""
        post_num = 0
        for post in query:
            #if post we are looking at has any text content associated with it.
            if(len(post) > 2):
                post_num += 1
                text += post[2]
        #extract nouns
        nouns = Komoran().nouns(text)
        count_dict = defaultdict(int)

        #count the occurance of each noun.
        for noun in nouns:
            count_dict[noun] += 1
        dict_list.append(count_dict)

    #for each noun, if that noun appeared less than 10% of the times, delete.
    for i in range(len(dict_list)):
        for item in list(dict_list[i]):
            if dict_list[i][item] < post_num/10:
                del dict_list[i][item]
    return dict_list

#wrapper function to combine everything
def cycle():
    conn = connect_to_db()
    store_data(conn)

def connect_to_db():
    try:
        conn = psycopg2.connect("dbname='' user='' host='localhost' password=''")
    except:
        print("cannot connect to database")
    return conn

def get_data():
    path = os.getcwd() + "\\phantomjs\\bin\\phantomjs"
    driver = webdriver.PhantomJS(path)

    buzz_per_query, post_list = crawler.run_scraper(["리니지m", "소녀전선"], "2", driver)
    dict_list = create_dict(post_list)

    driver.quit()

    return [buzz_per_query, dict_list]

#store dictionary data to designated database
def store_data(conn):
    data = get_data()
    buzz_per_query = data[0]
    dict_list = data[1]

    cur = conn.cursor()
    try:
        for i in range(len(buzz_per_query)):
            #insert 'search term' and 'dictionary'
            insert_statement = "INSERT INTO DATABASENAME VALUES (" + "'" + buzz_per_query[i][0] + "'" + ",'" + json.dumps(dict_list[i]) +  "')"
            cur.execute(insert_statement)
    except:
        print("could not insert")

    conn.commit()
    conn.close()


def main():

    cycle()

main()
