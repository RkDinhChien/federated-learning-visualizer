# ============================================================
# Passive Label Inference Attack using MixMatch for VFL
# FOR RESEARCH / SECURITY AUDIT PURPOSES ONLY
# ============================================================

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.distributions import Beta
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from typing import Tuple
from PIL import Image

# ──────────────────────────────────────────────────────────────
#  0. VFL Image Split Helper
# ──────────────────────────────────────────────────────────────

def _split_client_half(images: torch.Tensor, side: str = "right") -> torch.Tensor:
    if images.dim() == 3:
        images = images.unsqueeze(0)
    if side == "right":
        return images[:, :, :, 16:]
    elif side == "left":
        return images[:, :, :, :16]
    else:
        raise ValueError(f"side must be 'right' or 'left', got '{side}'")


def _validate_and_convert_image(img, expected_shape=(3, 32, 32)):
    if isinstance(img, torch.Tensor):
        if img.ndim != 3:
            raise ValueError(f"Expected tensor shape (C, H, W), got {img.shape}.")
        if img.max() > 1.0:
            img = img.float() / 255.0
        if img.shape != expected_shape:
            raise ValueError(f"Shape mismatch: expected {expected_shape}, got {img.shape}")
        return img
    elif isinstance(img, Image.Image):
        img_array = np.array(img, dtype=np.float32)
        if img_array.ndim == 2:
            img_array = np.stack([img_array] * 3, axis=-1)
        if img_array.max() > 1.0:
            img_array = img_array / 255.0
        img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).float()
        if img_tensor.shape != expected_shape:
            raise ValueError(f"Shape mismatch: expected {expected_shape}, got {img_tensor.shape}.")
        return img_tensor
    elif isinstance(img, np.ndarray):
        img_array = img.astype(np.float32)
        if img_array.ndim == 3:
            if img_array.shape[0] in [1, 3, 4]:
                img_tensor = torch.from_numpy(img_array).float()
            else:
                if img_array.max() > 1.0:
                    img_array = img_array / 255.0
                img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).float()
        elif img_array.ndim == 2:
            if img_array.max() > 1.0:
                img_array = img_array / 255.0
            img_tensor = torch.from_numpy(img_array).unsqueeze(0).float()
        else:
            raise ValueError(f"Unexpected image shape: {img_array.shape}")
        if img_tensor.shape != expected_shape:
            raise ValueError(f"Shape mismatch: expected {expected_shape}, got {img_tensor.shape}")
        return img_tensor
    else:
        raise TypeError(f"Unsupported image format: {type(img).__name__}.")


# ──────────────────────────────────────────────────────────────
#  1. InferenceHead
# ──────────────────────────────────────────────────────────────

class InferenceHead(nn.Module):
    """
    MLP head appended after a frozen BottomModel.
    Improved architecture với BatchNorm để training ổn định hơn.

    Architecture:
        Linear(128 → 512) → BN → ReLU → Dropout(0.3)
        Linear(512 → 256) → BN → ReLU → Dropout(0.3)
        Linear(256 → 128) → BN → ReLU
        Linear(128 → 10)
    """

    def __init__(
        self,
        embedding_dim: int = 128,
        hidden_dim: int = 512,
        num_classes: int = 10,
        dropout_rate: float = 0.3,
    ):
        super(InferenceHead, self).__init__()

        self.layer1 = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_rate),
        )

        self.layer2 = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.BatchNorm1d(hidden_dim // 2),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_rate),
        )

        self.layer3 = nn.Sequential(
            nn.Linear(hidden_dim // 2, embedding_dim),
            nn.BatchNorm1d(embedding_dim),
            nn.ReLU(inplace=True),
        )

        self.output_layer = nn.Linear(embedding_dim, num_classes)

        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight, nonlinearity="relu")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, embedding: torch.Tensor) -> torch.Tensor:
        x = self.layer1(embedding)
        x = self.layer2(x)
        x = self.layer3(x)
        logits = self.output_layer(x)
        return logits


