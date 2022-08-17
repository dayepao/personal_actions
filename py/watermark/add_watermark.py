import colorsys
import io
import os
import sys

import fitz
from PIL import Image, ImageDraw, ImageFont
from collections import Counter

# pip install pillow
# pip install pymupdf


# 获取资源文件路径
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# 将16进制颜色转换为RGBA颜色
def hex_to_rgba(hex_color: str, opacity: int):
    assert len(hex_color) == 7, "颜色格式错误"
    assert 0 <= opacity <= 100, "不透明度范围错误"
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    a = int((opacity / 100) * 255)
    return (r, g, b, a)


# 获取图片主要颜色
def get_image_dominant_color(image: Image.Image):
    image = image.copy()  # 创建图片副本，防止修改原图
    # image = image.convert('RGBA')  # 转换为RGBA格式
    image.thumbnail((200, 200))  # 生成缩略图，减少计算量
    max_score = 0
    dominant_color = None
    for count, (r, g, b, a) in image.getcolors(image.size[0] * image.size[1]):
        # 跳过完全透明的像素
        if a == 0:
            continue

        saturation = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)[1]  # 获得HSV色彩空间饱和度，0-1
        y = min((abs(r * 2104 + g * 4130 + b * 802 + 4096 + 131072) >> 13), 235)  # 获得YUV色彩空间亮度
        y = (y - 16.0) / (235 - 16)  # 将亮度从 16-235 放缩到 0-1
        # 忽略高亮色
        if y > 0.9:
            continue

        score = (saturation + 0.1) * count
        if score > max_score:
            max_score = score
            dominant_color = (r, g, b)
    return dominant_color


# 计算两个颜色色差，参考自：https://www.compuphase.com/cmetric.htm
def color_diff(color1: tuple, color2: tuple):
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    r_mean = (r1 + r2) / 2
    R = r1 - r2
    G = g1 - g2
    B = b1 - b2
    return pow(((2 + r_mean / 256) * (R ** 2) + 4 * (G ** 2) + (2 + (255 - r_mean) / 256) * (B ** 2)), 0.5)


# 获取字典中出现次数最多的键值
def get_most_freq_value_in_dict(dic: dict):
    x1 = dict(Counter(dic.values()))
    dic1SortList = sorted(x1.items(), key=lambda x: x[1], reverse=True)
    return dic1SortList[0][0]


# 给图片添加文字水印
def add_text_watermark_to_image(img_path: str, text: str, font_path: str = resource_path(os.path.join('fonts', 'SourceHanSansCN-Regular.otf')), font_size: int | str = "auto", color: str = "#696969", opacity: int = 30, angle: int = 20, with_stroke: bool = True):
    assert os.path.exists(img_path), "图片不存在"
    draw_kargs = {}  # 水印参数
    draw_kargs["xy"] = (0, 0)
    # 打开图片
    img = Image.open(img_path).convert('RGBA')
    # 创建画布
    text_canvas_size = int(pow((img.size[0] ** 2 + img.size[1] ** 2), 0.5))  # 计算斜边长度
    text_canvas = Image.new("RGBA", (text_canvas_size * 2, text_canvas_size * 2))  # 提高水印分辨率
    draw = ImageDraw.Draw(text_canvas)
    # 创建字体
    if font_size == "auto":
        temp_font_size = int(text_canvas_size / 12)
        temp_font = ImageFont.truetype(font_path, temp_font_size)
        # 判断水印文字是否过长
        while draw.textbbox((0, 0), text, temp_font)[2] > text_canvas_size:
            temp_font_size = int(temp_font_size * 0.9)
            temp_font = ImageFont.truetype(font_path, temp_font_size)
        font_size = temp_font_size
    font = ImageFont.truetype(font_path, font_size)
    draw_kargs["font"] = font
    # 确定文字数量，准备要绘制的文字
    text_width, text_height = draw.textbbox((0, 0), text, font)[2:4]
    wm_text = "{}  ".format(text) * (int(text_canvas.size[0] / text_width) + 1)  # 将文字复制成画布宽度的倍数
    wm_text = "{}\n\n\n".format(wm_text) * (int(text_canvas.size[1] / text_height) + 1)  # 将文字复制成画布高度的倍数
    draw_kargs["text"] = wm_text
    if with_stroke:
        # 确定文字描边颜色
        image_dominant_color = get_image_dominant_color(img)  # 获取图片主要颜色
        if color_diff(image_dominant_color, (0, 0, 0)) > color_diff(image_dominant_color, (255, 255, 255)):
            text_stroke_color = (0, 0, 0)
        else:
            text_stroke_color = (220, 220, 220)
        draw_kargs["stroke_fill"] = text_stroke_color
        draw_kargs["stroke_width"] = 1
    # 绘制文字
    rgba_text_color = hex_to_rgba(color, opacity)  # 转换颜色
    draw_kargs["fill"] = rgba_text_color
    draw.multiline_text(**draw_kargs)
    text_canvas = text_canvas.rotate(angle)  # 旋转画布
    # 合并图片
    text_canvas = text_canvas.resize((text_canvas_size, text_canvas_size))  # 缩放画布
    img.paste(text_canvas, (int((img.size[0] - text_canvas_size) / 2), int((img.size[1] - text_canvas_size) / 2)), text_canvas)
    # img.show()
    # 保存图片
    if os.path.splitext(img_path)[1] != ".png":
        img = img.convert("RGB")
    img.save("{}_wm.{}".format(os.path.splitext(img_path)[0], os.path.splitext(img_path)[1]), quality=90)
    # 关闭图片
    img.close()


