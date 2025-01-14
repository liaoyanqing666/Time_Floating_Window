import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from tkinter.font import families
import json
from datetime import datetime
import os
import locale
import ctypes
import sys

class FloatingClockApp():
    def __init__(self):
        self.config_file = "TimeWindowSettings.json"
        self.load_settings()
        self.root = tk.Tk()
        self.root.withdraw()
        self.init_language()
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.settings.setdefault("max_width", self.screen_width)
        self.settings.setdefault("max_height", self.screen_height)
        self.settings_window = None  # To track if settings window is open
        self.create_window()

    def load_settings(self):
        # Load settings from file or use defaults
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.settings = json.load(f)
        else:
            self.settings = {
                "bg_color": "#000000",
                "text_color": "#FFFFFF",
                "bg_opacity": 0.8,
                "width": 180,
                "height": 60,
                "font_family": "Consolas",
                "time_font_size": 17,
                "icon_size": 10,
                "is_movable": True,
                "last_position": None,
                "time_precision": "seconds",
                "sync_interval": 1000,
                "language": "default",
                "show_buttons_when_locked": True,
                "show_buttons_when_unlocked": True,
                "settings_window_size": None,
                "settings_window_position": None,
            }

    def save_settings(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    def init_language(self):
        if self.settings["language"] == "default":
            sys_locale = locale.getdefaultlocale()[0]
            if sys_locale:
                if sys_locale.startswith("zh"):  # Chinese
                    self.lang = "zh"
                # elif sys_locale.startswith("other_languages"):
                #     self.lang = "ol"
            else:  # Default to English
                self.lang = "en"
        else:
            self.lang = self.settings["language"]
        self.translations = {
            "en": {
                "language_code": "en",
                "lang_label": "English",
                "bg_color": "Background Color",
                "text_color": "Text Color",
                "bg_opacity": "Background Opacity",
                "width": "Width",
                "height": "Height",
                "precision": "Time Precision",
                "seconds": "Seconds",
                "milliseconds": "Milliseconds",
                "settings": "Settings",
                "settings_hw": "465x465",
                "choose_color": "Choose Color",
                "lock": "Lock",
                "unlock": "Unlock",
                "close": "Close",
                "time_font_size": "Time Font Size",
                "icon_font_size": "Icon Font Size",
                "font_label": "Font (Scroll)",
                "increase": " + ",
                "decrease": " - ",
                "show_buttons_when_locked": "Show Buttons When Locked",
                "show_buttons_when_unlocked": "Show Buttons When Unlocked",
                "lang_switch": "Language",
                "restore_default": "Restore Default",
                "restore_confirm": "Restore default settings?",
                "restore_done": "Default settings restored. Please reopen the settings window.",
                "lang_changed_hint": "Language changed, please reopen settings or restart.",
                "confirm": "Confirm",
                "info": "Info",
                "lang_switch_confirm": "Are you sure you want to switch to {language}? The application will close."
            },
            "zh": {
                "language_code": "zh",
                "lang_label": "中文",
                "bg_color": "背景颜色",
                "text_color": "文字颜色",
                "bg_opacity": "背景透明度",
                "width": "宽度",
                "height": "高度",
                "precision": "时间精度",
                "seconds": "秒",
                "milliseconds": "毫秒",
                "settings": "设置",
                "settings_hw": "365x460",
                "choose_color": "选择颜色",
                "lock": "锁定",
                "unlock": "解锁",
                "close": "关闭",
                "time_font_size": "时间字体大小",
                "icon_font_size": "图标大小",
                "font_label": "字体（滚动选择）",
                "increase": " + ",
                "decrease": " - ",
                "show_buttons_when_locked": "锁定时显示按钮",
                "show_buttons_when_unlocked": "解锁时显示按钮",
                "lang_switch": "语言",
                "restore_default": "恢复默认",
                "restore_confirm": "是否恢复默认设置？",
                "restore_done": "默认设置已恢复。请重新打开设置窗口。",
                "lang_changed_hint": "语言已更改，请重新打开设置或重启。",
                "confirm": "确认",
                "info": "提示",
                "lang_switch_confirm": "确定要切换到{language}语言吗？应用程序将关闭。"
            }
        }
        self.available_languages = [val["lang_label"] for val in self.translations.values()] # get all language labels
        self.texts = self.translations.get(self.lang, self.translations["en"])

    def create_window(self):
        # Create the floating window
        self.floating_window = tk.Toplevel(self.root)
        self.floating_window.title("Floating Clock")
        self.floating_window.overrideredirect(True)
        self.floating_window.attributes("-topmost", True)
        self.floating_window.bind("<FocusOut>", lambda e: self.keep_on_top())
        self.update_geometry()
        self.floating_window.attributes("-alpha", self.settings["bg_opacity"])
        if os.name == "nt":
            hwnd = ctypes.windll.user32.GetParent(self.floating_window.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x80000)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 2, ctypes.byref(ctypes.c_int(2)), 4)

        # If the window was moved before, apply the position
        if self.settings["last_position"]:
            self.apply_position_or_center()
        else:
            self.center_window()

        # Create the time label
        self.time_label = tk.Label(
            self.floating_window,
            text="",
            font=(self.settings["font_family"], self.settings["time_font_size"]),
            bg=self.settings["bg_color"],
            fg=self.settings["text_color"]
        )
        self.time_label.pack(fill="both", expand=True)

        self.is_movable = self.settings["is_movable"]

        # Create the lock/unlock button
        self.pin_button = tk.Button(
            self.floating_window,
            text=self.get_lock_icon(),
            command=self.toggle_lock,
            bg=self.settings["bg_color"],
            fg=self.settings["text_color"],
            relief="flat",
            font=(self.settings["font_family"], self.settings["icon_size"])
        )

        # Create the close button
        self.close_button = tk.Button(
            self.floating_window,
            text="X",
            command=self.quit_app,
            bg=self.settings["bg_color"],
            fg=self.settings["text_color"],
            relief="flat",
            font=(self.settings["font_family"], self.settings["icon_size"])
        )

        self.start_x = 0
        self.start_y = 0

        self.arrange_buttons()
        self.floating_window.bind("<Button-3>", self.show_context)
        self.floating_window.bind("<Button-1>", self.drag_start)
        self.floating_window.bind("<B1-Motion>", self.drag_move)

        self.update_time()

    def arrange_buttons(self):
        # Place the buttons according to the settings
        condition = (self.is_movable and self.settings["show_buttons_when_unlocked"]) or \
                    (not self.is_movable and self.settings["show_buttons_when_locked"])
        if condition:
            self.pin_button.place(relx=0.05, rely=0.05, anchor="nw")
            self.close_button.place(relx=0.95, rely=0.05, anchor="ne")
        else:
            self.pin_button.place_forget()
            self.close_button.place_forget()

    def keep_on_top(self):
        # Keep the time window on top
        self.floating_window.after(1, lambda: (
            self.floating_window.attributes("-topmost", True),
            self.floating_window.lift()
        ))

    def get_lock_icon(self):
        return "🔓" if self.is_movable else "🔒"

    def toggle_lock(self):
        # Toggle the movable state of the window
        self.is_movable = not self.is_movable
        self.settings["is_movable"] = self.is_movable
        self.pin_button.config(text=self.get_lock_icon())
        self.arrange_buttons()
        self.save_settings()

    def drag_start(self, e):
        if self.is_movable:
            self.start_x = e.x
            self.start_y = e.y

    def drag_move(self, e):
        # Move the window
        if self.is_movable:
            x = self.floating_window.winfo_x() + e.x - self.start_x
            y = self.floating_window.winfo_y() + e.y - self.start_y
            self.floating_window.geometry(f"+{x}+{y}")
            self.settings["last_position"] = [x, y]

    def show_context(self, e):
        # Right click context menu
        menu = tk.Menu(self.floating_window, tearoff=0)
        menu.add_command(label=self.texts["lock"] if self.is_movable else self.texts["unlock"], command=self.toggle_lock)
        menu.add_command(label=self.texts["settings"], command=self.open_settings)
        menu.add_command(label=self.texts["close"], command=self.quit_app)
        menu.post(e.x_root, e.y_root)

    def open_settings(self):
        # Open the settings window only if it's not already open
        if self.settings_window and tk.Toplevel.winfo_exists(self.settings_window):
            self.settings_window.lift()
            return

        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title(self.texts["settings"])
        size = self.settings.get("settings_window_size")
        pos = self.settings.get("settings_window_position")
        if size and pos:
            self.settings_window.geometry(f"{size[0]}x{size[1]}+{pos[0]}+{pos[1]}")
        else:
            size_hw = self.texts["settings_hw"]
            w, h = map(int, size_hw.split('x'))
            sw, sh = self.screen_width, self.screen_height
            x, y = (sw - w) // 2, (sh - h) // 2
            self.settings_window.geometry(f"{w}x{h}+{x}+{y}")

        def on_configure(event):
            # Save when the size or position of the window changes
            self.settings["settings_window_size"] = [self.settings_window.winfo_width(), self.settings_window.winfo_height()]
            self.settings["settings_window_position"] = [self.settings_window.winfo_x(), self.settings_window.winfo_y()]
            self.save_settings()

        def on_close():
            self.settings_window.destroy()
            self.settings_window = None

        self.settings_window.bind("<Configure>", on_configure)
        self.settings_window.protocol("WM_DELETE_WINDOW", on_close)

        cf = ttk.Frame(self.settings_window)
        cv = tk.Canvas(cf)
        sb = ttk.Scrollbar(cf, orient="vertical", command=cv.yview)
        frm = ttk.Frame(cv)
        frm.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0, 0), window=frm, anchor="nw")
        cv.configure(yscrollcommand=sb.set)
        cf.pack(fill="both", expand=True)
        cv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Disable mouse wheel scrolling
        def disable_mousewheel(wid):
            wid.bind("<MouseWheel>", lambda e: "break")
        for widget in [cf, cv, sb, frm]:
            disable_mousewheel(widget)

        r = 0 # row number, used for grid layout
        ttk.Label(frm, text=self.texts["bg_color"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        ttk.Button(frm, text=self.texts["choose_color"], command=self.pick_bg_color).grid(row=r, column=1, padx=10, pady=5, sticky="w")
        r += 1

        ttk.Label(frm, text=self.texts["text_color"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        ttk.Button(frm, text=self.texts["choose_color"], command=self.pick_text_color).grid(row=r, column=1, padx=10, pady=5, sticky="w")
        r += 1

        # Background opacity settings
        ttk.Label(frm, text=self.texts["bg_opacity"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        alpha_frame = ttk.Frame(frm)
        alpha_frame.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        self.alpha_scale = ttk.Scale(
            alpha_frame,
            from_=0.05,
            to=1.0,
            value=self.settings["bg_opacity"],
            orient="horizontal",
            length=120,
            command=self.alpha_scale_changed
        )
        self.alpha_scale.pack(side="left")

        self.alpha_entry = ttk.Entry(alpha_frame, width=5)
        self.alpha_entry.insert(0, str(self.settings["bg_opacity"]))
        self.alpha_entry.pack(side="left", padx=5)
        self.alpha_entry.bind("<FocusOut>", lambda e: self.alpha_entry_apply())
        self.alpha_entry.bind("<Return>", lambda e: self.alpha_entry_apply())
        r += 1

        chk_l = tk.BooleanVar(value=self.settings["show_buttons_when_locked"])
        ttk.Label(frm, text=self.texts["show_buttons_when_locked"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        ttk.Checkbutton(frm, variable=chk_l, command=lambda: self.swbl(chk_l.get())).grid(row=r, column=1, padx=10, pady=5, sticky="w")
        r += 1

        chk_u = tk.BooleanVar(value=self.settings["show_buttons_when_unlocked"])
        ttk.Label(frm, text=self.texts["show_buttons_when_unlocked"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        ttk.Checkbutton(frm, variable=chk_u, command=lambda: self.swbu(chk_u.get())).grid(row=r, column=1, padx=10, pady=5, sticky="w")
        r += 1

        ttk.Label(frm, text=self.texts["lang_switch"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        combo_lang = ttk.Combobox(frm, values=self.available_languages, state="readonly")
        combo_lang.set(self.translations[self.lang]["lang_label"])
        combo_lang.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        combo_lang.bind("<MouseWheel>", lambda e: "break") # disable mouse wheel scrolling
        combo_lang.bind("<<ComboboxSelected>>", lambda e: self.switch_lang_by_label(combo_lang.get()))
        r += 1

        ttk.Label(frm, text=self.texts["font_label"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        combo_font = ttk.Combobox(frm, values=sorted(families()), state="readonly")
        combo_font.set(self.settings["font_family"])
        combo_font.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        combo_font.bind("<MouseWheel>", self.font_mouse_wheel) # enable mouse wheel scrolling
        combo_font.bind("<<ComboboxSelected>>", lambda e: self.change_font(combo_font.get()))
        r += 1

        ttk.Label(frm, text=self.texts["time_font_size"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        ftf = ttk.Frame(frm)
        ftf.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        ttk.Button(ftf, text=self.texts["decrease"], command=self.dec_time_font).pack(side="left")
        self.lbl_time_font = ttk.Label(ftf, text=str(self.settings["time_font_size"]))
        self.lbl_time_font.pack(side="left")
        ttk.Button(ftf, text=self.texts["increase"], command=self.inc_time_font).pack(side="left")
        r += 1

        ttk.Label(frm, text=self.texts["icon_font_size"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        fic = ttk.Frame(frm)
        fic.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        ttk.Button(fic, text=self.texts["decrease"], command=self.dec_icon_size).pack(side="left")
        self.lbl_icon_font = ttk.Label(fic, text=str(self.settings["icon_size"]))
        self.lbl_icon_font.pack(side="left")
        ttk.Button(fic, text=self.texts["increase"], command=self.inc_icon_size).pack(side="left")
        r += 1

        pcv = [self.texts["seconds"], self.texts["milliseconds"]]
        ttk.Label(frm, text=self.texts["precision"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        combo_tp = ttk.Combobox(frm, values=pcv, state="readonly")
        combo_tp.bind("<MouseWheel>", lambda e: "break")
        combo_tp.set(self.texts[self.settings["time_precision"]])
        combo_tp.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        combo_tp.bind("<<ComboboxSelected>>", lambda e: self.change_precision_by_text(combo_tp.get()))
        r += 1

        ttk.Label(frm, text=self.texts["width"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        width_frame = ttk.Frame(frm)
        width_frame.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        ttk.Button(width_frame, text="-10", command=self.dec_width_by_10).pack(side="left")
        self.width_entry = ttk.Entry(width_frame, width=6)
        self.width_entry.insert(0, str(self.settings["width"]))
        self.width_entry.pack(side="left", padx=5)
        ttk.Button(width_frame, text="+10", command=self.inc_width_by_10).pack(side="left")
        self.width_entry.bind("<KeyRelease>", lambda e: self.change_width(self.width_entry.get()))
        r += 1

        ttk.Label(frm, text=self.texts["height"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        height_frame = ttk.Frame(frm)
        height_frame.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        ttk.Button(height_frame, text="-10", command=self.dec_height_by_10).pack(side="left")
        self.height_entry = ttk.Entry(height_frame, width=6)
        self.height_entry.insert(0, str(self.settings["height"]))
        self.height_entry.pack(side="left", padx=5)
        ttk.Button(height_frame, text="+10", command=self.inc_height_by_10).pack(side="left")
        self.height_entry.bind("<KeyRelease>", lambda e: self.change_height(self.height_entry.get()))
        r += 1

        ttk.Button(frm, text=self.texts["restore_default"], command=self.restore_default).grid(row=r, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        r += 1

    def font_mouse_wheel(self, e):
        # Enable mouse wheel scrolling for the font combobox
        self.inc_font() if e.delta > 0 else self.dec_font()

    def inc_font(self):
        # Get the font families and change to the next one
        fonts = sorted(families())
        current = self.settings["font_family"]
        try:
            idx = fonts.index(current)
        except ValueError:
            idx = 0
        if idx < len(fonts) - 1:
            self.change_font(fonts[idx + 1])

    def dec_font(self):
        # Get the font families and change to the previous one
        fonts = sorted(families())
        current = self.settings["font_family"]
        try:
            idx = fonts.index(current)
        except ValueError:
            idx = 0
        if idx > 0:
            self.change_font(fonts[idx - 1])

    def alpha_scale_changed(self, v):
        # When the value of the scale widget changes
        try:
            f = max(0.05, min(float(v), 1.0))
            f = round(f, 2)
            self.settings["bg_opacity"] = f
            self.floating_window.attributes("-alpha", f)
            self.alpha_entry.delete(0, tk.END)
            self.alpha_entry.insert(0, str(f))
            self.save_settings()
        except ValueError:
            pass

    def alpha_entry_apply(self):
        # Apply the opacity value from the entry box
        try:
            f = float(self.alpha_entry.get())
            f = max(self.settings.get("min_opacity", 0.05), min(f, 1.0))
            f = round(f, 2)
            self.settings["bg_opacity"] = f
            self.floating_window.attributes("-alpha", f)
            self.alpha_scale.set(f)
            self.alpha_entry.delete(0, tk.END)
            self.alpha_entry.insert(0, str(f))
            self.save_settings()
        except ValueError:
            # Reset to current setting if invalid
            self.alpha_entry.delete(0, tk.END)
            self.alpha_entry.insert(0, str(self.settings["bg_opacity"]))

    def restore_default(self):
        # When the user clicks the Restore Default Settings button, confirm and restore
        if messagebox.askyesno(self.texts["confirm"], self.texts["restore_confirm"]):
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
            self.load_settings()
            self.save_settings()
            messagebox.showinfo(self.texts["info"], self.texts["restore_done"])
            self.quit_app()

    def swbl(self, v):
        self.settings["show_buttons_when_locked"] = v
        self.arrange_buttons()
        self.save_settings()

    def swbu(self, v):
        self.settings["show_buttons_when_unlocked"] = v
        self.arrange_buttons()
        self.save_settings()

    def pick_bg_color(self):
        # Open the color chooser dialog and set the background color
        c = colorchooser.askcolor()[1]
        if c:
            self.settings["bg_color"] = c
            for widget in [self.floating_window, self.time_label, self.pin_button, self.close_button]:
                widget.config(bg=c)
            self.save_settings()

    def pick_text_color(self):
        # Open the color chooser dialog and set the text color
        c = colorchooser.askcolor()[1]
        if c:
            self.settings["text_color"] = c
            for widget in [self.time_label, self.pin_button, self.close_button]:
                widget.config(fg=c)
            self.save_settings()

    def change_font(self, f):
        # Change the font family
        self.settings["font_family"] = f
        self.time_label.config(font=(f, self.settings["time_font_size"]))
        self.pin_button.config(font=(f, self.settings["icon_size"]))
        self.close_button.config(font=(f, self.settings["icon_size"]))
        self.save_settings()
        self.check_size_for_font_change()

    def check_size_for_font_change(self):
        # Check if the window size is enough for the new font size
        w, h = self.settings["width"], self.settings["height"]
        lw, lh = self.min_label_w(), self.min_label_h()
        resized = False
        if w < lw:
            self.settings["width"] = lw
            resized = True
        if h < lh:
            self.settings["height"] = lh
            resized = True
        if resized:
            self.update_geometry()
            self.save_settings()

    def change_precision_by_text(self, txt):
        # Change the time precision
        self.set_precision("milliseconds" if txt == self.texts["milliseconds"] else "seconds")

    def set_precision(self, p):
        # Set the time precision and adjust the window size if necessary
        self.settings["time_precision"] = p
        self.settings["sync_interval"] = 100 if p == "milliseconds" else 1000
        if p == "milliseconds" and self.settings["width"] < self.min_label_w():
            self.settings["width"] = self.min_label_w()
            self.update_geometry()
        self.save_settings()

    def change_width(self, v):
        # Change the width of the window
        if v.isdigit():
            w = max(int(v), self.min_label_w())
            self.settings["width"] = min(w, self.settings["max_width"])
            self.update_geometry()
            self.save_settings()

    def change_height(self, v):
        # Change the height of the window
        if v.isdigit():
            h = max(int(v), self.min_label_h())
            self.settings["height"] = min(h, self.settings["max_height"])
            self.update_geometry()
            self.save_settings()

    def inc_width_by_10(self):
        try:
            current = int(self.width_entry.get())
        except ValueError:
            current = self.settings["width"]
        new_width = current + 10
        self.width_entry.delete(0, tk.END)
        self.width_entry.insert(0, str(new_width))
        self.change_width(str(new_width))

    def dec_width_by_10(self):
        try:
            current = int(self.width_entry.get())
        except ValueError:
            current = self.settings["width"]
        new_width = current - 10
        self.width_entry.delete(0, tk.END)
        self.width_entry.insert(0, str(new_width))
        self.change_width(str(new_width))

    def inc_height_by_10(self):
        try:
            current = int(self.height_entry.get())
        except ValueError:
            current = self.settings["height"]
        new_height = current + 10
        self.height_entry.delete(0, tk.END)
        self.height_entry.insert(0, str(new_height))
        self.change_height(str(new_height))

    def dec_height_by_10(self):
        try:
            current = int(self.height_entry.get())
        except ValueError:
            current = self.settings["height"]
        new_height = current - 10
        self.height_entry.delete(0, tk.END)
        self.height_entry.insert(0, str(new_height))
        self.change_height(str(new_height))

    def dec_time_font(self):
        # Decrease the time font size
        if self.settings["time_font_size"] > 8:
            self.settings["time_font_size"] -= 1
            self.lbl_time_font.config(text=str(self.settings["time_font_size"]))
            self.time_label.config(font=(self.settings["font_family"], self.settings["time_font_size"]))
            self.save_settings()
            self.check_size_for_font_change()

    def inc_time_font(self):
        # Increase the time font size
        if self.settings["time_font_size"] < 72:
            self.settings["time_font_size"] += 1
            self.lbl_time_font.config(text=str(self.settings["time_font_size"]))
            self.time_label.config(font=(self.settings["font_family"], self.settings["time_font_size"]))
            self.save_settings()
            self.check_size_for_font_change()

    def dec_icon_size(self):
        # Decrease the icon font size
        if self.settings["icon_size"] > 8:
            self.settings["icon_size"] -= 1
            self.lbl_icon_font.config(text=str(self.settings["icon_size"]))
            self.update_buttons()
            self.save_settings()

    def inc_icon_size(self):
        # Increase the icon font size
        if self.settings["icon_size"] < 40:
            self.settings["icon_size"] += 1
            self.lbl_icon_font.config(text=str(self.settings["icon_size"]))
            self.update_buttons()
            self.save_settings()

    def update_buttons(self):
        # Update the font size of the buttons
        for button in [self.pin_button, self.close_button]:
            button.config(font=(self.settings["font_family"], self.settings["icon_size"]))

    def min_label_w(self):
        # Get the minimum width of the time label to ensure the text fits
        original_text = self.time_label.cget("text")
        test_text = "88:88:88.888" if self.settings["time_precision"] == "milliseconds" else "88:88:88"
        self.time_label.config(text=test_text)
        self.floating_window.update_idletasks()
        lw = self.time_label.winfo_reqwidth() + 40
        self.time_label.config(text=original_text)
        return lw

    def min_label_h(self):
        # Get the minimum height of the time label to ensure the text fits
        original_text = self.time_label.cget("text")
        test_text = "88:88:88.888" if self.settings["time_precision"] == "milliseconds" else "88:88:88"
        self.time_label.config(text=test_text)
        self.floating_window.update_idletasks()
        lh = self.time_label.winfo_reqheight() + 20
        self.time_label.config(text=original_text)
        return lh

    def apply_position_or_center(self):
        # Apply the position if it is valid, otherwise center the window
        x, y = self.settings["last_position"]
        w, h = self.settings["width"], self.settings["height"]
        if not self.center_in_screen(x, y, w, h):
            self.center_window()
        else:
            self.floating_window.geometry(f'{w}x{h}+{x}+{y}')

    def center_window(self):
        # Center the window on the screen
        w, h = self.settings["width"], self.settings["height"]
        sw, sh = self.floating_window.winfo_screenwidth(), self.floating_window.winfo_screenheight()
        x, y = (sw - w) // 2, (sh - h) // 2
        self.floating_window.geometry(f'{w}x{h}+{x}+{y}')

    def update_geometry(self):
        # Update the window geometry
        if self.settings["last_position"]:
            x, y = self.settings["last_position"]
            w, h = self.settings["width"], self.settings["height"]
            self.floating_window.geometry(f'{w}x{h}+{x}+{y}')
        else:
            self.center_window()

    def center_in_screen(self, x, y, w, h):
        # Check if the window is within the screen boundaries
        cx, cy = x + w / 2, y + h / 2
        sw, sh = self.floating_window.winfo_screenwidth(), self.floating_window.winfo_screenheight()
        return 0 <= cx <= sw and 0 <= cy <= sh

    def update_time(self):
        # Update the time label
        now = datetime.now()
        if self.settings["time_precision"] == "milliseconds":
            formatted_time = now.strftime("%H:%M:%S.%f")[:-3]
        else:
            formatted_time = now.strftime("%H:%M:%S")
        self.time_label.config(text=formatted_time)
        self.floating_window.after(self.settings["sync_interval"], self.update_time)

    def quit_app(self):
        # Quit the application
        self.settings["last_position"] = [self.floating_window.winfo_x(), self.floating_window.winfo_y()]
        self.save_settings()
        if self.settings_window and tk.Toplevel.winfo_exists(self.settings_window):
            self.settings_window.destroy()
        self.floating_window.destroy()
        self.root.destroy()

    def switch_lang_by_label(self, lb):
        # Switch the language by the language label
        found_key = next((k for k, v in self.translations.items() if v["lang_label"] == lb), None)
        if found_key and found_key != self.lang:
            confirm_message = self.texts["lang_switch_confirm"].format(language=lb)
            if messagebox.askyesno(self.texts["confirm"], confirm_message):
                self.settings["language"] = found_key
                self.settings["settings_window_size"] = None
                self.quit_app()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    FloatingClockApp().run()
