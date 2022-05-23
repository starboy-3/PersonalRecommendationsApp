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
    # do some requests in DB
    result = {'indices': '[' + ', '.join(list(
                            map(lambda x: str(x), db_indices))) + ']'}
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
        print("loading started...")
        search_eng.load(
            "data/data.csv",
            item_id_cname,
            item_content_cname,
            ["product_name", "description", "seller"]
        )
        print("loading finished...")

        print("building started...")
        search_eng.build()
        print("building finished...")
        print('server started')
        app.run(host='192.168.211.84', port=8080)


if __name__ == '__main__':
    server = RecommendationSysServer()
    server.run()
