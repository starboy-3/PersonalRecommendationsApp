import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from basics import loaders, structural


class SearchEngine(structural.ContentBasedFiltering):
    """
    Class represents search engine. After loading data and building
    model, object of this type will be able to find items, which
    contents are the most similar to given query.
    """
    def __init__(self, stemmer):
        """
        :param stemmer: stemmer to stem words from text data
        """
        super(SearchEngine, self).__init__(stemmer)
        # transformer to vectorize contents
        self.transformer = TfidfVectorizer()
        # tf/idf matrix of items' contents
        self.tfidf_matrix = None

    def build(self):
        """
        building model
        """
        # applying transformer (tf/idf)
        raw_data = self.transformer.fit_transform(self.df_data[self.content_cname])
        # casting to pd.DataFrame type
        self.tfidf_matrix = pd.DataFrame(raw_data.T.toarray())

    @staticmethod
    def cosine_sim(a, b):
        """
        :param a: some vector of size n
        :param b: other vector of size n
        :return: cosine similarity of vectors a and b
        """
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def search(self,
               query: str,
               res_n: int = 20):
        """
        :param query: search query
        :param res_n: items count to be find
        :return: list (of size no more res_n elements) of most
            competent items' indices (as they saved in data source)
        """
        rows_count, columns_count = self.tfidf_matrix.shape
        # applying transformer's transform to query and getting it's vector
        query_raw = self.transformer.transform([loaders.StemmerWrapper.clean_string(query)])
        query_vec = query_raw.toarray().reshape(rows_count)

        # counting cosine similarity of query and each item-content (in tfidf_matrix)
        """
            I have tried this code, but it was slower for 10% compared to raw iterations,
            `sim = self.tfidf_matrix.apply(lambda x: self.cosine_sim(x, query_vec))`
        """

        # NOTE: able to be parallelized
        similarities = list()
        for i in range(columns_count):
            similarities.append(
                    self.cosine_sim(
                            self.tfidf_matrix.loc[:, i].values,
                            query_vec
                    )
            )

        # sort from the best matching to the worst
        similarities = sorted(
                enumerate(similarities),
                key=lambda x: x[1],
                reverse=True
        )

        # getting top `res_count` results' indices
        indices = [pair[0] for pair in similarities[:res_n]]

        # return found items ids
        return self.df_data.iloc[indices][self.item_id_cname].values


if __name__ == '__main__':
    ws = loaders.StemmerWrapper()
    search_eng = SearchEngine(ws)

    item_id_cname, item_content_cname = "product_id", "content_info"

    print("loading started...")
    search_eng.load(
            "small_data/product.csv",
            item_id_cname,
            item_content_cname,
            ["product_name", "description", "seller"]
    )
    print("loading finished...")

    print("building started...")
    search_eng.build()
    print("building finished...")

    query = "золотое с бриллиантами"
    res_indices = search_eng.search(query)

    print(res_indices)


    def translate(df, indices, to_print=True):
        """ prints out content of found to our query items' ids"""
        content_info = df.loc[df[item_id_cname].isin(indices)][item_content_cname].tolist()
        if to_print:
            print(*content_info, sep='\n\n')
        else:
            return content_info

    translate(search_eng.df_data, res_indices)
