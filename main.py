import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
from PIL import Image, ImageTk
import pygame
import os

# Asset mapping
image_files = {
    "Barot Valley": "D:\\vscode\\New folder\\pormodore\\assests\\Barot Valley.jpg",
    "Lawson mount fuji": "D:\\vscode\\New folder\\pormodore\\assests\\japan_mount_fuji.jpg",
    "Japan": "D:\\vscode\\New folder\\pormodore\\assests\\japanese_nature.jpg",
    "Waterfall": "D:\\vscode\\New folder\\pormodore\\assests\\Meghalaya_waterfall.jpg",
    "Parvati Valley Kalga": "D:\\vscode\\New folder\\pormodore\\assests\\Parvati_valley_kalga.jpg"
}

music_files = {
    "Barot Valley": "D:\\vscode\\New folder\\pormodore\\assests\\birds.mp3",
    "Lawson mount fuji": "D:\\vscode\\New folder\\pormodore\\assests\\dark academia.mp3",
    "Meghalaya": "D:\\vscode\\New folder\\pormodore\\assests\\rain.mp3",
    "Waterfall": "D:\\vscode\\New folder\\pormodore\\assests\\waves.mp3",
    "Parvati Valley Kalga": "D:\\vscode\\New folder\\pormodore\\assests\\lofi.mp3"
}

theme_list = list(image_files.keys())

POMODORO_MODES = {
    "Focus": 25 * 60,
    "Short Break": 5 * 60,
    "Long Break": 15 * 60
}

icon_path = "D:\\New folder (3)\\New folder\\pormodore\\assests\\"

