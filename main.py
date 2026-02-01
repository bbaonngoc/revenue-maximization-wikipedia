import networkx as nx
import numpy as np
import math
import heapq
import time

def solve_revenue_maximization_snap(file_path, B):
    # 1. Tải đồ thị từ file .txt (định dạng edge list của SNAP)
    print(f"--- Đang tải dữ liệu từ {file_path} ---")
    G = nx.read_edgelist(file_path, nodetype=int)
    
    # 2. Gán trọng số ngẫu nhiên w(u, v) trong [0, 1] như đề bài yêu cầu
    np.random.seed(42) # Để kết quả có thể tái lập
    for (u, v) in G.edges():
        G[u][v]['weight'] = np.random.uniform(0, 1)
    
    print(f"Đồ thị: {G.number_of_nodes()} đỉnh, {G.number_of_edges()} cạnh.")

    # 3. Tính chi phí c(u) dựa trên công thức đề bài
    costs = {}
    for u in G.nodes():
        total_w_u = sum(data['weight'] for _, _, data in G.edges(u, data=True))
        # Công thức: c(u) = 1 - e^(-0.2 * sqrt(sum_w))
        costs[u] = 1 - math.exp(-0.2 * math.sqrt(total_w_u))

    def get_marginal_gain(node, current_S):
        """Tính mức tăng doanh thu delta_f bằng cách duyệt lân cận"""
        gain = 0
        # Duyệt các đỉnh v kề với node u được chọn
        for v in G.neighbors(node):
            if v in current_S: continue
            
            # Tính tổng trọng số từ S đến v
            w_sum_old = 0
            for neighbor_of_v in G.neighbors(v):
                if neighbor_of_v in current_S:
                    w_sum_old += G[neighbor_of_v][v]['weight']
            
            w_sum_new = w_sum_old + G[node][v]['weight']
            gain += (math.sqrt(w_sum_new) - math.sqrt(w_sum_old))
        return gain

    # 4. Thuật toán CELF (Lazy Greedy)
    print("--- Đang chạy tối ưu hóa (CELF) ---")
    start_time = time.time()
    
    S = set()
    current_cost = 0
    current_f = 0
    priority_queue = []

    # Khởi tạo hàng đợi ban đầu
    for u in G.nodes():
        if costs[u] <= B:
            gain = get_marginal_gain(u, S)
            efficiency = gain / costs[u]
            # heapq là min-heap nên dùng giá trị âm để làm max-heap
            heapq.heappush(priority_queue, (-efficiency, u, 0))

    iteration = 1
    while priority_queue and current_cost < B:
        neg_eff, u, last_it = heapq.heappop(priority_queue)
        
        if last_it == iteration:
            # Nếu đỉnh này là tốt nhất sau khi đã được cập nhật ở vòng này
            if current_cost + costs[u] <= B:
                S.add(u)
                current_cost += costs[u]
                current_f += (-neg_eff * costs[u])
                iteration += 1
                # print(f"Chọn đỉnh {u:4}: Doanh thu +{-neg_eff*costs[u]:.4f}, Tổng cost: {current_cost:.4f}")
            continue
        
        # Lazy update: chỉ tính lại gain cho đỉnh đầu bảng
        new_gain = get_marginal_gain(u, S)
        new_eff = new_gain / costs[u]
        heapq.heappush(priority_queue, (-new_eff, u, iteration))
            
    end_time = time.time()
    
    print("-" * 40)
    print(f"Kết quả sau {end_time - start_time:.2f} giây:")
    print(f"Số lượng đỉnh trong tập S: {len(S)}")
    print(f"Tổng doanh thu f(S): {current_f:.4f}")
    print(f"Tổng chi phí: {current_cost:.4f} / Ngân sách B: {B}")
    
    return S

if __name__ == "__main__":
    # Chạy với file dữ liệu và ngân sách B
    result = solve_revenue_maximization_snap("/Users/baongoc/Downloads/wiki_demo.txt", B=5.0)