# ──────────────────────────────────────────────────────────────
#  2. sharpen()
# ──────────────────────────────────────────────────────────────

def sharpen(predictions: torch.Tensor, temperature: float = 0.5) -> torch.Tensor:
    if temperature <= 0:
        raise ValueError(f"temperature must be > 0, got {temperature}")
    sharpened = predictions.pow(1.0 / temperature)
    pseudo_labels = sharpened / (sharpened.sum(dim=1, keepdim=True) + 1e-8)
    return pseudo_labels


# ──────────────────────────────────────────────────────────────
#  3. mixup()
# ──────────────────────────────────────────────────────────────

def mixup(
    x1: torch.Tensor,
    x2: torch.Tensor,
    y1: torch.Tensor,
    y2: torch.Tensor,
    alpha: float = 0.75,
) -> Tuple[torch.Tensor, torch.Tensor]:
    if alpha <= 0:
        raise ValueError(f"alpha must be > 0, got {alpha}")
    dist = Beta(
        torch.tensor(alpha, dtype=torch.float32),
        torch.tensor(alpha, dtype=torch.float32),
    )
    lam = dist.sample().item()
    lam = max(lam, 1.0 - lam)
    x_mixed = lam * x1 + (1.0 - lam) * x2
    y_mixed = lam * y1 + (1.0 - lam) * y2
    return x_mixed, y_mixed


# ──────────────────────────────────────────────────────────────
#  4. generate_auxiliary_labels()
# ──────────────────────────────────────────────────────────────

def generate_auxiliary_labels(
    dataset,
    num_labels: int = 200,   # FIX: tăng từ 40 → 200 (20 per class)
    seed: int = 42,
    balanced: bool = True,   # FIX: lấy đều theo class để tránh bias
) -> Tuple[Tuple[torch.Tensor, torch.Tensor], Tuple[torch.Tensor, torch.Tensor]]:
    """
    Split dataset thành labeled set X và unlabeled set U.

    FIX quan trọng:
    - Tăng num_labels lên 200 (20 per class) thay vì 40 (quá ít)
    - Lấy đều theo class (balanced=True) để tránh class imbalance

    Args:
        dataset    : PyTorch Dataset. Each item is (image, label).
        num_labels : Số labeled samples. Default 200 (20 per class × 10 classes).
        seed       : Random seed.
        balanced   : Nếu True, lấy đều mỗi class.

    Returns:
        X = (images_X, labels_X)
        U = (images_U, labels_U_true)
    """
    np.random.seed(seed)
    torch.manual_seed(seed)

    n_total = len(dataset)

    def _get_label(dataset, idx):
        """Get label without loading full image."""
        if hasattr(dataset, 'targets'):
            return int(dataset.targets[idx])
        else:
            _, lbl = dataset[idx]
            return int(lbl)

    if balanced:
        # Lấy num_labels/10 mẫu từ mỗi class
        num_classes = 10
        per_class   = num_labels // num_classes

        # Group indices by class
        class_indices = {c: [] for c in range(num_classes)}
        for i in range(n_total):
            lbl = _get_label(dataset, i)
            class_indices[lbl].append(i)

        labeled_indices = []
        for c in range(num_classes):
            idxs = np.array(class_indices[c])
            chosen = np.random.choice(idxs, size=min(per_class, len(idxs)), replace=False)
            labeled_indices.extend(chosen.tolist())

        labeled_set   = set(labeled_indices)
        unlabeled_indices = [i for i in range(n_total) if i not in labeled_set]
        unlabeled_indices = np.random.permutation(unlabeled_indices).tolist()
    else:
        all_indices = np.random.permutation(n_total)
        labeled_indices   = all_indices[:num_labels].tolist()
        unlabeled_indices = all_indices[num_labels:].tolist()

    def _collect(indices):
        imgs, labels = [], []
        for idx in indices:
            img, lbl = dataset[int(idx)]
            img = _validate_and_convert_image(img, expected_shape=(3, 32, 32))
            imgs.append(img)
            labels.append(int(lbl))
        return torch.stack(imgs), torch.tensor(labels, dtype=torch.long)

    print(f"[generate_auxiliary_labels] Collecting {len(labeled_indices)} labeled samples (balanced)...")
    images_X, labels_X = _collect(labeled_indices)

    print(f"[generate_auxiliary_labels] Collecting {len(unlabeled_indices)} unlabeled samples...")
    images_U, labels_U_true = _collect(unlabeled_indices)

    print(f"[generate_auxiliary_labels] Done. X: {images_X.shape}, U: {images_U.shape}")
    return (images_X, labels_X), (images_U, labels_U_true)


