from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

from nltk.corpus import stopwords
# run "import nltk\nnltk.download('stopwords')\n" if package not found

from basics import loaders, structural


class SubstituteItemRS(structural.ContentBasedFiltering):
    """
    Class represents recommendation system, that recommends items,
    which are most similar to exact item with their contents.
    Actually, it is substitute items recommendation system.
    """
    def __init__(self,
                 stemmer,
                 max_features=int(1e5),
                 stop_words=stopwords.words("russian")):
        """
        :param stemmer: stemmer to stem words from text data
        :param max_features: argument for CountVectorizer transformer
            (for saving `max_features` most common words from data)
        :param stop_words: argument for CountVectorizer transformer
            (list of meaningless words to be ignored)
        """
        super(SubstituteItemRS, self).__init__(stemmer)
        self.transformer = CountVectorizer(max_features=max_features,
                                           stop_words=stop_words)
        # similarity matrix
        self.similarity = None

    def build(self):
        """
        building model
        """
        raw_data = self.transformer.fit_transform(self.df_data[self.content_cname])
        # dropping axis which will not be actually used
        self.df_data.drop(self.content_cname, axis=1, inplace=True)
        self.similarity = cosine_similarity(raw_data.toarray())

    def find_closest(self,
                     item_id: str,
                     res_n: int = 20):
        """
            :param item_id: item's id (as it's saved in data source),
                which substitutes will be found
            :param res_n: substitutes count to be find
            :return: list (of size no more res_n elements) of most
                competent items' indices (as they saved in data source)
        """
        # get index of item as it is saved in our dataframe
        item_index = self.df_data[self.df_data[self.item_id_cname] == item_id].index[0]

        # get it's similarities to all other items (as vector)
        cos_distances = self.similarity[item_index]
        # choose top `res_n` items with most similarities scores
        items_list = sorted(list(enumerate(cos_distances)), reverse=True, key=lambda x: x[1])[1:res_n + 1]
        indices = [item[0] for item in items_list]

        # return found items ids
        return self.df_data.iloc[indices][self.item_id_cname].values


if __name__ == '__main__':
    # !! MAKE SURE you have commented `drop()`-line   !!
    # !! in `build` method, if run this part of code  !!

    ws = loaders.StemmerWrapper()
    substitutes_rs = SubstituteItemRS(ws)
    item_id_cname, item_content_cname = "product_id", "content_info"

    print("loading started...")
    substitutes_rs.load(
            "small_data/product.csv",
            item_id_cname,
            item_content_cname,
            ["product_name", "description", "seller"]
    )
    print("loading finished...")

    print("building started...")
    substitutes_rs.build()
    print("building finished...")

    m_item_id = substitutes_rs.df_data[item_id_cname].iloc[2440]
    print("item id (m_item_id):\t", m_item_id)

    res_indices = substitutes_rs.find_closest(m_item_id)
    print("top closest items_ids:\t", res_indices)


    def translate(df, indices, to_print=False):
        content_info = df.loc[df[item_id_cname].isin(indices)][item_content_cname].tolist()
        if to_print:
            print(*content_info, sep='\n\n')
        else:
            return content_info

    print("content of m_item_id:")
    translate(substitutes_rs.df_data, [m_item_id], True)

    print("content of closest items:")
    translate(substitutes_rs.df_data, res_indices, True)
