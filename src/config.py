"""
Cấu hình tham số cho dự án Tối đa hoá Doanh thu.
Thay đổi các giá trị tại đây để áp dụng cho toàn bộ dự án.
"""

# ================== THAM SỐ CHÍNH ==================

# Ngân sách tối đa B - thay đổi giá trị này để thử nghiệm
BUDGET = 40.0

# Tham số lợi suất giảm dần alpha ∈ (0, 1]
# α = 0.5 là giá trị phổ biến (căn bậc 2)
ALPHA = 0.5

# Seed ngẫu nhiên để tái tạo kết quả
SEED = 42

# ================== TIỀN XỬ LÝ ==================

# Bậc tối thiểu của đỉnh để giữ lại khi lọc
MIN_DEGREE = 5

# Số đỉnh tối đa sau khi lọc
MAX_NODES = 50000

# ================== ĐƯỜNG DẪN ==================

import os

# Thư mục gốc của dự án (parent của src/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DATA_PATH = os.path.join(DATA_DIR, "wiki-Talk.txt")
FILTERED_DATA_PATH = os.path.join(DATA_DIR, "wiki-talk-filtered.txt")
