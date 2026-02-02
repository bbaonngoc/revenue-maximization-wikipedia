# BÁO CÁO DỰ ÁN

## Thông tin dự án

| Thông tin | Chi tiết |
|-----------|----------|
| **Tên đề tài** | Tối đa hóa doanh thu trên mạng thảo luận Wikipedia |
| **Sinh viên thực hiện** | Nguyễn Minh Sang, Vũ Thị Diệu Linh, Đỗ Trịnh Lệ Quyên, Tạ Vương Bảo Ngọc |
| **MSSV** | *(để trống)* |
| **Lớp** | *(để trống)* |
| **GVHD** | *(để trống)* |

---

## Mục lục

1. [Mô tả dữ liệu](#1-mô-tả-dữ-liệu)
2. [Các phương pháp giải quyết bài toán](#2-các-phương-pháp-giải-quyết-bài-toán)
3. [Kiến trúc hệ thống](#3-kiến-trúc-hệ-thống)
4. [Thực nghiệm và kết quả](#4-thực-nghiệm-và-kết-quả)
5. [Kết luận](#5-kết-luận)
6. [Tài liệu tham khảo](#6-tài-liệu-tham-khảo)
7. [Phụ lục: Hướng dẫn chạy dự án](#7-phụ-lục-hướng-dẫn-chạy-dự-án)

---

## 1. Mô tả dữ liệu

### 1.1 Nguồn dữ liệu

Dự án sử dụng bộ dữ liệu **Wiki-Talk** từ Stanford Large Network Dataset Collection (SNAP).

| Thuộc tính | Giá trị |
|------------|---------|
| **Nguồn** | [SNAP - Wiki-Talk](https://snap.stanford.edu/data/wiki-Talk.html) |
| **Loại đồ thị** | Có hướng (Directed Graph) |
| **Số đỉnh gốc** | 2,394,385 |
| **Số cạnh gốc** | 5,021,410 |
| **Số đỉnh sau lọc** | 49,967 |
| **Số cạnh sau lọc** | 1,556,613 |

### 1.2 Ý nghĩa dữ liệu

- Mỗi **đỉnh** đại diện cho một người dùng Wikipedia
- Mỗi **cạnh có hướng** (u → v) nghĩa là người dùng u đã chỉnh sửa trang thảo luận của người dùng v
- Đồ thị phản ánh mạng lưới tương tác và ảnh hưởng giữa các users

### 1.3 Tiền xử lý dữ liệu

1. **Lọc đỉnh theo degree**: Chỉ giữ lại các đỉnh có bậc (in + out degree) ≥ 5
2. **Giới hạn số lượng**: Lấy tối đa 50,000 đỉnh có degree cao nhất
3. **Gán trọng số cạnh**: w(u,v) ~ Uniform(0, 1) với seed cố định để tái tạo kết quả

---

## 2. Các phương pháp giải quyết bài toán

### 2.1 Ý tưởng chính

**Bài toán**: Cho ngân sách B, tìm tập seed S sao cho tối đa hóa doanh thu:

$$f(S) = \sum_{v \notin S} \left( \sum_{u \in S} w(u,v) \right)^\alpha$$

trong đó:
- α ∈ (0, 1] là tham số lợi suất giảm dần (diminishing returns)
- w(u,v) là trọng số cạnh từ u đến v

**Ràng buộc**: Tổng chi phí của S không vượt quá ngân sách B:

$$c(S) = \sum_{u \in S} c(u) \leq B$$

**Chi phí đỉnh**:

$$c(u) = 1 - e^{-0.2\sqrt{\sum_{(u,v) \in E} w(u,v)}}$$

### 2.2 Tổng quan Pipeline

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Dữ liệu thô   │───▶│   Tiền xử lý     │───▶│   Đồ thị đã    │
│   Wiki-Talk     │    │   (preprocess)   │    │   lọc + trọng  │
└─────────────────┘    └──────────────────┘    │   số           │
                                               └────────┬────────┘
                                                        │
                       ┌────────────────────────────────▼────────┐
                       │           Thuật toán CELF               │
                       │  (Cost-Effective Lazy Forward)          │
                       └────────────────────────────────┬────────┘
                                                        │
                       ┌────────────────────────────────▼────────┐
                       │         Tập seed tối ưu S*              │
                       │         + Doanh thu f(S*)               │
                       └─────────────────────────────────────────┘
```

### 2.3 Thuật toán Greedy (Baseline)

**Ý tưởng**: Tại mỗi bước, chọn đỉnh có tỉ lệ marginal gain / cost cao nhất.

**Pseudocode**:
```
S ← ∅
while budget còn:
    for each node u ∉ S với cost(u) ≤ remaining_budget:
        Δ(u|S) ← f(S ∪ {u}) - f(S)    // Marginal gain
        ratio(u) ← Δ(u|S) / cost(u)
    u* ← argmax ratio(u)
    S ← S ∪ {u*}
return S
```

**Độ phức tạp**: O(k × n²) với n = số đỉnh, k = số đỉnh được chọn
- Mỗi vòng duyệt n đỉnh, mỗi lần tính f(S) mất O(n)
- Rất chậm với đồ thị lớn

### 2.4 Thuật toán CELF (Cost-Effective Lazy Forward)

**Ý tưởng**: Khai thác tính chất **submodular** - marginal gain chỉ **giảm** khi S mở rộng.

**Cải tiến so với Greedy**:

| Kỹ thuật | Mô tả | Lợi ích |
|----------|-------|--------|
| **Lazy Evaluation** | Dùng max-heap, chỉ tính lại gain khi cần | Giảm số lần tính |
| **Incremental w_sum** | Duy trì `w_sum[v] = Σ_{u∈S} w(u,v)` | O(degree) thay vì O(n) |
| **Marginal Gain trực tiếp** | Không gọi f(S), tính Δ từ w_sum | Tránh duyệt toàn bộ đồ thị |

**Công thức Marginal Gain**:
$$\Delta(u|S) = \sum_{v: u \to v, v \notin S} \left[ (w\_sum[v] + w(u,v))^\alpha - w\_sum[v]^\alpha \right]$$

**Pseudocode CELF**:
```
1. Khởi tạo heap với gain ban đầu cho mỗi đỉnh
2. while heap không rỗng:
      u ← pop(heap)  // đỉnh có ratio cao nhất
      if gain(u) đã cũ:
          Tính lại gain(u) từ w_sum
          push(heap, u)
      else:
          S ← S ∪ {u}
          Cập nhật: w_sum[v] += w(u,v) cho mọi v mà u → v
```

### 2.5 So sánh độ phức tạp

| Thuật toán | Khởi tạo | Mỗi vòng chọn | Tổng | Ký hiệu |
|------------|----------|---------------|------|--------|
| Greedy naive | O(n²) | O(n²) | O(k × n²) | n = đỉnh |
| **CELF tối ưu** | O(n × d̄) | O(d̄ + R) | **O(n × d̄ + k × R)** | d̄ = bậc TB, R = recompute |

**Trong thực tế**: 
- Với n = 50,000 đỉnh: Greedy mất **hàng giờ**, CELF mất **vài giây**
- R (số lần tính lại) thường rất nhỏ nhờ lazy evaluation

---

## 3. Kiến trúc hệ thống

### 3.1 Cấu trúc thư mục

```
revenue-maximization/
├── config.py              # Cấu hình tham số (BUDGET, ALPHA, SEED,...)
├── main.py                # Điểm khởi chạy chính
├── celf.py                # Thuật toán CELF tối ưu
├── greedy.py              # Thuật toán Greedy (baseline)
├── utils.py               # Các hàm tiện ích
├── preprocess.py          # Tiền xử lý dữ liệu
├── verify_correctness.py  # Kiểm tra độ chính xác
├── REPORT.md              # Báo cáo dự án
└── data/
    ├── wiki-Talk.txt          # Dữ liệu gốc
    └── wiki-talk-filtered.txt # Dữ liệu đã lọc
```

### 3.2 Mô tả các module

| Module | Chức năng |
|--------|-----------|
| `config.py` | Tập trung tham số: B, α, SEED, đường dẫn dữ liệu |
| `utils.py` | load_graph, compute_node_costs, compute_marginal_gain |
| `celf.py` | Thuật toán CELF với incremental w_sum |
| `main.py` | Điều phối chạy thử nghiệm |

---

## 4. Thực nghiệm và kết quả

### 4.0 Môi trường thực nghiệm

| Thành phần | Chi tiết |
|------------|----------|
| **Hệ điều hành** | macOS |
| **CPU** | Intel Core |
| **RAM** | ≥ 4GB |
| **Ngôn ngữ** | Python 3.8+ |
| **Thư viện** | Python Standard Library |

### 4.1 Cấu hình thử nghiệm

| Tham số | Giá trị | Mô tả |
|---------|---------|-------|
| **α (alpha)** | 0.5 | Tham số diminishing returns (căn bậc 2) |
| **SEED** | 42 | Seed cho random để tái tạo kết quả |
| **Số đỉnh** | 49,967 | Sau khi lọc từ 2.4M đỉnh |
| **Số cạnh** | 1,556,613 | Sau khi lọc từ 5M cạnh |

### 4.2 Kết quả với các giá trị ngân sách B

| B | \|S\| | Chi phí | Doanh thu | Thời gian (s) |
|---|-------|---------|-----------|---------------|
| 1 | 1 | 1.0000 | 4,539.28 | 0.36 |
| 3 | 3 | 2.9960 | 10,678.40 | 1.21 |
| 5 | 5 | 4.9935 | 14,561.23 | 1.45 |
| 10 | 10 | 9.9987 | 19,701.86 | 1.60 |
| 20 | 20 | 19.9935 | 27,682.21 | 1.91 |
| 30 | 30 | 29.9856 | 33,573.35 | 2.08 |
| 40 | 40 | 39.9713 | 38,332.79 | 2.24 |
| 50 | 50 | 49.9523 | 42,286.54 | 2.45 |

### 4.3 Kiểm tra độ chính xác

| B | Revenue (cache) | Revenue (verify) | Sai số | Kết quả |
|---|-----------------|------------------|--------|---------|
| 0.3 | 4.5814 | 4.5814 | 0.0000 | ✓ |
| 0.5 | 16.4026 | 16.4026 | 0.0000 | ✓ |
| 1.0 | 4539.2809 | 4539.2809 | 0.0000 | ✓ |
| 3.0 | 10678.4034 | 10678.4034 | 0.0000 | ✓ |

**Kết luận**: Thuật toán CELF tối ưu cho kết quả **chính xác 100%** so với tính toán từ công thức gốc.

### 4.4 Nhận xét

1. **Hiệu ứng Submodular**: Khi B tăng, số lượng seed |S| tăng, nhưng doanh thu tăng **chậm dần** do tính chất diminishing returns của hàm mục tiêu.

2. **Thời gian chạy ổn định**: Dù B tăng từ 1 đến 50, thời gian chỉ tăng từ 0.36s lên 2.45s - cho thấy thuật toán CELF hiệu quả.

3. **Chi phí sát ngân sách**: Thuật toán tận dụng gần hết ngân sách (ví dụ: B=50, chi phí=49.95).

4. **Scalability**: Thuật toán xử lý được đồ thị ~50K đỉnh, 1.5M cạnh trong vài giây.

---

## 5. Kết luận

### 5.1 Kết quả đạt được

- Triển khai thành công thuật toán **CELF tối ưu** cho bài toán tối đa hóa doanh thu
- Áp dụng kỹ thuật **incremental w_sum** để tăng tốc tính toán
- Đạt **độ chính xác 100%** khi so sánh với công thức gốc
- Thời gian chạy **nhanh** trên đồ thị lớn

### 5.2 Hạn chế

- Trọng số cạnh được gán ngẫu nhiên
- Chưa so sánh với các phương pháp khác (Influence Maximization, PageRank-based,...)

### 5.3 Hướng phát triển

- Sử dụng mô hình Weighted Cascade: w(u,v) = 1/in_degree(v)

---

## 6. Tài liệu tham khảo

1. **Kempe, D., Kleinberg, J., & Tardos, É.** (2003). Maximizing the Spread of Influence through a Social Network. *KDD '03*.

2. **Leskovec, J., Krause, A., Guestrin, C., Faloutsos, C., VanBriesen, J., & Glance, N.** (2007). Cost-effective Outbreak Detection in Networks. *KDD '07*.

3. **SNAP Dataset**: [Stanford Wiki-Talk Network](https://snap.stanford.edu/data/wiki-Talk.html)

4. **Goyal, A., Lu, W., & Lakshmanan, L. V.** (2011). CELF++: Optimizing the Greedy Algorithm for Influence Maximization in Social Networks. *WWW '11*.

---

## 7. Phụ lục: Hướng dẫn chạy dự án

### 7.1 Yêu cầu hệ thống

- Python 3.8+
- RAM: ≥ 4GB
- Disk: ≥ 500MB

### 7.2 Cài đặt

```bash
# Clone repository
git clone <repository-url>
cd revenue-maximization

# Không cần cài thư viện bên ngoài (chỉ dùng Python standard library)
```

### 7.3 Chuẩn bị dữ liệu

```bash
# Tải dữ liệu Wiki-Talk từ SNAP
wget https://snap.stanford.edu/data/wiki-Talk.txt.gz
gunzip wiki-Talk.txt.gz
mv wiki-Talk.txt data/

# Tiền xử lý dữ liệu
python3 preprocess.py
```

### 7.4 Chạy thử nghiệm

```bash
# Cấu hình tham số trong config.py
# Ví dụ: BUDGET = 10.0, ALPHA = 0.5

# Chạy thuật toán CELF
python3 main.py
```

### 7.5 Kết quả mẫu

```
=== CẤU HÌNH ===
Ngân sách B = 10.0
Alpha = 0.5
Seed = 42

Đang tải đồ thị...
Đã tải đồ thị: 49967 đỉnh, 1556613 cạnh

--- THUẬT TOÁN CELF ---
...
Kích thước tập seed: 10
Tổng chi phí: 9.9987 / Ngân sách: 10.0000
Doanh thu: 19701.8562
```

### 7.6 Kiểm tra độ chính xác

```bash
python3 verify_correctness.py
```

---

*Báo cáo được tạo tự động - Ngày 02/02/2026*
