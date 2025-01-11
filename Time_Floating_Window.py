import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from tkinter.font import families, Font
import json
from datetime import datetime
import os
import locale
import ctypes

class FloatingClockApp:
    def __init__(self): # init
        self.config_file = "settings.json"
        self.load_settings() # load
        self.root = tk.Tk()
        self.root.withdraw()
        self.init_language() # lang
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        if "max_width" not in self.settings:
            self.settings["max_width"] = self.screen_width
        if "max_height" not in self.settings:
            self.settings["max_height"] = self.screen_height
        self.create_window() # create

    def load_settings(self): # load
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.settings = json.load(f)
        else:
            self.settings = {
                "bg_color": "#000000",
                "text_color": "#FFFFFF",
                "bg_opacity": 0.8,
                "width": 200,
                "height": 100,
                "font_family": "Segoe UI",
                "time_font_size": 18,
                "icon_size": 10,
                "is_movable": True,
                "last_position": None,
                "time_precision": "seconds",
                "sync_interval": 1000,
                "language": "default",
                "min_width": 120,
                "min_height": 60,
                "show_buttons_when_locked": True,
                "show_buttons_when_unlocked": True
            }

    def save_settings(self): # save
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    def init_language(self): # lang
        if self.settings["language"] == "default":
            sys_locale = locale.getdefaultlocale()[0]
            if sys_locale and sys_locale.startswith("zh"):
                self.lang = "zh"
            else:
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
                "settings_hw": "500x500+100+10",
                "choose_color": "Choose Color",
                "lock": "Lock",
                "unlock": "Unlock",
                "close": "Close",
                "time_font_size": "Time Font Size",
                "icon_font_size": "Icon Font Size",
                "font_label": "Font",
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
                "info": "Info"
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
                "settings_hw": "400x500+100+10",
                "choose_color": "选择颜色",
                "lock": "锁定",
                "unlock": "解锁",
                "close": "关闭",
                "time_font_size": "时间字体大小",
                "icon_font_size": "图标大小",
                "font_label": "字体",
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
                "info": "提示"
            }
        }
        self.available_languages = []
        for key, val in self.translations.items():
            self.available_languages.append(val["lang_label"])
        self.texts = self.translations.get(self.lang, self.translations["en"])

    def create_window(self): # create
        self.floating_window = tk.Toplevel(self.root)
        self.floating_window.title("Floating Clock")
        self.floating_window.overrideredirect(True)
        self.floating_window.attributes("-topmost", True)
        self.floating_window.bind("<FocusOut>", lambda e: self.keep_on_top()) # top
        self.update_geometry() # geometry
        self.floating_window.attributes("-alpha", self.settings["bg_opacity"])
        if os.name == "nt":
            hwnd = ctypes.windll.user32.GetParent(self.floating_window.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x80000)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 2, ctypes.byref(ctypes.c_int(2)), 4)
        if self.settings["last_position"]:
            self.apply_position_or_center() # apply
        else:
            self.center_window() # center
        self.time_label = tk.Label(
            self.floating_window,
            text="",
            font=(self.settings["font_family"], self.settings["time_font_size"]),
            bg=self.settings["bg_color"],
            fg=self.settings["text_color"]
        )
        self.time_label.pack(fill="both", expand=True)
        self.is_movable = self.settings["is_movable"]
        self.pin_button = tk.Button(
            self.floating_window,
            text=self.get_lock_icon(), # icon
            command=self.toggle_lock, # lock
            bg=self.settings["bg_color"],
            fg=self.settings["text_color"],
            relief="flat",
            font=(self.settings["font_family"], self.settings["icon_size"])
        )
        self.close_button = tk.Button(
            self.floating_window,
            text="❌",
            command=self.quit_app, # quit
            bg=self.settings["bg_color"],
            fg=self.settings["text_color"],
            relief="flat",
            font=(self.settings["font_family"], self.settings["icon_size"])
        )
        self.arrange_buttons() # arrange
        self.floating_window.bind("<Button-3>", self.show_context) # context
        self.start_x = 0
        self.start_y = 0
        self.floating_window.bind("<Button-1>", self.drag_start) # dstart
        self.floating_window.bind("<B1-Motion>", self.drag_move) # dmove
        self.floating_window.bind("<MouseWheel>", self.mouse_wheel) # wheel
        self.update_time() # time

    def arrange_buttons(self): # arrange
        if self.is_movable and self.settings["show_buttons_when_unlocked"]:
            self.pin_button.place(relx=0.05, rely=0.05, anchor="nw")
            self.close_button.place(relx=0.95, rely=0.05, anchor="ne")
        elif (not self.is_movable) and self.settings["show_buttons_when_locked"]:
            self.pin_button.place(relx=0.05, rely=0.05, anchor="nw")
            self.close_button.place(relx=0.95, rely=0.05, anchor="ne")
        else:
            self.pin_button.place_forget()
            self.close_button.place_forget()

    def keep_on_top(self): # top
        self.floating_window.after(1, lambda: (
            self.floating_window.attributes("-topmost", True),
            self.floating_window.lift()
        ))

    def get_lock_icon(self): # icon
        return "🔓" if self.is_movable else "🔒"

    def toggle_lock(self): # lock
        self.is_movable = not self.is_movable
        self.settings["is_movable"] = self.is_movable
        self.pin_button.config(text=self.get_lock_icon())
        self.arrange_buttons()
        self.save_settings()

    def drag_start(self, e): # dstart
        if self.is_movable:
            self.start_x = e.x
            self.start_y = e.y

    def drag_move(self, e): # dmove
        if self.is_movable:
            x = self.floating_window.winfo_x() + e.x - self.start_x
            y = self.floating_window.winfo_y() + e.y - self.start_y
            self.floating_window.geometry(f"+{x}+{y}")
            self.settings["last_position"] = [x, y]

    def mouse_wheel(self, e): # wheel
        # no changes to logic here except we clamp min alpha to 0.02
        delta = 0.01 if e.delta > 0 else -0.01
        new_val = self.settings["bg_opacity"] + delta
        if new_val < 0.02:
            new_val = 0.02
        if new_val > 1.0:
            new_val = 1.0
        self.settings["bg_opacity"] = new_val
        self.floating_window.attributes("-alpha", new_val)
        self.save_settings()

    def show_context(self, e): # context
        menu = tk.Menu(self.floating_window, tearoff=0)
        if self.is_movable:
            menu.add_command(label=self.texts["lock"], command=self.toggle_lock)
        else:
            menu.add_command(label=self.texts["unlock"], command=self.toggle_lock)
        menu.add_command(label=self.texts["settings"], command=self.open_settings)
        menu.add_command(label=self.texts["close"], command=self.quit_app)
        menu.post(e.x_root, e.y_root)

    def open_settings(self): # settings
        sw = tk.Toplevel(self.root)
        sw.title(self.texts["settings"])
        sw.geometry(self.texts["settings_hw"])
        sw.attributes("-topmost", True)
        sw_font = Font(family="Segoe UI", size=11)
        sw.option_add("*Font", sw_font)
        cf = ttk.Frame(sw)
        cv = tk.Canvas(cf)
        sb = ttk.Scrollbar(cf, orient="vertical", command=cv.yview)
        frm = ttk.Frame(cv)
        frm.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0, 0), window=frm, anchor="nw")
        cv.configure(yscrollcommand=sb.set)
        cf.pack(fill="both", expand=True)
        cv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        def disable_mousewheel_for_widget(wid):
            wid.bind("<MouseWheel>", lambda e: "break")

        disable_mousewheel_for_widget(cf)
        disable_mousewheel_for_widget(cv)
        disable_mousewheel_for_widget(sb)
        disable_mousewheel_for_widget(frm)

        r = 0
        ttk.Label(frm, text=self.texts["bg_color"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        ttk.Button(frm, text=self.texts["choose_color"], command=self.pick_bg_color).grid(row=r, column=1, padx=10, pady=5, sticky="w")
        r += 1

        ttk.Label(frm, text=self.texts["text_color"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        ttk.Button(frm, text=self.texts["choose_color"], command=self.pick_text_color).grid(row=r, column=1, padx=10, pady=5, sticky="w")
        r += 1

        ttk.Label(frm, text=self.texts["bg_opacity"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        alpha_frame = ttk.Frame(frm)
        alpha_frame.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        self.alpha_scale = ttk.Scale(
            alpha_frame,
            from_=0.02,  # doubled min alpha
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
        self.alpha_entry.bind("<KeyRelease>", lambda e: self.alpha_entry_changed())

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
        combo_lang.bind("<MouseWheel>", lambda e: "break")
        combo_lang.bind("<<ComboboxSelected>>", lambda e: self.switch_lang_by_label(combo_lang.get()))
        r += 1

        ttk.Label(frm, text=self.texts["font_label"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        combo_font = ttk.Combobox(frm, values=sorted(families()), state="readonly")
        combo_font.set(self.settings["font_family"])
        combo_font.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        combo_font.bind("<MouseWheel>", lambda e: "break")
        combo_font.bind("<<ComboboxSelected>>", lambda e: self.change_font(combo_font.get()))
        r += 1

        ttk.Label(frm, text=self.texts["time_font_size"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        ftf = ttk.Frame(frm)
        ftf.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        bdt = ttk.Button(ftf, text=self.texts["decrease"], command=self.dec_time_font)
        bdt.pack(side="left")
        self.lbl_time_font = ttk.Label(ftf, text=str(self.settings["time_font_size"]))
        self.lbl_time_font.pack(side="left")
        bit = ttk.Button(ftf, text=self.texts["increase"], command=self.inc_time_font)
        bit.pack(side="left")
        r += 1

        ttk.Label(frm, text=self.texts["icon_font_size"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        fic = ttk.Frame(frm)
        fic.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        bdi = ttk.Button(fic, text=self.texts["decrease"], command=self.dec_icon_size)
        bdi.pack(side="left")
        self.lbl_icon_font = ttk.Label(fic, text=str(self.settings["icon_size"]))
        self.lbl_icon_font.pack(side="left")
        bii = ttk.Button(fic, text=self.texts["increase"], command=self.inc_icon_size)
        bii.pack(side="left")
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
        ew = ttk.Entry(frm)
        ew.insert(0, str(self.settings["width"]))
        ew.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        ew.bind("<KeyRelease>", lambda e: self.change_width(ew.get()))
        r += 1

        ttk.Label(frm, text=self.texts["height"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        eh = ttk.Entry(frm)
        eh.insert(0, str(self.settings["height"]))
        eh.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        eh.bind("<KeyRelease>", lambda e: self.change_height(eh.get()))
        r += 1

        ttk.Button(frm, text=self.texts["restore_default"], command=self.restore_default).grid(row=r, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        r += 1

    def alpha_scale_changed(self, v): # alpha scale
        try:
            f = float(v)
            if f < 0.02: f = 0.02
            if f > 1.0: f = 1.0
            self.settings["bg_opacity"] = f
            self.floating_window.attributes("-alpha", f)
            self.alpha_entry.delete(0, tk.END)
            self.alpha_entry.insert(0, str(f))
            self.save_settings()
        except:
            pass

    def alpha_entry_changed(self): # alpha entry
        val = self.alpha_entry.get()
        try:
            f = float(val)
            if f < 0.02: f = 0.02
            if f > 1.0: f = 1.0
            self.settings["bg_opacity"] = f
            self.floating_window.attributes("-alpha", f)
            self.alpha_scale.set(f)
            self.save_settings()
        except:
            pass

    def restore_default(self): # restore
        if messagebox.askyesno(self.texts["confirm"], self.texts["restore_confirm"]):
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
            self.load_settings()
            self.save_settings()
            messagebox.showinfo(self.texts["info"], self.texts["restore_done"])

    def swbl(self, v): # swbl
        self.settings["show_buttons_when_locked"] = v
        self.arrange_buttons()
        self.save_settings()

    def swbu(self, v): # swbu
        self.settings["show_buttons_when_unlocked"] = v
        self.arrange_buttons()
        self.save_settings()

    def pick_bg_color(self): # pick bg
        c = colorchooser.askcolor()[1]
        if c:
            self.settings["bg_color"] = c
            self.floating_window.config(bg=c)
            self.time_label.config(bg=c)
            self.pin_button.config(bg=c)
            self.close_button.config(bg=c)
            self.save_settings()

    def pick_text_color(self): # pick text
        c = colorchooser.askcolor()[1]
        if c:
            self.settings["text_color"] = c
            self.time_label.config(fg=c)
            self.pin_button.config(fg=c)
            self.close_button.config(fg=c)
            self.save_settings()

    def change_font(self, f): # font
        self.settings["font_family"] = f
        self.time_label.config(font=(f, self.settings["time_font_size"]))
        self.pin_button.config(font=(f, self.settings["icon_size"]))
        self.close_button.config(font=(f, self.settings["icon_size"]))
        self.save_settings()
        self.check_size_for_font_change()

    def check_size_for_font_change(self): # font check
        w = self.settings["width"]
        h = self.settings["height"]
        lw = self.min_label_w()
        lh = self.min_label_h()
        resized = False
        if w < lw:
            w = lw
            resized = True
        if h < lh:
            h = lh
            resized = True
        if resized:
            self.settings["width"] = w
            self.settings["height"] = h
            self.update_geometry()
            self.save_settings()

    def change_precision_by_text(self, txt): # prec by txt
        if txt == self.texts["milliseconds"]:
            self.set_precision("milliseconds")
        else:
            self.set_precision("seconds")

    def set_precision(self, p): # set prec
        self.settings["time_precision"] = p
        if p == "milliseconds":
            self.settings["sync_interval"] = 100
            if self.settings["width"] < 220:
                self.settings["width"] = 220
                self.update_geometry()
        else:
            self.settings["sync_interval"] = 1000
        self.save_settings()

    def change_width(self, v): # width
        if v.isdigit():
            w = int(v)
            w = max(w, self.min_label_w(), self.settings["min_width"])
            w = min(w, self.settings["max_width"])
            self.settings["width"] = w
            self.update_geometry()
            self.save_settings()

    def change_height(self, v): # height
        if v.isdigit():
            h = int(v)
            h = max(h, self.min_label_h(), self.settings["min_height"])
            h = min(h, self.settings["max_height"])
            self.settings["height"] = h
            self.update_geometry()
            self.save_settings()

    def dec_time_font(self): # dec tf
        c = self.settings["time_font_size"]
        n = max(c - 1, 8)
        if n != c:
            self.settings["time_font_size"] = n
            self.lbl_time_font.config(text=str(n))
            self.time_label.config(font=(self.settings["font_family"], n))
            self.save_settings()
            self.check_size_for_font_change()

    def inc_time_font(self): # inc tf
        c = self.settings["time_font_size"]
        n = min(c + 1, 72)
        if n != c:
            self.settings["time_font_size"] = n
            self.lbl_time_font.config(text=str(n))
            self.time_label.config(font=(self.settings["font_family"], n))
            self.save_settings()
            self.check_size_for_font_change()

    def dec_icon_size(self): # dec ic
        c = self.settings["icon_size"]
        n = max(c - 1, 8)
        if n != c:
            self.settings["icon_size"] = n
            self.lbl_icon_font.config(text=str(n))
            self.update_buttons()
            self.save_settings()

    def inc_icon_size(self): # inc ic
        c = self.settings["icon_size"]
        n = min(c + 1, 40)
        if n != c:
            self.settings["icon_size"] = n
            self.lbl_icon_font.config(text=str(n))
            self.update_buttons()
            self.save_settings()

    def update_buttons(self): # ub
        self.pin_button.config(font=(self.settings["font_family"], self.settings["icon_size"]))
        self.close_button.config(font=(self.settings["font_family"], self.settings["icon_size"]))

    def min_label_w(self): # min lw
        o = self.time_label.cget("text")
        t = "88:88:88" + (".888" if self.settings["time_precision"] == "milliseconds" else "")
        self.time_label.config(text=t)
        self.floating_window.update_idletasks()
        lw = self.time_label.winfo_reqwidth() + 40
        self.time_label.config(text=o)
        return lw

    def min_label_h(self): # min lh
        o = self.time_label.cget("text")
        t = "88:88:88" + (".888" if self.settings["time_precision"] == "milliseconds" else "")
        self.time_label.config(text=t)
        self.floating_window.update_idletasks()
        lh = self.time_label.winfo_reqheight() + 20
        self.time_label.config(text=o)
        return lh

    def apply_position_or_center(self): # apply
        x, y = self.settings["last_position"]
        w = self.settings["width"]
        h = self.settings["height"]
        if not self.center_in_screen(x, y, w, h):
            self.center_window()
        else:
            self.floating_window.geometry(f'{w}x{h}+{x}+{y}')

    def center_window(self): # center
        w = self.settings["width"]
        h = self.settings["height"]
        sw = self.floating_window.winfo_screenwidth()
        sh = self.floating_window.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.floating_window.geometry(f'{w}x{h}+{x}+{y}')

    def update_geometry(self): # geometry
        if self.settings["last_position"]:
            x, y = self.settings["last_position"]
            self.floating_window.geometry(f'{self.settings["width"]}x{self.settings["height"]}+{x}+{y}')
        else:
            self.center_window()

    def center_in_screen(self, x, y, w, h): # in screen
        cx = x + w/2
        cy = y + h/2
        sw = self.floating_window.winfo_screenwidth()
        sh = self.floating_window.winfo_screenheight()
        return (0 <= cx <= sw) and (0 <= cy <= sh)

    def update_time(self): # time
        now = datetime.now()
        if self.settings["time_precision"] == "seconds":
            text_time = now.strftime("%H:%M:%S")
        else:
            text_time = now.strftime("%H:%M:%S.%f")[:-3]
        self.time_label.config(text=text_time)
        self.floating_window.after(self.settings["sync_interval"], self.update_time)

    def quit_app(self): # quit
        self.settings["last_position"] = (self.floating_window.winfo_x(), self.floating_window.winfo_y())
        self.save_settings()
        self.floating_window.destroy()
        self.root.destroy()

    def switch_lang_by_label(self, lb): # sw lang
        found_key = None
        for k, v in self.translations.items():
            if v["lang_label"] == lb:
                found_key = k
                break
        if not found_key or found_key == self.lang:
            return
        self.settings["language"] = found_key
        self.save_settings()
        msg = self.translations[found_key].get("lang_changed_hint", "Language changed.")
        messagebox.showinfo(self.texts["info"], msg)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    FloatingClockApp().run()
