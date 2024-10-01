import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import threading
import time
import cv2

from visual import extract_frame

class ImageDeformationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tracking Tool")

        # 设置主窗口的初始尺寸
        self.root.geometry('800x800')
        self.root.minsize(800, 600)

        self.canvas_width   = 800
        self.canvas_height  = 400
        
        self.rectangle_scale  = 1/20
        # 初始化变量
        self.image = None
        self.photo = None
        self.line  = None
        self.start_x = None
        self.start_y = None

        self.battens = None
        self.lines = []
        self.line_coords = []
        self.line_coords_np = []
        self.group_numbers = []  # 保存每个矩形所属的组号

        self.current_group = 1  # 当前组号

        # 创建界面组件
        self.create_widgets()

    def create_widgets(self):
        # 顶部输入图片路径的框架
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=5)

        self.path_label = tk.Label(self.top_frame, text="Video Path (*.mp4, *.avi):")
        self.path_label.pack(side=tk.LEFT)

        self.path_entry = tk.Entry(self.top_frame, width=50)
        self.path_entry.pack(side=tk.LEFT, padx=5)

        self.load_button = tk.Button(self.top_frame, text="Load", command=self.load_video)
        self.load_button.pack(side=tk.LEFT, padx=5)

        # 组号显示和控制按钮
        self.group_frame = tk.Frame(self.root)
        self.group_frame.pack(pady=5)

        self.group_label = tk.Label(self.group_frame, text=f"Batten Group {self.current_group}")
        self.group_label.pack(side=tk.LEFT)

        self.next_group_button = tk.Button(self.group_frame, text="Next group", command=self.next_group)
        self.next_group_button.pack(side=tk.LEFT, padx=5)

        self.previous_group_button  = tk.Button(self.group_frame, text="Previous group", command=self.previous_group)
        self.previous_group_button.pack(side=tk.LEFT, padx=5)

        self.cancel_group_button = tk.Button(self.group_frame, text="Clear all", command=self.cancel_group)
        self.cancel_group_button.pack(side=tk.LEFT, padx=5)

        # 显示图片的画布和滚动条
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(expand=True, fill=tk.BOTH)

        # 创建Canvas并绑定滚动条，设置较大的尺寸
        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            cursor="cross"
        )
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        # 创建一个新的框架用于放置滑块
        self.slider_frame = tk.Frame(self.root)
        self.slider_frame.pack(fill=tk.X)
        self.frame_slider = tk.Scale(self.root, from_=0, to=0, orient=tk.HORIZONTAL, command=self.show_frame)
        self.frame_slider.pack(fill=tk.X)

        # 确认和取消按钮
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=5)

        self.confirm_button = tk.Button(self.button_frame, text="Confirm", command=self.confirm_selection)
        self.confirm_button.pack(side=tk.LEFT, padx=5)

        self.cancel_button = tk.Button(self.button_frame, text="Cancel", command=self.cancel_selection)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = tk.Button(self.button_frame, text="Delete", command=self.delete_selected)
        self.delete_button.pack(pady=5)

        # 带滚动条的坐标列表框架
        self.list_frame = tk.Frame(self.root)
        self.list_frame.pack(pady=5, fill=tk.BOTH, expand=True)

        self.list_scrollbar = tk.Scrollbar(self.list_frame)
        self.list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.coord_listbox = tk.Listbox(
            self.list_frame, width=60, height=6, yscrollcommand=self.list_scrollbar.set
        )
        self.coord_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.list_scrollbar.config(command=self.coord_listbox.yview)

        # 删除按钮
        self.GetDeformation_button = tk.Button(self.root, text="get deformation", command=self.get_deformation)
        self.GetDeformation_button.pack(pady=5)

    def show_frame(self, frame_number):
        if self.cap:
            frame_number = int(frame_number)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                original_width, original_height = frame.shape[1], frame.shape[0]

                # 获取 Canvas 的尺寸
                self.canvas.update_idletasks()
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()

                self.rect_width  = canvas_width * self.rectangle_scale
                self.rect_height = canvas_height * self.rectangle_scale 

                # 计算缩放比例，保持宽高比
                scale_w = canvas_width / original_width
                scale_h = canvas_height / original_height
                scale = min(scale_w, scale_h)

                new_width = int(original_width * scale)
                new_height = int(original_height * scale)

                img = Image.fromarray(frame)
                img = img.resize((new_width, new_height), Image.LANCZOS)
                imgtk = ImageTk.PhotoImage(image=img)
                self.canvas.delete("all")
                x = (canvas_width - new_width) // 2
                y = (canvas_height - new_height) // 2
                self.canvas.create_image(x, y, anchor=tk.NW, image=imgtk)
                self.canvas.image = imgtk

                self.canvas.bind("<ButtonPress-1>", self.on_button_press)
                self.canvas.bind("<B1-Motion>", self.on_move_press)
                self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
            else:
                print("Can not get the frame!")


    def load_video(self):
        # 让用户选择视频文件
        self.video_path = filedialog.askopenfilename(filetypes=[("Video file", "*.mp4;*.avi;*.mov")])
        if self.video_path:
            # 使用 OpenCV 加载视频
            self.cap = cv2.VideoCapture(self.video_path)
            if self.cap.isOpened():
                # 获取视频的总帧数
                self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                # 更新滑块的最大值
                self.frame_slider.config(to=self.total_frames - 1)
                
                # 获取视频的原始尺寸
                original_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                original_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                # 设置 Canvas 的尺寸（保持最大为 800x400）
                max_canvas_width = 800
                max_canvas_height = 400
                
                # 计算缩放比例，保持宽高比
                self.scale_w = max_canvas_width / original_width
                self.scale_h = max_canvas_height / original_height
                scale = min(self.scale_w, self.scale_h, 1)  # 确保不放大图像
                
                # 计算新的 Canvas 尺寸
                canvas_width = int(original_width * scale)
                canvas_height = int(original_height * scale)
                
                # 更新 Canvas 尺寸
                self.canvas.config(width=canvas_width, height=canvas_height)
                
                # 更新 Canvas 的滚动区域
                self.canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))
                
                # 显示第一帧
                self.show_frame(0)
            else:
                print("Can not open the file!")

    def on_button_press(self, event):
        # 保存起始点
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        # 创建矩形
        if self.line:
            self.canvas.delete(self.line)
            self.line = None
            
        self.line = self.canvas.create_line(
            self.start_x, self.start_y, self.start_x, self.start_y, fill='green', width=4
        )

    def on_move_press(self, event):
        curX, curY = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

        # 随鼠标拖动更新矩形大小
        self.canvas.coords(self.line, self.start_x, self.start_y, curX, curY)

    def on_button_release(self, event):
        pass  # 通过“确定”按钮处理确认

    def confirm_selection(self):
        if self.line:
            if not self.current_group in self.group_numbers:
                coords = self.canvas.coords(self.line)
                # 将坐标转换为 numpy 数组
                coords[0] = int(coords[0] / self.scale_w)
                coords[1] = int(coords[1] / self.scale_h)
                coords[2] = int(coords[2] / self.scale_w)
                coords[3] = int(coords[3] / self.scale_h)
                coords_np = np.array([[coords[0] - self.rect_width/2 ,coords[2] + self.rect_height /2, coords[0] + self.rect_width/2 ,coords[2] - self.rect_height /2], \
                                      [coords[1] - self.rect_width/2 ,coords[3] + self.rect_height /2, coords[1] + self.rect_width/2 ,coords[3] - self.rect_height /2]])
                # 添加到列表
                self.lines.append(self.line)
                self.line_coords.append(coords)
                self.line_coords_np.append(coords_np)
                self.group_numbers.append(self.current_group)
                # 显示在列表框中，包含组号信息
                self.coord_listbox.insert(
                    tk.END, f"Batten {self.current_group}: From ({coords[0]}, {coords[1]}) to ({coords[2]}, {coords[3]})"
                )
                self.line = None
                self.current_group += 1
                self.group_label.config( text=f"Batten Group {self.current_group}")
            else:
                self.canvas.delete(self.line)
                self.line = None
                messagebox.showwarning("Warning", "Batten have existed.")
        else:
            messagebox.showwarning("Warning", "No line to identify.")

    def cancel_selection(self):
        if self.line:
            self.canvas.delete(self.line)
            self.line = None
        else:
            messagebox.showwarning("Warning", "No line to identify.")

    def delete_selected(self):
        selected = self.coord_listbox.curselection()
        if selected:
            index = selected[0]
            # 从画布中删除矩形
            self.canvas.delete(self.lines[index])
            # 从列表中删除
            del self.lines[index]
            del self.line_coords[index]
            del self.line_coords_np[index]
            del self.group_numbers[index]
            # 从列表框中删除
            self.coord_listbox.delete(index)
        else:
            messagebox.showwarning("Warning", "Please select the item to delete.")

    def get_deformation(self):
        # Create a popup window
        self.waiting_window = tk.Toplevel(self.root)
        self.waiting_window.title("Processing")
        tk.Label(self.waiting_window, text="Waiting for processing ...").pack(padx=20, pady=20)
        # Execute tracking in a new thread
        threading.Thread(target=self.run_tracking_fitting).start()

    def run_tracking_fitting(self):
        self.batten_groups = {}
        for arr, num in zip(self.line_coords_np, self.group_numbers):
            if num not in self.batten_groups:
                self.batten_groups[num] = []
            self.batten_groups[num].append(arr)
    

        for num,group in self.batten_groups.items():
            print(num, group)
        
        self.tracking_fitting_one()
        # Close the waiting window in the main thread
        self.root.after(0, self.waiting_window.destroy)

    def tracking_fitting_one(self):
        # Your tracking function implementation
        time.sleep(5)
        pass

    def next_group(self):
        # 增加组号
        self.current_group += 1
        self.group_label.config(text=f"Batten Group {self.current_group}")

    def previous_group(self):
        self.current_group -= 1
        self.group_label.config(text=f"Batten Group {self.current_group}")

    def cancel_group(self):
        # 重置组号
        self.current_group = 1
        self.group_label.config(text=f"Batten Group {self.current_group}")
        # 清空所有矩形和列表
        for line in self.lines:
            self.canvas.delete(line)
        self.lines.clear()
        self.line_coords.clear()
        self.line_coords_np.clear()
        self.group_numbers.clear()
        self.coord_listbox.delete(0, tk.END)

class ImageAnnotationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tracking Tool")

        # 设置主窗口的初始尺寸
        self.root.geometry('1200x800')
        self.root.minsize(800, 600)

        # 初始化变量
        self.image = None
        self.photo = None
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.rectangles = []
        self.rect_coords = []
        self.rect_coords_np = []
        self.group_numbers = []  # 保存每个矩形所属的组号

        self.current_group = 1  # 当前组号

        # 创建界面组件
        self.create_widgets()

    def create_widgets(self):
        # 顶部输入图片路径的框架
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=5)

        self.path_label = tk.Label(self.top_frame, text="Video Path (*.mp4, *.avi):")
        self.path_label.pack(side=tk.LEFT)

        self.path_entry = tk.Entry(self.top_frame, width=50)
        self.path_entry.pack(side=tk.LEFT, padx=5)

        self.browse_button = tk.Button(self.top_frame, text="Browse", command=self.browse_image)
        self.browse_button.pack(side=tk.LEFT)

        self.load_button = tk.Button(self.top_frame, text="Load", command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5)

        # 组号显示和控制按钮
        self.group_frame = tk.Frame(self.root)
        self.group_frame.pack(pady=5)

        self.group_label = tk.Label(self.group_frame, text=f"Batten Group {self.current_group}")
        self.group_label.pack(side=tk.LEFT)

        self.next_group_button = tk.Button(self.group_frame, text="Next group", command=self.next_group)
        self.next_group_button.pack(side=tk.LEFT, padx=5)

        self.previous_group_button  = tk.Button(self.group_frame, text="Previous group", command=self.previous_group)
        self.previous_group_button.pack(side=tk.LEFT, padx=5)

        self.cancel_group_button = tk.Button(self.group_frame, text="Clear all", command=self.cancel_group)
        self.cancel_group_button.pack(side=tk.LEFT, padx=5)

        # 显示图片的画布和滚动条
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(expand=True, fill=tk.BOTH)

        # 创建垂直和水平滚动条
        self.v_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.h_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # 创建Canvas并绑定滚动条，设置较大的尺寸
        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=800,
            height=400,
            xscrollcommand=self.h_scrollbar.set,
            yscrollcommand=self.v_scrollbar.set,
            cursor="cross"
        )
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.h_scrollbar.config(command=self.canvas.xview)
        self.v_scrollbar.config(command=self.canvas.yview)

        # 确认和取消按钮
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=5)

        self.confirm_button = tk.Button(self.button_frame, text="Confirm", command=self.confirm_selection)
        self.confirm_button.pack(side=tk.LEFT, padx=5)

        self.cancel_button = tk.Button(self.button_frame, text="Cancel", command=self.cancel_selection)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = tk.Button(self.button_frame, text="Delete", command=self.delete_selected)
        self.delete_button.pack(pady=5)

        # 带滚动条的坐标列表框架
        self.list_frame = tk.Frame(self.root)
        self.list_frame.pack(pady=5, fill=tk.BOTH, expand=True)

        self.list_scrollbar = tk.Scrollbar(self.list_frame)
        self.list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.coord_listbox = tk.Listbox(
            self.list_frame, width=60, height=6, yscrollcommand=self.list_scrollbar.set
        )
        self.coord_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.list_scrollbar.config(command=self.coord_listbox.yview)

        # 删除按钮
        self.CompleteSelection_button = tk.Button(self.root, text="Complete Selection", command=self.complete_selection)
        self.CompleteSelection_button.pack(pady=5)

    def browse_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, file_path)

    def load_image(self):
        image_path = self.path_entry.get()

        if image_path:
            try:
                self.image = Image.fromarray(extract_frame(image_path,1))
                self.photo = ImageTk.PhotoImage(self.image)
                self.canvas.config(scrollregion=(0, 0, self.photo.width(), self.photo.height()))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
                self.canvas.bind("<ButtonPress-1>", self.on_button_press)
                self.canvas.bind("<B1-Motion>", self.on_move_press)
                self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
            except Exception as e:
                messagebox.showerror("Error", "Loading Failed:\n" + str(e))
        else:
            messagebox.showwarning("Warning", "Please input the Image path")

    def on_button_press(self, event):
        # 保存起始点
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        # 创建矩形
        if self.rect:
            self.canvas.delete(self.rect)
            self.rect = None
            
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline='red'
        )

    def on_move_press(self, event):
        curX, curY = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

        # 随鼠标拖动更新矩形大小
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def on_button_release(self, event):
        pass  # 通过“确定”按钮处理确认

    def confirm_selection(self):
        if self.rect:
            coords = self.canvas.coords(self.rect)
            # 将坐标转换为 numpy 数组
            coords_np = np.array(coords)
            # 添加到列表
            self.rectangles.append(self.rect)
            self.rect_coords.append(coords)
            self.rect_coords_np.append(coords_np)
            self.group_numbers.append(self.current_group)
            # 显示在列表框中，包含组号信息
            self.coord_listbox.insert(
                tk.END, f"Batten Group {self.current_group} - rectangle {len(self.rectangles)}: Top left({coords[0]}, {coords[1]}), Bottom right({coords[2]}, {coords[3]})"
            )
            self.rect = None
        else:
            messagebox.showwarning("Warning", "No rectangle to identify.")

    def cancel_selection(self):
        if self.rect:
            self.canvas.delete(self.rect)
            self.rect = None
        else:
            messagebox.showwarning("Warning", "No rectangle to identify.")

    def delete_selected(self):
        selected = self.coord_listbox.curselection()
        if selected:
            index = selected[0]
            # 从画布中删除矩形
            self.canvas.delete(self.rectangles[index])
            # 从列表中删除
            del self.rectangles[index]
            del self.rect_coords[index]
            del self.rect_coords_np[index]
            del self.group_numbers[index]
            # 从列表框中删除
            self.coord_listbox.delete(index)
        else:
            messagebox.showwarning("Warning", "Please select the item to delete.")

    def complete_selection(self):
        # Create a popup window
        self.waiting_window = tk.Toplevel(self.root)
        self.waiting_window.title("Processing")
        tk.Label(self.waiting_window, text="Waiting for tracking ...").pack(padx=20, pady=20)
        # Execute tracking in a new thread
        threading.Thread(target=self.run_tracking).start()

    def run_tracking(self):
        self.batten_groups = {}
        for arr, num in zip(self.rect_coords_np, self.group_numbers):
            if num not in self.batten_groups:
                self.batten_groups[num] = []
            self.batten_groups[num].append(arr)
    

        # for num,group in self.batten_groups.items():
        #     print(num, group)
        
        self.tracking()
        # Close the waiting window in the main thread
        self.root.after(0, self.waiting_window.destroy)

    def tracking(self):
        # Your tracking function implementation
        time.sleep(5)
        pass


    def next_group(self):
        # 增加组号
        self.current_group += 1
        self.group_label.config(text=f"Batten Group {self.current_group}")

    def previous_group(self):
        self.current_group -= 1
        self.group_label.config(text=f"Batten Group {self.current_group}")

    def cancel_group(self):
        # 重置组号
        self.current_group = 1
        self.group_label.config(text=f"Batten Group {self.current_group}")
        # 清空所有矩形和列表
        for rect in self.rectangles:
            self.canvas.delete(rect)
        self.rectangles.clear()
        self.rect_coords.clear()
        self.rect_coords_np.clear()
        self.group_numbers.clear()
        self.coord_listbox.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()

    # app = ImageAnnotationApp(root)
    # root.mainloop()
    
    app = ImageDeformationApp(root)
    root.mainloop()