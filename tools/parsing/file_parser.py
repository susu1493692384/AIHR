# tools/parsing/file_parser.py
"""文件解析工具"""
import os
from PyPDF2 import PdfReader
from docx import Document
from utils.error_handler import FileParseError


class FileParserTool:
    """文件解析工具类"""

    @staticmethod
    def supported_types() -> list:
        """返回支持的文件类型"""
        return [".pdf", ".docx"]

    @staticmethod
    def get_file_type(file_path: str) -> str:
        """获取文件类型"""
        _, ext = os.path.splitext(file_path)
        return ext.lower().replace(".", "")

    @staticmethod
    def parse(file_path: str) -> str:
        """
        解析文件并提取文本内容

        Args:
            file_path: 文件路径

        Returns:
            str: 提取的文本内容

        Raises:
            FileParseError: 文件解析失败
        """
        file_type = FileParserTool.get_file_type(file_path)

        if file_type == "pdf":
            return FileParserTool._parse_pdf(file_path)
        elif file_type == "docx":
            return FileParserTool._parse_docx(file_path)
        else:
            raise FileParseError(
                f"不支持的文件类型: {file_type}，"
                f"支持的类型: {', '.join(FileParserTool.supported_types())}"
            )

    @staticmethod
    def _parse_pdf(file_path: str) -> str:
        """
        解析PDF文件
        支持文本型PDF和扫描型PDF（使用OCR）
        """
        try:
            # 步骤1：尝试使用PyPDF2提取文本
            reader = PdfReader(file_path)
            text_parts = []

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            extracted_text = "\n".join(text_parts)

            # 步骤2：检查提取的文本是否足够
            # 如果文本太少（少于100个字符），可能是扫描型PDF
            if len(extracted_text.strip()) < 100:
                print(f"[WARNING] PDF文本提取失败或内容过少（{len(extracted_text)} 字符），尝试使用OCR...")
                return FileParserTool._parse_pdf_with_ocr(file_path)

            return extracted_text

        except Exception as e:
            raise FileParseError(f"PDF解析失败: {str(e)}")

    @staticmethod
    def _parse_pdf_with_ocr(file_path: str) -> str:
        """
        使用OCR解析扫描型PDF文件

        需要安装：
        - Tesseract OCR引擎
        - Python库：pytesseract, pdf2image, pillow

        安装方法：
        Windows: 下载安装 https://github.com/UB-Mannheim/tesseract/wiki
        Linux: sudo apt install tesseract-ocr
        Mac: brew install tesseract

        pip安装：
        pip install pytesseract pdf2image pillow
        """
        try:
            # 尝试导入OCR相关库
            import pytesseract
            from pdf2image import convert_from_path
            from PIL import Image
            import io

            # 检查tesseract是否可用
            try:
                pytesseract.get_tesseract_version()
            except EnvironmentError:
                raise FileParseError(
                    "未找到Tesseract OCR引擎。请安装Tesseract:\n"
                    "Windows: https://github.com/UB-Mannheim/tesseract/wiki\n"
                    "Linux: sudo apt install tesseract-ocr\n"
                    "Mac: brew install tesseract\n\n"
                    "Python依赖: pip install pytesseract pdf2image pillow"
                )

            print("[INFO] 开始OCR识别，这可能需要一些时间...")

            # 将PDF转换为图片
            # dpi=200 提高识别率，但会增加处理时间
            images = convert_from_path(file_path, dpi=200)

            ocr_text_parts = []

            for i, image in enumerate(images):
                print(f"[INFO] 正在识别第 {i+1}/{len(images)} 页...")

                # 使用pytesseract提取文本
                # lang='chi_sim+eng' 支持简体中文和英文
                text = pytesseract.image_to_string(
                    image,
                    lang='chi_sim+eng',
                    config='--psm 6'  # 假设单列文本块
                )

                if text.strip():
                    ocr_text_parts.append(text)

            extracted_text = "\n".join(ocr_text_parts)

            if not extracted_text.strip():
                raise FileParseError("OCR未能识别出任何文本，请确保PDF图片清晰")

            print(f"[INFO] OCR识别完成，提取了 {len(extracted_text)} 个字符")

            return extracted_text

        except ImportError as e:
            raise FileParseError(
                f"缺少OCR依赖库: {str(e)}\n\n"
                "请安装：pip install pytesseract pdf2image pillow"
            )
        except Exception as e:
            raise FileParseError(f"OCR解析失败: {str(e)}")

    @staticmethod
    def _parse_docx(file_path: str) -> str:
        """解析DOCX文件"""
        try:
            doc = Document(file_path)
            text_parts = []

            for paragraph in doc.paragraphs:
                if paragraph.text:
                    text_parts.append(paragraph.text)

            return "\n".join(text_parts)
        except Exception as e:
            raise FileParseError(f"DOCX解析失败: {str(e)}")
