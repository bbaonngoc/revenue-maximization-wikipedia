"""
Thuật toán CELF tối ưu cho Tối đa hoá Doanh thu.

Triển khai theo yêu cầu:
- KHÔNG gọi compute_revenue(S) trong vòng lặp
- Duy trì trạng thái w_sum[v] = Σ_{u ∈ S} w(u, v)
- Tính marginal gain trực tiếp: Δ(u|S) = Σ_{v:u→v} [(w_sum[v] + w(u,v))^α - w_sum[v]^α]
"""

import heapq
from collections import defaultdict
from .utils import total_cost, print_result


class CELFHeapItem:
    """Phần tử heap cho thuật toán CELF."""
    def __init__(self, node, gain, cost, iteration):
        self.node = node
        self.gain = gain
        self.cost = cost
        self.ratio = gain / cost if cost > 0 else float('inf')
        self.iteration = iteration
    
    def __lt__(self, other):
        return self.ratio > other.ratio


def build_reverse_graph(graph):
    """
    Xây dựng đồ thị ngược.
    reverse_graph[v] = [(u, weight)] nghĩa là có cạnh u → v
    """
    reverse_graph = defaultdict(list)
    for u, neighbors in graph.items():
        for v, weight in neighbors:
            reverse_graph[v].append((u, weight))
    return dict(reverse_graph)


def compute_marginal_gain_incremental(node, graph, w_sum, S_set, alpha):
    """
    Tính marginal gain TRỰC TIẾP từ w_sum cache.
    
    Δ(u|S) = Σ_{v: u→v, v∉S} [(w_sum[v] + w(u,v))^α - (w_sum[v])^α]
    
    Độ phức tạp: O(out_degree(u))
    """
    if node not in graph:
        return 0.0
    
    marginal = 0.0
    
    for neighbor, weight in graph[node]:
        # Bỏ qua nếu neighbor đã trong S hoặc là chính node
        if neighbor in S_set or neighbor == node:
            continue
        
        old_influence = w_sum.get(neighbor, 0.0)
        new_influence = old_influence + weight
        
        old_contrib = old_influence ** alpha if old_influence > 0 else 0.0
        new_contrib = new_influence ** alpha
        
        marginal += new_contrib - old_contrib
    
    return marginal


def update_w_sum(node, graph, w_sum, S_set):
    """
    Cập nhật w_sum khi thêm node vào S.
    
    w_sum[v] += w(node, v) cho mọi v mà node → v
    
    Độ phức tạp: O(out_degree(node))
    """
    if node not in graph:
        return
    
    for neighbor, weight in graph[node]:
        if neighbor not in S_set and neighbor != node:
            w_sum[neighbor] = w_sum.get(neighbor, 0.0) + weight


def compute_revenue_from_w_sum(w_sum, S_set, alpha):
    """
    Tính doanh thu từ w_sum cache.
    
    f(S) = Σ_{v ∉ S} (w_sum[v])^α
    
    Độ phức tạp: O(|w_sum|)
    """
    revenue = 0.0
    for v, influence in w_sum.items():
        if v not in S_set and influence > 0:
            revenue += influence ** alpha
    return revenue


def celf_optimized(graph, nodes, costs, budget, alpha=0.5, verbose=True):
    """
    Thuật toán CELF tối ưu - KHÔNG gọi compute_revenue(S) trong vòng lặp.
    
    Duy trì:
    - w_sum[v]: tổng trọng số từ S đến v
    - Cập nhật incremental khi thêm node
    """
    S = set()
    remaining_budget = budget
    current_iteration = 0
    
    # w_sum[v] = Σ_{u ∈ S} w(u, v) - khởi tạo rỗng
    w_sum = {}
    
    if verbose:
        print(f"Bắt đầu CELF Tối ưu (Ngân sách={budget}, alpha={alpha})")
        print("-" * 50)
    
    # Giai đoạn 1: Khởi tạo heap
    if verbose:
        print("Đang khởi tạo heap...")
    
    heap = []
    eligible_nodes = [n for n in nodes if costs.get(n, 0) <= budget]
    total_eligible = len(eligible_nodes)
    
    if verbose:
        print(f"Số đỉnh vừa ngân sách: {total_eligible}")
    
    for i, node in enumerate(eligible_nodes):
        node_cost = costs.get(node, 0)
        # Khi S = ∅, marginal gain = f({node}) = Σ w(node, v)^α
        gain = compute_marginal_gain_incremental(node, graph, w_sum, S, alpha)
        item = CELFHeapItem(node, gain, node_cost, current_iteration)
        heapq.heappush(heap, item)
        
        if verbose and (i + 1) % 5000 == 0:
            print(f"  Đã xử lý {i + 1}/{total_eligible} đỉnh ({100*(i+1)/total_eligible:.1f}%)")
    
    if verbose:
        print(f"Heap đã khởi tạo với {len(heap)} ứng viên")
    
    # Giai đoạn 2: Chọn lọc lazy forward
    recompute_count = 0
    
    while heap:
        top = heapq.heappop(heap)
        
        if top.cost > remaining_budget:
            continue
        
        if top.iteration == current_iteration:
            # Chọn đỉnh này
            S.add(top.node)
            remaining_budget -= top.cost
            current_iteration += 1
            
            # CẬP NHẬT w_sum incremental
            update_w_sum(top.node, graph, w_sum, S)
            
            if verbose and current_iteration % 10 == 0:
                revenue = compute_revenue_from_w_sum(w_sum, S, alpha)
                print(f"  Vòng {current_iteration}: |S|={len(S)}, Doanh thu={revenue:.4f}, Còn={remaining_budget:.4f}")
        else:
            # Tính lại marginal gain từ w_sum hiện tại
            new_gain = compute_marginal_gain_incremental(top.node, graph, w_sum, S, alpha)
            new_item = CELFHeapItem(top.node, new_gain, top.cost, current_iteration)
            heapq.heappush(heap, new_item)
            recompute_count += 1
    
    # Tính kết quả cuối cùng
    final_revenue = compute_revenue_from_w_sum(w_sum, S, alpha)
    final_cost = total_cost(S, costs)
    
    if verbose:
        print(f"\nTổng số lần tính lại: {recompute_count}")
        print_result(S, final_revenue, final_cost, budget, "CELF Tối ưu")
    
    return S, final_revenue, final_cost


if __name__ == "__main__":
    import random
    from .config import BUDGET, ALPHA, SEED, FILTERED_DATA_PATH
    from .utils import load_graph, compute_node_costs
    
    random.seed(SEED)
    
    print("Đang tải đồ thị...")
    graph, nodes = load_graph(FILTERED_DATA_PATH)
    print(f"Đã tải {len(nodes)} đỉnh")
    
    print("Đang tính chi phí các đỉnh...")
    costs = compute_node_costs(graph, nodes)
    
    S, revenue, cost = celf_optimized(graph, nodes, costs, BUDGET, ALPHA)
