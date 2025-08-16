from PIL import Image, ImageDraw, ImageFont
import os
import numpy as np

# 扩展的 ASCII 字符集（从深到浅，共70个字符）
ASCII_CHARS = "@$B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

def high_precision_image_to_ascii(image_path, output_width=200, contrast=1.2, gamma=0.8):
    """高精度图片转 ASCII 字符矩阵"""
    # 打开图片并转换为灰度
    img = Image.open(image_path)
    img = img.convert('L')  # 转换为灰度图
    
    # 应用对比度增强
    img = np.array(img)
    img = img.astype(np.float32)
    img = (img - 128) * contrast + 128
    img = np.clip(img, 0, 255).astype(np.uint8)
    img = Image.fromarray(img)
    
    # 调整尺寸（保持宽高比）
    width, height = img.size
    aspect_ratio = height / width
    # 考虑字符的高宽比（通常字符高度是宽度的2倍）
    new_height = int(output_width * aspect_ratio * 0.5)
    
    # 高质量缩放
    img = img.resize((output_width, new_height), Image.LANCZOS)  # lanczos算法提高细腻程度
    
    # 获取像素数据
    pixels = np.array(img)
    
    # 高精度灰度到字符映射
    char_length = len(ASCII_CHARS)
    # 将像素值映射到0-1范围
    normalized = pixels.astype(np.float32) / 255.0
    # 应用gamma校正增强细节
    normalized = np.power(normalized, gamma)
    # 映射到字符索引
    indices = (normalized * (char_length - 1)).astype(np.int32)
    
    # 创建ASCII字符串
    ascii_str = ''.join([ASCII_CHARS[i] for i in indices.flatten()])
    
    # 分割为行列表
    return [ascii_str[i:i+output_width] for i in range(0, len(ascii_str), output_width)]

def save_high_res_ascii(ascii_lines, output_path, font_size=8, bg_color=(0, 0, 0), text_color=(255, 255, 255)):
    """将 ASCII 字符画保存为高分辨率 PNG 图片"""
    # 加载等宽字体
    try:
        # 尝试加载更清晰的字体
        font_paths = [
            '/System/Library/Fonts/Menlo.ttc',      # macOS
            '/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf',  # Ubuntu
            'C:/Windows/Fonts/consola.ttf',         # Windows
            'C:/Windows/Fonts/lucon.ttf',           # Windows
            'C:/Windows/Fonts/CascadiaMono.ttf'     # 清晰度更高的现代字体
        ]
        
        font = None
        for path in font_paths:
            if os.path.exists(path):
                try:
                    font = ImageFont.truetype(path, font_size)
                    break
                except:
                    continue
        
        if font is None:
            # 尝试使用更常见的字体
            common_fonts = ["consola", "cour", "menlo", "dejavusansmono", "ubuntumono"]
            for name in common_fonts:
                try:
                    font = ImageFont.truetype(name, font_size)
                    break
                except:
                    continue
        
        # 最终回退
        if font is None:
            font = ImageFont.load_default()
            print("警告：使用默认字体，精度可能受限,请检查您的系统文件配置")
    except Exception as e:
        font = ImageFont.load_default()
        print(f"字体加载失败，使用默认字体: {str(e)}")

    # 计算字符尺寸
    if hasattr(font, 'getsize'):
        char_width, char_height = font.getsize("A")
    else:
        # 回退尺寸
        char_width, char_height = 6, 12
    
    # 计算图片尺寸
    img_width = char_width * len(ascii_lines[0])
    img_height = char_height * len(ascii_lines)
    
    # 创建高分辨率图片（使用RGB模式）
    img = Image.new('RGB', (img_width, img_height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # 使用抗锯齿渲染
    try:
        if hasattr(ImageFont, 'FreeTypeFont'):
            # 使用FreeType渲染器（更清晰）
            draw.fontmode = "L"  # 抗锯齿
    except Exception as e:
        print(f"抗锯齿设置失败: {str(e)}")
    
    # 绘制ASCII字符（逐行渲染）
    y = 0
    for line in ascii_lines:
        draw.text((0, y), line, fill=text_color, font=font)
        y += char_height
    
    # 保存为高质量PNG
    img.save(output_path, 'PNG', compress_level=1)
    print(f"高精度 ASCII 图片已保存至: {output_path}")
    return img

# 使用示例
if __name__ == "__main__":
    input_image = "kun.jpg"  # 输入图片路径
    output_txt = "output.txt"  # 文本输出路径
    output_png = "high_res_ascii.png"  # PNG输出路径
    
    # 生成高精度ASCII字符画（增加宽度提高细节）
    ascii_lines = high_precision_image_to_ascii(
        input_image, 
        output_width=300,  # 增加宽度获取更多细节
        contrast=1.5,      # 增强对比度
        gamma=0.7          # 调整gamma值
    )
    
    # 输出到控制台（预览）
    print('\n'.join(ascii_lines[:20]))  # 只打印前20行预览
    
    # 保存为文本文件
    with open(output_txt, "w") as f:
        f.write('\n'.join(ascii_lines))
    print(f"ASCII 文本已保存至: {output_txt}")
    
    # 保存为高分辨率PNG图片
    ascii_image = save_high_res_ascii(
        ascii_lines, 
        output_png,
        font_size=10,        # 更小的字体大小获取更多细节
        bg_color=(3, 3, 3), # 黑色背景
        text_color=(255, 255, 255) # 亮绿色文字
    )
    
    # 可选：显示生成的图片
    ascii_image.show()