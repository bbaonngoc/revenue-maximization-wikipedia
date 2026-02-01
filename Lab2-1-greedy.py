import networkx as nx
import numpy as np
import math
import time


def solve_revenue_maximization_greedy(file_path, B):
    # ==============================
    # 1. Load graph (SNAP edge list)
    # ==============================
    print(f"--- Đang tải dữ liệu từ {file_path} ---")
    G = nx.read_edgelist(file_path, nodetype=int)
    print(f"Đồ thị có {G.number_of_nodes()} đỉnh và {G.number_of_edges()} cạnh")

    # ==============================
    # 2. Gán trọng số cạnh w(u,v) ~ U(0,1]
    # ==============================
    np.random.seed(42)
    for u, v in G.edges():
        G[u][v]["weight"] = np.random.uniform(0, 1)

    # ==============================
    # 3. Tính chi phí c(u)
    # c(u) = 1 - exp(-0.2 * sqrt(sum_w))
    # ==============================
    costs = {}
    for u in G.nodes():
        total_w = sum(G[u][v]["weight"] for v in G.neighbors(u))
        costs[u] = 1 - math.exp(-0.2 * math.sqrt(total_w))

    # ==============================
    # 4. Hàm tính độ lợi biên Δf(u | S)
    # ==============================
    def marginal_gain(u, S):
        gain = 0.0

        for v in G.neighbors(u):
            if v in S:
                continue

            # tổng trọng số từ S tới v
            w_old = 0.0
            for x in G.neighbors(v):
                if x in S:
                    w_old += G[x][v]["weight"]

            w_new = w_old + G[u][v]["weight"]
            gain += math.sqrt(w_new) - math.sqrt(w_old)

        return gain

    # ==============================
    # 5. Greedy thuần
    # ==============================
    print("--- Đang chạy Greedy thuần ---")
    start_time = time.time()

    S = set()
    current_cost = 0.0
    current_f = 0.0

    while True:
        best_node = None
        best_efficiency = 0.0
        best_gain = 0.0

        for u in G.nodes():
            if u in S:
                continue
            if current_cost + costs[u] > B:
                continue

            gain = marginal_gain(u, S)
            efficiency = gain / costs[u] if costs[u] > 0 else 0

            if efficiency > best_efficiency:
                best_efficiency = efficiency
                best_node = u
                best_gain = gain

        if best_node is None:
            break

        S.add(best_node)
        current_cost += costs[best_node]
        current_f += best_gain

    end_time = time.time()

    # ==============================
    # 6. Output
    # ==============================
    print("-" * 40)
    print(f"Kết quả sau {end_time - start_time:.2f} giây:")
    print(f"Số lượng đỉnh trong tập S: {len(S)}")
    print(f"Tổng doanh thu f(S): {current_f:.4f}")
    print(f"Tổng chi phí: {current_cost:.4f}")
    print(f"Ngân sách B: {B}")

    return S


if __name__ == "__main__":
    solve_revenue_maximization_greedy(
        "/Users/baongoc/Downloads/wiki-demo.txt",
        B=20.0
    )
