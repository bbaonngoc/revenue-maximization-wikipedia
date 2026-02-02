"""
Các hàm tiện ích cho bài toán Tối đa hoá Doanh thu.
"""

import random
from collections import defaultdict


def load_graph(filepath):
    """
    Tải đồ thị từ file danh sách cạnh.
    Trả về danh sách kề với trọng số ngẫu nhiên trong [0, 1].
    
    Tham số:
        filepath: Đường dẫn đến file cạnh (định dạng: "đỉnh_nguồn đỉnh_đích" mỗi dòng)
    
    Trả về:
        graph: dict[đỉnh] -> danh sách (đỉnh kề, trọng số)
        nodes: tập tất cả các đỉnh
    """
    graph = defaultdict(list)
    nodes = set()
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 2:
                u, v = int(parts[0]), int(parts[1])
                weight = random.uniform(0, 1)  # Trọng số ngẫu nhiên trong [0, 1]
                graph[u].append((v, weight))
                nodes.add(u)
                nodes.add(v)
    
    return dict(graph), nodes


def compute_node_costs(graph, nodes):
    """
    Tính chi phí cho mỗi đỉnh dựa trên tổng trọng số các cạnh.
    
    Công thức chi phí: c(u) = 1 - exp(-tổng trọng số các cạnh liên quan đến u)
    
    Đảm bảo:
    - Chi phí tăng khi độ liên kết (tổng trọng số) của đỉnh tăng
    - Chi phí luôn nằm trong khoảng (0, 1)
    
    Tham số:
        graph: danh sách kề với trọng số
        nodes: tập tất cả các đỉnh
    
    Trả về:
        costs: dict[đỉnh] -> giá trị chi phí trong (0, 1)
    """
    import math
    
    # Tính tổng trọng số cho mỗi đỉnh: Σ_{(u,v)∈E} w(u,v)
    total_weights = defaultdict(float)
    
    for u, neighbors in graph.items():
        for v, weight in neighbors:
            total_weights[u] += weight
            total_weights[v] += weight  # Tính cả cho đỉnh đích
    
    # Công thức: c(u) = 1 - e^(-0.2 × √(Σ w(u,v)))
    costs = {}
    for node in nodes:
        w_sum = total_weights[node]
        costs[node] = 1 - math.exp(-0.2 * math.sqrt(w_sum))
    
    return costs


def build_reverse_graph(graph):
    """
    Xây dựng đồ thị ngược để lookup nhanh hơn.
    reverse_graph[v] = [(u, weight)] nghĩa là có cạnh u → v với trọng số weight
    """
    reverse_graph = defaultdict(list)
    for u, neighbors in graph.items():
        for v, weight in neighbors:
            reverse_graph[v].append((u, weight))
    return dict(reverse_graph)


def compute_revenue(S, graph, nodes, alpha=0.5, reverse_graph=None):
    """
    Tính hàm doanh thu f(S) cho tập seed S.
    
    Công thức doanh thu: f(S) = Σ_{v ∉ S} (Σ_{u ∈ S} w(u,v))^α
    
    Phiên bản tối ưu: Sử dụng reverse_graph để lookup O(1)
    """
    revenue = 0.0
    S_set = set(S)
    
    if not S_set:
        return 0.0
    
    # Với mỗi đỉnh v không thuộc S
    for v in nodes:
        if v in S_set:
            continue
        
        # Tổng trọng số từ các đỉnh trong S đến v
        influence_sum = 0.0
        
        if reverse_graph and v in reverse_graph:
            # Dùng reverse_graph: O(in_degree(v))
            for u, weight in reverse_graph[v]:
                if u in S_set:
                    influence_sum += weight
        else:
            # Fallback: O(|S| * avg_degree)
            for u in S_set:
                if u in graph:
                    for neighbor, weight in graph[u]:
                        if neighbor == v:
                            influence_sum += weight
        
        if influence_sum > 0:
            revenue += influence_sum ** alpha
    
    return revenue


def compute_marginal_gain(node, S, graph, nodes, alpha=0.5, reverse_graph=None, influence_cache=None):
    """
    Tính độ lợi biên khi thêm một đỉnh vào tập S.
    
    Độ lợi biên = f(S ∪ {node}) - f(S)
    
    Phiên bản tối ưu: Tính trực tiếp chỉ phần thay đổi
    """
    # Tối ưu: Khi S rỗng, marginal gain = f({node}) đơn giản hơn
    if len(S) == 0:
        if node not in graph:
            return 0.0
        gain = 0.0
        for neighbor, weight in graph[node]:
            if neighbor != node:
                gain += weight ** alpha
        return gain
    
    S_set = set(S)
    
    # Nếu node đã trong S, gain = 0
    if node in S_set:
        return 0.0
    
    # Tính marginal gain trực tiếp:
    # Δf = f(S∪{node}) - f(S)
    # Chỉ các đỉnh mà node có cạnh đến mới bị ảnh hưởng
    
    if node not in graph:
        return 0.0
    
    marginal = 0.0
    
    for neighbor, weight in graph[node]:
        if neighbor in S_set or neighbor == node:
            continue
        
        # Tính influence cũ từ S đến neighbor
        old_influence = 0.0
        if reverse_graph and neighbor in reverse_graph:
            for u, w in reverse_graph[neighbor]:
                if u in S_set:
                    old_influence += w
        else:
            for u in S_set:
                if u in graph:
                    for nb, w in graph[u]:
                        if nb == neighbor:
                            old_influence += w
        
        # Influence mới = old + weight từ node
        new_influence = old_influence + weight
        
        # Δ = new^α - old^α
        old_contrib = old_influence ** alpha if old_influence > 0 else 0
        new_contrib = new_influence ** alpha
        marginal += new_contrib - old_contrib
    
    return marginal


def total_cost(S, costs):
    """
    Tính tổng chi phí của tập seed.
    
    Tham số:
        S: tập các đỉnh seed
        costs: dict[đỉnh] -> chi phí
    
    Trả về:
        Tổng chi phí của S
    """
    return sum(costs.get(node, 0) for node in S)


def is_valid_budget(S, costs, budget):
    """
    Kiểm tra xem tập seed S có thỏa mãn ràng buộc ngân sách không.
    
    Tham số:
        S: tập các đỉnh seed
        costs: dict[đỉnh] -> chi phí
        budget: ngân sách tối đa B
    
    Trả về:
        True nếu tổng chi phí <= ngân sách
    """
    return total_cost(S, costs) <= budget


def print_result(S, revenue, cost, budget, algorithm_name="Thuật toán"):
    """
    In kết quả đã định dạng của thuật toán.
    """
    print(f"\n{'='*50}")
    print(f"Kết quả {algorithm_name}")
    print(f"{'='*50}")
    print(f"Kích thước tập seed: {len(S)}")
    print(f"Tổng chi phí: {cost:.4f} / Ngân sách: {budget:.4f}")
    print(f"Doanh thu: {revenue:.4f}")
    print(f"Các đỉnh seed (10 đầu tiên): {list(S)[:10]}...")
    print(f"{'='*50}\n")
