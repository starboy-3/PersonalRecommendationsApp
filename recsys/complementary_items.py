from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from basics import structural


class ComplementItemRS(structural.CollaborativeFiltering):
    """
    COMPLEMENTARY ITEM
    collaborative user-based filtering recommendation system
    to find item that is frequently being consumed with some item

    будет точь-в-точь complementary, если матрица будет строиться
    по отношениям order-item, где order-item = 1, если item
    был в order, иначе 0.
    """

    def __init__(self):
        super(ComplementItemRS, self).__init__()
        # sparse matrix of implicit user-item interactions
        self.sparse_matrix = None

        # dataframes, so we could map indices used in class
        # methods with indices used in database
        self.user_indices_decode = None
        self.item_indices_decode = None

        # column names in database corresponding to user and item
        self.user_cname = None
        self.item_cname = None

        self.df_data = None
        self.similarities = None

    def build(self):
        self.similarities = cosine_similarity(self.sparse_matrix.tranpose())

    def find_similar_item(self,
                          item,
                          res_n: int = 10):
        item_id = self.item2index(item)
        item_vec = self.similarities[item_id].reshape(1, -1)[0]
        return self.index2item(np.argsort(item_vec)[::-1][:res_n])

    def recommend_to_user(self,
                          user: str,
                          res_n: int = 10):
        """ если хотим recommend for this order, то user (здесь это order)
            должен быть пустым; для лучше работы нужен метод update или тп
        """
        user_id = self.user2index(user)

        # getting items which user already consumed
        user_interactions_ids = list()
        for i in range(self.sparse_matrix.indptr[user_id],
                       self.sparse_matrix.indptr[user_id + 1]):
            user_interactions_ids.append(self.sparse_matrix.indices[i])

        scores_vec = (self.similarities @ self.sparse_matrix[user_id, :].T) / (self.similarities.sum(axis=1))
        non_zero_c = 0
        for i in range(len(scores_vec)):
            if non_zero_c >= len(user_interactions_ids):
                break
            elif i < user_interactions_ids[non_zero_c]:
                continue
            elif i == user_interactions_ids[non_zero_c]:
                scores_vec[i, 0] = 0
                non_zero_c += 1
        return self.index2item(np.argsort(scores_vec.T)[::-1][:res_n])


if __name__ == '__main__':
    complement_items = ComplementItemRS()
    # complement_items.load()
    # complement_items.build()
    # complement_items.find_similar_item()
    # complement_items.recommend_to_user()