class ThemedPomodoro:
    def __init__(self, root):
        self.root = root
        self.root.title("Themed Pomodoro Timer")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        pygame.mixer.init()

        self.theme_var = tk.StringVar(value=theme_list[0])
        theme_menu = ttk.Combobox(root, textvariable=self.theme_var, values=theme_list, state="readonly")
        theme_menu.place(x=10, y=10)
        theme_menu.bind("<<ComboboxSelected>>", self.update_theme)

        self.music_btn = tk.Button(root, text="Select Music", command=self.select_music)
        self.music_btn.place(x=200, y=10)

        self.play_btn = tk.Button(root, text="Play Music", command=self.play_music)
        self.play_btn.place(x=320, y=10)
        self.stop_btn = tk.Button(root, text="Stop Music", command=self.stop_music)
        self.stop_btn.place(x=400, y=10)

        self.volume_scale = tk.Scale(root, from_=0, to=100, orient="horizontal", command=self.set_volume, label="Volume")
        self.volume_scale.set(50)
        self.volume_scale.place(x=500, y=0)

        self.img_label = tk.Label(root, bd=0)
        self.img_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.img_label.bind("<Button-1>", self.next_theme)

        self.current_mode = "Focus"
        self.time_left = POMODORO_MODES[self.current_mode]
        self.timer_running = False

        # Fixed bg color from "" to "#222"
        self.tab_frame = tk.Frame(root, bg="#222", bd=0)
        self.tab_frame.place(relx=0.5, rely=0.08, anchor="n")
        self.tabs = {}
        for idx, mode in enumerate(POMODORO_MODES):
            btn = tk.Button(self.tab_frame, text=mode, font=("Helvetica", 12, "bold"),
                            command=lambda m=mode: self.change_mode(m),
                            bg="#222" if mode == "Focus" else "#333",
                            fg="#fff", activebackground="#444", activeforeground="#fff",
                            relief="flat", padx=10, pady=2)
            btn.grid(row=0, column=idx, padx=2)
            self.tabs[mode] = btn

        self.focus_title = tk.StringVar(value="click to add focus title")
        self.title_label = tk.Label(root, textvariable=self.focus_title, font=("Helvetica", 14),
                                    fg="#fff", bg="#000", cursor="hand2")
        self.title_label.place(relx=0.5, rely=0.16, anchor="n")
        self.title_label.bind("<Button-1>", self.edit_title)

        self.timer_label = tk.Label(root, text=self.format_time(self.time_left),
                                    font=("Helvetica", 48, "bold"), fg="#fff", bg="#000")
        self.timer_label.place(relx=0.5, rely=0.25, anchor="n")

        self.start_btn = tk.Button(root, text="Start Timer", font=("Helvetica", 14, "bold"),
                                   command=self.start_timer, bg="#222", fg="#fff", width=16)
        self.start_btn.place(relx=0.5, rely=0.5, anchor="n")

        self.stop_btn_timer = tk.Button(root, text="Stop", command=self.stop_timer, bg="#333", fg="#fff")
        self.stop_btn_timer.place(relx=0.42, rely=0.6, anchor="n")
        self.reset_btn = tk.Button(root, text="Reset", command=self.reset_timer, bg="#333", fg="#fff")
        self.reset_btn.place(relx=0.58, rely=0.6, anchor="n")

        self.toolbar = tk.Frame(root, bg="#222")
        self.toolbar.place(relx=0, rely=1, relwidth=1, anchor="sw", height=60)

        self.icons = {}
        icon_names = [
            ("image", "icon_image.png"),
            ("cloud", "icon_cloud.png"),
            ("briefcase", "icon_briefcase.png"),
            ("alarm", "icon_alarm.png"),
            ("music", "icon_music.png"),
            ("checklist", "icon_checklist.png"),
        ]
        for name, filename in icon_names:
            try:
                img = Image.open(os.path.join(icon_path, filename)).resize((36, 36))
                self.icons[name] = ImageTk.PhotoImage(img)
            except Exception as e:
                self.icons[name] = tk.PhotoImage(width=36, height=36)

        self.toolbar_buttons = []
        for idx, (name, _) in enumerate(icon_names):
            if name == "alarm":
                btn = tk.Button(
                    self.toolbar,
                    image=self.icons[name],
                    bg="#222",
                    bd=0,
                    highlightthickness=2,
                    highlightbackground="#ff9800",
                    activebackground="#444",
                    command=lambda n=name: self.toolbar_action(n)
                )
            else:
                btn = tk.Button(
                    self.toolbar,
                    image=self.icons[name],
                    bg="#222",
                    bd=0,
                    highlightthickness=0,
                    activebackground="#444",
                    command=lambda n=name: self.toolbar_action(n)
                )
            btn.grid(row=0, column=idx, padx=16, pady=8)
            self.toolbar_buttons.append(btn)

        self.signature_label = tk.Label(
            root,
            text="study with Abhijeet Ranjan",
            font=("Helvetica", 10, "italic"),
            fg="#fff",
            bg="#222"
        )
        self.signature_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.signature_label.lift()

        for widget in [theme_menu, self.music_btn, self.play_btn, self.stop_btn, self.volume_scale,
                       self.tab_frame, self.title_label, self.timer_label,
                       self.start_btn, self.stop_btn_timer, self.reset_btn, self.toolbar, self.signature_label]:
            widget.lift()

        self.update_theme(self.theme_var.get())

    def toolbar_action(self, name):
        if name == "image":
            self.select_background_image()
        elif name == "cloud":
            print("Cloud action")
        elif name == "briefcase":
            self.change_mode("Focus")
        elif name == "alarm":
            self.change_mode("Focus")
        elif name == "music":
            self.select_music()
        elif name == "checklist":
            print("Checklist action")

    def select_background_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if file_path:
            img = Image.open(file_path).resize((800, 600))
            self.tk_img = ImageTk.PhotoImage(img)
            self.img_label.config(image=self.tk_img)
            self.img_label.image = self.tk_img

    def update_theme(self, event_or_name):
        theme_name = self.theme_var.get() if isinstance(event_or_name, tk.Event) else event_or_name
        img_path = image_files[theme_name]
        img = Image.open(img_path).resize((800, 600))
        self.tk_img = ImageTk.PhotoImage(img)
        self.img_label.config(image=self.tk_img)
        self.img_label.image = self.tk_img
        self.current_music = music_files.get(theme_name, "")

    def next_theme(self, event=None):
        current = theme_list.index(self.theme_var.get())
        next_index = (current + 1) % len(theme_list)
        self.theme_var.set(theme_list[next_index])
        self.update_theme(theme_list[next_index])

    def select_music(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if file_path:
            self.current_music = file_path

    def play_music(self):
        if hasattr(self, 'current_music') and os.path.exists(self.current_music):
            pygame.mixer.music.load(self.current_music)
            pygame.mixer.music.play(-1)

    def stop_music(self):
        pygame.mixer.music.stop()

    def set_volume(self, val):
        pygame.mixer.music.set_volume(int(val)/100)

    def format_time(self, seconds):
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d} : {m:02d} : {s:02d}"

    def change_mode(self, mode):
        self.current_mode = mode
        self.time_left = POMODORO_MODES[mode]
        self.timer_running = False
        self.timer_label.config(text=self.format_time(self.time_left))
        for m, btn in self.tabs.items():
            btn.config(bg="#222" if m == mode else "#333")

    def edit_title(self, event=None):
        new_title = simpledialog.askstring("Focus Title", "Enter focus title:", initialvalue=self.focus_title.get())
        if new_title is not None and new_title.strip() != "":
            self.focus_title.set(new_title)
        else:
            self.focus_title.set("click to add focus title")

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.countdown()

    def stop_timer(self):
        self.timer_running = False

    def reset_timer(self):
        self.time_left = POMODORO_MODES[self.current_mode]
        self.timer_label.config(text=self.format_time(self.time_left))
        self.timer_running = False

    def countdown(self):
        if self.timer_running and self.time_left > 0:
            self.timer_label.config(text=self.format_time(self.time_left))
            self.time_left -= 1
            self.root.after(1000, self.countdown)
        elif self.time_left == 0:
            self.timer_label.config(text=self.format_time(0))
            self.timer_running = False

if __name__ == "__main__":
    root = tk.Tk()
    app = ThemedPomodoro(root)
    root.mainloop()
    pygame.mixer.quit()
