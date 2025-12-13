# 🚀 Hướng dẫn Push lên GitHub và Deploy Vercel

## Bước 1: Tạo GitHub Repository

1. Vào [github.com/new](https://github.com/new)
2. Tạo repository mới:
   - **Name:** `federated-learning-visualizer`
   - **Description:** Byzantine Attack Visualization for Federated Learning
   - **Public** hoặc **Private** (tùy chọn)
   - ⚠️ **KHÔNG** tích "Add README" hoặc ".gitignore" (đã có sẵn)
3. Click "Create repository"

## Bước 2: Push code lên GitHub

Sau khi tạo repo, GitHub sẽ hiển thị URL. Copy và chạy:

```bash
# Add remote (thay YOUR_USERNAME và YOUR_REPO)
git remote add origin https://github.com/YOUR_USERNAME/federated-learning-visualizer.git

# Push code
git push -u origin master
```

**Hoặc nếu dùng SSH:**
```bash
git remote add origin git@github.com:YOUR_USERNAME/federated-learning-visualizer.git
git push -u origin master
```

## Bước 3: Deploy lên Vercel

### Cách 1: Import từ GitHub (Khuyên dùng)

1. Vào [vercel.com/new](https://vercel.com/new)
2. Login bằng GitHub
3. Click "Import Git Repository"
4. Chọn repository `federated-learning-visualizer`
5. Vercel tự động detect Next.js:
   ```
   Framework Preset: Next.js
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```
6. Click **"Deploy"** 🚀

### Cách 2: Vercel CLI

```bash
# Install CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

## Sau khi deploy thành công:

✅ Vercel sẽ tạo URL production: `https://your-project.vercel.app`  
✅ Mỗi lần push code mới, Vercel tự động re-deploy  
✅ Preview deployments cho mỗi pull request  

## 🎯 Test các trang sau deploy:

- 🏠 `https://your-project.vercel.app/`
- 🔬 `https://your-project.vercel.app/topology`
- ⚔️ `https://your-project.vercel.app/attack-demo`
- 📊 `https://your-project.vercel.app/compare`
- 🛡️ `https://your-project.vercel.app/aggregation-defense`

---

**Ready to show! 🎉**
