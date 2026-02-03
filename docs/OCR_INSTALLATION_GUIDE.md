# OCR扫描型PDF支持指南

## 问题说明

如果您上传的PDF文件无法复制文本，说明这是**扫描型PDF**（图片格式），需要使用OCR（光学字符识别）技术来提取文本。

系统会自动检测这种情况并尝试使用OCR。

## 快速安装（推荐）

### Windows用户

#### 步骤1：安装Tesseract OCR引擎

1. **下载安装程序**
   - 访问：https://github.com/UB-Mannheim/tesseract/wiki
   - 下载：`tesseract-ocr-w64-setup-5.x.x.exe`（64位Windows）

2. **运行安装程序**
   - 双击安装文件
   - **重要**：记住安装路径，例如：`C:\Program Files\Tesseract-OCR`
   - 勾选"Additional language data（download）"
   - 选择"Chinese (Simplified)" - `chi_sim`
   - 选择"English" - `eng`
   - 完成安装

3. **配置环境变量**
   - 右键"此电脑" → "属性" → "高级系统设置" → "环境变量"
   - 在"系统变量"中添加：
     - 变量名：`TESSDATA_PREFIX`
     - 变量值：`C:\Program Files\Tesseract-OCR\tessdata`（根据实际安装路径修改）
   - 在"系统变量"的`Path`中添加：
     - `C:\Program Files\Tesseract-OCR`（根据实际安装路径修改）

#### 步骤2：安装Python依赖

```bash
pip install pytesseract pdf2image pillow
```

或者从项目根目录：

```bash
pip install -r requirements.txt
```

#### 步骤3：验证安装

```bash
# 测试Tesseract是否安装成功
tesseract --version

# 测试Python库
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

### Linux用户

#### Ubuntu/Debian

```bash
# 1. 安装Tesseract OCR引擎
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-chi-sim

# 2. 安装Python依赖
pip install pytesseract pdf2image pillow

# 3. 验证安装
tesseract --version
```

#### CentOS/RHEL

```bash
# 1. 安装EPEL仓库
sudo yum install -y epel-release

# 2. 安装Tesseract
sudo yum install -y tesseract tesseract-langpack-chi-sim

# 3. 安装Python依赖
pip install pytesseract pdf2image pillow
```

### Mac用户

```bash
# 1. 使用Homebrew安装Tesseract
brew install tesseract

# 2. 安装中文语言包
brew install tesseract-lang

# 3. 安装Python依赖
pip install pytesseract pdf2image pillow

# 4. 验证安装
tesseract --version
```

## 详细说明

### OCR功能工作流程

```
扫描型PDF上传
    ↓
PyPDF2尝试提取文本（失败或文本少于100字符）
    ↓
系统自动切换到OCR模式
    ↓
pdf2image将PDF转换为图片
    ↓
pytesseract识别图片中的文字
    ↓
返回提取的文本
```

### OCR配置说明

系统使用以下OCR配置：

| 参数 | 值 | 说明 |
|------|---|------|
| 语言 | `chi_sim+eng` | 支持简体中文和英文混合识别 |
| DPI | 200 | 提高识别准确率（可调） |
| 页面模式 | `--psm 6` | 假设单列文本块 |

### 性能优化

| PDF页数 | 预计处理时间 | 内存占用 |
|---------|------------|---------|
| 1页 | 5-10秒 | ~200MB |
| 3页 | 15-30秒 | ~400MB |
| 5页 | 30-60秒 | ~600MB |

**优化建议**：
- 降低DPI可以加快速度但降低准确率：`dpi=150`
- 对于纯英文PDF，使用`lang='eng'`更快

## 常见问题

### Q1: 安装后仍然报错"未找到Tesseract OCR引擎"

**Windows解决**：
1. 确认Tesseract已安装：在命令行输入 `tesseract --version`
2. 如果提示"命令不存在"，需要添加到PATH环境变量
3. 重启IDE或终端

**Linux/Mac解决**：
```bash
# 查看tesseract位置
which tesseract

# 如果输出为空，重新安装
# Ubuntu/Debian
sudo apt install tesseract-ocr

