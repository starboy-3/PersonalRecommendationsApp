import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

"""
!pip install sentence-transformers
!pip install umap-learn
!pip install hdbscan
"""

from sentence_transformers import SentenceTransformer
import umap
import hdbscan


from basics import loaders


class DataClusterizer:
    def __init__(self,
                 stemmer):
        # using stemmer
        self.stemmer = stemmer
        # similarity matrix (items_count x items_count)
        self.df_data = None
        # item-representing and content columns names
        self.item_id_cname = None
        self.content_cname = None

        self.embeddings = None
        self.cluster = None

    def set_data(self,
                 data, *args):
        """
        :param data: 2-column pandas dataframe. One of the columns
            must contains texts, and other their ids.
        :param args: if given, then expected to consist of two values:
            columns names of data for text's id and text itself
            exactly in this order
        """
        self.df_data = data
        if args:
            self.item_id_cname, self.content_cname = args
        else:
            self.item_id_cname, self.content_cname = data.columns

    def load(self,
             table: str,
             item_id_cname: str,
             content_cname: str,
             content_columns: list,
             loader_type: str = "csv",
             connection=None):
        """
        :param table: table name where from data will be read (this
            either table of database or path to csv file, depending
            on loader_typ)
        :param item_id_cname: item-representing-column's name
        :param content_cname: content-representing-column's name
        :param content_columns: columns, which contents will be used
            to build model
        :param loader_type: equals either to "csv" or "db", depending
            on `table`
        :param connection: if loader_type equals to db, it must be
            connection to using database (otherwise - whatever)

        Loads data necessary to build model
        """
        self.item_id_cname = item_id_cname
        self.content_cname = content_cname
        if loader_type == "csv":
            loader = loaders.CsvLoader(self.stemmer)
        elif loader_type == "db":
            if connection is None:
                raise RuntimeError("SearchEngine::load: received connection "
                                   "equals to None with a loader_type equals "
                                   "db")
            loader = loaders.DataBaseLoader(self.stemmer, connection)
        else:
            raise RuntimeError("SearchEngine::load: no loader available for "
                               "given loader_type")
        self.df_data = loader.merge_contents(
                table,
                self.item_id_cname,
                content_cname,
                content_columns
        )

    def build(self,
              n_components=5,
              min_cluster_size=15,
              data=None):
        # extracting data structure
        if data is None:
            data = self.df_data[self.content_cname]

        # getting texts embeddings
        model = SentenceTransformer('distilbert-base-nli-mean-tokens')
        # you can run encoding with argument show_progress_bar=True
        self.embeddings = model.encode(data)

        # decreasing dimensions of embeddings
        # target dimensionality must be given to `n_components`
        # and local neighbourhood
        umap_embeddings = umap.UMAP(
                n_neighbors=n_components,
                n_components=5,
                metric='cosine'
        ).fit_transform(self.embeddings)
        # clustering data
        self.cluster = hdbscan.HDBSCAN(
                min_cluster_size=min_cluster_size,
                metric='euclidean',
                cluster_selection_method='eom'
        ).fit(umap_embeddings)

    def visualize(self):
        """
        decreases built embeddings to 2 components and visualizes
        them by formatted clusterization labels.
        Note! Run method after building cluster!
        """
        # decreasing dimensions of embeddings to 2,
        # so we can represent it in graphic
        umap_data = umap.UMAP(
                n_neighbors=15,
                n_components=2,
                min_dist=0.0,
                metric='cosine'
        ).fit_transform(self.embeddings)

        result = pd.DataFrame(umap_data, columns=['x', 'y'])
        result['labels'] = self.cluster.labels_

        # Visualize clusters
        fig, ax = plt.subplots(figsize=(20, 10))
        # texts that could be clustered
        outliers = result.loc[result.labels == -1, :]
        # clustered texts
        clustered = result.loc[result.labels != -1, :]
        plt.scatter(outliers.x,
                    outliers.y,
                    color='#BDBDBD',
                    s=0.05)
        plt.scatter(clustered.x,
                    clustered.y,
                    c=clustered.labels,
                    s=0.05,
                    cmap='hsv_r')
        plt.colorbar()

    def get_labels(self):
        """ return labeled items """
        return self.cluster.labels_

    def get_item_category(self,
                          item):
        """
        :param item: item as it is stored in dataframe
        :return: category of item after clusterization
        """
        results = self.cluster.labels_[
            self.df_data.index[
                self.df_data[self.item_id_cname] == item
                ]
        ]
        if results:
            return results[0]
        return None

    def get_items_in_category(self,
                              topic_id):
        """
        :param topic_id: one of the categories gotten after
            clusterization
        :return: all items with given topic_id
        """
        items_indices = np.argwhere(dc.cluster.labels_ == topic_id).T[0]
        if items_indices:
            return self.df_data[self.item_id_cname].iloc[items_indices]
        return None


if __name__ == '__main__':
    from sklearn.datasets import fetch_20newsgroups

    train = fetch_20newsgroups(subset='train')['data']
    train = pd.DataFrame(train)
    train['id'] = range(1, len(train) + 1)
    ws = loaders.StemmerWrapper()
    dc = DataClusterizer(stemmer=ws)
    dc.set_data(train, 'id', 0)
    dc.build()
    dc.visualize()

    category = dc.get_item_category(1)
    items = dc.get_items_in_category(category)
