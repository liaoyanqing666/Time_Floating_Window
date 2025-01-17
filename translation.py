import locale

def get_local_language():
    sys_locale = locale.getdefaultlocale()[0]
    if sys_locale:
        if sys_locale.startswith("zh"):  # Chinese
            return "zh"
        # elif sys_locale.startswith("other_languages"):
        #     return "ol"
    else:  # Default to English
        return "en"

all_translations = \
{
    "en": {
        "language_code": "en",
        "lang_label": "English",
        "app_name": "Time Window",
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
        "show_buttons_when_locked": "Show Buttons When Locked",
        "show_buttons_when_unlocked": "Show Buttons When Unlocked",
        "auto_start": "Auto Start",
        "lang_switch": "Language",
        "restore_default": "Restore Default",
        "restore_confirm": "Restore default settings?",
        "restore_done": "Default settings restored. Please reopen the settings window.",
        "lang_changed_hint": "Language changed, please reopen settings or restart.",
        "confirm": "Confirm",
        "info": "Info",
        "lang_switch_confirm": "Are you sure you want to switch to {language}? The application will close.",
        "create_desktop_shortcut_confirm": "Create desktop shortcut?",
        "create_menu_shortcut_confirm": "Create start menu shortcut?",
        "error": "Error",
    },
    "zh": {
        "language_code": "zh",
        "lang_label": "中文",
        "app_name": "时间悬浮窗",
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
        "show_buttons_when_locked": "锁定时显示按钮",
        "show_buttons_when_unlocked": "解锁时显示按钮",
        "auto_start": "开机自启动",
        "lang_switch": "语言",
        "restore_default": "恢复默认",
        "restore_confirm": "是否恢复默认设置？",
        "restore_done": "默认设置已恢复。请重新打开设置窗口。",
        "lang_changed_hint": "语言已更改，请重新打开设置或重启。",
        "confirm": "确认",
        "info": "提示",
        "lang_switch_confirm": "确定要切换到{language}语言吗？应用程序将关闭。",
        "create_desktop_shortcut_confirm": "是否创建桌面快捷方式？",
        "create_menu_shortcut_confirm": "是否创建开始菜单快捷方式？",
        "error": "错误",
    }
}