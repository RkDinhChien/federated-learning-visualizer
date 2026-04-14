# HƯỚNG DẪN TẠO MÁY ẢO VMWARE CHO ĐỒ ÁN

## PHẦN 1: CHUẨN BỊ

### 1.1. Yêu cầu Hệ thống
- **VMware Workstation/Fusion:** Version 16+ hoặc VMware Player (Free)
- **Dung lượng USB:** Tối thiểu 16GB (khuyến nghị 32GB)
- **RAM máy host:** Tối thiểu 8GB (để chạy VM 4GB)
- **Disk space:** ~15GB cho VM image

### 1.2. Download VMware
**Windows:**
- VMware Workstation Pro: https://www.vmware.com/products/workstation-pro/workstation-pro-evaluation.html
- VMware Player (Free): https://www.vmware.com/products/workstation-player.html

**macOS:**
- VMware Fusion: https://www.vmware.com/products/fusion.html

### 1.3. Download Ubuntu ISO
- **Ubuntu 22.04 LTS Desktop:** https://ubuntu.com/download/desktop
- File: `ubuntu-22.04.3-desktop-amd64.iso` (~4.7GB)

---

## PHẦN 2: TẠO MÁY ẢO

### 2.1. Cấu hình VM
```
Hệ điều hành: Ubuntu 22.04 LTS Desktop
CPU: 2 cores
RAM: 4GB (4096 MB)
Disk: 40GB (dynamically allocated)
Network: NAT (default)
```

### 2.2. Các bước tạo VM trong VMware

**Bước 1: Tạo Virtual Machine mới**
1. Mở VMware Workstation/Fusion
2. File → New Virtual Machine
3. Chọn "Typical" configuration
4. Next

**Bước 2: Chọn ISO**
1. Installer disc image file (iso): Browse → chọn file `ubuntu-22.04.3-desktop-amd64.iso`
2. Next

**Bước 3: Cấu hình thông tin**
```
Full name: FL Demo
Username: fldemo
Password: 123456  (hoặc password khác, GHI CHÚ LẠI)
```
3. Next

**Bước 4: Đặt tên VM**
```
Virtual machine name: Federated_Learning_Demo
Location: Chọn thư mục lưu (ví dụ: Documents/Virtual Machines/)
```
4. Next

**Bước 5: Disk size**
```
Maximum disk size: 40 GB
○ Store virtual disk as a single file
```
5. Next

**Bước 6: Customize Hardware**
1. Click "Customize Hardware"
2. Thiết lập:
   - Memory: 4096 MB
   - Processors: 2 cores
   - Network Adapter: NAT
   - Sound Card: Remove (không cần)
   - Printer: Remove (không cần)
3. Close → Finish

**Bước 7: Cài đặt Ubuntu**
VM sẽ tự động boot và cài đặt Ubuntu (mất ~20-30 phút)

### 2.3. Sau khi cài xong Ubuntu

**Đăng nhập:**
- Username: `fldemo`
- Password: `123456`

**Cập nhật hệ thống:**
```bash
sudo apt update
sudo apt upgrade -y
```

**Cài VMware Tools (để copy/paste, shared folder):**
1. VM menu → Install VMware Tools
2. Trong Ubuntu, mở terminal:
```bash
sudo apt install open-vm-tools open-vm-tools-desktop -y
sudo reboot
```

---

## PHẦN 3: CÀI ĐẶT HỆ THỐNG DEMO

### 3.1. Cài đặt Node.js và npm

```bash
# Cài Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Kiểm tra version
node --version  # v20.x.x
npm --version   # 10.x.x
```

### 3.2. Cài đặt Git

```bash
sudo apt install git -y
git --version
```

### 3.3. Clone Project từ GitHub

```bash
# Tạo thư mục projects
mkdir -p ~/projects
cd ~/projects

# Clone repository
git clone https://github.com/pengj97/LPA.git
cd LPA

# Hoặc nếu repo private, dùng HTTPS với token
# git clone https://ghp_YOUR_TOKEN@github.com/pengj97/LPA.git
```

### 3.4. Cài đặt Dependencies

```bash
# Cài đặt packages
npm install

# Có thể mất 5-10 phút
```

### 3.5. Build Production

```bash
# Build cho production
npm run build

# Nếu build thành công, sẽ thấy:
# ✓ Compiled successfully
# Creating an optimized production build...
```

### 3.6. Test chạy

```bash
# Chạy dev server để test
npm run start-dev

# Mở browser: http://localhost:3000
# Kiểm tra tất cả pages hoạt động:
# - Homepage
# - /topology
# - /attack-demo
# - /aggregation-defense
# - /compare
```

