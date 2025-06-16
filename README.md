# Time_Floating_Window
Windows上的时间悬浮窗, Time floating window on Windows

使用Python，Tkinter和pyinstaller, made with Python, Tkinter, and pyinstaller

<p align="center">
    <img src="images/gif_1.gif" alt="GIF" width="200"/>
</p>

**English Introduction:**

When you need to grab tickets, coupons, watch movies, or just focus on work, you might need a simple floating clock to stay on top of things. This project was created to solve that problem. Windows doesn't natively support floating clocks, and setting up a clock that updates every second is pretty tricky, so that's how this project came to life. It's inspired by an app I often use on Android called "Time Window."

Below, I'll give you a detailed overview of the app, with instructions in both **English** and **Chinese**. If you're just looking to use it, simply head to the right-hand side and click on **Releases** to download the latest version (exe). Settings can be opened by right-clicking.

**Chinese Introduction:**

当你需要抢票，抢券，看电影，或者需要专心工作时，你可能会需要一个简单的时间悬浮窗，这个项目就是为了解决这个问题而诞生的。而Windows并不支持原生时间悬浮窗，且设置秒级显示时间也很麻烦，因此这个项目就诞生了。此项目受到Android上我个人常用的“时间窗”APP的启示。

下面，我将告诉你详细介绍这个应用程序，包括**英语**和**中文**说明。如果你只是想使用，只需要点击右侧**Releases**，下载最新版本（exe）即可（支持中文），注意可以右键打开设置。

