# 🎤 Presentation Script - Federated Learning Visualizer

## 📋 OUTLINE THUYẾT TRÌNH (10-15 phút)

---

## 1. GIỚI THIỆU (2 phút)

### Opening Hook
> "Xin chào mọi người! Hôm nay em xin giới thiệu **Federated Learning Visualizer** - một web application trực quan hóa các cuộc tấn công Byzantine trong học liên kết."

### Bối cảnh vấn đề
- **Federated Learning** là gì?
  - Phương pháp ML cho phép nhiều thiết bị cùng huấn luyện model mà KHÔNG chia sẻ data
  - Ví dụ: Google keyboard học typing habits từ hàng triệu điện thoại
  
- **Vấn đề Byzantine Attack**:
  - 1 trong 10 workers có thể bị hack/malicious
  - Gửi gradients độc hại → làm sụp đổ global model
  - Accuracy giảm từ 90% → 65% chỉ với 1 attacker!

### Mục tiêu project
> "Em build app này để:
> 1. **Trực quan hóa** 4 loại tấn công Byzantine phổ biến
> 2. **So sánh** 5 thuật toán robust aggregation 
> 3. **Phân tích** data thật từ 20,000 iterations trên SR_MNIST dataset"

---

## 2. QUY TRÌNH HOẠT ĐỘNG - FEDERATED LEARNING (2 phút)

> "Trước khi vào demo, em sẽ giải thích **quy trình hoạt động** của Federated Learning để mọi người hiểu cách Byzantine attack hoạt động."

### 📊 Workflow Bình Thường (Không có tấn công)

*[Vẽ diagram trên bảng hoặc show slide]*

**Bước 1: Initialize Model**
- Parameter Server khởi tạo global model với weights ngẫu nhiên
- VD: Neural network cho phân loại chữ số 0-9

**Bước 2: Distribute Model**
- Server gửi model weights xuống 10 workers
- Mỗi worker có local data (6,000 samples/worker)

**Bước 3: Local Training**
- Mỗi worker train model trên data riêng của mình
- Tính gradients: ∇Loss = how to update weights
- VD: Worker 1 có nhiều chữ số 0,1 → gradients optimize cho 0,1

**Bước 4: Upload Gradients**
- 10 workers gửi gradients về Parameter Server
- Server nhận được: [g₁, g₂, g₃, ..., g₁₀]

**Bước 5: Aggregate**
- Server tính **mean**: g_global = (g₁ + g₂ + ... + g₁₀) / 10
- Update global model: w_new = w_old - learning_rate × g_global

**Bước 6: Repeat**
- 200 rounds × 100 iterations = 20,000 updates
- Accuracy tăng dần: 10% → 50% → 85% → 90%

> "Đó là workflow bình thường. Vậy **Byzantine attack** phá vỡ quy trình này như nào?"

---

### ⚠️ Khi Có Byzantine Attack

**Bước 3 bị phá vỡ: Poisoned Local Training**
- Honest workers (9): Train bình thường → correct gradients
- Byzantine worker (1): **Modifies data or gradients** → poisoned gradients

**4 Loại Tấn Công:**

1. **Label Flipping**: Đổi labels trước khi train
   - Data: Image "0" với label "1" 
   - Gradient sai lệch → confuse model

2. **Furthest Label**: Đổi labels sang opposite class
   - 0→5, 1→6, 2→7 (distance max)
   - Gradient maximize confusion

3. **Gradient Scaling**: Scale gradients lên 10×
   - Byzantine gradient = 10 × honest gradient
   - Dominate aggregation: 10/19 = 53% influence!

4. **Sign Flipping**: Đảo ngược gradient (×-1)
   - Honest: gradient descent (loss↓)
   - Byzantine: gradient ascent (loss↑)

**Bước 5 bị phá vỡ: Poisoned Aggregation**
- Mean aggregator: (9×correct + 1×poisoned) / 10
- Nếu poisoned quá lớn → global model bị skew
- **Result**: Accuracy chỉ còn 65-70% thay vì 90%!

> "Đó là lý do cần **Robust Aggregation** để filter malicious updates!"

---

## 3. DEMO TÍNH NĂNG (6 phút)

### 🏠 HOMEPAGE (30 giây)
*[Mở trang chủ]*

> "Bây giờ vào demo app. Đây là trang chủ với:
> 
> - Quick stats: 4 attack types, 5 aggregators, 60K samples, 10 workers
> - Experiment config: SR_MNIST dataset, 10 workers (9 honest + 1 Byzantine), 3 data partition strategies, 200 rounds training
> - Navigation cards để explore từng tính năng"

