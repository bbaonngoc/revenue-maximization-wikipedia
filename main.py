"""
Điểm khởi chạy chính cho các thử nghiệm Tối đa hoá Doanh thu.

Chạy thuật toán CELF với ngân sách được cấu hình trong config.py.
"""

import os
import time
import random
from config import BUDGET, ALPHA, SEED, FILTERED_DATA_PATH, RAW_DATA_PATH
from utils import load_graph, compute_node_costs
from celf import celf_optimized as celf_revenue_maximization


def run_experiment(graph, nodes, costs, budget, alpha=0.5):
    """
    Chạy thử nghiệm so sánh thuật toán Tham lam và CELF.
    
    Tham số:
        graph: danh sách kề với trọng số
        nodes: tập tất cả các đỉnh
        costs: dict[đỉnh] -> chi phí
        budget: ngân sách B
        alpha: tham số lợi suất giảm dần
    
    Trả về:
        results: dict chứa kết quả thử nghiệm
    """
    print("\n" + "=" * 60)
    print("THỬ NGHIỆM TỐI ĐA HOÁ DOANH THU")
    print(f"Đồ thị: {len(nodes)} đỉnh, alpha={alpha}, B={budget}")
    print("=" * 60)
    
    # Chạy Tham lam
    # print("\n--- THUẬT TOÁN THAM LAM ---")
    # start_time = time.time()
    # S_greedy, rev_greedy, cost_greedy = greedy_revenue_maximization(
    #     graph, nodes, costs, budget, alpha, verbose=True
    # )
    # greedy_time = time.time() - start_time
    
    # Chạy CELF
    print("\n--- THUẬT TOÁN CELF ---")
    start_time = time.time()
    S_celf, rev_celf, cost_celf = celf_revenue_maximization(
        graph, nodes, costs, budget, alpha, verbose=True
    )
    celf_time = time.time() - start_time
    
    # So sánh
    # print("\n" + "=" * 60)
    # print("SO SÁNH KẾT QUẢ")
    # print("=" * 60)
    print(f"{'Thuật toán':<15} {'Doanh thu':<12} {'|S|':<8} {'Chi phí':<12} {'Thời gian':<12}")
    # print("-" * 60)
    #print(f"{'Tham lam':<15} {rev_greedy:<12.4f} {len(S_greedy):<8} {cost_greedy:<12.4f} {greedy_time:.2f}s")
    print(f"{'CELF':<15} {rev_celf:<12.4f} {len(S_celf):<8} {cost_celf:<12.4f} {celf_time:.2f}s")
    print("=" * 60)
    
    # if celf_time > 0:
    #     speedup = greedy_time / celf_time
    #     print(f"\nCELF nhanh hơn Tham lam: {speedup:.2f} lần")
    
    return {
    #     'greedy': {'S': S_greedy, 'revenue': rev_greedy, 'cost': cost_greedy, 'time': greedy_time},
        'celf': {'S': S_celf, 'revenue': rev_celf, 'cost': cost_celf, 'time': celf_time}
    }


def main():
    """
    Hàm chính để chạy thử nghiệm.
    """
    print(f"=== CẤU HÌNH ===")
    print(f"Ngân sách B = {BUDGET}")
    print(f"Alpha = {ALPHA}")
    print(f"Seed = {SEED}")
    
    # Kiểm tra dữ liệu đã lọc có tồn tại không
    if os.path.exists(FILTERED_DATA_PATH):
        data_path = FILTERED_DATA_PATH
        print(f"\nSử dụng dữ liệu đã lọc: {data_path}")
    elif os.path.exists(RAW_DATA_PATH):
        print("Không tìm thấy dữ liệu đã lọc. Đang chạy tiền xử lý...")
        from preprocess import preprocess_wiki_talk
        from config import MIN_DEGREE, MAX_NODES
        preprocess_wiki_talk(RAW_DATA_PATH, FILTERED_DATA_PATH, MIN_DEGREE, MAX_NODES)
        data_path = FILTERED_DATA_PATH
    else:
        print(f"Lỗi: Không tìm thấy file dữ liệu tại {RAW_DATA_PATH}")
        print("Vui lòng tải xuống tập dữ liệu wiki-Talk.txt.")
        return
    
    # Đặt seed ngẫu nhiên để tái tạo kết quả
    random.seed(SEED)
    
    # Tải đồ thị
    print("\nĐang tải đồ thị...")
    graph, nodes = load_graph(data_path)
    print(f"Đã tải đồ thị: {len(nodes)} đỉnh, {sum(len(v) for v in graph.values())} cạnh")
    
    # Tính chi phí
    print("Đang tính chi phí các đỉnh...")
    costs = compute_node_costs(graph, nodes)
    
    # In thống kê chi phí
    cost_values = list(costs.values())
    print(f"Thống kê chi phí: min={min(cost_values):.4f}, "
          f"max={max(cost_values):.4f}, "
          f"trung bình={sum(cost_values)/len(cost_values):.4f}")
    
    # Chạy thử nghiệm với ngân sách từ config
    results = run_experiment(graph, nodes, costs, BUDGET, ALPHA)
    
    print("\n✓ Thử nghiệm hoàn tất!")


if __name__ == "__main__":
    main()