想要获得更加详细的中文介绍，可以的访问[*功能详解*](https://blog.csdn.net/m0_61718615/article/details/145261677)，和[*开发代码介绍*](https://blog.csdn.net/m0_61718615/article/details/145265002)。

**Examples**:
<p align="center">
    <img src="images/img_1.png" alt="Movie" width="600" />
</p>
<p align="center">Watching a movie (left lower)</p>

<p align="center">
    <img src="images/gif_2.gif" alt="Movie" width="600" />
</p>
<p align="center">Move and lock the window</p>

<p align="center">
    <img src="images/img_2.png" alt="Movie" width="600" />
</p>
<p align="center">Remove the system time and use Time Window instead</p>

---

## **Time Floating Window (English)**

### **Features**
- **Real-Time Display**: Shows the current time in seconds or milliseconds.
- **Customizable Appearance**:
  - Change the clock's background and text colors.
  - Adjust the opacity.
  - Choose your preferred font and font size.
- **Resizable Window**: Dynamically adjust the clock's width and height.
- **Lock and Unlock**: Move the clock freely when unlocked, or lock it in place.
- **Set Delay**: Manually set the time increment or automatically sync with the network.
- **Language Support**: Automatically detects system language and allows manual language switching. Now supports English and Chinese, and you are welcome to add more languages.
- **Settings Persistence**: Automatically saves all settings (colors, position, size) to `TimeWindowSettings.json` and restores them on restart.
- **Context Menu**: Right-click to access settings, lock/unlock, and quit options.
- **First Launch**: Determine whether it is the first launch by reading whether there is a json file. When it is the first launch, it will ask if you need to add related shortcuts.
- **Auto-Start**: Choose whether to start automatically when the computer starts.

### Usage

1. **Open Settings**:
   - Right-click the floating clock and select "Settings" from the context menu.
   - Adjust background color, text color, opacity, font size, and more.
   - Changes are applied immediately and saved automatically.

2. **Move and Lock**:
   - Click the lock/unlock button (🔒/🔓) to toggle between movable and locked states.
   - Drag the clock when unlocked to reposition it.

3. **Close**:
   - Click the X button or select "Close" from the context menu to exit.

### Configuration File

The application saves all settings in a `TimeWindowSettings.json` file located in the same directory. Key settings include:
- Language.
- Colors (`bg_color`, `text_color`).
- Window size and position (`width`, `height`, `last_position`).
- Time precision (`seconds` or `milliseconds`).
- Font settings (`font`, `font_size`).
- Many more settings.

Of course, you can delete this file to reset all settings to default.

### Installation (Developer content)

### Install (English)

To install and run the Time Floating Window, follow these steps:

#### 1. Clone the repository
First, clone this repository to your local machine using `git`:

```bash
git clone https://github.com/liaoyanqing666/Time_Floating_Window.git
```

#### 2. Install dependencies
This project uses `Tkinter` (comes pre-installed with Python). If you are using simplified version of python without `Tkinter`, you can install it using:

```bash
pip install python-tk
```

#### 3. Build with PyInstaller
Once all dependencies are installed, you can package the app as an executable for Windows using `PyInstaller`. To do this, run:

```bash
pip install pyinstaller
```

Then, to create the executable, run:

```bash
pyinstaller --onefile --noconsole --icon=images/icon.ico --name TimeWindow .\Time_Floating_Window.py
```

If there is a problem with the above-mentioned files, the command to package all the packages needed is:

```bash
pyinstaller --onefile --noconsole --icon=images/icon.ico --name TimeWindow_all_python_attached --collect-all tkinter --collect-all ntplib --collect-all win32com --collect-all win32api --collect-all win32con --collect-all pywintypes Time_Floating_Window.py
```

Here are some common `PyInstaller` flags you might use:
- `--onefile`: Optional. Package everything into a single executable file.
- `--noconsole`: Prevent the console window from showing (useful for GUI-only apps).
- `--icon`: Specify the icon for the application.
- `--name`: Specify the name of the generated executable.

The executable (`.exe`) will be located in the `dist` folder.


#### Feel free to fork this repository and make improvements. If you find bugs, want to add new language translation, or have ideas for new features, open an issue or submit a pull request.

---

## 时间悬浮窗 (Chinese)

### 功能

- **实时显示**：以1秒，100毫秒，10毫秒，1毫秒为单位显示当前时间。
- **可自定义外观**：
  - 更改时钟的背景和文字颜色。
  - 调整透明度。
  - 选择你喜欢的字体和字体大小。
- **可调整窗口大小**：动态调整时钟的宽度和高度。
- **锁定和解锁**：解锁时可以自由移动时钟，或者锁定位置。
- **可设置延迟**：可以手动设置时间更改量，也可以通过网络同步自动设置。
- **语言支持**：自动检测系统语言，并允许手动切换语言。现支持英语和中文，你也可以添加更多语言。
- **设置持久化**：自动保存所有设置（颜色、位置、大小）到 `TimeWindowSettings.json` 文件，并在重启时恢复。
- **右键菜单**：右键点击可访问设置、锁定/解锁和关闭选项。
- **首次启动**：通过读取是否有json文件判断是否为首次启动。首次启动时，会询问是否需要添加相关快捷方式。
- **自启动**：可以选择是否开机自启动。

### 使用方法

1. **打开设置**：
   - 右键点击悬浮窗，选择右键菜单中的“设置”。
   - 调整背景色、文字颜色、透明度、字体大小等设置。
   - 设置会立即生效并自动保存。

2. **移动和锁定**：
   - 点击锁定/解锁按钮（🔒/🔓）切换时钟的可移动和锁定状态。
   - 在解锁状态下，拖动时钟可以重新定位它。

3. **关闭**：
   - 点击右上角的 X 按钮，或在右键菜单中选择“关闭”来退出应用。

### 配置文件

该应用会将所有设置保存在 `TimeWindowSettings.json` 文件中，文件位置与应用程序相同。主要的设置包括：
- 语言。
- 颜色 (`bg_color`, `text_color`)。
- 窗口大小和位置 (`width`, `height`, `last_position`)。
- 时间精度（`seconds` 或 `milliseconds`）。
- 字体设置（`font`, `font_size`）。
- 其他设置。

当然，你也可以删除该文件来重置所有设置为默认值。

### 安装 (开发者内容)

要安装并运行时间悬浮窗，按以下步骤进行：

#### 1. 克隆代码库
首先，使用 `git` 克隆这个仓库到本地：

```bash
git clone https://github.com/liaoyanqing666/Time_Floating_Window.git
```

#### 2. **安装依赖**
本项目使用了 `Tkinter`（Python自带）。如果你的Python版本不包含 `Tkinter`，你可以使用以下命令安装：

```bash
pip install python-tk
```

#### 3. 使用PyInstaller打包
安装好所有依赖后，你可以使用 `pyinstaller` 将应用打包成Windows可执行文件。首先安装 `pyinstaller`：

```bash
pip install pyinstaller
```

然后，使用以下命令创建可执行文件：

```bash
pyinstaller --onefile --noconsole --icon=images/icon.ico --name TimeWindow .\Time_Floating_Window.py
```

如果上述文件出现问题，则把所有需要用到的包全打包的命令为：

```bash
pyinstaller --onefile --noconsole --icon=images/icon.ico --name TimeWindow_all_python_attached --collect-all tkinter --collect-all ntplib --collect-all win32com --collect-all win32api --collect-all win32con --collect-all pywintypes Time_Floating_Window.py
```

`PyInstaller` 参数介绍：
- `--onefile`：将所有文件打包成一个单独的可执行文件。
- `--noconsole`：不显示控制台窗口（对于GUI应用很有用）。
- `--icon`：指定应用程序图标。
- `--name`：指定生成的可执行文件的名称。

可执行文件（`.exe`）将位于 `dist` 文件夹内。

#### 你可以随意fork这个存储库并进行改进。如果你发现了bug，想要添加新的语言翻译，或者对新功能有想法，请提issue或提交pull request。

---

#### If you have any questions or suggestions, feel free to contact my Email: *1793706453@qq.com*

