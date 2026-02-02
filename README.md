# Tối đa hoá doanh thu trên mạng thảo luận Wikipedia

## 1. Mô tả bài toán

Cho một mạng xã hội (mạng thảo luận Wikipedia) được mô hình hóa dưới dạng đồ thị có hướng hoặc vô hướng:
- **G = (V, E)**, trong đó:
  - **V** là tập các đỉnh, mỗi đỉnh tương ứng với một người dùng.
  - **E** là tập các cạnh, mỗi cạnh \((u, v) \in E\) biểu diễn một mối quan hệ/tương tác giữa hai người dùng.

Mỗi cạnh \((u, v)\) được gán một **trọng số dương** \(w(u, v)\), được sinh ngẫu nhiên theo phân phối đều trong khoảng \([0, 1]\). Trọng số này phản ánh cường độ ảnh hưởng hoặc mức độ tương tác giữa hai người dùng.

## 2. Chi phí của đỉnh

Mỗi đỉnh \(u \in V\) được gán một **chi phí dương** \(c(u)\), được xác định dựa trên tổng trọng số các cạnh liên quan đến đỉnh đó:

<img width="280" height="180" alt="Ảnh màn hình 2026-02-01 lúc 16 35 42" src="https://github.com/user-attachments/assets/841f8a81-53db-4ef1-a97d-129e2e1e6b55" />


Công thức này đảm bảo:
- Chi phí \(c(u)\) tăng khi mức độ kết nối (tổng trọng số cạnh) của đỉnh \(u\) tăng.
- Chi phí luôn nằm trong khoảng \((0, 1)\).

## 3. Hàm doanh thu

Với một tập con các đỉnh được chọn \(S \subseteq V\) (tập seed), **doanh thu** thu được từ \(S\) được xác định bởi hàm:

<img width="250" height="180" alt="Ảnh màn hình 2026-02-01 lúc 16 36 28" src="https://github.com/user-attachments/assets/45b11251-0938-41f9-8868-41f27e9bb106" />


trong đó:
- \(\alpha \in (0,1]\) là tham số điều chỉnh mức độ lợi suất giảm dần (diminishing returns).

Hàm \(f(S)\) đo lường tổng mức ảnh hưởng mà tập seed \(S\) tác động lên các đỉnh chưa được chọn, và mang tính **dưới mô-đun (submodular)** khi \(0 < \alpha \le 1\).

## 4. Ràng buộc ngân sách

Cho một **ngân sách** \(B > 0\). Một tập seed \(S\) được coi là hợp lệ nếu tổng chi phí không vượt quá ngân sách:

<img width="180" height="85" alt="Ảnh màn hình 2026-02-01 lúc 16 36 46" src="https://github.com/user-attachments/assets/402fe0e9-c3dc-4bcd-86a8-4e34130146c7" />

## 5. Mục tiêu tối ưu

Mục tiêu của bài toán **Revenue Maximization (RM)** là:

<img width="450" height="85" alt="Ảnh màn hình 2026-02-01 lúc 16 37 15" src="https://github.com/user-attachments/assets/b5617ebc-d5d4-419d-991e-b2e10e2001ef" />

Nói cách khác, bài toán yêu cầu lựa chọn một tập người dùng ban đầu (seed set) sao cho:
- Tổng chi phí kích hoạt không vượt quá ngân sách cho phép.
- Doanh thu (mức độ ảnh hưởng kỳ vọng) đạt giá trị lớn nhất.

## 6. Ý nghĩa trong bối cảnh Wikipedia

Trong mạng thảo luận Wikipedia:
- Các đỉnh đại diện cho người dùng tham gia thảo luận.
- Trọng số cạnh phản ánh khả năng ảnh hưởng giữa người dùng.
- Tập seed \(S\) có thể được hiểu là nhóm người dùng được ưu tiên kêu gọi, gợi ý hoặc tác động.



```mermaid
flowchart TD
    START([Bắt đầu]) --> INPUT[/Nhập: graph, nodes, costs, budget, alpha/]
    INPUT --> INIT["S ← ∅, w_sum ← {}, heap ← []"]
    
    INIT --> INIT_LOOP["Với mỗi đỉnh u có cost ≤ budget"]
    INIT_LOOP --> CALC_GAIN["Tính gain(u) = Δ(u|∅)"]
    CALC_GAIN --> PUSH_HEAP["Push (u, gain, cost, iteration=0) vào heap"]
    PUSH_HEAP --> CHECK_MORE{Còn đỉnh?}
    CHECK_MORE -->|Có| INIT_LOOP
    CHECK_MORE -->|Không| MAIN_LOOP
    
    MAIN_LOOP{heap rỗng?}
    MAIN_LOOP -->|Có| FINAL["Tính revenue từ w_sum"]
    MAIN_LOOP -->|Không| POP["u ← pop(heap)"]
    
    POP --> CHECK_BUDGET{"cost(u) > remaining?"}
    CHECK_BUDGET -->|Có| MAIN_LOOP
    CHECK_BUDGET -->|Không| CHECK_FRESH{"iteration = current?"}
    
    CHECK_FRESH -->|Không - Cũ| RECOMPUTE["Tính lại gain(u) từ w_sum"]
    RECOMPUTE --> REPUSH["Push lại u với gain mới"]
    REPUSH --> MAIN_LOOP
    
    CHECK_FRESH -->|Có - Mới| SELECT["S ← S ∪ {u}"]
    SELECT --> UPDATE_BUDGET["remaining -= cost(u)"]
    UPDATE_BUDGET --> UPDATE_WSUM["Cập nhật w_sum[v] += w(u,v)"]
    UPDATE_WSUM --> INC_ITER["iteration++"]
    INC_ITER --> MAIN_LOOP
    
    FINAL --> OUTPUT[/Xuất: S, revenue, total_cost/]
    OUTPUT --> END([Kết thúc])
```
