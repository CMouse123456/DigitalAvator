import os
import numpy as np
import sys
import threading
from PIL import Image, ImageDraw, ImageFont, ImageTk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import tkinter.font as tkfont

# 深色主题配色方案
DARK_BG = "#EDF0F3"
DARK_FG = "#6B6A6A"
ACCENT_COLOR = "#0C0C0C"
HIGHLIGHT_COLOR = "#83838A"
BUTTON_COLOR = "#635F64"
BUTTON_HOVER = "#5E565D"
SLIDER_COLOR = "#665A6200"
TEXT_COLOR = "#FFFFFF"

class AsciiArtGenerator:
    """高级ASCII艺术生成器"""
    
    # 默认字符集（从深到浅）
    ASCII_CHARS = "@$B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
    
    def __init__(self):
        self.font_cache = {}
        self.default_font_paths = [
            '/System/Library/Fonts/Menlo.ttc',      # macOS
            '/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf',  # Ubuntu
            'C:/Windows/Fonts/consola.ttf',         # Windows
            'C:/Windows/Fonts/lucon.ttf',           # Windows
            'C:/Windows/Fonts/CascadiaMono.ttf'     # 清晰度更高的现代字体
        ]
    
    def generate_ascii_art(self, image_path, output_width=200, contrast=1.2, gamma=0.8):
        """生成ASCII艺术"""
        try:
            # 打开图片并转换为灰度
            img = Image.open(image_path)
            img = img.convert('L')
            
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
            img = img.resize((output_width, new_height), Image.LANCZOS)
            
            # 获取像素数据
            pixels = np.array(img)
            
            # 高精度灰度到字符映射
            char_length = len(self.ASCII_CHARS)
            # 将像素值映射到0-1范围
            normalized = pixels.astype(np.float32) / 255.0
            # 应用gamma校正增强细节
            normalized = np.power(normalized, gamma)
            # 映射到字符索引
            indices = (normalized * (char_length - 1)).astype(np.int32)
            
            # 创建ASCII字符串
            ascii_str = ''.join([self.ASCII_CHARS[i] for i in indices.flatten()])
            
            # 分割为行列表
            return [ascii_str[i:i+output_width] for i in range(0, len(ascii_str), output_width)]
        
        except Exception as e:
            raise RuntimeError(f"生成ASCII艺术失败: {str(e)}")
    
    def save_ascii_text(self, ascii_lines, output_path):
        """保存为文本文件"""
        try:
            with open(output_path, "w") as f:
                f.write('\n'.join(ascii_lines))
            return True
        except Exception as e:
            raise RuntimeError(f"保存文本文件失败: {str(e)}")
    
    def save_ascii_image(self, ascii_lines, output_path, font_size=10, 
                         bg_color=(3, 3, 3), text_color=(255, 255, 255)):
        """保存为PNG图片"""
        try:
            # 获取字体
            font = self._get_font(font_size)
            
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
            return True
        
        except Exception as e:
            raise RuntimeError(f"保存图片失败: {str(e)}")
    
    def _get_font(self, font_size):
        """获取字体对象（带缓存）"""
        # 检查缓存
        cache_key = f"{font_size}"
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        try:
            # 尝试加载字体
            font = None
            
            # 先尝试默认路径
            for path in self.default_font_paths:
                if os.path.exists(path):
                    try:
                        font = ImageFont.truetype(path, font_size)
                        break
                    except:
                        continue
            
            # 尝试常见字体名称
            if font is None:
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
            
            # 缓存字体
            self.font_cache[cache_key] = font
            return font
        
        except Exception as e:
            raise RuntimeError(f"加载字体失败: {str(e)}")


class ModernButton(ttk.Button):
    """现代风格按钮"""
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.configure(style="Modern.TButton")
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def on_enter(self, e):
        self.configure(style="Hover.TButton")
    
    def on_leave(self, e):
        self.configure(style="Modern.TButton")


