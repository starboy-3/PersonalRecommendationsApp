import os
import time
import signal
import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from recs_systems_model.basics.loaders import *
from recs_systems_model.basics.structural import *
from recs_systems_model.search_engine import *


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
ws = loaders.StemmerWrapper()
search_eng = SearchEngine(ws)
item_id_cname, item_content_cname = "product_id", "content_info"
child_pid, parent_pid = 0, 0


def get_info_from_dbs(indices) -> list:
    """
    get information from data base
    :param indices: list of product indices in db
    :return: list with descriptions of requested product
    """
    descriptions = []
    dataframe = pd.read_csv('data/data.csv')
    for i in range(len(indices)):
        print(dataframe.iloc[indices[i] - 1])
        descriptions.append(dataframe.iloc[indices[i] - 1].to_dict())
    return descriptions


def get_info_from_db(indices):
    """
    get information from data base
    :param indices: list of product indices in db
    :return: list with descriptions of requested product
    """
    hostname = settings["db_hostname"]
    username = settings['db_username']
    password = settings['db_password']
    database = settings["db_name"]
    connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
    connection.set_session(autocommit=True)
    try:
        cursor = connection.cursor()
        cursor.execute(
            "insert into shops(name, rating) values (%s, %s) RETURNING seller_id;",
            ("d", 4.7,)
        )
        id = cursor.fetchall()
        print(id)

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
    return []


@app.route('/search/<string:search_query>', methods=['GET'])
@cross_origin()
def receive_search_request(search_query):
    """
    handler, which based on the user's search query,
    provides the necessary information about the goods for placement on the website

    :param search_query: text of user search query
    :return: jsonify information about products
    """
    print('got some search query:', search_query)
    db_indices = search_eng.search(search_query)
    info = get_info_from_dbs(db_indices)
    result = dict()
    for i in range(len(info)):
        result[i] = info[i]
    print('res:', result)
    return jsonify(result), 200


class RecommendationSysServer:
    """
    Class represents recommendation system REST API service,
    which ensure correct work of web-site.
    """
    def run(self) -> None:
        """
        load data for recommendation models and run server
        """
        child_pid = os.fork()
        parent_pid = os.getpid()
        if child_pid == 0:
            while True:
                os.kill(parent_pid, signal.SIGTERM)
                time.sleep(86400)
        print('start working child process with pid', child_pid)
        RecommendationSysServer.load_data(self)
        print("building started...")
        search_eng.build()
        print("building finished...")
        print('server started')
        app.run(host='10.77.15.146', port=8080)

    @staticmethod
    def load_data(self):
        """
        load data
        """
        print("loading started...")
        search_eng.load(
            "data/data.csv",
            item_id_cname,
            item_content_cname,
            ["product_name", "description", "seller"]
        )
        print("loading finished...")


def sigint_handler(sig_num, frame):
    """
    handler for sigint handler
    :param sig_num: number of signal
    :param frame:
    :return: None
    """
    global child_pid
    print('kill child process with child pid:', child_pid)
    os.kill(child_pid, signal.SIGKILL)


def sigterm_handler(sig_num, frame):
    """
    handler for sigterm handler
    :param sig_num: number of signal
    :param frame:
    :return: None
    """
    global child_pid
    print('run updating data')
    RecommendationSysServer.load_data(None)


signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGINT, sigint_handler)

if __name__ == '__main__':
    server = RecommendationSysServer()
    server.run()
