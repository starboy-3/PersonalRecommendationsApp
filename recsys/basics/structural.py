import scipy.sparse as sparse  # for sparse matrix

from basics import loaders


class RecommendationSystem:
    """
    Root-class representing recommendation system
    """

    def __init__(self):
        pass

    def load_and_build(self, *args):
        pass

    def load(self, *args):
        pass

    def build(self, *args):
        pass


class CollaborativeFiltering(RecommendationSystem):
    """
    Represents recommendation system based on collaborative-filtering
    """

    def __init__(self):
        super(CollaborativeFiltering, self).__init__()
        # sparse matrix of implicit user-item interactions
        self.sparse_matrix = None

        # dataframes, so we could map indices used in class
        # methods with indices used in database
        self.user_indices_decode = None
        self.item_indices_decode = None

        # column names in database corresponding to user and item
        self.user_cname = None
        self.item_cname = None

    def load(self,
             table: str,
             columns: list,
             loader_type: str = "csv",
             connection=None):
        """
        :param table: table name where from data will be read (this
            either table of database or path to csv file, depending
            on loader_typ)
        :param columns: 2 or 3 elements array - names of columns of
            user, item and their relationship coefficients (if it's
            provided)
        :param loader_type: equals either to "csv" or "db", depending
            on `table`
        :param connection: if loader_type equals to db, it must be
            connection to using database (otherwise - whatever)

        Loads data necessary to build model
        """
        # check for `columns` length
        if len(columns) < 2 or len(columns) > 3:
            raise RuntimeError("CollaborativeFiltering::load: columns "
                               "argument invalid format")

        # initialize loader
        if loader_type == "csv":
            loader = loaders.CsvLoader(None)
        elif loader_type == "db":
            if connection is None:
                raise RuntimeError("CollaborativeFiltering::load: received "
                                   "connection equals to None with a "
                                   "loader_type equals db")
            loader = loaders.DataBaseLoader(None, connection)
        else:
            raise RuntimeError("CollaborativeFiltering::load: no loader "
                               "available for given loader_type")

        # load implicit data in 3-column dataframe
        dataframe = loader.parse(table, columns)
        dataframe.dropna(inplace=True)

        relations_count = dataframe.shape[0]
        # copying column names explicitly
        self.user_cname, self.item_cname = columns[0] + "", columns[1] + ""
        user_id_cname, item_id_cname = columns[0] + "_id", columns[1] + "_id"

        # save user and item columns, so we will be able to return to
        # caller recommendation as it is stored in database
        dataframe[user_id_cname] = dataframe[columns[0]].astype(
                "category").cat.codes
        dataframe[item_id_cname] = dataframe[columns[1]].astype(
                "category").cat.codes
        self.user_indices_decode = dataframe[
            [user_id_cname, columns[0]]].drop_duplicates()
        self.item_indices_decode = dataframe[
            [item_id_cname, columns[1]]].drop_duplicates()
        dataframe.drop(columns[:2], axis=1, inplace=True)

        # initializing sparse matrix
        users = dataframe[user_id_cname].astype(int)
        items = dataframe[item_id_cname].astype(int)
        users_count = len(dataframe[user_id_cname].unique())
        items_count = len(dataframe[item_id_cname].unique())
        if len(columns) == 3:
            self.sparse_matrix = sparse.csr_matrix(
                    (dataframe[columns[2]], (users, items)),
                    shape=(users_count, items_count)
            )
        elif len(columns) == 2:
            self.sparse_matrix = sparse.csr_matrix(
                    ([1 for _ in range(relations_count)], (users, items)),
                    shape=(users_count, items_count)
            )

    def _item2index(self,
                    item):
        """
        :param item: item as it is stored in database
        :return: index used in this object for `item`
        """
        return self.item_indices_decode[
            self.item_cname + "_id"
            ].loc[self.item_indices_decode[self.item_cname] == item].iloc[0]

    def _user2index(self,
                    user):
        """
        :param user: user as it is stored in database
        :return: index used in this object for `user`
        """
        return self.user_indices_decode[
            self.user_cname + "_id"
            ].loc[self.user_indices_decode[self.user_cname] == user].iloc[0]

    def _index2item(self,
                    items_ids: list):
        """
        :param items_ids: list of indices as they are stored in this
            object
        :return: corresponding to `indices` values of items
        """
        result = list()
        for item_id in items_ids:
            result.append(
                    self.item_indices_decode[
                        self.item_cname
                    ].loc[
                        self.item_indices_decode[
                            self.item_cname + "_id"] == item_id
                        ].iloc[0]
            )
        return result


class ContentBasedFiltering(RecommendationSystem):
    """
    Represents recommendation system based on content-based-filtering
    """

    def __init__(self,
                 stemmer):
        super(ContentBasedFiltering, self).__init__()
        # using stemmer
        self.stemmer = stemmer
        # similarity matrix (items_count x items_count)
        self.df_data = None
        # item-representing and content columns names
        self.item_id_cname = None
        self.content_cname = None

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
