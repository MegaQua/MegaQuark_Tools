# -*- coding: utf-8 -*-
# JCQVCam_Mobu_ROI_UI.py
# Run inside MotionBuilder Python Editor

import sys, os, math, time, threading, socket, queue, ctypes, atexit
from ctypes import wintypes
from pyfbsdk import *

# ===== 固定 virtucamera 包路径（不要改）=====
PKG_DIR = r"S:\Public\qiu_yi\JCQ_Tool\tools\JCQVCamTool\packages\virtucamera_blender"
if not os.path.isdir(PKG_DIR):
    raise FileNotFoundError(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)

from virtucamera import VCBase, VCServer

try:
    from PySide2 import QtCore, QtWidgets, QtGui
    import shiboken2 as shiboken
except:
    from PySide6 import QtCore, QtWidgets, QtGui
    import shiboken6 as shiboken


# =============================== 主窗口 ===============================
class JCQVCam(QtWidgets.QMainWindow):
    def __init__(self):
        super(JCQVCam, self).__init__(None)
        self.setWindowTitle("JCQ VCam (ROI UI) v0.1")
        self.resize(760, 560)

        # === UI 构建 ===
        cw = QtWidgets.QWidget(self); self.setCentralWidget(cw)
        vbox = QtWidgets.QVBoxLayout(cw)

        # 顶部状态栏
        top = QtWidgets.QGridLayout()
        self.lbl_status   = QtWidgets.QLabel("Idle")
        self.lbl_camera   = QtWidgets.QLabel("-")
        self.lbl_focal    = QtWidgets.QLabel("-")
        self.lbl_frame    = QtWidgets.QLabel("-")
        self.lbl_phonefps = QtWidgets.QLabel("0.0")
        top.addWidget(QtWidgets.QLabel("Status:"),     0, 0); top.addWidget(self.lbl_status,   0, 1)
        top.addWidget(QtWidgets.QLabel("Camera:"),     0, 2); top.addWidget(self.lbl_camera,   0, 3)
        top.addWidget(QtWidgets.QLabel("Focal (mm):"), 1, 0); top.addWidget(self.lbl_focal,    1, 1)
        top.addWidget(QtWidgets.QLabel("Frame:"),      1, 2); top.addWidget(self.lbl_frame,    1, 3)
        top.addWidget(QtWidgets.QLabel("Phone FPS:"),  2, 0); top.addWidget(self.lbl_phonefps, 2, 1)
        vbox.addLayout(top)

        # —— ROI 控件 ——（只有 ROI）
        grp_cap = QtWidgets.QGroupBox("ROI (输出尺寸 = 选区尺寸)")
        grid = QtWidgets.QGridLayout(grp_cap)
        self.btn_pick_roi = QtWidgets.QPushButton("Pick ROI")
        self.btn_full_roi = QtWidgets.QPushButton("Full Screen")
        self.lbl_roi      = QtWidgets.QLabel("ROI: Full Screen")
        grid.addWidget(self.btn_pick_roi, 0, 0)
        grid.addWidget(self.btn_full_roi, 0, 1)
        grid.addWidget(self.lbl_roi,      0, 2, 1, 2)
        vbox.addWidget(grp_cap)

        # 位姿
        grp_pose = QtWidgets.QGroupBox("Transform (Y+ up / Maya, Mobu)")
        grid2 = QtWidgets.QGridLayout(grp_pose)
        self.lbl_tx = QtWidgets.QLabel("0.00")
        self.lbl_ty = QtWidgets.QLabel("0.00")
        self.lbl_tz = QtWidgets.QLabel("0.00")
        self.lbl_rx = QtWidgets.QLabel("0.00")
        self.lbl_ry = QtWidgets.QLabel("0.00")
        self.lbl_rz = QtWidgets.QLabel("0.00")
        grid2.addWidget(QtWidgets.QLabel("TX"), 0, 0); grid2.addWidget(self.lbl_tx, 0, 1)
        grid2.addWidget(QtWidgets.QLabel("TY"), 0, 2); grid2.addWidget(self.lbl_ty, 0, 3)
        grid2.addWidget(QtWidgets.QLabel("TZ"), 0, 4); grid2.addWidget(self.lbl_tz, 0, 5)
        grid2.addWidget(QtWidgets.QLabel("RX°(Pitch)"), 1, 0); grid2.addWidget(self.lbl_rx, 1, 1)
        grid2.addWidget(QtWidgets.QLabel("RY°(Yaw)"),   1, 2); grid2.addWidget(self.lbl_ry, 1, 3)
        grid2.addWidget(QtWidgets.QLabel("RZ°(Roll)"),  1, 4); grid2.addWidget(self.lbl_rz, 1, 5)
        vbox.addWidget(grp_pose)

        # 日志
        self.txt_log = QtWidgets.QTextEdit(); self.txt_log.setReadOnly(True)
        vbox.addWidget(self.txt_log, 1)

        # 控制区
        hctrl = QtWidgets.QHBoxLayout()
        self.btn_start = QtWidgets.QPushButton("Start Server")
        self.btn_stop  = QtWidgets.QPushButton("Stop"); self.btn_stop.setEnabled(False)
        self.edit_port = QtWidgets.QSpinBox(); self.edit_port.setRange(1, 65535); self.edit_port.setValue(7000)
        hctrl.addWidget(QtWidgets.QLabel("Port")); hctrl.addWidget(self.edit_port)
        hctrl.addWidget(self.btn_start); hctrl.addWidget(self.btn_stop); hctrl.addStretch(1)
        vbox.addLayout(hctrl)

        # === Bridge & HeadlessVC/VCServer ===
        self.bridge = self.Bridge()
        self._connect_signals()

        self.vc = self.HeadlessVC(self.bridge)
        self.server = None

        # 轮询队列 -> 刷 UI
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._poll_bus)
        self.timer.start(50)

        # ROI picker 引用（防 GC）
        self._roi_picker = None

        # 退出清理
        QtWidgets.QApplication.instance().aboutToQuit.connect(self._stop_on_quit)
        atexit.register(self._stop_on_quit)

        # 绑定按钮
        self.btn_start.clicked.connect(self._on_start)
        self.btn_stop.clicked.connect(self._on_stop)
        self.btn_pick_roi.clicked.connect(self.on_pick_roi)
        self.btn_full_roi.clicked.connect(self.on_full_roi)

        self.show()

    # === 内部类：ROI 选择器（放入 JCQVCam，确保前置与多屏支持）===
    class _ROIPicker(QtWidgets.QWidget):
        sig_roi = QtCore.Signal(tuple)  # (x1,y1,x2,y2) in GLOBAL/screen coords, or None

        def __init__(self, parent=None):
            super().__init__(None)  # 顶层独立窗口，不挂父对象
            self.setWindowFlags(
                QtCore.Qt.FramelessWindowHint |
                QtCore.Qt.WindowStaysOnTopHint |
                QtCore.Qt.Tool
            )
            self.setWindowModality(QtCore.Qt.ApplicationModal)
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
            self.setCursor(QtCore.Qt.CrossCursor)

            # 覆盖整个虚拟桌面（含负坐标）
            user32 = ctypes.windll.user32
            SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN, SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN = 76, 77, 78, 79
            vx = user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
            vy = user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
            vw = user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
            vh = user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)
            self.setGeometry(vx, vy, vw, vh)

            # 拖拽状态
            self._dragging = False
            self._g0 = QtCore.QPoint()  # global
            self._g1 = QtCore.QPoint()
            self._l0 = QtCore.QPoint()  # local (for drawing)
            self._l1 = QtCore.QPoint()

            self.show()
            self.raise_()
            self.activateWindow()
            QtWidgets.QApplication.processEvents()

        def mousePressEvent(self, e):
            if e.button() == QtCore.Qt.LeftButton:
                self._dragging = True
                self._g0 = e.globalPos()
                self._g1 = e.globalPos()
                self._l0 = e.pos()
                self._l1 = e.pos()
                self.update()
            elif e.button() == QtCore.Qt.RightButton:
                self.sig_roi.emit(None)
                self.close()

        def mouseMoveEvent(self, e):
            if self._dragging:
                self._g1 = e.globalPos()
                self._l1 = e.pos()
                self.update()

        def mouseReleaseEvent(self, e):
            if e.button() == QtCore.Qt.LeftButton and self._dragging:
                self._dragging = False
                # 用全局坐标作为最终 ROI（跨多屏）
                p0, p1 = self._g0, self._g1
                x1, y1 = min(p0.x(), p1.x()), min(p0.y(), p1.y())
                x2, y2 = max(p0.x(), p1.x()), max(p0.y(), p1.y())
                if x2 == x1: x2 += 2
                if y2 == y1: y2 += 2
                self.sig_roi.emit((x1, y1, x2, y2))
                self.close()

        def paintEvent(self, ev):
            p = QtGui.QPainter(self)
            p.setRenderHint(QtGui.QPainter.Antialiasing)
            # 始终画半透明遮罩，给用户“进入选区模式”的反馈
            p.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 96))

            if self._dragging:
                # 用“本地坐标”画框
                r = QtCore.QRect(self._l0, self._l1).normalized()
                p.setPen(QtGui.QPen(QtGui.QColor(0, 180, 255), 2))
                p.setBrush(QtCore.Qt.NoBrush)
                p.drawRect(r)
                p.setPen(QtGui.QColor(255, 255, 255))
                p.drawText(r.bottomLeft() + QtCore.QPoint(6, -6), f"{r.width()} x {r.height()}")

            # 简要提示
            hint = "左键拖拽划定区域，右键取消"
            fm = QtGui.QFontMetrics(p.font())
            tw, th = fm.width(hint) + 12, fm.height() + 8
            rect = QtCore.QRect(12, 12, tw, th)
            p.setBrush(QtGui.QColor(0, 0, 0, 140))
            p.setPen(QtCore.Qt.NoPen)
            p.drawRoundedRect(rect, 6, 6)
            p.setPen(QtGui.QColor(255, 255, 255))
            p.drawText(rect.adjusted(6, 4, -6, -4), QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, hint)

    # ---------------- Bridge ----------------
    class Bridge(QtCore.QObject):
        sig_status    = QtCore.Signal(str)
        sig_log       = QtCore.Signal(str)
        sig_camera    = QtCore.Signal(str)
        sig_focal     = QtCore.Signal(float)
        sig_frame     = QtCore.Signal(float)
        sig_transform = QtCore.Signal(tuple)  # 16 floats
        sig_phonefps  = QtCore.Signal(float)

    def _connect_signals(self):
        self.bridge.sig_status.connect(self._set_status)
        self.bridge.sig_log.connect(self._log)
        self.bridge.sig_camera.connect(lambda s: self.lbl_camera.setText(s))
        self.bridge.sig_focal.connect(lambda v: self.lbl_focal.setText(f"{v:.2f}"))
        self.bridge.sig_frame.connect(lambda f: self.lbl_frame.setText(f"{f:.2f}"))
        self.bridge.sig_phonefps.connect(lambda fps: self.lbl_phonefps.setText(f"{fps:.1f}"))
        self.bridge.sig_transform.connect(self._on_transform_pose)

    # ---------------- 状态/日志/轮询 ----------------
    def _set_status(self, s):
        self.lbl_status.setText(s)
        self._log(s)

    def _log(self, t):
        self.txt_log.append(str(t))
        sb = self.txt_log.verticalScrollBar(); sb.setValue(sb.maximum())

    def _poll_bus(self):
        # 这里只消费 HeadlessVC 推来的 pose 与 log
        try:
            while True:
                p = self.vc_bus.pose_q.get_nowait()
                tx,ty,tz = p["t"]; yaw,pitch,roll = p["ypr"]
                self.lbl_tx.setText(f"{tx:.2f}")
                self.lbl_ty.setText(f"{ty:.2f}")
                self.lbl_tz.setText(f"{tz:.2f}")
                # 注意：UI上标注 RX=Pitch, RY=Yaw, RZ=Roll
                self.lbl_rx.setText(f"{pitch:.2f}")
                self.lbl_ry.setText(f"{yaw:.2f}")
                self.lbl_rz.setText(f"{roll:.2f}")
        except queue.Empty:
            pass
        try:
            while True:
                self._log(self.vc_bus.log_q.get_nowait())
        except queue.Empty:
            pass

    # ---------------- ROI ----------------
    def on_pick_roi(self):
        if self._roi_picker and self._roi_picker.isVisible():
            self._roi_picker.raise_();
            self._roi_picker.activateWindow();
            return
        self._roi_picker = self._ROIPicker(None)  # 顶层独立窗口
        self._roi_picker.sig_roi.connect(self._apply_roi_from_picker)
        self._roi_picker.show()
        self._roi_picker.raise_()
        self._roi_picker.activateWindow()

    def _apply_roi_from_picker(self, roi_or_none):
        if roi_or_none is None:
            return
        x1,y1,x2,y2 = roi_or_none
        self.vc.apply_roi((x1,y1,x2,y2))
        # 立即触发一次重配置，获取实际输出尺寸
        self.vc._do_reconfig_if_needed()
        w,h = self.vc._cap_w, self.vc._cap_h
        self.lbl_roi.setText(f"ROI: ({x1},{y1})-({x2},{y2}) => {w}x{h}")
        self._log(f"[ROI] Set to ({x1},{y1})-({x2},{y2}) => {w}x{h}")

    def on_full_roi(self):
        self.vc.apply_roi(None)
        self.vc._do_reconfig_if_needed()
        w,h = self.vc._cap_w, self.vc._cap_h
        self.lbl_roi.setText(f"ROI: Full Screen => {w}x{h}")
        self._log(f"[ROI] Full screen => {w}x{h}")

    # ---------------- 启停 ----------------
    def _on_start(self):
        if self.server: return
        port = int(self.edit_port.value())
        ver = (2,0,2)
        self.vc.PLUGIN_VERSION = ver
        self.server = VCServer(
            platform="Maya",
            plugin_version=ver,
            event_mode=VCServer.EVENTMODE_PUSH,
            vcbase=self.vc,
            main_thread_func=lambda fn, *a, **k: fn(*a, **k),
            python_executable=r"S:\Public\qiu_yi\py3716\Scripts\python.exe"  # 固定外部 Python
        )
        if not self.server.start_serving(port):
            QtWidgets.QMessageBox.critical(self, "VCam", f"Port {port} failed.")
            self.server = None
            return
        self.btn_start.setEnabled(False); self.btn_stop.setEnabled(True); self.edit_port.setEnabled(False)
        self._set_status(f"Serving on {self._current_ipv4()}:{port}")

    def _on_stop(self):
        if not self.server: return
        try:
            self.server.stop_serving()
        finally:
            self.server = None
            self.btn_start.setEnabled(True); self.btn_stop.setEnabled(False); self.edit_port.setEnabled(True)
            self._set_status("Stopped")

    def _stop_on_quit(self):
        try: self._on_stop()
        except: pass

    # ---------------- 变换矩阵 -> 位姿（并入 UI 队列） ----------------
    def _on_transform_pose(self, m16):
        tx, ty, tz, yaw, pitch, roll = self.HeadlessVC.mat_to_pose(m16)
        payload = {"time": time.time(), "t":[tx,ty,tz], "ypr":[yaw,pitch,roll]}
        self.vc_bus.set_pose(payload)

    def _current_ipv4(self):
        ip = "127.0.0.1"
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except: pass
        return ip

    # =============== 内部：UI 与 HeadlessVC 的轻量总线 ===============
    class _Bus:
        def __init__(self):
            self.pose_q = queue.Queue()
            self.log_q  = queue.Queue()
            self._lock = threading.Lock()
            self._last_pose = None
        def set_pose(self, payload: dict):
            try: self.pose_q.put_nowait(payload)
            except: pass
            with self._lock:
                self._last_pose = payload

    # 供 _poll_bus 使用
    vc_bus = _Bus()

    # ===================== HeadlessVC（抓屏 + VCServer 回调） =====================
    class HeadlessVC(VCBase):
        class _RECT(ctypes.Structure):
            _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG),
                        ("right", wintypes.LONG), ("bottom", wintypes.LONG)]

        class _BITMAPV4HEADER(ctypes.Structure):
            _fields_ = [
                ("bV4Size", ctypes.c_uint32), ("bV4Width", ctypes.c_int32), ("bV4Height", ctypes.c_int32),
                ("bV4Planes", ctypes.c_uint16), ("bV4BitCount", ctypes.c_uint16),
                ("bV4V4Compression", ctypes.c_uint32), ("bV4SizeImage", ctypes.c_uint32),
                ("bV4XPelsPerMeter", ctypes.c_int32), ("bV4YPelsPerMeter", ctypes.c_int32),
                ("bV4ClrUsed", ctypes.c_uint32), ("bV4ClrImportant", ctypes.c_uint32),
                ("bV4RedMask", ctypes.c_uint32), ("bV4GreenMask", ctypes.c_uint32),
                ("bV4BlueMask", ctypes.c_uint32), ("bV4AlphaMask", ctypes.c_uint32),
                ("bV4CSType", ctypes.c_uint32), ("bV4Endpoints", ctypes.c_byte * (9 * 4 * 3)),
                ("bV4GammaRed", ctypes.c_uint32), ("bV4GammaGreen", ctypes.c_uint32), ("bV4GammaBlue", ctypes.c_uint32),
            ]

        class _ScreenGrabberWin:
            BI_BITFIELDS = 3
            LCS_WINDOWS_COLOR_SPACE = 0x57696E20
            SRCCOPY = 0x00CC0020
            COLORONCOLOR = 3
            def __init__(self, outer, out_w, out_h):
                self._outer = outer
                self.user32 = ctypes.windll.user32
                self.gdi32  = ctypes.windll.gdi32
                self.virtual_rect = self._get_virtual_rect()
                self.src_rect = outer._RECT(self.virtual_rect.left, self.virtual_rect.top,
                                            self.virtual_rect.right, self.virtual_rect.bottom)
                self.out_w, self.out_h = int(out_w), int(out_h)
                self.hdc_screen = self.user32.GetDC(0)
                self.hdc_mem    = self.gdi32.CreateCompatibleDC(self.hdc_screen)
                self.ppv_bits   = ctypes.c_void_p()
                self.hbmp = None; self.hbmp_old = None
                self._create_rgba_dib(self.out_w, self.out_h)

            def _get_virtual_rect(self):
                SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN, SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN = 76,77,78,79
                x = self.user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
                y = self.user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
                w = self.user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
                h = self.user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)
                return self._outer._RECT(x, y, x+w, y+h)

            def update_roi(self, roi_tuple_or_none):
                vr = self.virtual_rect
                if roi_tuple_or_none is None:
                    self.src_rect = self._outer._RECT(vr.left, vr.top, vr.right, vr.bottom); return
                x1,y1,x2,y2 = roi_tuple_or_none
                if x2 < x1: x1,x2 = x2,x1
                if y2 < y1: y1,y2 = y2,y1
                x1 = max(vr.left,  min(x1, vr.right))
                x2 = max(vr.left,  min(x2, vr.right))
                y1 = max(vr.top,   min(y1, vr.bottom))
                y2 = max(vr.top,   min(y2, vr.bottom))
                if x2 == x1: x2 = x1 + 2
                if y2 == y1: y2 = y1 + 2
                # 末尾替换 self.src_rect = ...
                w = max(2, int(x2 - x1));
                h = max(2, int(y2 - y1))
                # 保持右下角 = 左上 + 尺寸（偶数）
                w = w + (w & 1);
                h = h + (h & 1)
                self.src_rect = self._outer._RECT(int(x1), int(y1), int(x1 + w), int(y1 + h))



            def _create_rgba_dib(self, w, h):
                if self.hbmp:
                    self.gdi32.SelectObject(self.hdc_mem, self.hbmp_old)
                    self.gdi32.DeleteObject(self.hbmp)
                v4 = self._outer._BITMAPV4HEADER()
                v4.bV4Size = ctypes.sizeof(self._outer._BITMAPV4HEADER)
                v4.bV4Width, v4.bV4Height = int(w), -int(h)  # top-down
                v4.bV4Planes = 1; v4.bV4BitCount = 32; v4.bV4V4Compression = self.BI_BITFIELDS
                v4.bV4SizeImage = int(w) * int(h) * 4
                v4.bV4RedMask, v4.bV4GreenMask, v4.bV4BlueMask, v4.bV4AlphaMask = 0x000000FF,0x0000FF00,0x00FF0000,0xFF000000
                v4.bV4CSType = self.LCS_WINDOWS_COLOR_SPACE
                self.ppv_bits = ctypes.c_void_p()
                self.hbmp = self.gdi32.CreateDIBSection(self.hdc_screen, ctypes.byref(v4), 0,
                                                        ctypes.byref(self.ppv_bits), None, 0)
                if not self.hbmp:
                    raise RuntimeError("CreateDIBSection failed")
                self.hbmp_old = self.gdi32.SelectObject(self.hdc_mem, self.hbmp)
                self.out_w, self.out_h = int(w), int(h)

            def ensure_size(self, out_w, out_h):
                out_w, out_h = int(out_w), int(out_h)
                if out_w == self.out_w and out_h == self.out_h: return
                self._create_rgba_dib(out_w, out_h)

            def grab_into(self):
                sr = self.src_rect
                sx, sy = int(sr.left), int(sr.top)
                sw, sh = int(sr.right - sr.left), int(sr.bottom - sr.top)

                # 关键：把全局(虚拟桌面)坐标换算到 Desktop DC 的源坐标系
                # 对于 GetDC(0)，源 (0,0) == 虚拟桌面 (virtual_rect.left, virtual_rect.top)
                sx_adj = sx - self.virtual_rect.left
                sy_adj = sy - self.virtual_rect.top

                self.gdi32.SetStretchBltMode(self.hdc_mem, self.COLORONCOLOR)
                self.gdi32.StretchBlt(self.hdc_mem, 0, 0, self.out_w, self.out_h,
                                      self.hdc_screen, sx_adj, sy_adj, sw, sh, self.SRCCOPY)

            def get_ptr(self): return int(self.ppv_bits.value)

            def release(self):
                try:
                    if self.hbmp:
                        ctypes.windll.gdi32.SelectObject(self.hdc_mem, self.hbmp_old)
                        ctypes.windll.gdi32.DeleteObject(self.hbmp)
                    if self.hdc_mem:
                        ctypes.windll.gdi32.DeleteDC(self.hdc_mem)
                    if self.hdc_screen:
                        ctypes.windll.user32.ReleaseDC(0, self.hdc_screen)
                except: pass

        # ---------- HeadlessVC ----------
        def __init__(self, bridge):
            super().__init__()
            self.bridge = bridge
            self._current_frame = 1.0; self._range = (1.0, 250.0); self._fps = 30.0
            self._cams = ["VirtualCam"]; self._active_cam = "VirtualCam"
            self._flen = 35.0
            self._tm = (1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1)
            self._has_keys = {"transform":False, "flen":False}
            self._roi = None; self._cap_w = 2; self._cap_h = 2; self._buf_ptr = 0
            self._grab = None; self._server = None
            self._cap_lock = threading.Lock(); self._pending_reconfig = True
            self._last_ts = None; self._fps_ema = None; self._ema_alpha = 0.2

        @staticmethod
        def _even(v): v = int(v); return v if (v % 2 == 0) else (v + 1)

        def apply_roi(self, roi_tuple_or_none):
            self._roi = roi_tuple_or_none
            self._pending_reconfig = True

        # --- VCServer 播放接口 ---
        def get_playback_state(self, vcserver): return (self._current_frame, self._range[0], self._range[1])
        def get_playback_fps(self, vcserver): return self._fps
        def set_frame(self, vcserver, frame: float):
            self._current_frame = float(frame); self.bridge.sig_frame.emit(self._current_frame)
        def set_playback_range(self, vcserver, start: float, end: float): self._range = (float(start), float(end))
        def start_playback(self, vcserver, forward: bool): pass
        def stop_playback(self, vcserver): pass

        # --- 相机接口 ---
        def get_scene_cameras(self, vcserver): return list(self._cams)
        def get_camera_exists(self, vcserver, camera_name: str): return camera_name in self._cams
        def get_camera_has_keys(self, vcserver, camera_name: str): return (self._has_keys["transform"], self._has_keys["flen"])
        def get_camera_focal_length(self, vcserver, camera_name: str): return float(self._flen)
        def get_camera_transform(self, vcserver, camera_name: str): return tuple(self._tm)
        def set_camera_focal_length(self, vcserver, camera_name: str, focal_length: float):
            self._flen = float(focal_length); self.bridge.sig_focal.emit(self._flen); self.bridge.sig_log.emit(f"[VCam] Focal -> {self._flen:.2f}mm")
        def set_camera_transform(self, vcserver, camera_name: str, transform_matrix):
            if len(transform_matrix) != 16: raise ValueError("transform_matrix must be 16 floats")
            self._tm = tuple(float(x) for x in transform_matrix); self.bridge.sig_transform.emit(self._tm)
        def set_camera_flen_keys(self, vcserver, camera_name: str, keyframes, focal_length_values):
            self._has_keys["flen"] = True
            self._flen = float(focal_length_values[-1]) if focal_length_values else self._flen
            self.bridge.sig_focal.emit(self._flen)
        def set_camera_transform_keys(self, vcserver, camera_name: str, keyframes, transform_matrix_values):
            self._has_keys["transform"] = True
            if transform_matrix_values and len(transform_matrix_values[-1]) == 16:
                self._tm = tuple(float(x) for x in transform_matrix_values[-1]); self.bridge.sig_transform.emit(self._tm)
        def remove_camera_keys(self, vcserver, camera_name: str): self._has_keys = {"transform": False, "flen": False}
        def create_new_camera(self, vcserver):
            base = "VirtualCam"; idx=1; name=base
            while name in self._cams: idx += 1; name = f"{base}{idx}"
            self._cams.append(name); return name
        def look_through_camera(self, vcserver, camera_name: str):
            if camera_name in self._cams:
                self._active_cam = camera_name; self.bridge.sig_camera.emit(camera_name); self.bridge.sig_log.emit(f"[VCam] Look through: {camera_name}")

        # --- 重配置与抓屏 ---
        def _do_reconfig_if_needed(self):
            if not self._pending_reconfig: return
            with self._cap_lock:
                self._pending_reconfig = False
                if self._grab is None:
                    self._grab = JCQVCam.HeadlessVC._ScreenGrabberWin(self, 2, 2)
                self._grab.update_roi(self._roi)
                sr = self._grab.src_rect
                roi_w = max(2, int(sr.right - sr.left)); roi_h = max(2, int(sr.bottom - sr.top))
                out_w = self._even(roi_w); out_h = self._even(roi_h)
                self._grab.ensure_size(out_w, out_h)
                self._buf_ptr = self._grab.get_ptr()
                self._cap_w, self._cap_h = self._grab.out_w, self._grab.out_h
                if self._server: self._server.set_capture_resolution(self._cap_w, self._cap_h)
                self.bridge.sig_log.emit(f"[VCam] Reconfig: ROI ({sr.left},{sr.top})-({sr.right},{sr.bottom}) => {self._cap_w}x{self._cap_h}")

        def capture_will_start(self, vcserver):
            self._server = vcserver
            self._pending_reconfig = True
            self._do_reconfig_if_needed()
            with self._cap_lock:
                vcserver.set_capture_resolution(self._cap_w, self._cap_h)
                vcserver.set_capture_mode(vcserver.CAPMODE_BUFFER_POINTER, vcserver.CAPFORMAT_UBYTE_RGBA)
            self._last_ts = None; self._fps_ema = None
            r = self._grab.src_rect
            self.bridge.sig_status.emit("Capturing")
            self.bridge.sig_log.emit(f"[VCam] Start capture: ROI ({r.left},{r.top})-({r.right},{r.bottom}) => {self._cap_w}x{self._cap_h}")

        def capture_did_end(self, vcserver):
            with self._cap_lock:
                if self._grab: self._grab.release(); self._grab = None
                self._buf_ptr = 0
            self._last_ts = None; self._fps_ema = None; self._server = None
            self.bridge.sig_status.emit("Idle")
            self.bridge.sig_log.emit("[VCam] Capture stopped")

        def _update_phone_fps(self):
            now = time.time()
            if self._last_ts is None: self._last_ts = now; return
            dt = now - self._last_ts; self._last_ts = now
            if dt <= 0: return
            inst = 1.0/dt
            self._fps_ema = inst if self._fps_ema is None else (0.2*inst + 0.8*(self._fps_ema))
            self.bridge.sig_phonefps.emit(self._fps_ema)

        def get_capture_pointer(self, vcserver, camera_name: str):
            self._do_reconfig_if_needed()
            with self._cap_lock:
                if self._grab: self._grab.grab_into()
                self._update_phone_fps()
                return int(self._buf_ptr)

        # --- 矩阵 -> (tx,ty,tz,yaw,pitch,roll)（Y+）---
        @staticmethod
        def mat_to_pose(m16):
            r11,r12,r13 = m16[0],m16[1],m16[2]
            r21,r22,r23 = m16[4],m16[5],m16[6]
            r31,r32,r33 = m16[8],m16[9],m16[10]
            tx,ty,tz    = -1*m16[14], m16[13], m16[12]
            pitch = math.asin(max(-1.0, min(1.0, -r31)))
            cp = math.cos(pitch)
            if abs(cp) > 1e-6:
                roll = math.atan2(r32, r33)
                yaw  = math.atan2(r21, r11)
            else:
                roll = 0.0
                yaw  = math.atan2(-r12, r22)
            deg = 180.0 / math.pi
            return tx,ty,tz, yaw*deg, -pitch*deg, -roll*deg

        # --- 回调反馈 ---
        def client_connected(self, vcserver, client_ip, client_port):
            self.bridge.sig_status.emit(f"Connected {client_ip}:{client_port}")
            self.bridge.sig_log.emit(f"[VCam] Client connected: {client_ip}:{client_port}")

        def client_disconnected(self, vcserver):
            self.bridge.sig_status.emit("Disconnected")
            self.bridge.sig_log.emit("[VCam] Client disconnected")

        def current_camera_changed(self, vcserver, current_camera):
            self.bridge.sig_camera.emit(current_camera)
            self.bridge.sig_log.emit(f"[VCam] Current camera: {current_camera}")

        def server_did_stop(self, vcserver):
            self.bridge.sig_status.emit("Stopped")
            self.bridge.sig_log.emit("[VCam] Server stopped")


# ====== 单实例（重复运行脚本时：关闭旧窗，开启新窗）======
def _alive(w): return (w is not None) and shiboken.isValid(w)

_old = globals().get("VCamUI")
if _alive(_old):
    try: _old.close(); _old.deleteLater()
    except: pass

VCamUI = JCQVCam()
VCamUI.show()
VCamUI.raise_()
VCamUI.activateWindow()
