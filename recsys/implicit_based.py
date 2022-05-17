import numpy as np

from sklearn.preprocessing import MinMaxScaler

from basics import structural


class ImplicitRS(structural.CollaborativeFiltering):
    """
        Implementing collaborative-filtering recommendation system
        on implicit data of user-item interactions.

        Used algorithm: Implicit-ALS via Conjugate Gradient Method
        (in each step, vector is minimized along a search direction)

        Used materials:
        - http://www.sze.hu/~gtakacs/download/recsys_2011_draft.pdf
        - http://www.yifanhu.net/PUB/cf.pdf

        Briefly, implicit data is going to be gathered by user's
        behaviour on exact product. If he will visit product site-page,
        we will assume, that he is interested in such kind of products
        and will look for other users with similar interests to
        make a recommendation. Otherwise, we will assume, that we
        know nothing about users opinion on product and will construct
        model with a some small positive value for this product.

        In build method, we are asking for `rank`, `iter_count`,
        `lambda_val` and `alpha` parameters.
    """

    def __init__(self):
        super(ImplicitRS, self).__init__()
        # users matrix in lower rank
        self.users_matrix = None
        # items matrix in lower rank
        self.items_matrix = None
        # recsys builted matrix
        self.recommendations = None

        # projecting [min, max) on range [0, 1) # not sure about
        # boundary points
        self.min_max_scaler = MinMaxScaler()

        # use to save memory resources from lots of data possibly
        # never been recommended
        self.fast_reqs_limit = -1

    def set_limit(self, value: int = 100):
        """
        :param value: new value to be set
        """
        self.fast_reqs_limit = value

    def build(self,
              rank=20,
              iter_count=25,
              lambda_val=0.1,
              alpha=40):
        """
        :param rank: (int) aim-rank to user and item representing
            matrices. We want A ~ U @ V,  where A (m x n) is our
            sparse matrix of interactions, matrix U (m x rank)
            represents users and matrix V (n x rank) represents items.
        :param iter_count: (int) iterations count to build matrix
        :param lambda_val: (double) parameter used in algo...
        :param alpha: (double) parameter representing how strongly
            we will be confident about the fact of interaction
            between user and item
        """
        self.__implicit_als(rank, iter_count, lambda_val, alpha)
        # other possible variants:
        # 1. recs = np.argsort(-users_matrix @ items_matrix.T, axis=1)
        # 2. qr(items_matrix)
        #    recs = np.argsort(-users_matrix @ q.T, axis=1)
        # all of them show quite equal results
        q, r = np.linalg.qr(self.items_matrix)
        self.recommendations = np.argsort(
                -(self.sparse_matrix @ q) @ q.T,
                axis=1
        )[:, :self.fast_reqs_limit]

    @staticmethod
    def _non_zeros_in_row(csr_matrix,
                          row):
        """
        :param csr_matrix: sparse matrix
        :param row: row of sparse matrix
        :return: range of tuples of 2 elements: index of column of
            non-zero element in csr_matrix's row and value of non-zero
            element itself
        """
        for i in range(csr_matrix.indptr[row], csr_matrix.indptr[row + 1]):
            yield csr_matrix.indices[i], csr_matrix.data[i]

    def __wrr(self,
              init_vec,
              a_mat,
              r_vec,
              c_mat,
              item_mat,
              u_id: int,
              iter_count: int):
        """
        Weighted Ridge Regression.
        I accepted M (from algorithm) equals to identity matrix.
        To understand what is going on in code below, take a look to
        one of those two links in class declaration docstring above.
        :param init_vec: vector w with which we are currently
            working; we are minimizing with respect to this vector.
        :param a_mat: matrix A from algorithm.
        :param r_vec: difference between Aw and b.
        :param c_mat: matrix representing confidence.
        :param item_mat: matrix of items.
        :param u_id: user's id of one whose vector we are formatting.
        :param iter_count: count of iterations to be done.
        :return: preconditioned conjugate gradient method for
            solving Aw = b.
        """
        p_vec = r_vec.copy()
        gamma = r_vec.dot(r_vec)  # gamma = r^T z, where z = M^1 r
        for _ in range(iter_count):
            # find A
            a_dot_p = a_mat @ p_vec
            for it_id, conf in self._non_zeros_in_row(c_mat, u_id):
                a_dot_p += (conf - 1) * (
                        item_mat[it_id] @ p_vec) * item_mat[it_id]

            # updating w and r vectors
            alpha = gamma / (p_vec @ a_dot_p)
            init_vec += alpha * p_vec
            r_vec -= alpha * a_dot_p

            # below: p = z + beta p, beta = gamma / (r^T z)
            tmp_gamma = r_vec.dot(r_vec)
            p_vec = r_vec + (gamma / tmp_gamma) * p_vec
            gamma = tmp_gamma
        return init_vec

    def __least_squares(self,
                        c_mat,
                        user_mat,
                        item_mat,
                        lambda_val,
                        iter_count=5):
        """
        We will to solve next equations for each u (user) and v (item):
        (U.T @ U + lambda * I + U.T @ (C_v - I) @ U) @ v
            = U.T @ C_v * interacted(v)
        (V.T @ V + lambda * I + V.T @ (C_u - I) @ V) @ u
            = V.T @ C_u * interacted(u)
        with a conjugate gradient method, where
        A = U.T @ U + lambda * I + U.T @ (C_v - I) @ U,
        b = U.T @ C_v * interacted(v)
        :param c_mat: mat represents confidence about u-i interactions
            (by our definition, confidence_{ui} = 1 + alpha r_{ui})
        :param user_mat: matrix of size m x rank, represents users
        :param item_mat: matrix of size n x rank, represents items
        :param lambda_val: non-negative regularization coefficient
        :param iter_count: count of iterations to be done
        """
        users_count, rank = user_mat.shape

        # matrix of size (r, r)
        a_mat = item_mat.T @ item_mat + lambda_val * np.eye(rank)

        for u_id in range(users_count):
            # vector of size (r, )
            w = user_mat[u_id]

            # find r = b − Aw, vector of size (r, )
            r_vec = -a_mat @ w
            for it_id, conf in self._non_zeros_in_row(c_mat, u_id):
                r_vec += (conf - (conf - 1) *
                          (item_mat[it_id] @ w)) * item_mat[it_id]

            # applying __wrr to user_mat[u_id]
            user_mat[u_id] = self.__wrr(
                    w, a_mat, r_vec, c_mat, item_mat, u_id, iter_count
            )

    def __implicit_als(self,
                       rank,
                       iter_count,
                       lambda_val,
                       alpha):
        """
        here are used same params as in method `build`
        """
        # formatting confidences matrix
        c_user_item = (self.sparse_matrix * alpha).astype('double').tocsr()
        c_item_user = c_user_item.T.tocsr()

        # initializing user and item representing matrices
        user_size, item_size = self.sparse_matrix.shape
        # zero-matrices consume more time, so rands are better
        user = np.random.rand(user_size, rank) * 0.01
        item = np.random.rand(item_size, rank) * 0.01

        # algo itself
        for _ in range(iter_count):
            self.__least_squares(c_user_item, user, item, lambda_val)
            self.__least_squares(c_item_user, item, user, lambda_val)

        # defining object's attributes
        self.users_matrix, self.items_matrix = user, item

    def find_similar_item(self,
                          item,
                          res_n: int = 10):
        """
        :param item: item as it is stored in database
            (meant it is in column that was given to load)
        :param res_n: count of items to find
        :return: `res_n` most similar to `item` items
        """
        item_id = self._item2index(item)
        # get vector corresponding to item
        item_vec = self.items_matrix[item_id].T
        # multiply item_vec to items_matrix,
        # so we will just sort scalar products of vectors
        scores = self.items_matrix.dot(item_vec).reshape(1, -1)[0]
        # choose top `res_n` and return them
        return self._index2item(np.argsort(scores)[::-1][:res_n])

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

        # to not recommend items user has consumed/interacted
        user_interactions = self.sparse_matrix[user_id, :].toarray()
        user_interactions = user_interactions.reshape(-1) + 1
        user_interactions[user_interactions > 1] = 0

        # calculate the recommendation by taking the product
        # of user vector with the item vectors
        rec_vector = (self.users_matrix[user_id, :] @
                      self.items_matrix.T)

        # scaling scores to make them easier to interpret
        rec_vector_scaled = self.min_max_scaler.fit_transform(
                rec_vector.reshape(-1, 1)
        )[:, 0]

        # do not multiply, if want consumed items to be recommended too
        recommend_vector = user_interactions * rec_vector_scaled

        # choose top `res_n` and return them
        return self._index2item(np.argsort(recommend_vector)[::-1][:res_n])

    def fast_recommend(self,
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
        del self.sparse_matrix
        del self.users_matrix
        del self.items_matrix
        del self.min_max_scaler


if __name__ == '__main__':
    implicit_rec = ImplicitRS()

    print("loading started...")
    implicit_rec.load("small_data/lastfm2collab.csv", ["user_id", "item_id"])
    print("loading finished...")
    implicit_rec.set_limit()
    print("building started...")
    implicit_rec.build()
    print("building finished...")

    q_item = "linkin park"
    similar_items = implicit_rec.find_similar_item(q_item)
    print("similar items:", *similar_items, sep="\n")

    q_user = 5985
    user_recs = implicit_rec.recommend_to_user(q_user)
    print("\nusers recs:", *user_recs, sep="\n")

    implicit_rec.drop_slow()
    user_fast_recs = implicit_rec.fast_recommend(q_user)
    print("\nusers fast recs:", *user_fast_recs, sep="\n")