class AsciiArtUI(tk.Tk):   
    def __init__(self):
        super().__init__()
        self.title("DigitalAvator")
        self.geometry("900x700")
        self.resizable(True, True)
        self.generator = AsciiArtGenerator()
        
        # 设置应用图标
        try:
            self.iconbitmap("logo.ico")
        except:
            pass
        
        # 设置现代风格
        self.configure(background=DARK_BG)
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # 创建UI元素
        self.create_widgets()
        
        # 设置默认值
        self.output_dir.set(os.getcwd())
        self.preview_var.set(1)
        self.save_text_var.set(1)
        self.save_image_var.set(1)
        
        # 绑定事件
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def configure_styles(self):
        """配置现代风格"""
        # 全局样式
        self.style.configure(".", 
                            background=DARK_BG, 
                            foreground=DARK_FG,
                            font=("consola", 10))
        
        # 框架样式
        self.style.configure("TFrame", background=DARK_BG)
        self.style.configure("TLabelframe", 
                            background=DARK_BG, 
                            foreground=ACCENT_COLOR,
                            font=("consola", 10, "bold"))
        self.style.configure("TLabelframe.Label", 
                            background=DARK_BG, 
                            foreground=ACCENT_COLOR)
        
        # 按钮样式
        self.style.configure("Modern.TButton", 
                            background=BUTTON_COLOR,
                            foreground=TEXT_COLOR,
                            borderwidth=0,
                            relief="flat",
                            font=("consola", 10, "bold"),
                            padding=6)
        self.style.map("Modern.TButton", 
                      background=[("active", BUTTON_HOVER), ("pressed", BUTTON_COLOR)])
        
        self.style.configure("Hover.TButton", 
                            background=BUTTON_HOVER,
                            foreground=TEXT_COLOR,
                            borderwidth=0,
                            relief="flat",
                            font=("consola", 10, "bold"),
                            padding=6)
        
        # 标签样式
        self.style.configure("TLabel", 
                            background=DARK_BG, 
                            foreground=DARK_FG,
                            font=("consola", 9))
        
        # 输入框样式
        self.style.configure("TEntry", 
                            fieldbackground=HIGHLIGHT_COLOR,
                            foreground=TEXT_COLOR,
                            insertcolor=TEXT_COLOR,
                            borderwidth=1,
                            relief="flat",
                            padding=5)
        
        # 滑块样式
        self.style.configure("Horizontal.TScale", 
                            background=DARK_BG,
                            troughcolor=HIGHLIGHT_COLOR)
        self.style.map("Horizontal.TScale", 
                      slidercolor=[("active", SLIDER_COLOR), ("!active", ACCENT_COLOR)])
        
        # 复选框样式
        self.style.configure("TCheckbutton", 
                            background=DARK_BG,
                            foreground=DARK_FG,
                            indicatorbackground=DARK_BG,
                            indicatordiameter=15)
        self.style.map("TCheckbutton", 
                      background=[("active", DARK_BG)],
                      indicatorcolor=[("selected", ACCENT_COLOR), ("!selected", HIGHLIGHT_COLOR)])
        
        # 状态栏样式
        self.style.configure("Status.TLabel", 
                            background=HIGHLIGHT_COLOR,
                            foreground=ACCENT_COLOR,
                            relief="sunken",
                            anchor="w",
                            font=("consola", 9),
                            padding=(5, 3))
        
        # 滚动文本框样式
        self.style.configure("consola",
                            background=HIGHLIGHT_COLOR,
                            foreground=TEXT_COLOR,
                            insertbackground=TEXT_COLOR,
                            borderwidth=1,
                            relief="flat")
    
    def create_widgets(self):
        """创建所有UI组件"""
        # 创建主框架
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(title_frame, 
                               text="DigitalAvator", 
                               font=("consola", 16, "bold"),
                               foreground=ACCENT_COLOR)
        title_label.pack(side=tk.LEFT)
        
        # 分隔线
        sep = ttk.Separator(main_frame, orient="horizontal")
        sep.pack(fill=tk.X, pady=5)
        
        # 左侧面板（输入和控制）
        left_panel = ttk.LabelFrame(main_frame, text="设置", padding=15)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 输入部分
        input_frame = ttk.Frame(left_panel)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="输入图片:").pack(side=tk.LEFT, padx=(0, 5))
        self.input_path = tk.StringVar()
        input_entry = ttk.Entry(input_frame, textvariable=self.input_path, width=40)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ModernButton(input_frame, text="浏览...", command=self.browse_image).pack(side=tk.LEFT)
        
        # 输出目录
        output_frame = ttk.Frame(left_panel)
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text="输出目录:").pack(side=tk.LEFT, padx=(0, 5))
        self.output_dir = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir, width=40)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ModernButton(output_frame, text="浏览...", command=self.browse_output).pack(side=tk.LEFT)
        
        # 参数控制
        params_frame = ttk.Frame(left_panel)
        params_frame.pack(fill=tk.X, pady=10)
        
        # 输出宽度
        width_frame = ttk.Frame(params_frame)
        width_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(width_frame, text="输出宽度:").pack(side=tk.LEFT, anchor="w", padx=(0, 10))
        self.width_var = tk.IntVar(value=200)
        self.width_label = ttk.Label(width_frame, text="200", width=5)
        self.width_label.pack(side=tk.RIGHT)
        width_scale = ttk.Scale(width_frame, from_=50, to=500, variable=self.width_var, 
                               orient=tk.HORIZONTAL, length=250)
        width_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # 对比度
        contrast_frame = ttk.Frame(params_frame)
        contrast_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(contrast_frame, text="对比度:").pack(side=tk.LEFT, anchor="w", padx=(0, 10))
        self.contrast_var = tk.DoubleVar(value=1.2)
        self.contrast_label = ttk.Label(contrast_frame, text="1.2", width=5)
        self.contrast_label.pack(side=tk.RIGHT)
        contrast_scale = ttk.Scale(contrast_frame, from_=0.5, to=3.0, variable=self.contrast_var, 
                                  orient=tk.HORIZONTAL, length=250)
        contrast_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Gamma值
        gamma_frame = ttk.Frame(params_frame)
        gamma_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(gamma_frame, text="Gamma值:").pack(side=tk.LEFT, anchor="w", padx=(0, 10))
        self.gamma_var = tk.DoubleVar(value=0.8)
        self.gamma_label = ttk.Label(gamma_frame, text="0.8", width=5)
        self.gamma_label.pack(side=tk.RIGHT)
        gamma_scale = ttk.Scale(gamma_frame, from_=0.1, to=2.0, variable=self.gamma_var, 
                               orient=tk.HORIZONTAL, length=250)
        gamma_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # 字体大小
        font_frame = ttk.Frame(params_frame)
        font_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(font_frame, text="字体大小:").pack(side=tk.LEFT, anchor="w", padx=(0, 10))
        self.font_size_var = tk.IntVar(value=8)
        self.font_size_label = ttk.Label(font_frame, text="8", width=5)
        self.font_size_label.pack(side=tk.RIGHT)
        font_scale = ttk.Scale(font_frame, from_=4, to=24, variable=self.font_size_var, 
                              orient=tk.HORIZONTAL, length=250)
        font_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # 绑定滑块事件
        width_scale.bind("<Motion>", lambda e: self.width_label.config(text=str(self.width_var.get())))
        contrast_scale.bind("<Motion>", lambda e: self.contrast_label.config(text=f"{self.contrast_var.get():.1f}"))
        gamma_scale.bind("<Motion>", lambda e: self.gamma_label.config(text=f"{self.gamma_var.get():.1f}"))
        font_scale.bind("<Motion>", lambda e: self.font_size_label.config(text=str(self.font_size_var.get())))
        
        # 输出选项
        options_frame = ttk.LabelFrame(left_panel, text="输出选项", padding=10)
        options_frame.pack(fill=tk.X, pady=10)
        
        options_inner = ttk.Frame(options_frame)
        options_inner.pack(fill=tk.X)
        
        self.preview_var = tk.IntVar(value=1)
        ttk.Checkbutton(options_inner, text="生成预览", variable=self.preview_var).pack(side=tk.LEFT, padx=10, pady=5)
        
        self.save_text_var = tk.IntVar(value=1)
        ttk.Checkbutton(options_inner, text="保存文本文件", variable=self.save_text_var).pack(side=tk.LEFT, padx=10, pady=5)
        
        self.save_image_var = tk.IntVar(value=1)
        ttk.Checkbutton(options_inner, text="保存PNG图片", variable=self.save_image_var).pack(side=tk.LEFT, padx=10, pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X, pady=10)
        
        ModernButton(button_frame, text="开始生成", command=self.start_generation).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ModernButton(button_frame, text="打开输出目录", command=self.open_output_dir).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ModernButton(button_frame, text="退出", command=self.on_close).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 状态栏
        status_frame = ttk.Frame(left_panel)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="就绪：选择图片并点击生成按钮")
        status_bar = ttk.Label(status_frame, 
                              textvariable=self.status_var, 
                              style="Status.TLabel")
        status_bar.pack(fill=tk.X)
        
        # 右侧面板（预览）
        right_panel = ttk.LabelFrame(main_frame, text="预览", padding=15)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 预览区域
        preview_frame = ttk.Frame(right_panel)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_text = scrolledtext.ScrolledText(
                preview_frame, 
                wrap=tk.NONE,
                font=("Consolas", 8),
                width=80,
                height=30,
                bg=HIGHLIGHT_COLOR,
                fg=TEXT_COLOR,
                insertbackground=TEXT_COLOR
            )

        self.preview_text.pack(fill=tk.BOTH, expand=True)

    def browse_image(self):
        """浏览选择图片"""
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图像文件", "*.jpg *.jpeg *.png *.bmp"), ("所有文件", "*.*")]
        )
        if file_path:
            self.input_path.set(file_path)
            self.status_var.set(f"已选择: {os.path.basename(file_path)}")
    
    def browse_output(self):
        """浏览选择输出目录"""
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.output_dir.set(dir_path)
    
    def open_output_dir(self):
        """打开输出目录"""
        output_dir = self.output_dir.get()
        if os.path.exists(output_dir):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(output_dir)
                elif os.name == 'posix':  # macOS, Linux
                    if sys.platform == 'darwin':
                        os.system(f'open "{output_dir}"')
                    else:
                        os.system(f'xdg-open "{output_dir}"')
            except Exception as e:
                messagebox.showerror("错误", f"无法打开目录: {str(e)}")
        else:
            messagebox.showwarning("警告", "输出目录不存在!")
    
    def start_generation(self):
        """开始生成ASCII,在后台线程"""
        input_path = self.input_path.get()
        if not input_path or not os.path.exists(input_path):
            messagebox.showwarning("警告", "请先选择有效的图片文件!")
            return
        
        # 禁用按钮防止重复点击
        for widget in self.winfo_children():
            if isinstance(widget, (ttk.Button, ModernButton)):
                widget.config(state=tk.DISABLED)
        
        # 更新状态
        self.status_var.set("处理中...")
        
        # 在后台线程中运行生成过程
        threading.Thread(target=self.generate_ascii, daemon=True).start()
    
    def generate_ascii(self):
        """生成ascciArt的核心方法"""
        try:
            # 获取输入参数
            input_path = self.input_path.get()
            output_dir = self.output_dir.get()
            
            # 验证输入
            if not input_path or not os.path.exists(input_path):
                self.status_var.set("请选择有效的图片文件!")
                return
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 准备输出路径
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            txt_path = os.path.join(output_dir, f"{base_name}_ascii.txt")
            png_path = os.path.join(output_dir, f"{base_name}_ascii.png")
            
            # 生成ASCII艺术
            ascii_lines = self.generator.generate_ascii_art(
                input_path,
                output_width=self.width_var.get(),
                contrast=self.contrast_var.get(),
                gamma=self.gamma_var.get()
            )
            
            # 显示预览
            if self.preview_var.get() == 1:
                # 只显示前100行以避免界面卡顿
                preview_text = '\n'.join(ascii_lines[:100])
                self.preview_text.config(state=tk.NORMAL)
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(tk.END, preview_text)
                self.preview_text.config(state=tk.DISABLED)
            
            # 保存文本文件
            if self.save_text_var.get() == 1:
                self.generator.save_ascii_text(ascii_lines, txt_path)
            
            # 保存PNG图片
            if self.save_image_var.get() == 1:
                self.generator.save_ascii_image(
                    ascii_lines,
                    png_path,
                    font_size=self.font_size_var.get(),
                    bg_color=(3, 3, 3),
                    text_color=(255, 255, 255)
                )
            
            self.status_var.set(f"完成! 输出到: {output_dir}")
        
        except Exception as e:
            self.status_var.set(f"错误: {str(e)}")
            messagebox.showerror("错误", str(e))
        finally:
            # 重新启用按钮
            for widget in self.winfo_children():
                if isinstance(widget, (ttk.Button, ModernButton)):
                    widget.config(state=tk.NORMAL)
    
    def on_close(self):
        """关闭窗口前的清理工作"""
        if messagebox.askokcancel("退出", "确定要退出程序吗?"):
            self.destroy()


if __name__ == "__main__":
    # 检查必要的库
    try:
        import numpy as np
        from PIL import Image
    except ImportError as e:
        print(f"错误: 缺少必要的库 - {e}")
        print("请安装: pip install pillow numpy")
        exit(1)
    
    # 创建并运行UI
    app = AsciiArtUI()
    app.mainloop()