---

### ⚔️ ATTACK DEMO (2 phút)
*[Click vào Attack Demo]*

> "Đầu tiên, trang **Attack Demo** - nơi demo 4 loại tấn công Byzantine:

#### **1. Label Flipping Attack** (Demo này)
*[Chọn Label Flipping, click Play]*

> "Nhìn 2 charts:
> 
> **Left (Honest)**: Blue bars = distribution bình thường
> - Digit 0: 7%, Digit 1: 9%, balanced across digits
> 
> **Right (Byzantine)**: Watch animation!
> - Khi click Play ▶️, bars turn RED
> - Numbers show transformations: 0→1, 1→0, 2→3, 3→2, 8→9
> - Distribution bị đảo ngược
> 
> **Ý nghĩa**: Byzantine worker train trên sai labels → gradients sai → poison model
> 
> **Impact**: Accuracy drop 5-15% (shown in mechanism box)"

#### **2. Furthest Label Flipping** 
*[Switch sang Furthest]*

- Aggressive hơn: 0→5, 1→6, 2→7... (map to opposite)
- Impact: 10-25% accuracy drop, worst case ~10% (random guessing)

#### **3. Gradient Scaling Attack**
*[Switch sang Gradient Scaling]*

- Model poisoning: Gửi gradient 10× larger magnitude
- Byzantine worker không đổi data, chỉ scale gradients lên 10 lần
- Impact: Có thể làm training diverge hoàn toàn

### 🛡️ AGGREGATION DEFENSE (2.5 phút)
*[Click vào Aggregation Defense]*

> "Vậy làm sao chống lại attacks? → **Robust Aggregation!**
> 
> Nhớ Bước 5 trong workflow: Server phải aggregate 10 gradients
> - Simple mean: Treat all equal → vulnerable
> - Robust methods: Detect và filter outliers"

#### Giải thích concept trước khi xem charts
*[Scroll đến Key Concept box]*

> "Scenario cụ thể:
> 
> - 10 workers gửi gradients: [g₁, g₂, ..., g₁₀]
> - 9 honest: magnitude ~1.0
> - 1 Byzantine: magnitude ~5.0 (attack bằng scaling)
> 
> **Mean Aggregator** (vulnerable):
> - Công thức: (g₁+g₂+...+g₁₀)/10
> - Byzantine g₁₀=5.0 → pulls average toward 5
> - Result: Global model bị skew, accuracy drop to 70%
> 
> **Robust Aggregators** (defended):
> - Detect g₁₀ là outlier
> - Remove hoặc clip nó
> - Aggregate only honest gradients
> - Result: Accuracy maintained at 85-90%"
> "Vậy làm sao chống lại attacks? → **Robust Aggregation!**

#### Giải thích concept
*[Scroll đến Key Concept box]*

- Scenario: 10 workers gửi gradients về Parameter Server
- Byzantine worker gửi gradients 5× larger
- Nếu dùng **simple mean**: Byzantine chiếm 50% weight → model bị poison
- **Robust aggregators** detect và filter malicious updates

#### Demo 5 aggregators

**Mean (Baseline)** - Red card
- Simple average: (w₁+w₂+...+w₁₀)/10
- ❌ VULNERABLE: No defense, treats all equal
- Byzantine 10× gradient = 10× influence

**Trimmed Mean** - Yellow card  
- Removes top & bottom 20% (2 smallest + 2 largest)
- ⚠️ MODERATE: Works if Byzantine extreme
- Fails if attacker adapts values
#### Real Experiment Results - Giải thích chart trước
*[Scroll xuống biểu đồ]*

> "Trước khi nhìn chart, em giải thích axes:
> 
> **X-axis (Iterations)**: 0 → 20,000
> - Mỗi point = 1 gradient update
> - Training từ trái sang phải (time progresses)
> 
> **Y-axis (Test Accuracy)**: 0% → 100%
> - Cao hơn = tốt hơn
> - Target: ~90% for MNIST
> 
> **5 Lines (5 Aggregators)**:
> - Red = mean (vulnerable baseline)
> - Yellow = trimmed_mean
> - Blue = CC (Coordinate Clipping)
> - Green = LFighter
> - Purple = FABA (best)
> 
> **Ý nghĩa animation**: Nhìn lines tăng dần → model đang học!

#### Phân tích kết quả

*[Point to specific lines]*