# ──────────────────────────────────────────────────────────────
#  5. train_inference_head()
# ──────────────────────────────────────────────────────────────

def train_inference_head(
    bottom_model: nn.Module,
    inference_head: nn.Module,
    X: Tuple[torch.Tensor, torch.Tensor],
    U: Tuple[torch.Tensor, torch.Tensor],
    epochs: int = 200,
    lr: float = 1e-3,
    batch_size: int = 64,
    lambda_u: float = 1.0,
    temperature: float = 0.5,
    alpha_mixup: float = 0.75,
    K_augments: int = 2,
    device: str = "cuda",
    warmup_epochs: int = 20,
) -> nn.Module:
    """
    Train InferenceHead dung loop theo unlabeled data.
    Loop chinh chay theo unlabeled_loader (9800 samples),
    labeled data duoc cycle lai - dam bao unlabeled duoc hoc day du.
    """
    bottom_model   = bottom_model.to(device)
    inference_head = inference_head.to(device)

    for param in bottom_model.parameters():
        param.requires_grad_(False)
    bottom_model.eval()

    optimizer = optim.Adam(inference_head.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    ce_loss  = nn.CrossEntropyLoss()
    mse_loss = nn.MSELoss()

    images_X, labels_X = X
    images_U, _        = U
    num_classes        = 10

    # Pre-compute ALL embeddings once (frozen model, save time)
    print("  Pre-computing embeddings...")
    bottom_model.eval()
    with torch.no_grad():
        # Encode labeled
        emb_X_all = []
        for i in range(0, len(images_X), batch_size):
            batch = images_X[i:i+batch_size].to(device)
            emb_X_all.append(bottom_model(_split_client_half(batch)).cpu())
        emb_X_all = torch.cat(emb_X_all, dim=0)  # [200, 128]

        # Encode unlabeled
        emb_U_all = []
        for i in range(0, len(images_U), 256):
            batch = images_U[i:i+256].to(device)
            emb_U_all.append(bottom_model(_split_client_half(batch)).cpu())
        emb_U_all = torch.cat(emb_U_all, dim=0)  # [9800, 128]
    print(f"  Embeddings ready: X={emb_X_all.shape}, U={emb_U_all.shape}")

    # DataLoaders tren embeddings (nhanh hon qua image)
    # Loop chinh chay theo UNLABELED (so luong lon hon)
    labeled_ds   = TensorDataset(emb_X_all, labels_X)
    unlabeled_ds = TensorDataset(emb_U_all)

    unlabeled_loader = DataLoader(unlabeled_ds, batch_size=batch_size, shuffle=True, drop_last=True)
    # Labeled loader se duoc cycle
    labeled_loader   = DataLoader(labeled_ds,   batch_size=min(batch_size, len(images_X)),
                                  shuffle=True, drop_last=False)

    sep = chr(8212) * 60
    print(f"\n{sep}")
    print(f"  MixMatch Training - {epochs} epochs")
    print(f"  Labeled   : {len(images_X)} samples  ({len(labeled_loader)} batches/epoch)")
    print(f"  Unlabeled : {len(images_U)} samples  ({len(unlabeled_loader)} batches/epoch)")
    print(f"  Warmup    : {warmup_epochs} epochs (supervised only)")
    print(f"  Device    : {device}")
    print(f"{sep}\n")

    for epoch in range(1, epochs + 1):
        inference_head.train()

        epoch_loss_x = 0.0
        epoch_loss_u = 0.0
        n_batches    = 0

        labeled_iter = iter(labeled_loader)

        # Loop chinh theo UNLABELED
        for (emb_u_batch,) in unlabeled_loader:
            # Lay labeled batch (cycle)
            try:
                emb_x_batch, labels_x_batch = next(labeled_iter)
            except StopIteration:
                labeled_iter = iter(labeled_loader)
                emb_x_batch, labels_x_batch = next(labeled_iter)

            emb_u_batch    = emb_u_batch.to(device)
            emb_x_batch    = emb_x_batch.to(device)
            labels_x_batch = labels_x_batch.to(device)

            # ── Pseudo-labels cho unlabeled ───────────────────
            with torch.no_grad():
                inference_head.eval()
                probs_u = F.softmax(inference_head(emb_u_batch), dim=1)
                pseudo_u = sharpen(probs_u, temperature).detach()
                inference_head.train()

            # ── Supervised loss ───────────────────────────────
            logits_x = inference_head(emb_x_batch)
            loss_x   = ce_loss(logits_x, labels_x_batch)

            # ── Consistency loss (chi sau warmup) ─────────────
            logits_u = inference_head(emb_u_batch)
            probs_u2 = F.softmax(logits_u, dim=1)
            loss_u   = mse_loss(probs_u2, pseudo_u)

            if epoch <= warmup_epochs:
                total_loss = loss_x
            else:
                total_loss = loss_x + lambda_u * loss_u

            optimizer.zero_grad()
            total_loss.backward()
            nn.utils.clip_grad_norm_(inference_head.parameters(), max_norm=5.0)
            optimizer.step()

            epoch_loss_x += loss_x.item()
            epoch_loss_u += loss_u.item()
            n_batches    += 1

        scheduler.step()

        avg_lx = epoch_loss_x / max(n_batches, 1)
        avg_lu = epoch_loss_u / max(n_batches, 1)

        if epoch % 10 == 0 or epoch <= 5:
            warmup_tag = " [WARMUP]" if epoch <= warmup_epochs else ""
            print(
                f"Epoch {epoch:3d}/{epochs}{warmup_tag} — "
                f"Loss_X: {avg_lx:.4f}, "
                f"Loss_U: {avg_lu:.4f}"
            )

    print(f"\n{sep}")
    print("  Training complete.")
    print(f"{sep}\n")

    return inference_head


# ──────────────────────────────────────────────────────────────
#  6. calculate_asr()
# ──────────────────────────────────────────────────────────────

@torch.no_grad()
def calculate_asr(
    bottom_model: nn.Module,
    inference_head: nn.Module,
    U_images: torch.Tensor,
    U_labels_true: torch.Tensor,
    batch_size: int = 256,
    device: str = "cpu",
) -> float:
    """
    Compute Attack Success Rate (ASR) = accuracy của label inference trên tập U.
    """
    bottom_model   = bottom_model.to(device).eval()
    inference_head = inference_head.to(device).eval()

    loader = DataLoader(
        TensorDataset(U_images, U_labels_true),
        batch_size=batch_size,
        shuffle=False,
    )

    correct = 0
    total   = 0

    for (imgs, labels) in loader:
        imgs   = imgs.to(device)
        labels = labels.to(device)

        emb     = bottom_model(_split_client_half(imgs))
        logits  = inference_head(emb)
        preds   = logits.argmax(dim=1)

        correct += (preds == labels).sum().item()
        total   += labels.size(0)

    asr = correct / total * 100.0

    print(f"\n{'='*50}")
    print(f"  🥷 Attack Success Rate: {asr:.2f}%")
    if asr >= 75.0:
        print("  🎉 BẢO ĐÃ THÀNH CÔNG ĂN CẮP DỮ LIỆU!")
    elif asr >= 40.0:
        print("  ⚠️  Tấn công một phần thành công — cần thêm epochs.")
    else:
        print("  ❌ Tấn công chưa thành công — kiểm tra lại BottomModel.")
    print(f"{'='*50}\n")

    return asr