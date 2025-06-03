import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt, QTimer, QUrl, QStandardPaths
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
import win32gui
import win32con

class CustomWebEngineView(QWebEngineView):
    def contextMenuEvent(self, event):
        # 禁用右键菜单
        pass

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Tab:
            # 忽略 Tab 键事件
            event.ignore()
        else:
            super().keyPressEvent(event)

class TickTickViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置无边框、不可拖动
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |  # Tool 窗口通常不出现在任务栏
            Qt.WindowType.WindowStaysOnBottomHint # Qt 级别的置底提示
        )
        self.setFixedSize(600, 640)  # 可改为你需要的尺寸
        self.move(70, 90) # 移动到屏幕左上角
        self.setWindowTitle("滴答清单")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.set_always_on_bottom() # 修正方法调用

        # 配置持久化存储
        data_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
        persistent_dir = os.path.join(data_path, "ticktick_profile")
        if not os.path.exists(persistent_dir):
            os.makedirs(persistent_dir)

        self.profile = QWebEngineProfile("ticktick_storage", self)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
        self.profile.setPersistentStoragePath(persistent_dir)
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)

        # 加载滴答清单网页
        self.browser = CustomWebEngineView(self.profile, self) # 使用自定义 profile
        self.browser.setUrl(QUrl("https://dida365.com/webapp"))
        self.browser.setGeometry(-50, 0, 650, 640) # WebEngineView相对于QMainWindow的位置
        # 确保 QWebEngineView 背景是透明的，以便 mix-blend-mode 生效
        self.browser.page().setBackgroundColor(Qt.GlobalColor.transparent)
        self.browser.loadFinished.connect(self.apply_multiply_effect)


    def apply_multiply_effect(self, ok):
        if ok:
            # 为 body 应用 mix-blend-mode 和透明背景
            # !important 用于尝试覆盖页面自身的样式
            script = """
                document.body.style.mixBlendMode = 'multiply';
                document.body.style.backgroundColor = 'transparent !important';
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
