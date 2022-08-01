import colorsys
import os
import sys

from PIL import Image, ImageDraw, ImageFont

# pip install pillow
# pip install borb


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
    img.paste(text_canvas, (int((img.size[0] - text_canvas_size)/2), int((img.size[1] - text_canvas_size)/2)), text_canvas)
    # img.show()
    # 保存图片
    if os.path.splitext(img_path)[1] != ".png":
        img = img.convert("RGB")
    img.save("{}_wm.{}".format(os.path.splitext(img_path)[0], os.path.splitext(img_path)[1]), quality=90)
    # 关闭图片
    img.close()


# 给PDF添加文字水印
def add_text_watermark_to_pdf(pdf_path: str, text: str, font_path: str = resource_path(os.path.join('fonts', 'SourceHanSansCN-Regular.otf')), font_size: int | str = "auto", color: str = "#696969", opacity: int = 30, angle: int = 20, with_stroke: bool = True):
    pass


if __name__ == "__main__":
    add_text_watermark_to_image(resource_path("test.jpg"), '测试水印abcdefghijklmnopqrstuvwxyz', color="#ff0000")
