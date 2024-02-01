import sys
from pathlib import Path

import fitz


# 检查pdf是否需要密码或被加密
def check_pdf(pdf):
    if pdf.needs_pass or pdf.is_encrypted:
        if not (pdf.authenticate("") in [1, 2]):
            return True
    return False


def decrypt_pdf(pdf, password):
    if not check_pdf(pdf):
        print("PDF文件不需要密码或未加密")
        return pdf
    pdf_status = pdf.authenticate(password)
    if not pdf_status:
        print("密码错误")
        return None
    if pdf_status == 1:
        print("PDF 不需要密码")
    elif pdf_status == 2:
        print("PDF 使用用户密码解密")
    elif pdf_status == 4:
        print("PDF 使用拥有者密码解密")
    elif pdf_status == 6:
        print("PDF 使用用户密码和拥有者密码解密，两个密码相同")
    else:
        print("未定义情况")
    return pdf


if __name__ == '__main__':
    pdf_path = Path(r"a.pdf")
    password = "123456"
    try:
        pdf = fitz.open(pdf_path)
    except Exception as e:
        print(e)
        print("PDF 文件打开失败")
        sys.exit(1)
    pdf_decrypted = decrypt_pdf(pdf, password)
    if pdf_decrypted:
        print("PDF 解密成功")
        pdf_decrypted_path = pdf_path.with_name(f"{pdf_path.stem}_decrypted{pdf_path.suffix}")
        if pdf_decrypted_path.exists():
            print(f"PDF 解密文件已存在: {pdf_decrypted_path}")
        else:
            pdf_decrypted.save(pdf_decrypted_path)
            print(f"PDF 解密文件已保存至: {pdf_decrypted_path}")
        pdf_decrypted.close()
    else:
        print("PDF 解密失败")
