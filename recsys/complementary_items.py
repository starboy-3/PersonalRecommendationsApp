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
        super(ComplementItemRS, self).__init__()
        # items similarities matrix (items x items)
        self.similarities = None
        # items similarities matrix QR-decomposition matrices
        self.sim_q, self.sim_r = None, None
        # fast-recommendations matrix
        self.recommendations = None
        # use to save memory resources from lots of data possibly
        # never been recommended
        self.fast_reqs_limit = -1

    def set_limit(self, value: int = 100):
        """
        :param value: new value to be set
        """
        self.fast_reqs_limit = value

    def build(self,
              via_normalize: bool = False,
              big_data: bool = False):
        """
        :param via_normalize: set true if want to normalize items'
            vectors. They can be normalized for the situations, where
            opinion of man is more valuable if he has expressed it
            less compared to others (briefly, in binary data it must
            be nice).
        :param big_data: set true if want to multiply QR-decomposition
            for items' similarities matrix (only for big data's)
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

        if big_data:
            self.sim_q, self.sim_r = np.linalg.qr(self.similarities)

            # counting how all users relates to all items
            self.recommendations = (self.sim_q @ (self.sim_r @ self.sparse_matrix.T))
        else:
            self.recommendations = (self.similarities @ self.sparse_matrix.T)
        # compared to max l1-norm of exact item's vector
        self.recommendations /= np.array([np.abs(self.similarities).sum(axis=1)]).T

        # remove from our answer set already liked by users items
        for user_id in range(self.sparse_matrix.shape[0]):
            for i in range(self.sparse_matrix.indptr[user_id],
                           self.sparse_matrix.indptr[user_id + 1]):
                self.recommendations[self.sparse_matrix.indices[i], user_id] = 0
        self.recommendations = np.argsort(-self.recommendations.T, axis=1)[:, :self.fast_reqs_limit]

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
        """
        :param user: user as it is stored in database
            (meant it is in column that was given to load)
        :param res_n: count of items to recommend
        :return: `res_n` most suitable (by RS) items for `user`
        """
        user_id = self.user2index(user)

        # counting how our user relates to all items
        if self.sim_q is None:
            scores_vec = (self.similarities @ self.sparse_matrix[user_id, :].T)
        else:
            scores_vec = (self.sim_q @ (self.sim_r @ self.sparse_matrix[user_id, :].T))
        # compared to max l1-norm of exact item's vector
        scores_vec /= np.array([np.abs(self.similarities).sum(axis=1)]).T

        # remove from our answer set already liked by user items
        for i in range(self.sparse_matrix.indptr[user_id],
                       self.sparse_matrix.indptr[user_id + 1]):
            scores_vec[self.sparse_matrix.indices[i], 0] = 0

        # choose top `res_n` and return them
        return self.index2item(np.argsort(scores_vec.T)[0][::-1][:res_n])

    def fast_recommend(self,
                       user,
                       res_n: int = 10):
        """
        :param user: user as it is stored in database
            (meant it is in column that was given to load)
        :param res_n: count of items to recommend
        :return: `res_n` most suitable (by RS) items for `user`
        """
        user_id = self.user2index(user)
        rec_vector = self.recommendations[user_id, :]
        return self.index2item(rec_vector[:res_n])

    def drop_slow(self):
        del self.similarities
        del self.sim_r
        del self.sim_q
        del self.sparse_matrix


if __name__ == '__main__':
    complement_items = ComplementItemRS()

    print("loading started...")
    complement_items.load("small_data/lastfm2collab.csv", ["user_id", "item_id"])
    print("loading finished...")
    complement_items.set_limit()
    print("building started...")
    complement_items.build()
    print("building finished...")

    q_item = "linkin park"
    similar_items = complement_items.find_similar_item(q_item)
    print("similar items:", *similar_items, sep="\n")

    q_user = 5985
    user_recs = complement_items.recommend_to_user(q_user)
    print("\nusers recs:", *user_recs, sep="\n")

    complement_items.drop_slow()
    user_fast_recs = complement_items.fast_recommend(q_user)
    print("\nusers fast recs:", *user_fast_recs, sep="\n")

    print("\ninter:", *(set(user_recs) & set(user_fast_recs)), sep="\n")
