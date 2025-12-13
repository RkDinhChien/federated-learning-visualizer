# 📄 PDF Export Instructions

## ❌ Automatic Export Failed
markdown-pdf gặp lỗi system. Dùng một trong các phương pháp sau:

---

## ✅ RECOMMENDED: VS Code Extension (Easiest)

### Bước 1: Install Extension
1. Mở VS Code
2. Nhấn `Cmd+Shift+X` (Extensions)
3. Tìm "Markdown PDF" by yzane
4. Click Install

### Bước 2: Export
1. Mở file `PRESENTATION_SCRIPT.md` trong VS Code
2. Nhấn `Cmd+Shift+P` → Gõ "Markdown PDF"
3. Chọn **"Markdown PDF: Export (pdf)"**
4. Lặp lại với `QA_PREPARATION.md`

**Result:** 2 PDF files cùng thư mục

---

## 🔧 Option 2: Install Pandoc (Better Quality)

### Install (macOS):
```bash
brew install pandoc basictex
```

### Export:
```bash
# Presentation Script
pandoc PRESENTATION_SCRIPT.md -o PRESENTATION_SCRIPT.pdf \
    --pdf-engine=xelatex \
    --variable mainfont="Arial" \
    --variable fontsize=11pt \
    --variable geometry:margin=1in \
    --toc

# Q&A Preparation
pandoc QA_PREPARATION.md -o QA_PREPARATION.pdf \
    --pdf-engine=xelatex \
    --variable mainfont="Arial" \
    --variable fontsize=11pt \
    --variable geometry:margin=1in \
    --toc
```

---

## 💻 Option 3: Online Converter

### Steps:
1. Visit: https://www.markdowntopdf.com/
2. Upload `PRESENTATION_SCRIPT.md`
3. Click "Convert to PDF"
4. Download
5. Repeat with `QA_PREPARATION.md`

---

## 📱 Option 4: Preview + Print (macOS Built-in)

### Steps:
1. Mở file `.md` trong VS Code
2. Nhấn `Cmd+Shift+V` (Preview markdown)
3. Nhấn `Cmd+K V` (Open preview to side)
4. Trong preview pane: Right-click → "Open in Browser"
5. Browser: `Cmd+P` → "Save as PDF"

---

## 🎯 Recommended Workflow

**For best results:**

1. **Use VS Code Extension** - Fastest, preserves formatting
2. **Check PDFs** - Verify emojis và code blocks render correctly
3. **Print from Preview** - Nếu cần adjust layout
4. **Combine if needed** - Use Preview để merge 2 PDFs thành 1

---

## 📋 Alternative: Print from Browser

### Direct from GitHub:
1. Push markdown files to GitHub (already done ✅)
2. Open on GitHub: `github.com/RkDinhChien/federated-learning-visualizer`
3. Click file → GitHub renders markdown beautifully
4. `Cmd+P` → "Save as PDF"

**Advantage:** GitHub's markdown rendering is excellent!

---

## ✨ Quick Fix

Nếu cần PDF gấp, chạy:

```bash
# Install VS Code extension via command
code --install-extension yzane.markdown-pdf

# Restart VS Code, then export as described above
```

---

**Recommend:** VS Code "Markdown PDF" extension = easiest & best quality! 🚀