> "Configuration: Dirichlet α=1 (non-IID), Label Flipping attack
> 
> Nhìn behavior của từng line:
> 
> - **Red (mean)**: 
>   - Starts at 10% (random)
>   - Climbs to only ~70%
>   - Fluctuates → unstable
>   - **Why?** Byzantine poisoned gradients pull model wrong direction
### 🔬 TOPOLOGY & TRAINING (1 phút)
*[Click Topology]*

> "Trang **Topology** visualize **quy trình 6 bước** mà em vừa giải thích:

#### Giải thích visualization trước

**Network Diagram** (top):
- 10 circles = 10 workers
- Blue circles = 9 honest workers
- Red circle = 1 Byzantine worker (attacked)
- Purple center = Parameter Server
- Gray lines = communication (upload gradients, download model)

**Animation Controls** (middle):
- Play ▶️ = Simulate training process
- Step Forward/Backward = Move by iterations
- Speed slider = Fast/slow playback

**Metrics Charts** (bottom):
- Top chart: Accuracy over time
- Middle chart: Loss over time (lower = better)
- Bottom chart: Learning rate schedule
---

## 4. RECAP - TẠI SAO CẦN APP NÀY? (30 giây)

> "Tóm lại workflow và vấn đề:
> 
> **Normal FL**: Workers → Train → Gradients → Aggregate (mean) → Update model → Repeat
> - ✅ Works nếu all workers honest
> - ✅ Accuracy reaches 90%
> 
> **With Byzantine Attack**: 1 malicious worker poisons gradients
> - ❌ Mean aggregator vulnerable
> - ❌ Accuracy drops to 65-70%
> - ❌ Model unusable!
> 
> **Solution**: Robust aggregators (FABA, LFighter, CC)
> - ✅ Detect outliers
> - ✅ Filter malicious updates
> - ✅ Maintain 85-90% accuracy
> 
> **App này demonstrate visually**:
> - 📊 How attacks work (Attack Demo)
> - 🛡️ How defenses work (Aggregation Defense)
> - 🔬 Real experimental results (Topology, Compare)
> 
> Better than reading 50 pages of papers!"

---

## 5. KỸ THUẬT IMPLEMENTATION (2 phút)
*[Click Play]*

> "Nhìn changes khi training:
> 
> - **Iteration counter tăng**: 0 → 1000 → 5000 → 20000
> - **Accuracy line goes up**: 10% → 50% → 85%
> - **Loss line goes down**: 2.3 → 0.5 (model improving!)
> - **Workers pulse**: Simulating gradient upload mỗi round
> 
> Đây là **real data** from experiments, not mock animation!"
> 
> - **Green (LFighter)**:
>   - ~88% accuracy
>   - Uses loss information to detect malicious workers
>   - **Smart:** Doesn't just look at gradient magnitude
> 
> - **Purple (FABA)**:
>   - ~90% - best performance!
>   - Iteratively removes outliers
>   - **Excellent:** Adapts to any attack pattern
> 
> Summary cards dưới show final numbers: 90% vs 70% = **20% improvement**!"
#### Real Experiment Results
*[Scroll xuống biểu đồ]*

> "Đây là kết quả thật từ SR_MNIST:
> 
> - Configuration: Dirichlet α=1 (non-IID), Label Flipping attack
> - 200 rounds × 100 iterations = 20,000 total iterations
> 
> Nhìn vào chart:
> - **Red line (mean)**: Accuracy chỉ ~70% - bị poison nặng
> - **Yellow (trimmed_mean)**: ~80% - khá hơn
> - **Blue (CC)**: ~85% - tốt
> - **Green (LFighter)**: ~88% - rất tốt
> - **Purple (FABA)**: ~90% - xuất sắc nhất!
>
> Summary cards dưới show final accuracy của từng aggregator."

---

### 🔬 TOPOLOGY & TRAINING (1 phút)
*[Click Topology]*

> "Trang **Topology** visualize network architecture:
> 
> - 10 workers (circles) connect to Parameter Server (center)
> - Byzantine worker highlighted red
> - Real-time metrics: accuracy, loss, learning rate qua từng iteration
> - Có thể playback training process, xem model học như thế nào
> - Data từ thật experiments, not mock data!"

---

### 📊 PERFORMANCE COMPARE (30 giây)
*[Click Compare]*

> "Trang **Compare** so sánh multiple experiments:
> 
> - Filter by partition, optimizer, attack type
> - Overlay accuracy curves của nhiều runs
> - Export metrics to CSV for further analysis
> - Best performer highlighted tự động"

