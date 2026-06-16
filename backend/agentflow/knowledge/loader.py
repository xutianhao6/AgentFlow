"""Document loaders for pdf / md / docx / txt.

重要：绝不把无法解析的二进制内容当作文本入库（那会污染知识库、产生乱码）。
解析失败时抛出明确错误，由上层提示用户。
"""
from __future__ import annotations

import io


class DocumentParseError(Exception):
    """文档解析失败（缺少依赖或文件损坏）。"""


def load_text(filename: str, content: bytes) -> str:
    """Extract plain text from an uploaded document by extension."""
    name = (filename or "").lower()
    if name.endswith((".txt", ".md", ".markdown", ".csv", ".json")):
        return _decode_text(content)
    if name.endswith(".pdf"):
        return _load_pdf(content)
    if name.endswith((".docx",)):
        return _load_docx(content)
    if name.endswith((".doc",)):
        raise DocumentParseError("暂不支持 .doc（旧版 Word），请另存为 .docx 或 PDF 后上传")
    # 未知扩展名：尝试按文本解码，但若包含大量不可打印字节则判定为二进制并拒绝
    text = _decode_text(content)
    if _looks_binary(text):
        raise DocumentParseError(f"无法识别的文件类型：{filename}（看起来是二进制文件）")
    return text


def _decode_text(content: bytes) -> str:
    """文本文件解码：优先 UTF-8，再尝试 GBK（中文 Windows 常见）。"""
    for enc in ("utf-8", "utf-8-sig", "gbk", "gb18030"):
        try:
            return content.decode(enc)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="ignore")


def _looks_binary(text: str) -> bool:
    if not text:
        return False
    # 统计不可打印字符比例
    bad = sum(1 for c in text[:2000] if ord(c) < 9 or (13 < ord(c) < 32))
    return bad > len(text[:2000]) * 0.05


def _load_pdf(content: bytes) -> str:
    # 1) pdfplumber（对中文 / 排版友好）
    try:
        import pdfplumber  # type: ignore

        parts = []
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                parts.append(page.extract_text() or "")
        text = "\n".join(parts).strip()
        if text:
            return text
    except ImportError:
        pass
    except Exception as e:  # 损坏的 PDF 等
        raise DocumentParseError(f"PDF 解析失败：{e}")

    # 2) pypdf 兜底
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(io.BytesIO(content))
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        if text:
            return text
        raise DocumentParseError(
            "PDF 中未提取到文本：可能是扫描件/图片型 PDF，需要 OCR，暂不支持"
        )
    except ImportError:
        raise DocumentParseError(
            "服务器未安装 PDF 解析库，请先 `pip install pdfplumber pypdf` 后重试"
        )
    except DocumentParseError:
        raise
    except Exception as e:
        raise DocumentParseError(f"PDF 解析失败：{e}")


def _load_docx(content: bytes) -> str:
    try:
        import docx  # type: ignore

        doc = docx.Document(io.BytesIO(content))
        text = "\n".join(p.text for p in doc.paragraphs).strip()
        if not text:
            raise DocumentParseError("DOCX 中未提取到文本")
        return text
    except ImportError:
        raise DocumentParseError("服务器未安装 DOCX 解析库，请先 `pip install python-docx` 后重试")
    except DocumentParseError:
        raise
    except Exception as e:
        raise DocumentParseError(f"DOCX 解析失败：{e}")
