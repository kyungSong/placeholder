import psycopg2
import json
from collections import Counter
import sys

#Connect to data base
def connect_to_db():
    try:
        conn = psycopg2.connect("dbname='' user='' host='' password=''")
    except:
        print("cannot connect to database")
    return conn

#retrieve data from database using provided parameters and return top 25 most common nouns.
def get_data(gameName, startDate, endDate):
    conn = connect_to_db()
    cur = conn.cursor()
    try:
        select_statement = "SELECT dictionary FROM table WHERE game_name = %s AND recorded_date BETWEEN %s AND %s"
        cur.execute(select_statement, (gameName, startDate, endDate))
    except:
        print("could not get data")

    rows = cur.fetchall()
    combined = Counter()
    #for each row(i.e record for different dates) returned, combine their dictionaries.
    for i in range(len(rows)):
        combined += Counter(json.loads(rows[i][0]))

    conn.close()
    return json.dumps(OrderedDict(combined.most_common(25)))

def main():
    combined = get_data(sys.argv[1], sys.argv[2], sys.argv[3])
    #response is read by output stream on the server application, so you need to print your result.
    print(combined)

main()

