"""
Script kiểm tra độ chính xác của thuật toán CELF.

So sánh với:
1. Tính revenue từ đầu (không dùng cache)
2. Thuật toán Greedy cơ bản
"""

import random
import time
from .config import BUDGET, ALPHA, SEED, FILTERED_DATA_PATH
from .utils import load_graph, compute_node_costs
from .celf import celf_optimized


def compute_revenue_naive(S, graph, nodes, alpha):
    """
    Tính revenue TRỰC TIẾP từ công thức gốc (để kiểm tra).
    
    f(S) = Σ_{v ∉ S} (Σ_{u ∈ S} w(u,v))^α
    """
    S_set = set(S)
    revenue = 0.0
    
    for v in nodes:
        if v in S_set:
            continue
        
        # Tổng influence từ S đến v
        influence = 0.0
        for u in S_set:
            if u in graph:
                for neighbor, weight in graph[u]:
                    if neighbor == v:
                        influence += weight
        
        if influence > 0:
            revenue += influence ** alpha
    
    return revenue


def greedy_naive(graph, nodes, costs, budget, alpha):
    """
    Thuật toán Greedy CƠ BẢN - O(n²), chậm nhưng chắc chắn đúng.
    """
    S = set()
    remaining = budget
    
    while True:
        best_node = None
        best_ratio = -1
        
        for node in nodes:
            if node in S:
                continue
            cost = costs.get(node, 0)
            if cost > remaining:
                continue
            
            # Tính marginal gain từ đầu
            old_rev = compute_revenue_naive(S, graph, nodes, alpha)
            new_rev = compute_revenue_naive(S | {node}, graph, nodes, alpha)
            gain = new_rev - old_rev
            
            ratio = gain / cost if cost > 0 else float('inf')
            if ratio > best_ratio:
                best_ratio = ratio
                best_node = node
        
        if best_node is None:
            break
        
        S.add(best_node)
        remaining -= costs[best_node]
        print(f"  Greedy chọn {best_node}, |S|={len(S)}, còn={remaining:.4f}")
    
    final_rev = compute_revenue_naive(S, graph, nodes, alpha)
    return S, final_rev


def main():
    print("=" * 60)
    print("KIỂM TRA ĐỘ CHÍNH XÁC THUẬT TOÁN")
    print("=" * 60)
    
    random.seed(SEED)
    
    # Dùng budget nhỏ để Greedy chạy nhanh
    TEST_BUDGET = 0.3
    
    print(f"\nĐang tải đồ thị...")
    graph, nodes = load_graph(FILTERED_DATA_PATH)
    costs = compute_node_costs(graph, nodes)
    print(f"Đã tải {len(nodes)} đỉnh")
    
    # 1. Chạy CELF
    print(f"\n--- CELF (Budget={TEST_BUDGET}) ---")
    start = time.time()
    S_celf, rev_celf, cost_celf = celf_optimized(
        graph, nodes, costs, TEST_BUDGET, ALPHA, verbose=False
    )
    celf_time = time.time() - start
    
    # 2. Tính lại revenue từ đầu để verify
    rev_verify = compute_revenue_naive(S_celf, graph, nodes, ALPHA)
    
    print(f"CELF:")
    print(f"  Seed: {sorted(S_celf)}")
    print(f"  Revenue (từ cache): {rev_celf:.4f}")
    print(f"  Revenue (tính lại): {rev_verify:.4f}")
    print(f"  Sai số: {abs(rev_celf - rev_verify):.6f}")
    print(f"  Thời gian: {celf_time:.2f}s")
    
    # 3. Chạy Greedy naive (chậm)
    print(f"\n--- GREEDY NAIVE (Budget={TEST_BUDGET}) ---")
    print("  (Chậm vì tính lại revenue từ đầu mỗi bước)")
    start = time.time()
    S_greedy, rev_greedy = greedy_naive(
        graph, nodes, costs, TEST_BUDGET, ALPHA
    )
    greedy_time = time.time() - start
    
    print(f"\nGreedy:")
    print(f"  Seed: {sorted(S_greedy)}")
    print(f"  Revenue: {rev_greedy:.4f}")
    print(f"  Thời gian: {greedy_time:.2f}s")
    
    # 4. So sánh
    print("\n" + "=" * 60)
    print("SO SÁNH")
    print("=" * 60)
    
    same_set = S_celf == S_greedy
    rev_match = abs(rev_celf - rev_greedy) < 0.001
    
    print(f"Cùng tập seed: {'✓ ĐÚNG' if same_set else '✗ KHÁC'}")
    print(f"Revenue khớp:  {'✓ ĐÚNG' if rev_match else '✗ KHÁC'}")
    print(f"CELF nhanh hơn: {greedy_time/celf_time:.1f}x")
    
    if same_set and rev_match:
        print("\nTHUẬT TOÁN CELF CHÍNH XÁC!")
    else:
        print("\nCÓ SAI KHÁC - CẦN KIỂM TRA!")


if __name__ == "__main__":
    main()