# https://pymupdf.readthedocs.io/en/latest/page.html#Page.insert_image
# 给PDF添加文字水印（初版）
def add_text_watermark_to_pdf_old(pdf_path: str, text: str, font_path: str = resource_path(os.path.join('fonts', 'SourceHanSansCN-Regular.otf')), font_size: int | str = "auto", color: str = "#696969", opacity: int = 30, angle: int = 20, with_stroke: bool = True):
    """
    生成整页水印图片后合并
    """
    assert os.path.exists(pdf_path), "PDF不存在"
    draw_kargs = {}  # 水印参数
    draw_kargs["xy"] = (0, 0)
    # 打开PDF
    size_dict = {}
    size_list = []
    pdf = fitz.Document(pdf_path)
    # 获取PDF页面尺寸
    for page in pdf:
        size_dict[page.number] = (int(page.rect[2]) + 1, int(page.rect[3]) + 1)
    # 尺寸去重
    for size in size_dict.values():
        if size not in size_list:
            size_list.append(size)
    # 创建水印图片
    watermark_dict = {}
    for size in size_list:
        # 创建画布
        text_canvas_size = int(pow((size[0] ** 2 + size[1] ** 2), 0.5))  # 计算斜边长度
        text_canvas = Image.new("RGBA", (text_canvas_size * 4, text_canvas_size * 4))  # 提高水印分辨率
        draw = ImageDraw.Draw(text_canvas)
        # 创建字体
        if font_size == "auto":
            temp_font_size = int(text_canvas_size / 4)
            temp_font = ImageFont.truetype(font_path, temp_font_size)
            # 判断水印文字是否过长
            while draw.textbbox((0, 0), text, temp_font)[2] > 3 * text_canvas_size:
                temp_font_size = int(temp_font_size * 0.9)
                temp_font = ImageFont.truetype(font_path, temp_font_size)
            font_size = temp_font_size
        font = ImageFont.truetype(font_path, font_size)
        draw_kargs["font"] = font
        # 确定文字数量，准备要绘制的文字
        text_width, text_height = draw.textbbox((0, 0), text, font)[2:4]
        wm_text = "{}  ".format(text) * (int(text_canvas.size[0] / text_width) + 1)  # 将文字复制成画布宽度的倍数
        wm_text = "{}\n\n\n".format(wm_text) * (int(text_canvas.size[1] / text_height) + 1)  # 将文字复制成画布高度的倍数
        draw_kargs["text"] = wm_text
        if with_stroke:
            draw_kargs["stroke_fill"] = (0, 0, 0)
            draw_kargs["stroke_width"] = 1
        # 绘制文字水印
        rgba_text_color = hex_to_rgba(color, opacity)  # 转换颜色
        draw_kargs["fill"] = rgba_text_color
        draw.multiline_text(**draw_kargs)
        text_canvas = text_canvas.rotate(angle)  # 旋转画布
        text_canvas = text_canvas.resize((text_canvas_size, text_canvas_size))  # 缩放画布
        text_canvas_byte_array = io.BytesIO()
        text_canvas.save(text_canvas_byte_array, format="PNG", quality=90)
        watermark_dict[size] = (text_canvas_byte_array.getvalue(), text_canvas_size)
    # 将水印添加至PDF
    for page in pdf:
        x0 = int((page.rect[2] - watermark_dict[size_dict[page.number]][1]) / 2)
        y0 = int((page.rect[3] - watermark_dict[size_dict[page.number]][1]) / 2)
        x1 = int(page.rect[2] - x0)
        y1 = int(page.rect[3] - y0)
        watermark_rect = fitz.Rect(x0, y0, x1, y1)
        page.insert_image(watermark_rect, stream=watermark_dict[size_dict[page.number]][0])
    # 保存PDF
    pdf.save("{}_wm.pdf".format(os.path.splitext(pdf_path)[0]), garbage=3, deflate=True)


