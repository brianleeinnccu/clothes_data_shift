import math

def calculate_npmi(count_i, count_j, count_ij, total_outfits):
    """
    計算兩個 category 之間的 NPMI

    Parameters
    ----------
    count_i : int
        category i 出現於多少個 outfit

    count_j : int
        category j 出現於多少個 outfit

    count_ij : int
        category i 與 j 同時出現於多少個 outfit

    total_outfits : int
        該年份的 outfit 總數

    Returns
    -------
    float
        NPMI，範圍通常介於 [-1, 1]
    """

    if total_outfits <= 0:
        raise ValueError("total_outfits 必須大於 0")

    # 如果其中一個 category 根本沒有出現
    if count_i == 0 or count_j == 0:
        return None

    # 完全沒有共同出現
    if count_ij == 0:
        return -1.0
    # 計算機率
    p_i = count_i / total_outfits
    p_j = count_j / total_outfits
    p_ij = count_ij / total_outfits

    # PMI
    pmi = math.log(p_ij / (p_i * p_j))
    # 特殊情況：兩個 category 在所有 outfit 都一起出現
    # 此時 p_ij = 1，-log(1) = 0
    if p_ij == 1.0:
        return 1.0

    # NPMI
    npmi = pmi / (-math.log(p_ij))

    return npmi