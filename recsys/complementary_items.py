import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from basics import structural


class ComplementItemRS(structural.CollaborativeFiltering):
    """
    Class represents recommendation system, that recommends items,
    which are most suitable to some user based on experience of
    what other users like he liked/used.
    Actually, it can be used as complement items recommendation system,
    if user would be set to some `order`-type (so we will see what
    to recommend into user's shopping cart).
    """

    def __init__(self):
        """
           TODO для скорости выдачи рекомендации юзеру можем использовать матричную факторизацию QR/SVD/RSVD
        """
        super(ComplementItemRS, self).__init__()
        # items similarities matrix (items x items)
        self.similarities = None

    def build(self, via_normalize: bool = False):
        """
        :param via_normalize: set true if want to normalize items'
            vectors. They can be normalized for the situations, where
            opinion of man is more valuable if he has expressed it
            less compared to others (briefly, in binary data it must
            be nice).
        """
        if via_normalize:
            self.sparse_matrix = self.sparse_matrix.astype(np.float32)
            # get l2-norm of rows
            magnitude = np.sqrt(self.sparse_matrix.power(2).sum(axis=1))

            # divide each row to it's l2-norm
            for i in range(magnitude.shape[0]):
                from_i = self.sparse_matrix.indptr[i]
                to_i = self.sparse_matrix.indptr[i + 1]
                self.sparse_matrix.data[from_i:to_i] = (
                        self.sparse_matrix.data[from_i:to_i] / magnitude[i][0]
                )
        # count cosine similarity matrix
        self.similarities = cosine_similarity(self.sparse_matrix.transpose())

    def find_similar_item(self,
                          item,
                          res_n: int = 10):
        """
        :param item: item as it is stored in database
            (meant it is in column that was given to load)
        :param res_n: count of items to find
        :return: `res_n` most similar to `item` items
        """
        item_id = self.item2index(item)
        # get vector corresponding to item
        item_vec = self.similarities[item_id].reshape(1, -1)[0]
        # choose top `res_n` and return them
        return self.index2item(np.argsort(item_vec)[::-1][1:res_n + 1])

    def recommend_to_user(self,
                          user,
                          res_n: int = 10):
        """ если хотим recommend for this order, то user (здесь это order)
            должен быть пустым; для лучше работы нужен метод update или тп
        """
        user_id = self.user2index(user)

        # counting how our user relates to all items
        scores_vec = (self.similarities @ self.sparse_matrix[user_id, :].T)
        # compared to max l1-norm of exact item's vector
        scores_vec /= np.array([np.abs(self.similarities).sum(axis=1)]).T

        # remove from our answer set already liked by user items
        for i in range(self.sparse_matrix.indptr[user_id],
                       self.sparse_matrix.indptr[user_id + 1]):
            scores_vec[self.sparse_matrix.indices[i], 0] = 0

        # choose top `res_n` and return them
        return self.index2item(np.argsort(scores_vec.T)[0][::-1][:res_n])


if __name__ == '__main__':
    complement_items = ComplementItemRS()

    print("loading started...")
    complement_items.load("small_data/lastfm2collab.csv", ["user_id", "item_id"])
    print("loading finished...")

    print("building started...")
    complement_items.build()
    print("building finished...")

    q_item = "linkin park"
    similar_items = complement_items.find_similar_item(q_item)
    print("similar items:", *similar_items, sep="\n")

    q_user = 5985
    user_recs = complement_items.recommend_to_user(q_user)
    print("\nusers recs:", *user_recs, sep="\n")
