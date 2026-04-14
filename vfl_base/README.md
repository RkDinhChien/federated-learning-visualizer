# 🚀 Vertical Federated Learning (VFL) Base System

Hệ thống VFL nền tảng được xây dựng trên **Split Learning** với CIFAR-10 dataset, phục vụ cho nghiên cứu học liên kết và an ninh dữ liệu.

## 📁 Cấu Trúc Thư Mục

```
vfl_base/
├── phase1/                    # GIAI ĐOẠN 1: VFL nền tảng (hoàn thành)
│   ├── src/
│   │   ├── dataset.py         # Module CIFAR-10 vertical partition
│   │   ├── client_bao.py      # Client (Bảo) - Bottom Model
│   │   ├── server_chien.py    # Server (Chiến) - Bottom + Top Model
│   │   └── main.py            # Training loop orchestration
│   ├── docs/
│   └── requirements.txt        # Python dependencies
│
├── phase2/                    # GIAI ĐOẠN 2: Malicious Optimizer + Defense (WIP)
│   ├── src/                   # Sẽ chứa code cho Phase 2
│   └── docs/
│
├── README.md                  # File này
└── data/                      # CIFAR-10 cache (tự động tải)
```

---

## 🎯 GIAI ĐOẠN 1: VFL Base System

### Kết Quả Training (Đã Hoàn Thành ✅)

```
🎉 TRAINING COMPLETE
⏱️  Total Time: 89.87 minutes (CPU)
📉 Final Loss: 1.2015
📈 Final Accuracy: 56.97%
📊 Loss Reduction: 0.7384 (38%)
📊 Accuracy Improvement: 30.87%
```

### Cấu Trúc Hệ Thống

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT (Bảo)                          │
│  Input: Right half image (3×32×16)                       │
│  Model: ResNet-18 Bottom Model                           │
│  Output: 128-dim embedding                               │
│  Training: SGD with gradient from server                 │
└──────────────────┬──────────────────────────────────────┘
                   │ Features
                   ↓
┌─────────────────────────────────────────────────────────┐
│                    SERVER (Chiến)                        │
│  Input: Left half image + Client embedding              │
│  Models:                                                 │
│    • Bottom Model: CNN for left half                     │
│    • Top Model: FCNN-4 classifier (10 classes)          │
│  Output: Class predictions + loss                        │
│  Training: Has labels, computes loss & gradients        │
└──────────────────┬──────────────────────────────────────┘
                   │ Gradients
                   ↓
```

### Các Component

#### 1. **dataset.py** - Dataset Module
- **Input**: CIFAR-10 (60K train, 10K test)
- **Processing**: Vertical partition - split image width-wise
  - Half A (Server): Left [0:16]
  - Half B (Client): Right [16:32]
- **Output**: DataLoader with partitioned images

#### 2. **client_bao.py** - Client Module
- **BottomModel**: Modified ResNet-18
  - Input: 3×32×16 (right half image)
  - Layers: ResNet18 layers + FC projection
  - Output: 128-dim embedding
- **ClientWorker**: Training orchestration
  - `forward(x_client)`: Process half image
  - `backward(gradient)`: Update weights with server gradient

#### 3. **server_chien.py** - Server Module
- **BottomModelServer**: Simple CNN
  - Input: 3×32×16 (left half image)
  - Output: 128-dim embedding
- **TopModel**: FCNN-4 classifier
  - Input: 256-dim (concatenated embeddings)
  - Hidden: 256 → 256 → 128 with BN, Dropout
  - Output: 10 class logits
- **ServerCoordinator**: Training orchestration
  - `forward_and_loss()`: Compute loss
  - `compute_gradients_and_update()`: Update and return gradient

#### 4. **main.py** - Training Loop
- **Configuration**:
  - Batch Size: 32
  - Learning Rate: 0.01
  - Epochs: 10
  - Embedding Dim: 128
  - Device: CUDA (if available) or CPU
- **Split Learning Loop**:
  1. Client: Forward pass → embedding
  2. Server: Forward + loss computation
  3. Server: Backward → gradient computation
  4. Client: Backward with server gradient
  5. Update weights both sides

---

## 🚀 Quick Start

### Yêu Cầu
- Python 3.8+
- PyTorch 2.0+
- CUDA 11.8 (optional, for GPU acceleration)

### Cài Đặt

```bash
# 1. Tạo virtual environment
cd phase1
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 2. Cài dependencies
pip install -r requirements.txt

