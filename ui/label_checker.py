import os
import cv2
import requests
import tkinter as tk
from tkinter import *
from tkinter import filedialog, messagebox, ttk, scrolledtext
from io import BytesIO
from PIL import Image, ImageTk
import numpy as np


class LabelCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Label Checker")
        self.data = []
        self.current_idx = -1
        self.file_path = ""
        self.vis_dir = ""

        # UI布局
        self.create_menu()
        self.create_widgets()
        self.bind_shortcuts()

    def create_menu(self):
        menubar = Menu(self.root)
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="导入", command=self.load_file)
        file_menu.add_command(label="导出", command=self.save_file)
        menubar.add_cascade(label="文件", menu=file_menu)
        self.root.config(menu=menubar)

    def create_widgets(self):
        # 左侧图像显示
        self.img_frame = ttk.Frame(self.root)
        self.img_frame.pack(side=LEFT, fill=BOTH, expand=True)
        self.img_label = Label(self.img_frame)
        self.img_label.pack(fill=BOTH, expand=True)
        self.img_frame.bind("<Configure>", self.on_frame_resize)

        # 右侧控制面板
        control_frame = ttk.Frame(self.root, width=300)
        control_frame.pack(side=RIGHT, fill=Y)

        # 标签编辑（改为ScrolledText）
        self.text_area = scrolledtext.ScrolledText(
            control_frame, wrap=tk.WORD, height=1, font=("微软雅黑", 10)
        )
        self.text_area.pack(pady=10, padx=5, fill=BOTH, expand=True)

        # 控制按钮（重新布局）
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(pady=10)

        # 上方按钮（保存、删除）
        top_btn_frame = ttk.Frame(btn_frame)
        top_btn_frame.pack(pady=2)
        ttk.Button(top_btn_frame, text="保存", command=self.save_item).pack(
            side=LEFT, padx=3
        )
        ttk.Button(top_btn_frame, text="删除", command=self.delete_item).pack(
            side=LEFT, padx=3
        )

        # 下方按钮（上一条、下一条）
        bottom_btn_frame = ttk.Frame(btn_frame)
        bottom_btn_frame.pack(pady=2)
        ttk.Button(bottom_btn_frame, text="上一条", command=self.prev_item).pack(
            side=LEFT, padx=3
        )
        ttk.Button(bottom_btn_frame, text="下一条", command=self.next_item).pack(
            side=LEFT, padx=3
        )

        # 进度条
        self.progress_frame = ttk.Frame(control_frame)
        self.progress_frame.pack(fill=X, pady=10)

        self.progress = ttk.Scale(
            self.progress_frame, from_=0, to=0, command=self.on_progress
        )
        self.progress.pack(fill=X)

        self.pos_var = tk.StringVar()
        self.pos_label = ttk.Label(
            self.progress_frame,
            textvariable=self.pos_var,
            anchor="center",
            font=("微软雅黑", 9),
        )
        self.pos_label.pack(fill=X)

    def bind_shortcuts(self):
        # 修改后的快捷键绑定
        self.root.bind("<Control-Left>", self.on_prev_shortcut)
        self.root.bind("<Control-Right>", self.on_next_shortcut)
        self.root.bind("<Delete>", self.on_delete_shortcut)
        self.root.bind("<Control-s>", self.on_save_shortcut)

    def on_prev_shortcut(self, event):
        self.prev_item()
        return "break"

    def on_next_shortcut(self, event):
        self.next_item()
        return "break"

    def on_delete_shortcut(self, event):
        self.delete_item()
        return "break"

    def on_save_shortcut(self, event):
        self.save_item()
        return "break"

    def on_frame_resize(self, event=None):
        self.show_item()

    def load_file(self):
        path = filedialog.askopenfilename()
        if not path:
            return

        try:
            with open(path, "r") as f:
                lines = [line.strip().split("\t") for line in f.readlines()]
                if any(len(parts) != 3 for parts in lines):
                    raise ValueError("格式错误：每行必须包含3个字段")

            self.file_path = path
            self.vis_dir = os.path.join(os.path.dirname(path), "images")
            os.makedirs(self.vis_dir, exist_ok=True)

            self.data = []
            for idx, (url, caption, label) in enumerate(lines):
                img_path = self.process_image(url, caption, idx + 1)
                self.data.append(
                    {
                        "url": url,
                        "caption": caption,
                        "label": label,
                        "img_path": img_path,
                        "deleted": False,
                    }
                )

            self.current_idx = 0
            self.update_progress()
            self.show_item()

        except Exception as e:
            messagebox.showerror("错误", str(e))

    def process_image(self, url, caption, line_num):
        try:
            response = requests.get(url, stream=True)
            if response.status_code != 200:
                return None

            img = Image.open(BytesIO(response.content))
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            cv2.putText(
                img_cv, caption, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2
            )

            filename = f"{line_num}_{os.path.basename(url.split('?')[0])}"
            save_path = os.path.join(self.vis_dir, filename)
            cv2.imwrite(save_path, img_cv)
            return save_path

        except Exception as e:
            print(f"Error processing image: {e}")
            return None

    def show_item(self):
        if not self.data or self.current_idx < 0:
            return

        item = self.data[self.current_idx]

        # 更新文本区域
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, item["label"])

        # 显示图像
        if item["img_path"] and os.path.exists(item["img_path"]):
            try:
                frame_width = self.img_frame.winfo_width()
                frame_height = self.img_frame.winfo_height()

                if frame_width <= 0 or frame_height <= 0:
                    return

                img_pil = Image.open(item["img_path"])
                original_width, original_height = img_pil.size

                ratio = min(
                    frame_width / original_width, frame_height / original_height
                )
                new_size = (int(original_width * ratio), int(original_height * ratio))

                img_resized = img_pil.resize(new_size, Image.LANCZOS)
                img_tk = ImageTk.PhotoImage(img_resized)

                self.img_label.config(image=img_tk)
                self.img_label.image = img_tk
            except Exception as e:
                print(f"Error loading image: {e}")

    def update_progress(self):
        total = len(self.data)
        self.progress.config(from_=1, to=total)
        self.progress.set(self.current_idx + 1)
        self.pos_var.set(f"{self.current_idx+1}/{total}")

    def prev_item(self):
        if self.current_idx > 0:
            self.current_idx -= 1
            self.show_item()
            self.update_progress()

    def next_item(self):
        if self.current_idx < len(self.data) - 1:
            self.current_idx += 1
            self.show_item()
            self.update_progress()

    def save_item(self):
        if self.current_idx >= 0:
            self.data[self.current_idx]["label"] = self.text_area.get(
                1.0, tk.END
            ).strip()

    def delete_item(self):
        if self.current_idx >= 0:
            self.data[self.current_idx]["deleted"] = True
            self.next_item()

    def on_progress(self, value):
        idx = int(float(value)) - 1
        if 0 <= idx < len(self.data):
            self.current_idx = idx
            self.show_item()

    def save_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if not path:
            return

        output = []
        for item in self.data:
            if not item["deleted"]:
                output.append(f"{item['url']}\t{item['caption']}\t{item['label']}\n")

        try:
            with open(path, "w") as f:
                f.writelines(output)
            messagebox.showinfo("成功", "文件保存成功")
        except Exception as e:
            messagebox.showerror("错误", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = LabelCheckerApp(root)
    root.geometry("1200x1200")
    root.mainloop()