# https://pymupdf.readthedocs.io/en/latest/page.html#Page.write_text
# https://pymupdf.readthedocs.io/en/latest/shape.html#Shape.insert_textbox
# https://pymupdf.readthedocs.io/en/latest/textwriter.html#textwriter
# 给PDF添加文字水印
def add_text_watermark_to_pdf(pdf_path: str, text: str, font_path: str = resource_path(os.path.join('fonts', 'SourceHanSansCN-Regular.otf')), font_size: int | str = "auto", color: str = "#696969", opacity: int = 30, angle: int = 20, with_stroke: bool = True):
    assert os.path.exists(pdf_path), "PDF不存在"
    # 打开PDF
    size_dict = {}
    size_list = []
    pdf = fitz.Document(pdf_path)
    # 获取PDF页面尺寸
    for page in pdf:
        size_dict[page.number] = (int(page.rect[2]), int(page.rect[3]))
    # 尺寸去重
    for size in size_dict.values():
        if size not in size_list:
            size_list.append(size)
    # 创建字体
    font = fitz.Font(fontfile=font_path)
    most_freq_size = get_most_freq_value_in_dict(size_dict)
    hypotenuse_len = int(pow((most_freq_size[0] ** 2 + most_freq_size[1] ** 2), 0.5))  # 计算斜边长度
    if font_size == "auto":
        temp_font_size = most_freq_size[1] / 12
        while font.text_length(text, fontsize=temp_font_size) > 0.6 * hypotenuse_len:
            temp_font_size = int(temp_font_size * 0.9)
        font_size = temp_font_size
    font_length = font.text_length(text, fontsize=font_size)  # 获取文字长度
    # 创建不同尺寸的水印TextWriter
    watermark_dict = {}
    for size in size_list:
        wm_rect = fitz.Rect(0, 0, size[0], size[1])
        tw = fitz.TextWriter(wm_rect, opacity=opacity / 100, color=tuple(x/255 for x in hex_to_rgba(color, opacity))[0:3])
        h = 0
        text_rect = fitz.Rect(0, 0, font_length, 1.5 * font_size)
        # 根据文字高度和长度填充水印TextWriter
        while h < size[1]:
            text_rect.x0 = 0
            w = 0
            while w < size[0]:
                tw.fill_textbox(text_rect, text, font=font, fontsize=font_size)
                text_rect += fitz.Rect(font_length + 50, 0, font_length + 50, 0)
                w += font_length
            text_rect += fitz.Rect(0, 4 * font_size, 0, 4 * font_size)
            h += (font_size * 1.5)
        # tw.fill_textbox(text_rect, text, font=font, fontsize=font_size)
        watermark_dict[size] = tw
    # 将水印添加至PDF
    for page in pdf:
        rotate_morph = (fitz.Point(int(page.rect[2] / 2), int(page.rect[3] / 2)), fitz.Matrix(1, 0, 0, 1, 0, 0).prerotate(angle))
        watermark_dict[size_dict[page.number]].write_text(page, morph=rotate_morph)
        # page.write_text(writers=watermark_dict[size_dict[page.number]])
    # 保存PDF
    pdf.save("{}_wm.pdf".format(os.path.splitext(pdf_path)[0]), garbage=3, deflate=True)


if __name__ == "__main__":
    # add_text_watermark_to_image(resource_path("test.jpg"), '测试水印', color="#ff0000")
    # add_text_watermark_to_pdf(resource_path("test.pdf"), '测试水印abcdefghijklmnopqrstuvwxyz')
    add_text_watermark_to_pdf(resource_path("test.pdf"), '测试水印abcdefghijklmnopqrstuvwxyz')