# Mac
brew reinstall tesseract
```

### Q2: OCR识别结果不准确

**可能原因**：
1. PDF图片质量过低
2. PDF是照片扫描（有阴影、倾斜）
3. 字体不标准

**解决方法**：
- 使用高清晰度扫描（300 DPI以上）
- 确保扫描件平整、光线充足
- 如果是手写体，OCR效果可能不好

### Q3: 处理速度很慢

**优化方法**：

1. **降低DPI**（会降低准确率）：
   ```python
   # 在 file_parser.py 中修改
   images = convert_from_path(file_path, dpi=150)  # 从200降到150
   ```

2. **只识别部分页面**：
   ```python
   # 只识别前3页
   images = convert_from_path(file_path, dpi=200, first_page=1, last_page=3)
   ```

3. **使用更快的OCR引擎**（可选）：
   - PaddleOCR（百度开源，中文效果好）
   - EasyOCR（支持多语言）

### Q4: 中文识别为乱码

**原因**：中文语言包未安装

**解决方法**：

```bash
# Windows：重新安装，选择语言包
# 或手动下载：https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata
# 放到：C:\Program Files\Tesseract-OCR\tessdata\

# Linux
sudo apt install tesseract-ocr-chi-sim

# Mac
brew install tesseract-lang
```

### Q5: 不想安装OCR，有其他方法吗？

**替代方案**：

1. **使用在线OCR工具**：
   - 阿里云OCR：https://www.aliyun.com/product/ocr
   - 腾讯云OCR：https://cloud.tencent.com/product/ocr
   - Adobe Acrobat DC

2. **转换PDF格式**：
   - 使用Adobe Acrobat将扫描型PDF转为可搜索PDF
   - 在线工具：https://www.ilovepdf.com/ocr-pdf

3. **使用DOCX格式**：
   - 最推荐：直接使用Word（DOCX）格式
   - DOCX可以直接提取文本，无需OCR

## 测试OCR功能

### 方法1：使用测试脚本

创建 `test_ocr.py`：

```python
"""测试OCR功能"""
from tools.parsing.file_parser import FileParserTool

# 测试扫描型PDF
file_path = "test_scan.pdf"  # 替换为您的PDF路径

try:
    text = FileParserTool.parse(file_path)
    print(f"✅ OCR成功！提取了 {len(text)} 个字符")
    print(f"前100个字符：\n{text[:100]}")
except Exception as e:
    print(f"❌ OCR失败：{e}")
```

### 方法2：直接使用Streamlit

1. 上传您的扫描型PDF
2. 点击"开始分析"
3. 查看日志输出，应该看到：
   ```
   [WARNING] PDF文本提取失败或内容过少（XX 字符），尝试使用OCR...
   [INFO] 开始OCR识别，这可能需要一些时间...
   [INFO] 正在识别第 1/X 页...
   [INFO] OCR识别完成，提取了 XXX 个字符
   ```

## 卸载OCR（可选）

如果不再需要OCR功能：

```bash
# 卸载Python库
pip uninstall pytesseract pdf2image pillow

# 卸载Tesseract引擎
# Windows：控制面板 → 程序和功能
# Linux: sudo apt remove tesseract-ocr
# Mac: brew uninstall tesseract
```

**注意**：卸载后，扫描型PDF将无法识别，但仍可处理文本型PDF和DOCX文件。

## 推荐做法

✅ **最佳实践**：
1. **优先使用DOCX格式**：直接提取文本，快速准确
2. **使用可搜索PDF**：PDF中包含文本层，可直接提取
3. **扫描件预处理**：使用高DPI扫描、确保图像清晰

⚠️ **避免**：
- 使用模糊的扫描件
- 使用倾斜的照片
- 使用低分辨率扫描（<150 DPI）

❌ **不推荐**：
- 手写体简历（OCR识别率低）
- 纯图片格式（JPG、PNG等，除非用OCR）
- 复杂排版（双栏、表格多）

## 技术支持

如果遇到问题：

1. 查看详细错误信息
2. 检查Tesseract安装：`tesseract --version`
3. 检查Python依赖：`pip list | grep -E "pytesseract|pdf2image|pillow"`
4. 查看 [故障排查文档](TROUBLESHOOTING_NO_FILE_PROVIDED.md)

---

**文档版本**: v1.0
**更新日期**: 2026-01-30