---
---

## 6. KẾT LUẬN (1 phút)
### Tech Stack
> "Em build với modern stack:

**Frontend:**
- ⚡ **Next.js 15** with App Router - Server-side rendering
- 🎨 **Tailwind CSS** - Utility-first styling
- 📊 **Recharts** - Interactive data visualization
- 🧩 **Radix UI** - Accessible components

**Data:**
- 📁 Real **SR_MNIST dataset**: 60,000 samples
- 📈 ~4.2MB experimental results
- 🔗 Loaded via static JSON files in `/public/data`

**Deployment:**
- 🚀 **Vercel** - Serverless deployment
- 🌐 **GitHub** - Version control
- ⚡ Build time: ~2-3 phút
- 🎯 Lighthouse Score: 90+

### Key Features
- ✅ Type-safe with **TypeScript**
- ✅ DailyEng-inspired friendly UI (không AI-generated)
- ✅ Real experiment data from 20K iterations
- ✅ Interactive animations với D3.js
- ✅ Responsive design (mobile-ready)
- ✅ Global navigation with breadcrumb"

---

## 4. CHALLENGES & SOLUTIONS (1 phút)

### Challenge 1: Data Structure
> "Data từ research có structure phức tạp:
> 
> Problem: nested JSON với iterations, meta, statistics
> Solution: Built type-safe dataLoader service với proper TypeScript interfaces"

### Challenge 2: Performance
> "20,000 iterations = quá nhiều data points
> 
> Problem: Chart lag với 20K points
> Solution: Sampling every 100 iterations → 200 points, still shows trends"

### Challenge 3: UI Design
> "Initial design trông quá 'AI-perfect', sterile
> 
> Problem: Too many gradients, shadows, formal language
> Solution: DailyEng-inspired redesign - friendly emojis, conversational text, clean cards"

---

## 5. KẾT LUẬN (1 phút)

### Key Takeaways
> "3 điểm chính từ project này:

1️⃣ **Byzantine attacks are real threat** in Federated Learning
   - Chỉ 1/10 malicious workers có thể drop accuracy từ 90% → 65%

2️⃣ **Robust aggregation is essential**
   - Simple mean không đủ
   - Advanced methods (FABA, LFighter) maintain 85-90% accuracy

3️⃣ **Visualization helps understanding**
   - Interactive demo better than reading papers
   - Real data proves effectiveness"

### Future Work
> "Hướng phát triển tiếp:
> 
> - Add more attack types (Backdoor, Model replacement)
> - Support multiple Byzantine workers (b=2, 3...)
> - Real-time training simulation
> - Comparison across different datasets (CIFAR-10, ImageNet)"

### Demo Link
> "Live demo tại: **https://federated-learning-visualizer.vercel.app**
> 
> GitHub: **github.com/RkDinhChien/federated-learning-visualizer**
> 
> Cảm ơn mọi người đã lắng nghe! Questions?"

---

## 📌 TIPS PRESENTATION

### Chuẩn bị trước:
1. ✅ Mở sẵn 5 tabs: Home, Attack Demo, Defense, Topology, Compare
2. ✅ Test animation playback trước
3. ✅ Screenshot backup nếu demo bị lag
4. ✅ Prepare for questions:
   - "Tại sao dùng Dirichlet α=1?"
   - "FABA algorithm works như nào?"
   - "Real data từ đâu?"

### Trong khi present:
- 🎯 **Maintain eye contact** - không chỉ nhìn màn hình
- 🗣️ **Speak slowly and clearly** - technical terms cần rõ ràng
- 👉 **Point to specific UI elements** - "Nhìn đây", "Chart này"
- ⏱️ **Watch timing** - có stopwatch để track
- 💡 **Highlight key insights** - "Điểm quan trọng là..."

### Q&A tips:
- "Câu hỏi hay!" - mua time để suy nghĩ
- "Em sẽ explain từ đầu..." - nếu phức tạp
- "That's actually covered in the Defense page..." - redirect
- "Đó là future work mà em đang plan" - nếu chưa implement

---

## 🎬 CLOSING LINES

> "Để kết thúc, em muốn nhấn mạnh: **Federated Learning** là future of privacy-preserving ML, nhưng **Byzantine attacks** là real security concern. 
> 
> App này không chỉ là visualization tool, mà còn là educational platform giúp mọi người hiểu threat và defense mechanisms.
> 
> Thank you! Em sẵn sàng trả lời câu hỏi! 🙏"

---

**Good luck với presentation! 🚀**