**Nếu mọi thứ hoạt động → Ctrl+C để dừng server**

---

## PHẦN 4: TẠO SCRIPT TỰ ĐỘNG KHỞI ĐỘNG

### 4.1. Tạo startup script

```bash
cd ~/projects/LPA

# Tạo script khởi động
cat > start-demo.sh << 'EOF'
#!/bin/bash

# Federated Learning Demo Auto-Start Script
echo "======================================"
echo "Federated Learning Demo Starting..."
echo "======================================"

cd ~/projects/LPA

# Kill any existing process on port 3000
lsof -ti:3000 | xargs kill -9 2>/dev/null

# Start the application
npm run dev &

# Wait for server to start
echo ""
echo "Waiting for server to start..."
sleep 10

# Open browser
xdg-open http://localhost:3000 2>/dev/null

echo ""
echo "======================================"
echo "✅ Demo is running on http://localhost:3000"
echo "======================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Keep script running
wait
EOF

# Cấp quyền execute
chmod +x start-demo.sh
```

### 4.2. Tạo Desktop Shortcut

```bash
# Tạo .desktop file
cat > ~/Desktop/FL-Demo.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=FL Demo
Comment=Federated Learning Visualization Demo
Exec=gnome-terminal -- bash -c "cd ~/projects/LPA && ./start-demo.sh; exec bash"
Icon=folder
Terminal=true
Categories=Development;
EOF

# Cấp quyền
chmod +x ~/Desktop/FL-Demo.desktop

# Trust the launcher (Ubuntu 22.04)
gio set ~/Desktop/FL-Demo.desktop metadata::trusted true
```

### 4.3. Auto-start khi boot (Optional)

```bash
# Tạo autostart entry
mkdir -p ~/.config/autostart

cat > ~/.config/autostart/fl-demo.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=FL Demo Auto Start
Comment=Start FL Demo on login
Exec=gnome-terminal -- bash -c "cd ~/projects/LPA && ./start-demo.sh; exec bash"
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
```

---

## PHẦN 5: TẠO FILE HƯỚNG DẪN SỬ DỤNG

### 5.1. Tạo README trên Desktop

```bash
cat > ~/Desktop/HUONG_DAN_SU_DUNG.txt << 'EOF'
=====================================================
HƯỚNG DẪN SỬ DỤNG FEDERATED LEARNING DEMO
Đồ án IE105 - Tìm hiểu Byzantine Attacks trong FL
=====================================================

THÔNG TIN ĐĂNG NHẬP:
--------------------
Username: fldemo
Password: 123456

CÁCH KHỞI ĐỘNG DEMO:
--------------------
Cách 1: Double-click icon "FL Demo" trên Desktop

Cách 2: Mở Terminal và chạy:
  cd ~/projects/LPA
  ./start-demo.sh

Cách 3: Chạy thủ công:
  cd ~/projects/LPA
  npm run dev

TRUY CẬP WEB DEMO:
------------------
URL: http://localhost:3000

CÁC TRANG CHÍNH:
----------------
1. Homepage (/)
   - Giới thiệu tổng quan
   - Onboarding guide

2. Topology (/topology)
   - Sơ đồ mạng FL
   - 10 workers + 1 server
   - Biểu đồ training

3. Attack Demo (/attack-demo)
   - Demo 4 loại tấn công:
     * Label Flipping
     * Furthest Label
     * Gradient Scaling  
     * Sign Flipping
   - Animation data transformation

4. Aggregation Defense (/aggregation-defense)
   - So sánh 5 aggregators:
     * mean (yếu)
     * trimmed_mean
     * CC (τ=0.3)
     * LFighter
     * FABA (mạnh nhất)

5. Compare (/compare)
   - So sánh nhiều experiments
   - Charts overlay
   - Performance table

DATASET:
--------
- SR_MNIST: 60,000 training samples
- 10 workers (9 honest + 1 Byzantine)
- 200 rounds training
- 20,000 iterations

TROUBLESHOOTING:
----------------
Nếu gặp lỗi "port 3000 already in use":
  lsof -ti:3000 | xargs kill -9
  npm run dev

Nếu cần rebuild:
  cd ~/projects/LPA
  rm -rf .next
  npm run build

Xem logs:
  cd ~/projects/LPA
  cat logs/app.log

LIÊN HỆ:
--------
GitHub: https://github.com/pengj97/LPA
Vercel: https://federated-learning-visualizer.vercel.app

=====================================================
EOF
```

---

