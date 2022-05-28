import numpy as np
from scipy.sparse.linalg import svds

from basics import structural


class FastComplementItemRS(structural.CollaborativeFiltering):
    """
    Class represents recommendation system, that recommends items,
    which are most suitable to some user based on experience of
    what other users like he liked/used.
    Actually, it can be used as complement items recommendation system,
    if user would be set to some `order`-type (so we will see what
    to recommend into user's shopping cart).

    Differences between this implementation of Complementary Items and
    ordinary one is that this Recommendation System uses matrix
    factorization for building model without normalizing values
    and forms matrix of recommendations in a build step
    """

    def __init__(self,
                 limit_per_user: int = -1):
        """
        :param limit_per_user: how many items to recommend for user
            we will save. If value is set to -1, then all items will
            be saved.
        """
        super(FastComplementItemRS, self).__init__()
        # items similarities matrix (items x items)
        self.items_matrix = None
        # fast-recommendations matrix
        self.recommendations = None
        # use to save memory resources from lots of data possibly
        # never been recommended
        self.fast_reqs_limit = limit_per_user

    def set_limit(self, value: int = 150):
        """
        :param value: new value to be set
        """
        self.fast_reqs_limit = value

    def build(self,
              remove_consumed: bool = True,
              rank: int = 10):
        """
        :param remove_consumed: set true if don't want to recommend
            to user already consumed items
        :param rank: item's matrix factorisation target-rank
        """
        # count cosine similarity matrix via SVD-decomposition
        _, _, self.items_matrix = svds(self.sparse_matrix.asfptype(), k=rank)
        self.recommendations = (self.items_matrix.transpose() @
                                (self.items_matrix @ self.sparse_matrix.T))

        # remove from our answer set already liked by users items
        if remove_consumed:
            for user_id in range(self.sparse_matrix.shape[0]):
                for i in range(self.sparse_matrix.indptr[user_id],
                               self.sparse_matrix.indptr[user_id + 1]):
                    self.recommendations[self.sparse_matrix.indices[i],
                                         user_id] = 0
        self.recommendations = np.argsort(-self.recommendations.T,
                                          axis=1)[:, :self.fast_reqs_limit]

    def recommend_to_user(self,
                          user,
                          res_n: int = 10):
        """
        :param user: user as it is stored in database
            (meant it is in column that was given to load)
        :param res_n: count of items to recommend
        :return: `res_n` most suitable (by RS) items for `user`
        """
        user_id = self._user2index(user)
        rec_vector = self.recommendations[user_id, :]
        return self._index2item(rec_vector[:res_n])

    def drop_slow(self):
        """
        delete all heavy object attrs that are not used in
        fast_recommend method
        """
        del self.items_matrix
        del self.sparse_matrix


if __name__ == '__main__':
    fci = FastComplementItemRS(150)

    print("loading started...")
    fci.load("small_data/lastfm2collab.csv", ["user_id", "item_id"])
    print("loading finished...")

    print("building started...")
    fci.build()
    print("building finished...")
    fci.drop_slow()

    q_user = 5985
    user_recs = fci.recommend_to_user(q_user)
    print("\nusers recs:", *user_recs, sep="\n")
