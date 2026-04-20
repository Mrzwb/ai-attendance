import numpy as np


def cosine_similarity(vec1, vec2):
    """
    余弦相似度
    :param vec1:
    :param vec2:
    :return:
    """
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    return dot_product / (norm_vec1 * norm_vec2)