## PHẦN 6: DỌN DẸP VÀ TỐI ƯU VM

### 6.1. Xóa files không cần thiết

```bash
# Xóa cache
sudo apt clean
sudo apt autoremove -y

# Xóa npm cache
npm cache clean --force

# Xóa browser cache
rm -rf ~/.cache/*

# Xóa temp files
sudo rm -rf /tmp/*
```

### 6.2. Giảm kích thước VM

```bash
# Tắt VM
sudo shutdown -h now
```

**Trong VMware:**
1. VM → Settings → Hard Disk
2. Utilities → Defragment (nếu Windows host)
3. Utilities → Compact

---

## PHẦN 7: XUẤT VM VÀ NỘP

### 7.1. Shutdown VM

Trong VMware:
- VM → Power → Shut Down Guest
- Hoặc trong Ubuntu: `sudo shutdown -h now`

### 7.2. Tìm files VM

**Windows:**
```
C:\Users\[YourName]\Documents\Virtual Machines\Federated_Learning_Demo\
```

**macOS:**
```
~/Documents/Virtual Machines/Federated_Learning_Demo.vmwarevm/
```

**Files quan trọng:**
- `*.vmx` - VM configuration file (QUAN TRỌNG)
- `*.vmdk` - Virtual disk files (QUAN TRỌNG)
- `*.nvram` - BIOS settings

### 7.3. Copy vào USB

**Cách 1: Copy toàn bộ folder**
```
Federated_Learning_Demo/  (~12-15 GB)
├── Federated_Learning_Demo.vmx
├── Federated_Learning_Demo.vmdk
├── Federated_Learning_Demo-s001.vmdk
├── Federated_Learning_Demo-s002.vmdk
├── ...
└── Federated_Learning_Demo.nvram
```

**Cách 2: Export as OVF/OVA (khuyến nghị)**
1. VM → File → Export to OVF/OVA
2. Chọn location: USB drive
3. Format: OVA (single file, dễ nộp hơn)
4. Export → Mất ~10-20 phút

Result: `Federated_Learning_Demo.ova` (~10-12 GB)

### 7.4. Cấu trúc USB nộp thầy

```
USB/
├── Federated_Learning_Demo.ova           # VM image
├── HUONG_DAN_IMPORT.txt                  # Hướng dẫn import VM
├── BAO_CAO_DO_AN.pdf                     # Báo cáo đồ án
├── SLIDES_TRINH_BAY.pptx                 # Slides thuyết trình
└── SOURCE_CODE/                          # Source code backup
    └── LPA-master.zip
```

### 7.5. File HUONG_DAN_IMPORT.txt

```
=====================================================
HƯỚNG DẪN IMPORT VIRTUAL MACHINE
=====================================================

BƯỚC 1: Cài VMware
------------------
- Download VMware Workstation (Windows) hoặc VMware Fusion (macOS)
- Hoặc dùng VMware Player (Free): 
  https://www.vmware.com/products/workstation-player.html

BƯỚC 2: Import VM
------------------
1. Mở VMware Workstation/Fusion
2. File → Open
3. Browse → chọn file "Federated_Learning_Demo.ova"
4. Import → Chọn thư mục lưu VM
5. Đợi import xong (~5 phút)

BƯỚC 3: Khởi động VM
---------------------
1. Power on VM
2. Đợi Ubuntu boot (~30 giây)
3. Đăng nhập:
   Username: fldemo
   Password: 123456

BƯỚC 4: Chạy Demo
------------------
1. Double-click icon "FL Demo" trên Desktop
2. Browser sẽ tự động mở http://localhost:3000
3. Explore các pages:
   - Homepage
   - Topology
   - Attack Demo
   - Aggregation Defense
   - Compare

LƯU Ý:
-------
- VM cần 4GB RAM
- Nếu máy yếu, giảm RAM VM xuống 2GB:
  VM → Settings → Memory → 2048 MB

LIÊN HỆ:
--------
Nếu gặp vấn đề khi import VM, liên hệ nhóm sinh viên.

=====================================================
```

---

## PHẦN 8: CHECKLIST TRƯỚC KHI NỘP

### 8.1. Test lần cuối

□ Boot VM thành công
□ Đăng nhập được (username: fldemo, password: 123456)
□ Double-click icon "FL Demo" → terminal mở, server start
□ Browser tự động mở http://localhost:3000
□ Homepage load được
□ Topology page hoạt động
□ Attack Demo page hoạt động, animation chạy
□ Aggregation Defense page hoạt động
□ Compare page hoạt động
□ Đọc được file HUONG_DAN_SU_DUNG.txt trên Desktop

