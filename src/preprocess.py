"""
Module tiền xử lý dữ liệu mạng thảo luận Wikipedia.
Lọc đồ thị để giảm kích thước cho việc thử nghiệm.
"""

import os
from collections import defaultdict


def load_raw_edges(filepath):
    """
    Tải các cạnh thô từ file.
    
    Tham số:
        filepath: Đường dẫn đến file danh sách cạnh thô
    
    Trả về:
        Danh sách các tuple (u, v)
    """
    edges = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 2:
                u, v = int(parts[0]), int(parts[1])
                edges.append((u, v))
    return edges


def filter_graph_by_degree(edges, min_degree=5, max_nodes=5000):
    """
    Lọc đồ thị để chỉ giữ lại các đỉnh có bậc tối thiểu.
    Đồng thời giới hạn tổng số đỉnh.
    
    Tham số:
        edges: Danh sách các tuple (u, v)
        min_degree: Ngưỡng bậc tối thiểu
        max_nodes: Số đỉnh tối đa được giữ lại
    
    Trả về:
        Danh sách các cạnh đã lọc
    """
    # Đếm bậc của các đỉnh
    degree = defaultdict(int)
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    
    # Lọc các đỉnh theo bậc
    high_degree_nodes = {
        node for node, deg in degree.items() 
        if deg >= min_degree
    }
    
    # Sắp xếp theo bậc và lấy top max_nodes
    sorted_nodes = sorted(high_degree_nodes, key=lambda x: degree[x], reverse=True)
    selected_nodes = set(sorted_nodes[:max_nodes])
    
    # Lọc các cạnh chỉ bao gồm các đỉnh được chọn
    filtered_edges = [
        (u, v) for u, v in edges 
        if u in selected_nodes and v in selected_nodes
    ]
    
    return filtered_edges


def save_edges(edges, filepath):
    """
    Lưu các cạnh vào file.
    
    Tham số:
        edges: Danh sách các tuple (u, v)
        filepath: Đường dẫn file đầu ra
    """
    with open(filepath, 'w') as f:
        f.write(f"# Đồ thị đã lọc: {len(edges)} cạnh\n")
        for u, v in edges:
            f.write(f"{u}\t{v}\n")


def preprocess_wiki_talk(input_path, output_path, min_degree=5, max_nodes=5000):
    """
    Hàm tiền xử lý chính cho tập dữ liệu Wiki-Talk.
    
    Tham số:
        input_path: Đường dẫn đến file wiki-Talk.txt gốc
        output_path: Đường dẫn để lưu đồ thị đã lọc
        min_degree: Ngưỡng bậc tối thiểu
        max_nodes: Số đỉnh tối đa
    """
    print(f"Đang tải các cạnh thô từ {input_path}...")
    edges = load_raw_edges(input_path)
    print(f"Đã tải {len(edges)} cạnh")
    
    # Lấy số đỉnh duy nhất
    nodes = set()
    for u, v in edges:
        nodes.add(u)
        nodes.add(v)
    print(f"Tổng số đỉnh duy nhất: {len(nodes)}")
    
    print(f"\nĐang lọc đồ thị (min_degree={min_degree}, max_nodes={max_nodes})...")
    filtered_edges = filter_graph_by_degree(edges, min_degree, max_nodes)
    
    # Đếm số đỉnh sau khi lọc
    filtered_nodes = set()
    for u, v in filtered_edges:
        filtered_nodes.add(u)
        filtered_nodes.add(v)
    
    print(f"Số cạnh sau lọc: {len(filtered_edges)}")
    print(f"Số đỉnh sau lọc: {len(filtered_nodes)}")
    
    print(f"\nĐang lưu vào {output_path}...")
    save_edges(filtered_edges, output_path)
    print("Hoàn tất!")
    
    return filtered_edges


if __name__ == "__main__":
    from config import RAW_DATA_PATH, FILTERED_DATA_PATH, MIN_DEGREE, MAX_NODES
    
    # Chạy tiền xử lý với tham số từ config
    preprocess_wiki_talk(
        input_path=RAW_DATA_PATH,
        output_path=FILTERED_DATA_PATH,
        min_degree=MIN_DEGREE,
        max_nodes=MAX_NODES
    )
