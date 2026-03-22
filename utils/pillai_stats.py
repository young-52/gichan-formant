import numpy as np


def calculate_pillai_score(group1_coords, group2_coords):
    """
    두 데이터 그룹(예: Group 1, Group 2) 간의 Pillai Score (Pillai's Trace)를 계산합니다.
    다변량 분산분석(MANOVA)을 통해 두 그룹이 얼마나 분리되어 있는지를 0~1 사이의 값으로 나타냅니다.

    Args:
        group1_coords (np.ndarray): 그룹 1의 좌표 데이터 (n, 2)
        group2_coords (np.ndarray): 그룹 2의 좌표 데이터 (m, 2)

    Returns:
        tuple[float|None, float|None]: (Pillai Score, p-value), 계산 실패 시 (None, None)
    """
    try:
        from scipy import stats

        # 데이터가 NumPy 배열인지 확인 및 변환
        g1 = np.asarray(group1_coords)
        g2 = np.asarray(group2_coords)
        if g1.ndim != 2 or g2.ndim != 2:
            return None, None

        n1 = g1.shape[0]
        n2 = g2.shape[0]
        p = g1.shape[1]
        N = n1 + n2

        # F-통계량 계산을 위한 데이터 기준 검사 (N >= p + 2 필요)
        if N < p + 2 or n1 < 1 or n2 < 1:
            return None, None

        # 역행렬 계산 오류를 막기 위해 데이터가 너무 적은 경우 처리
        if n1 < 2 or n2 < 2:
            return None, None

        mean1 = np.mean(g1, axis=0)
        mean2 = np.mean(g2, axis=0)
        mean_total = np.mean(np.vstack((g1, g2)), axis=0)

        W = np.zeros((p, p))
        for i in range(n1):
            diff = g1[i] - mean1
            W += np.outer(diff, diff)
        for i in range(n2):
            diff = g2[i] - mean2
            W += np.outer(diff, diff)

        B = np.zeros((p, p))
        diff1 = mean1 - mean_total
        B += n1 * np.outer(diff1, diff1)
        diff2 = mean2 - mean_total
        B += n2 * np.outer(diff2, diff2)

        T = W + B
        T_inv = np.linalg.pinv(T)
        matrix = np.dot(T_inv, B)
        # 모든 고유값의 합 (Pillai's Trace V)
        eigenvalues = np.linalg.eigvals(matrix)
        v = np.sum(np.real(eigenvalues))
        pillai_score = float(np.clip(v, 0.0, 1.0))

        # MANOVA g=2 그룹, 변수 p=2 인 경우의 F-분포 근사 계산
        # V = Pillai's trace
        # F = (V / p) / ((1 - V) / (N - p - 1))
        # df1 = p, df2 = N - p - 1
        # V = 1.0 인 경우 완전 분리이므로 p-value = 0.0 처리

        if pillai_score >= 1.0 - 1e-9:
            p_value = 0.0
        else:
            df1 = p
            df2 = N - p - 1
            f_stat = (pillai_score / df1) / ((1.0 - pillai_score) / df2)
            p_value = stats.f.sf(f_stat, df1, df2)

        return pillai_score, p_value
    except Exception:
        return None, None