# 3. Chạy training
python src/main.py
```

### Kết Quả Mong Đợi

```
Loading CIFAR-10 dataset...
✅ Dataset loaded! Train: 1563 batches, Test: 313 batches

Initializing models...
✅ Models initialized!

Starting training...

Epoch 1/10 | Batch 500/1563 | Loss: 2.1396 | Acc: 19.41%
Epoch 1/10 | Batch 1000/1563 | Loss: 2.0228 | Acc: 23.18%
...
✅ Epoch 1/10 Summary - Loss: 1.9399 | Accuracy: 26.10%

Epoch 2/10 | Batch 500/1563 | Loss: 1.7319 | Acc: 34.19%
...

[Training continues...]

🎉 TRAINING COMPLETE
Final Loss: 1.2015
Final Accuracy: 56.97%
```

---

## 📊 Metrics & Monitoring

### Loss Progression
- Epoch 1: 1.9399
- Epoch 5: 1.3948
- Epoch 10: 1.2015
- **Convergence**: ✅ Smooth downward trend

### Accuracy Progression
- Epoch 1: 26.10%
- Epoch 5: 48.76%
- Epoch 10: 56.97%
- **Improvement**: ✅ Steady increase

---

## 🔧 Tùy Chỉnh

### Thay đổi Hyperparameters

Trong `src/main.py`, sửa các dòng:

```python
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
BATCH_SIZE = 32          # Giảm nếu GPU OOM
LEARNING_RATE = 0.01     # Tăng/giảm tốc độ hội tụ
NUM_EPOCHS = 10          # Số epoch training
EMBEDDING_DIM = 128      # Kích thước embedding
```

### Sử Dụng GPU

Code sẽ tự động dùng GPU nếu có. Kiểm tra:

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

---

## 🐛 Troubleshooting

### Error: "No module named 'torch'"
```bash
pip install torch torchvision
```

### CUDA Out of Memory
```python
# Giảm BATCH_SIZE trong main.py
BATCH_SIZE = 16  # Thay từ 32
```

### Loss không giảm
```python
# Thử learning rate khác
LEARNING_RATE = 0.001  # Nhỏ hơn
```

### CIFAR-10 download bị stuck
```bash
# Xóa cache và chạy lại
rm -rf ~/.cache/torch
python src/main.py
```

---

## 📈 Kỳ Vọng Tiếp Theo

### GIAI ĐOẠN 2: Malicious Optimizer + Defense
- **Label Stealing Attack**: Bảo sẽ viết code ăn cắp nhãn từ Server gradient
- **Byzantine Defense**: Chiến sẽ implement Trimmed Mean, Median aggregation
- **Comparison**: So sánh hiệu suất VFL normal vs VFL under attack

---

## 📝 References

- **Split Learning**: ["Distributed deep learning without sharing raw data"](https://arxiv.org/abs/1812.03224)
- **Federated Learning**: [Google Federated Learning whitepaper](https://federated.withgoogle.com/)
- **CIFAR-10**: [CIFAR-10 dataset](https://www.cs.toronto.edu/~kriz/cifar.html)

---

## ✅ Checklist

- [x] Dataset module (vertical CIFAR-10 partition)
- [x] Client Bottom Model (ResNet-18)
- [x] Server Bottom + Top Model (CNN + FCNN-4)
- [x] Training loop with Split Learning
- [x] Loss decreasing (1.94 → 1.20)
- [x] Accuracy increasing (26% → 57%)
- [x] Documentation
- [ ] Phase 2: Malicious Optimizer (pending)
- [ ] Phase 2: Defense mechanisms (pending)

---

## 👥 Đội Ngũ

- **Bảo**: Client implementation (Bottom Model)
- **Chiến**: Server implementation (Bottom + Top Model)
- **Hệ thống**: Training orchestration & monitoring

---

**Phiên bản**: 1.0 (GIAI ĐOẠN 1 Hoàn Thành) ✅
**Ngày cập nhật**: April 14, 2026
**Trạng thái**: Ready for Phase 2