### 8.2. Test import lại VM

1. Export VM thành .ova
2. Xóa VM khỏi VMware
3. Import lại từ file .ova
4. Kiểm tra lại tất cả chức năng

### 8.3. Chuẩn bị USB

□ Format USB thành exFAT (tương thích cả Windows/macOS)
□ Copy file .ova vào USB
□ Copy các file hướng dẫn
□ Copy báo cáo, slides
□ Kiểm tra USB đọc được trên máy khác

---

## PHẦN 9: THÔNG TIN QUAN TRỌNG

### 9.1. Credentials

**VM Login:**
```
Username: fldemo
Password: 123456
```

**Sudo password:** `123456`

### 9.2. Ports

- **Web Demo:** http://localhost:3000
- **SSH (nếu enable):** Port 22

### 9.3. Specs VM

```
OS: Ubuntu 22.04 LTS Desktop
RAM: 4GB
CPU: 2 cores
Disk: 40GB (actual use ~12GB)
Network: NAT
```

### 9.4. Software đã cài

- Ubuntu 22.04 LTS Desktop
- Node.js 20.x
- npm 10.x
- Git
- VMware Tools
- Chromium Browser (default)

### 9.5. Project Location

```
~/projects/LPA/
```

---

## PHẦN 10: ALTERNATIVES (NẾU USB KHÔNG ĐỦ DUNG LƯỢNG)

### Option 1: Nén VM

```bash
# Trên host machine (Windows/macOS)
# Dùng 7-Zip hoặc WinRAR
# Nén file .ova với compression "Ultra"
# Có thể giảm từ 12GB → 6-8GB
```

### Option 2: Upload lên Cloud

```
Upload .ova lên Google Drive / OneDrive
Tạo public link
Ghi link vào USB với file "DOWNLOAD_VM.txt"
```

### Option 3: Nộp riêng source code + script deploy

```
USB chỉ chứa:
- Source code
- Script cài đặt tự động
- Hướng dẫn deploy trên máy thật
- Báo cáo + Slides
```

---

## PHẦN 11: DEMO TRƯỚC THẦY

### 11.1. Kịch bản demo (~10 phút)

**1. Boot VM (1 phút)**
- Bật VMware
- Power on VM
- Đợi Ubuntu boot

**2. Khởi động Demo (30 giây)**
- Double-click "FL Demo" icon
- Server tự start
- Browser tự mở

**3. Homepage (1 phút)**
- Giới thiệu project
- Show onboarding guide
- Dataset statistics

**4. Topology Page (2 phút)**
- Giải thích sơ đồ mạng FL
- 10 workers, 1 server
- Byzantine worker (màu đỏ)
- Show training charts

**5. Attack Demo (3 phút)**
- Select "Label Flipping"
- Nhấn Play
- Show animated transformation
- BEFORE vs AFTER charts
- Giải thích: Data bị đổi nhãn

**6. Aggregation Defense (2 phút)**
- So sánh mean vs FABA
- mean: Accuracy drop 55%
- FABA: Chỉ drop 5%
- Kết luận: FABA là robust nhất

**7. Q&A (còn lại)**
- Trả lời câu hỏi thầy
- Show source code nếu cần
- Giải thích technical details

### 11.2. Câu hỏi có thể gặp

**Q: Dữ liệu thật hay giả?**
A: Dữ liệu thật từ experiments trên MNIST dataset. 60,000 samples, 200 rounds training, 20,000 iterations.

**Q: Byzantine attack hoạt động như thế nào?**
A: Worker độc hại gửi gradient sai (ví dụ: đổi label 0↔1, 8↔9) để làm mô hình học sai.

**Q: FABA phòng thủ ra sao?**
A: Phát hiện gradients outlier (xa mean quá threshold), loại bỏ khỏi aggregation.

**Q: Tại sao không dùng simple mean?**
A: Mean không robust, Byzantine có thể dominate kết quả average.

**Q: Có thể scale lên nhiều workers không?**
A: Có, code hỗ trợ n workers. Demo dùng 10 workers để dễ visualize.

---

## KẾT LUẬN

VM đã sẵn sàng nộp khi:
✅ Có file .ova (~10-12 GB)
✅ Có file HUONG_DAN_IMPORT.txt
✅ Test import lại thành công
✅ Demo chạy tốt, không lỗi
✅ USB format exFAT, copy đầy đủ files
✅ Backup source code

**Thành công!** 🎉

---

**Ngày tạo:** December 2025  
**Môn học:** IE105  
**Đề tài:** Byzantine Attacks trong Federated Learning
