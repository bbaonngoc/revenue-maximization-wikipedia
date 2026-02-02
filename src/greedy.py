# """
# Thuật toán Tham lam (Greedy) cơ bản cho Tối đa hoá Doanh thu với Ràng buộc Ngân sách.

# Tại mỗi bước, chọn đỉnh có độ lợi biên trên chi phí cao nhất
# mà vẫn nằm trong ngân sách còn lại.
# """

# from utils import (
#     compute_revenue, 
#     compute_marginal_gain, 
#     total_cost,
#     print_result
# )


# def greedy_revenue_maximization(graph, nodes, costs, budget, alpha=0.5, verbose=True):
#     """
#     Thuật toán tham lam cho tối đa hoá doanh thu với ràng buộc ngân sách.
    
#     Tại mỗi vòng lặp:
#     1. Với mỗi đỉnh chưa chọn mà còn vừa ngân sách
#     2. Tính tỷ lệ độ lợi biên / chi phí
#     3. Chọn đỉnh có tỷ lệ cao nhất
#     4. Lặp lại cho đến khi không thể thêm đỉnh nào nữa
    
#     Tham số:
#         graph: danh sách kề với trọng số
#         nodes: tập tất cả các đỉnh
#         costs: dict[đỉnh] -> chi phí
#         budget: ngân sách tối đa B
#         alpha: tham số lợi suất giảm dần
#         verbose: in tiến trình
    
#     Trả về:
#         S: tập seed đã chọn
#         revenue: giá trị doanh thu cuối cùng
#         total_cost_value: tổng chi phí của S
#     """
#     S = set()
#     remaining_budget = budget
#     candidates = set(nodes)
#     iteration = 0
    
#     if verbose:
#         print(f"Bắt đầu (Ngân sách={budget}, alpha={alpha})")
#         print("-" * 50)
    
#     while candidates:
#         best_node = None
#         best_ratio = -1
#         best_gain = 0
        
#         # Tìm đỉnh tốt nhất dựa trên tỷ lệ độ lợi biên / chi phí
#         nodes_to_remove = []
        
#         for node in candidates:
#             node_cost = costs.get(node, 0)
            
#             # Bỏ qua nếu đỉnh không vừa ngân sách
#             if node_cost > remaining_budget:
#                 nodes_to_remove.append(node)
#                 continue
            
#             # Tính độ lợi biên
#             gain = compute_marginal_gain(node, S, graph, nodes, alpha)
            
#             # Tính tỷ lệ (tránh chia cho 0)
#             if node_cost > 0:
#                 ratio = gain / node_cost
#             else:
#                 ratio = float('inf') if gain > 0 else 0
            
#             if ratio > best_ratio:
#                 best_ratio = ratio
#                 best_node = node
#                 best_gain = gain
        
#         # Loại bỏ các đỉnh không vừa ngân sách
#         for node in nodes_to_remove:
#             candidates.discard(node)
        
#         # Nếu không tìm thấy đỉnh hợp lệ, dừng
#         if best_node is None or best_gain <= 0:
#             break
        
#         # Thêm đỉnh tốt nhất vào tập seed
#         node_cost = costs[best_node]
#         S.add(best_node)
#         remaining_budget -= node_cost
#         candidates.discard(best_node)
#         iteration += 1
        
#         if verbose and iteration % 10 == 0:
#             current_revenue = compute_revenue(S, graph, nodes, alpha)
#             print(f"  Vòng {iteration}: |S|={len(S)}, Doanh thu={current_revenue:.4f}, Còn={remaining_budget:.4f}")
    
#     # Tính doanh thu cuối cùng
#     final_revenue = compute_revenue(S, graph, nodes, alpha)
#     final_cost = total_cost(S, costs)
    
#     if verbose:
#         print_result(S, final_revenue, final_cost, budget, "Tham lam")
    
#     return S, final_revenue, final_cost


# if __name__ == "__main__":
#     import os
#     from config import BUDGET, ALPHA, SEED, FILTERED_DATA_PATH
#     from utils import load_graph, compute_node_costs
#     import random
    
#     random.seed(SEED)
    
#     print("Đang tải đồ thị...")
#     graph, nodes = load_graph(FILTERED_DATA_PATH)
#     print(f"Đã tải {len(nodes)} đỉnh")
    
#     print("Đang tính chi phí các đỉnh...")
#     costs = compute_node_costs(graph, nodes)
    
#     # Chạy với ngân sách từ config
#     S, revenue, cost = greedy_revenue_maximization(graph, nodes, costs, BUDGET, ALPHA)
