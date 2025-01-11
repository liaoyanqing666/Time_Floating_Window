# Time_Floating_Window
Windows上的时间悬浮窗, Time floating window on Windows

受到Android上常用的“时间窗”APP的启示，打算做一个简单的windows版的时间窗

Below, I'll walk you through how to use this application, including both **English** and **Chinese** instructions.

---

## **How to Use Floating Clock (English)**

### **Features**
- **Real-Time Display**: Shows the current time in seconds or milliseconds.
- **Customizable Appearance**:
  - Change the clock's background and text colors.
  - Adjust the opacity (supports full transparency).
  - Choose your preferred font and font size.
- **Resizable Window**: Dynamically adjust the clock's width and height.
- **Lock and Unlock**: Move the clock freely when unlocked, or lock it in place.
- **Language Support**: Automatically detects system language (English or Chinese) and allows manual language switching.
- **Settings Persistence**: Automatically saves all settings (colors, position, size) to `settings.json` and restores them on restart.
- **Context Menu**: Right-click to access settings, lock/unlock, and quit options.

---

### **Installation**

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/<your-username>/floating-clock.git
   cd floating-clock
   ```

2. **Install Dependencies**:
   Ensure Python 3.x is installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python floating_clock.py
   ```

---

### **Usage**

1. **Open Settings**:
   - Right-click the floating clock and select "Settings" from the context menu.
   - Adjust background color, text color, opacity, font size, and more.
   - Changes are applied immediately and saved automatically.

2. **Move and Lock**:
   - Click the lock/unlock button (🔒/🔓) to toggle between movable and locked states.
   - Drag the clock when unlocked to reposition it.

3. **Close**:
   - Click the ❌ button or select "Close" from the context menu to exit.

---

### **Configuration File**

The application saves all settings in a `settings.json` file located in the same directory. Key settings include:
- Colors (`bg_color`, `text_color`).
- Window size and position (`width`, `height`, `last_position`).
- Time precision (`seconds` or `milliseconds`).
- Language preference (`en` or `zh`).

You can delete this file to reset all settings to default.

---

## **如何使用浮动时钟 (Chinese)**

### **功能特点**
- **实时显示**：显示当前时间，支持秒和毫秒精度。
- **个性化外观**：
  - 更改背景色和文字颜色。
  - 调整透明度（支持完全透明）。
  - 选择字体和字体大小。
- **窗口可调整大小**：动态设置时钟宽度和高度。
- **锁定和解锁**：支持自由拖动和固定位置。
- **语言支持**：自动检测系统语言（中文或英文），也可手动切换语言。
- **设置持久化**：自动保存设置到 `settings.json` 文件，并在重新启动时恢复。
- **右键菜单**：右键单击浮动时钟访问设置、锁定/解锁和退出选项。

---

### **安装方法**

1. **克隆仓库**：
   ```bash
   git clone https://github.com/<your-username>/floating-clock.git
   cd floating-clock
   ```

2. **安装依赖**：
   确保安装了 Python 3.x，然后运行：
   ```bash
   pip install -r requirements.txt
   ```

3. **运行程序**：
   ```bash
   python floating_clock.py
   ```

---

### **使用方法**

1. **打开设置**：
   - 右键单击浮动时钟，选择“设置”。
   - 更改背景颜色、文字颜色、透明度、字体大小等。
   - 更改会立即生效并自动保存。

2. **移动和锁定**：
   - 单击锁定/解锁按钮（🔒/🔓）切换是否允许拖动。
   - 解锁状态下，可以拖动时钟重新定位。

3. **关闭**：
   - 单击 ❌ 按钮或从右键菜单中选择“关闭”以退出程序。

---

### **配置文件说明**

程序会将所有设置保存到 `settings.json` 文件中，包括：
- 颜色设置（`bg_color`、`text_color`）。
- 窗口大小和位置（`width`、`height`、`last_position`）。
- 时间精度（`seconds` 或 `milliseconds`）。
- 语言偏好（`en` 或 `zh`）。

如需重置为默认设置，可以删除该文件。

---

## **Contributing**

Feel free to fork this repository and make improvements. If you find bugs or have ideas for new features, open an issue or submit a pull request.

---

## **License**

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

### **Contact**

If you have any questions or suggestions, feel free to contact me:  
Email: 1793706453@qq.com

