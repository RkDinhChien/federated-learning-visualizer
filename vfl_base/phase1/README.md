# GIAI ĐOẠN 1: VFL Base System - Source Code

Bốn file Python chính cho hệ thống VFL nền tảng:

## 📂 Files

### 1. **dataset.py** (115 lines)
Module tải và xử lý CIFAR-10 với vertical partition.

```python
from vfl_base.phase1.src.dataset import VFLCIFARDataset, get_dataloaders

# Tải dataset
train_loader, test_loader = get_dataloaders(batch_size=32)
```

**Features**:
- Tự động tải CIFAR-10 (lần đầu ~5 phút)
- Vertical partition: Split ảnh theo chiều width
- Return: `(half_A, half_B, label)` cho mỗi sample
- Support augmentation: RandomCrop, HorizontalFlip, Normalization

---

### 2. **client_bao.py** (200 lines)
Client implementation - Bảo.

```python
from vfl_base.phase1.src.client_bao import ClientWorker, BottomModel

# Khởi tạo Client
client = ClientWorker(embedding_dim=128, learning_rate=0.01, device='cuda')

# Forward
embedding = client.forward(half_B_data)

# Backward
client.backward(gradient_from_server)
```

**Components**:
- **BottomModel**: Modified ResNet-18
  - Input: 3×32×16 (right half image)
  - Output: 128-dim embedding
- **ClientWorker**: Training orchestration
  - `forward()`: Process image, return embedding
  - `backward()`: Receive gradient, update weights
  - Optimizer: SGD

---

### 3. **server_chien.py** (250 lines)
Server implementation - Chiến.

```python
from vfl_base.phase1.src.server_chien import ServerCoordinator, TopModel, BottomModelServer

# Khởi tạo Server
server = ServerCoordinator(embedding_dim=128, learning_rate=0.01, device='cuda')

# Forward + Loss
loss, logits = server.forward_and_loss(half_A, client_embedding, labels)

# Backward + Gradient
gradient_for_client = server.compute_gradients_and_update()
```

**Components**:
- **BottomModelServer**: Simple CNN
  - Input: 3×32×16 (left half image)
  - Output: 128-dim embedding
- **TopModel**: FCNN-4 classifier
  - Input: 256-dim (concatenated embeddings)
  - Output: 10-class logits
- **ServerCoordinator**: Orchestration
  - Has labels
  - Computes loss (CrossEntropy)
  - Generates gradient for Client

---

### 4. **main.py** (350 lines)
Training loop orchestration.

```bash
python main.py
```

**Flow**:
1. Load CIFAR-10 dataset
2. Initialize Client + Server models
3. For each epoch:
   - For each batch:
     - Client forward → embedding
     - Server forward + loss
     - Server backward → gradient
     - Client backward with gradient
4. Print metrics per epoch
5. Final summary with loss & accuracy

**Configuration**:
```python
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
BATCH_SIZE = 32
LEARNING_RATE = 0.01
NUM_EPOCHS = 10
EMBEDDING_DIM = 128
```

---

## ⚡ Quick Run

```bash
# 1. Install dependencies
pip install -r ../requirements.txt

# 2. Run training
python main.py

# 3. Expected output
# Epoch 1/10 Summary - Loss: 1.9399 | Accuracy: 26.10%
# Epoch 2/10 Summary - Loss: 1.6795 | Accuracy: 36.30%
# ...
# Epoch 10/10 Summary - Loss: 1.2015 | Accuracy: 56.97%
```

---

## 🎯 Architecture

```
CIFAR-10 Dataset (3×32×32)
       ↓
  Vertical Split
  /            \
 /              \
Left (3×32×16)   Right (3×32×16)
   ↓                 ↓
Server.Bottom   Client.Bottom
CNN (128-dim)   ResNet-18 (128-dim)
   ↓                 ↓
   └────────┬────────┘
            ↓
      Concatenate (256-dim)
            ↓
        Server.Top
      FCNN-4 (10-class)
            ↓
        CrossEntropy Loss
            ↓
       Backpropagation
      /             \
  Server Update   Gradient to Client
                      ↓
                Client Update
```

---

## 📊 Expected Results

| Metric | Epoch 1 | Epoch 10 | Change |
|--------|---------|----------|--------|
| Loss | 1.94 | 1.20 | ↓ 38% |
| Accuracy | 26.10% | 56.97% | ↑ 31% |
| Convergence | Starting | Stable | ✅ |

---

## 🔧 Customization

### Change Embedding Dimension
```python
# main.py line: EMBEDDING_DIM = 128
EMBEDDING_DIM = 256  # Larger embeddings
```

### Change Learning Rate
```python
# main.py line: LEARNING_RATE = 0.01
LEARNING_RATE = 0.001  # Slower learning
```

### Use Different Batch Size
```python
# main.py line: BATCH_SIZE = 32
BATCH_SIZE = 64  # Larger batches
```

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| CUDA OOM | Reduce BATCH_SIZE to 16 |
| Slow training | Use GPU (CUDA) or reduce epochs |
| Loss doesn't decrease | Try different LEARNING_RATE |
| Import error | Ensure all 4 files in same directory |

---

## ✅ Files Checklist

- [x] dataset.py - CIFAR-10 vertical partition
- [x] client_bao.py - ResNet-18 Bottom Model
- [x] server_chien.py - CNN Bottom + FCNN-4 Top
- [x] main.py - Training orchestration

**Status**: ✅ Phase 1 Complete - Ready for Phase 2
