import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
import os
import platform

# Try importing vlc with fix for Windows path
try:
    if platform.system() == "Windows":
        vlc_path = r"C:\Program Files\VideoLAN\VLC"
        if os.path.exists(r"C:\Program Files\VideoLAN\VLC") and hasattr(os, "add_dll_directory"):
            os.add_dll_directory(r"C:\Program Files\VideoLAN\VLC")
    import vlc
except ImportError:
    raise ImportError("The 'python-vlc' module is not installed. Install it using: pip install python-vlc")


POMODORO_MODES = {
    "Focus": 25 * 60,
    "Short Break": 5 * 60,
    "Long Break": 15 * 60
}


class VideoPomodoro:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Background Pomodoro Timer")
        self.root.geometry("800x600")
        self.root.configure(bg="#000000")  # Simulated transparency
        self.root.resizable(False, False)

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        self.current_video = None
        self.timer_running = False
        self.current_mode = "Focus"
        self.time_left = POMODORO_MODES[self.current_mode]

        self.setup_video_background()
        self.setup_timer_interface()
        self.setup_toolbar()
        self.lift_all_widgets()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_video_background(self):
        self.video_panel = tk.Frame(self.root, bg="black", highlightthickness=0, borderwidth=0)
        self.video_panel.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.root.update_idletasks()

        if os.name == "nt":
            self.player.set_hwnd(self.video_panel.winfo_id())
        else:
            self.player.set_xwindow(self.video_panel.winfo_id())

    def setup_timer_interface(self):
        self.tab_frame = tk.Frame(self.root, bg="#000000", highlightthickness=0, borderwidth=0)
        self.tab_frame.place(relx=0.5, rely=0.08, anchor="n")
        self.tabs = {}
        for idx, mode in enumerate(POMODORO_MODES):
            btn = tk.Button(self.tab_frame, text=mode, font=("Helvetica", 12, "bold"),
                            command=lambda m=mode: self.change_mode(m),
                            bg="#000000" if mode == "Focus" else "#111111",
                            fg="#ffffff", activebackground="#222222", activeforeground="#ffffff",
                            relief="flat", borderwidth=0, highlightthickness=0, padx=10, pady=2)
            btn.grid(row=0, column=idx, padx=2)
            self.tabs[mode] = btn

        self.focus_title = tk.StringVar(value="click to add focus title")
        self.title_label = tk.Label(self.root, textvariable=self.focus_title, font=("Helvetica", 14),
                                    fg="#ffffff", bg="#000000", cursor="hand2", borderwidth=0)
        self.title_label.place(relx=0.5, rely=0.16, anchor="n")
        self.title_label.bind("<Button-1>", self.edit_title)

        self.timer_label = tk.Label(self.root, text=self.format_time(self.time_left),
                                    font=("Helvetica", 48, "bold"), fg="#ffffff", bg="#000000",
                                    borderwidth=0, highlightthickness=0)
        self.timer_label.place(relx=0.5, rely=0.25, anchor="n")

        self.start_btn = tk.Button(self.root, text="Start Timer", font=("Helvetica", 14, "bold"),
                                command=self.start_timer, bg="#000000", fg="#ffffff",
                                relief="flat", borderwidth=0, highlightthickness=0, width=16)
        self.start_btn.place(relx=0.5, rely=0.5, anchor="n")

        self.stop_btn_timer = tk.Button(self.root, text="Stop Timer", command=self.stop_timer,
                                        bg="#000000", fg="#ffffff", relief="flat", borderwidth=0)
        self.stop_btn_timer.place(relx=0.42, rely=0.6, anchor="n")

        self.reset_btn = tk.Button(self.root, text="Reset Timer", command=self.reset_timer,
                                bg="#000000", fg="#ffffff", relief="flat", borderwidth=0)
        self.reset_btn.place(relx=0.58, rely=0.6, anchor="n")

    def setup_toolbar(self):
        self.toolbar = tk.Frame(self.root, bg="#000000", highlightthickness=0, borderwidth=0)
        self.toolbar.place(relx=0, rely=1, relwidth=1, anchor="sw", height=60)

        actions = [
            ("Select Video", self.select_video),
            ("Play/Pause", self.toggle_video_playback),
            ("Focus Mode", lambda: self.change_mode("Focus")),
            ("Short Break", lambda: self.change_mode("Short Break")),
            ("Long Break", lambda: self.change_mode("Long Break")),
            ("Settings", self.show_settings)
        ]

        for idx, (label, cmd) in enumerate(actions):
            tk.Button(self.toolbar, text=label, bg="#000000", fg="#ffffff", bd=0,
                    font=("Helvetica", 9), activebackground="#222222",
                    activeforeground="#ffffff", command=cmd, relief="flat", padx=8).grid(row=0, column=idx, padx=12, pady=8)

        self.volume_scale = tk.Scale(self.toolbar, from_=0, to=100, orient="horizontal",
                                    command=self.set_volume, label="Volume", bg="#000000",
                                    fg="#ffffff", highlightthickness=0, troughcolor="#444", length=120)
        self.volume_scale.set(50)
        self.volume_scale.grid(row=0, column=len(actions), padx=12, pady=5)

        self.player.audio_set_volume(50)

    def lift_all_widgets(self):
        widgets = [self.tab_frame, self.title_label, self.timer_label,
                self.start_btn, self.stop_btn_timer, self.reset_btn,
                self.toolbar]
        for widget in widgets:
            widget.lift()

    def select_video(self):
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm")]
        )
        if file_path:
            self.current_video = file_path
            messagebox.showinfo("Video Selected", f"Selected: {os.path.basename(file_path)}")
            self.stop_video()

    def play_video(self):
        if self.current_video and os.path.exists(self.current_video):
            media = self.instance.media_new(self.current_video)
            self.player.set_media(media)
            self.player.play()
            self.player.audio_set_volume(self.volume_scale.get())
        else:
            messagebox.showwarning("No Video", "Please select a video file first")

    def pause_video(self):
        self.player.pause()

    def stop_video(self):
        self.player.stop()

    def toggle_video_playback(self):
        if self.player.is_playing():
            self.pause_video()
        else:
            self.play_video()

    def set_volume(self, val):
        self.player.audio_set_volume(int(val))

    def format_time(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{h:02d} : {m:02d} : {s:02d}"

    def change_mode(self, mode):
        self.current_mode = mode
        self.time_left = POMODORO_MODES[mode]
        self.timer_running = False
        self.timer_label.config(text=self.format_time(self.time_left))
        for m, btn in self.tabs.items():
            btn.config(bg="#000000" if m == mode else "#111111")

    def edit_title(self, _=None):
        new_title = simpledialog.askstring("Focus Title", "Enter focus title:",
                                        initialvalue=self.focus_title.get())
        self.focus_title.set(new_title.strip() if new_title else "click to add focus title")

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
            messagebox.showinfo("Timer Complete", f"{self.current_mode} session completed!")

    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg="#000000")

        tk.Label(settings_window, text="Timer Durations (minutes):",
                font=("Helvetica", 12, "bold"), fg="#ffffff", bg="#000000").pack(pady=10)

        def create_entry(label_text, mode_key):
            frame = tk.Frame(settings_window, bg="#000000")
            frame.pack(pady=5)
            tk.Label(frame, text=label_text, fg="#ffffff", bg="#000000").pack(side="left")
            entry = tk.Entry(frame, width=10)
            entry.insert(0, str(POMODORO_MODES[mode_key] // 60))
            entry.pack(side="left", padx=5)
            return entry

        focus_entry = create_entry("Focus:", "Focus")
        short_entry = create_entry("Short Break:", "Short Break")
        long_entry = create_entry("Long Break:", "Long Break")

        def save_settings():
            try:
                POMODORO_MODES["Focus"] = int(focus_entry.get()) * 60
                POMODORO_MODES["Short Break"] = int(short_entry.get()) * 60
                POMODORO_MODES["Long Break"] = int(long_entry.get()) * 60
                messagebox.showinfo("Settings", "Settings saved successfully!")
                settings_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers")

        tk.Button(settings_window, text="Save", command=save_settings,
                bg="#111111", fg="#ffffff").pack(pady=10)
        tk.Button(settings_window, text="Close", command=settings_window.destroy,
                bg="#111111", fg="#ffffff").pack(pady=5)

    def on_closing(self):
        self.stop_video()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoPomodoro(root)
    root.mainloop()
