import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
import win32gui
import win32con

class CustomWebEngineView(QWebEngineView):
    def contextMenuEvent(self, event):
        # 禁用右键菜单
        pass

class TickTickViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置无边框、不可拖动
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |  # Tool 窗口通常不出现在任务栏
            Qt.WindowType.WindowStaysOnBottomHint # Qt 级别的置底提示
        )
        # 获取屏幕尺寸并设置为全屏
        screen = QApplication.primaryScreen().geometry()
        self.setFixedSize(screen.width(), screen.height())
        self.move(0, 0)
        self.setWindowTitle("滴答清单")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.set_always_on_bottom() # 修正方法调用

        # 配置持久化存储
        # 判断程序是否被打包
        if getattr(sys, 'frozen', False):
            # 如果是打包状态，则基路径是可执行文件所在目录
            base_path = os.path.dirname(sys.executable)
        else:
            # 如果是正常运行状态，则基路径是脚本所在目录
            base_path = os.path.dirname(os.path.abspath(__file__))

        persistent_dir = os.path.join(base_path, "app_data", "ticktick_profile")
        if not os.path.exists(persistent_dir):
            os.makedirs(persistent_dir, exist_ok=True)

        self.profile = QWebEngineProfile("ticktick_storage", self)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
        self.profile.setPersistentStoragePath(persistent_dir)
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)

        # 加载滴答清单网页
        self.browser = CustomWebEngineView(self.profile, self) # 使用自定义 profile
        self.browser.setUrl(QUrl("https://dida365.com/webapp"))
        self.browser.setGeometry(0, 0, self.width(), self.height()) # WebEngineView相对于QMainWindow的位置
        self.browser.loadFinished.connect(self.apply_multiply_effect)


    def apply_multiply_effect(self, ok):
        if ok:
            script = """
                // Add event listener to prevent Tab key default action
                document.addEventListener('keydown', function(event) {
                    // Check for Tab key (event.key === 'Tab' or event.keyCode === 9 for older browsers)
                    if (event.key === 'Tab' || event.keyCode === 9) {
                        event.preventDefault();
                    }
                });
            """
            self.browser.page().runJavaScript(script)

    def set_always_on_bottom(self):
        hwnd = int(self.winId())
        if hwnd == 0: # 确保 hwnd 有效
            # print("Error: Could not get window handle on time.") # 可选的调试信息
            QTimer.singleShot(200, self.set_always_on_bottom) # 如果第一次失败，稍后再试
            return

        # 设置窗口扩展样式，使其不被激活 (WS_EX_NOACTIVATE)
        # 这有助于防止窗口在点击时被带到前景
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_NOACTIVATE)


    def mousePressEvent(self, _):
        pass  # 禁用拖动
 
    def mouseMoveEvent(self, _):
        pass

    def closeEvent(self, event):
        # 忽略关闭事件，防止 Alt+F4 关闭
        event.ignore()
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = TickTickViewer()
    viewer.show()
    sys.exit(app.exec())
