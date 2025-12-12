# -*- coding: utf-8 -*-
# Maya_YenStockSim20_v2.py — 日语UI / 固定20ティック / 右端が最新 / 凡例分離
import math, time, random
from datetime import datetime
from PySide2 import QtCore, QtGui, QtWidgets

TICK_MS     = 5000            # 5秒ごと
INIT_CASH   = 10000.0         # 初期資金
HIST_POINTS = 20              # グラフの表示点数固定

def now_ts(): return time.time()
def fmt_yen(x): return f"¥{int(round(x)):,.0f}"

# ===== エンジン =====
class _Base:
    def __init__(self, name, p0=100.0, seed=None):
        self.name = name; self.price = float(p0)
        self.last_update = now_ts()
        self.rng = random.Random(seed)
    def step(self, t): return self.price

class TrendUpGBM(_Base):
    def step(self, t):
        dt = max(t - self.last_update, 0.0); self.last_update = t
        mu, sigma = 0.05, 0.12
        scale = dt / (252*24*3600)
        z = self.rng.gauss(0,1)
        self.price *= math.exp((mu - 0.5 * sigma ** 2) * scale + sigma * math.sqrt(scale) * z)
        return self.price

class MeanRevertOU(_Base):
    def step(self, t):
        dt = max(t - self.last_update, 0.0); self.last_update = t
        kappa, theta, sigma = 1.2, 100.0, 3.0
        self.price += kappa * (theta - self.price) * (dt/30.0) + self.rng.gauss(0,sigma) * math.sqrt(max(dt, 1) / 30.0)
        self.price = max(1.0, self.price); return self.price

class JumpyHighVol(_Base):
    def step(self, t):
        dt = max(t - self.last_update, 0.0); self.last_update = t
        drift, vol = 0.0, 0.35
        scale = dt/(24*3600); z = self.rng.gauss(0,1)
        self.price *= math.exp((drift - 0.5 * vol ** 2) * scale + vol * math.sqrt(scale) * z)
        if self.rng.random() < min(0.03, dt/60.0*0.03):
            self.price *= self.rng.choice([0.85, 0.9, 1.1, 1.2, 1.3])
        self.price = max(0.5, self.price); return self.price

class CyclicalSine(_Base):
    def __init__(self, name, p0=90.0, seed=None):
        super().__init__(name, p0, seed)
        self.base, self.amp, self.period_s = p0, 12.0, 60.0
    def step(self, t):
        self.last_update = t
        phase = 2 * math.pi * (t % self.period_s) / self.period_s
        self.price = max(1.0, self.base + self.amp * math.sin(phase) + self.rng.gauss(0, 1.0))
        return self.price

class RegimeSwitchRW(_Base):
    def __init__(self, name, p0=70.0, seed=None):
        super().__init__(name, p0, seed); self.regime = "calm"
    def step(self, t):
        dt = max(t - self.last_update, 0.0); self.last_update = t
        if self.rng.random() < min(0.02, dt/60.0*0.02):
            self.regime = self.rng.choice(["calm","panic","hype"])
        if self.regime=="calm":  mu, sigma = 0.00, 0.08
        elif self.regime=="panic": mu, sigma = -0.20, 0.40
        else:                     mu, sigma = 0.25, 0.35
        scale = dt/(24*3600); z = self.rng.gauss(0,1)
        self.price *= math.exp((mu - 0.5 * sigma ** 2) * scale + sigma * math.sqrt(scale) * z)
        self.price = max(0.5, self.price); return self.price

# ===== マーケット（初期20点生成）=====
class Market(QtCore.QObject):
    ticked = QtCore.Signal(dict)
    def __init__(self, parent=None):
        super().__init__(parent)
        seed_base = int(datetime.now().strftime("%Y%m%d"))
        self.names = [
            "株式会社ジャストコーズプロダクション",  # A
            "残業証券",                               # B
            "株式会社CY○○games",                      # C
            "社長食堂",                               # D
            "JCQ銀行",                                # E
        ]
        self.engines = [
            TrendUpGBM(self.names[0], 100, seed_base+1),
            MeanRevertOU(self.names[1], 100, seed_base+2),
            JumpyHighVol(self.names[2], 60,  seed_base+3),
            CyclicalSine(self.names[3], 90,  seed_base+4),
            RegimeSwitchRW(self.names[4], 70, seed_base+5),
        ]
        self._prices = {e.name: e.price for e in self.engines}
        # 初期20点：5秒間隔で合成
        self.bootstrap_history = []
        t = now_ts() - (HIST_POINTS-1)*5
        for _ in range(HIST_POINTS):
            for e in self.engines: e.step(t)
            self._prices = {e.name: e.price for e in self.engines}
            self.bootstrap_history.append(dict(self._prices))
            t += 5
        # タイマー
        self.timer = QtCore.QTimer(self); self.timer.timeout.connect(self._on_tick); self.timer.start(TICK_MS)
    def prices(self): return dict(self._prices)
    @QtCore.Slot()
    def _on_tick(self):
        t = now_ts()
        for e in self.engines: e.step(t)
        self._prices = {e.name: e.price for e in self.engines}
        self.ticked.emit(self.prices())

# ===== 口座（空売り禁止）=====
class Account:
    def __init__(self, cash=INIT_CASH):
        self.cash = float(cash)
        self.pos = {}     # name -> {"qty":float, "avg":float}
        self.open_px = {} # 初期表示基準
    def get_qty(self, name): return self.pos.get(name, {}).get("qty", 0.0)
    def get_avg(self, name): return self.pos.get(name, {}).get("avg", 0.0)
    def ensure_open_px(self, name, px):
        if name not in self.open_px: self.open_px[name] = float(px)
    def trade_buy(self, name, px, qty):
        q0 = self.get_qty(name); a0 = self.get_avg(name)
        q1 = q0 + qty; cost = a0*q0 + px*qty; a1 = cost / q1 if q1>1e-8 else 0.0
        self.pos[name] = {"qty": q1, "avg": a1}; self.cash -= px * qty; return qty
    def trade_sell(self, name, px, qty):
        q0 = self.get_qty(name); sell_qty = min(qty, max(0.0, q0))
        if sell_qty <= 0: return 0.0
        q1 = q0 - sell_qty; a0 = self.get_avg(name)
        self.pos[name] = ({} if q1<=1e-8 else {"qty": q1, "avg": a0})
        self.cash += px * sell_qty; return sell_qty
    def mkt_value(self, prices):
        return sum((rec["qty"]*prices.get(n,0.0)) for n,rec in self.pos.items() if rec)
    def unreal_pnl(self, prices):
        pnl = 0.0
        for n,rec in self.pos.items():
            if not rec: continue
            pnl += (prices.get(n,0.0) - rec["avg"]) * rec["qty"]
        return pnl

# ===== ラインチャート（20点固定 / 右端が最新 / 凡例は別帯）=====
class LineChart(QtWidgets.QWidget):
    def __init__(self, names, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(280)
        pal = self.palette(); pal.setColor(QtGui.QPalette.Window, QtGui.QColor("#1e1e1e")); self.setPalette(pal)
        self.names = list(names)
        self.colors = {
            self.names[0]: QtGui.QColor(76,175,80),
            self.names[1]: QtGui.QColor(33,150,243),
            self.names[2]: QtGui.QColor(244,67,54),
            self.names[3]: QtGui.QColor(255,193,7),
            self.names[4]: QtGui.QColor(156,39,176),
        }
        # history[name] = list of float (価格) — インデックス0が最古, -1が最新
        self.history = {n: [] for n in self.names}

    def append_prices(self, prices):
        for n in self.names:
            hist = self.history[n]
            hist.append(float(prices[n]))
            if len(hist) > HIST_POINTS:
                del hist[0:len(hist)-HIST_POINTS]
        self.update()

    def seed_with_series(self, series_list):
        # series_list: 古→新 の dict(name->price) の配列
        for s in series_list: self.append_prices(s)

    def paintEvent(self, ev):
        if not any(self.history[n] for n in self.names): return
        p = QtGui.QPainter(self); p.setRenderHint(QtGui.QPainter.Antialiasing, True)

        # レイアウト：上に凡例帯、高さ legend_h
        legend_h = 28
        rect = self.rect().adjusted(56, legend_h+8, -12, -28)  # 軸余白＋凡例分
        self._draw_legend(p, legend_h)
        self._draw_grid(p, rect)

        # Yレンジ（全銘柄の20点から算出）
        all_vals=[]
        for n in self.names: all_vals += self.history[n]
        vmin, vmax = (min(all_vals), max(all_vals)) if all_vals else (0,1)
        if abs(vmax-vmin) < 1e-6: vmax += 1.0; vmin -= 1.0

        # Xはインデックス(0..HIST_POINTS-1) 固定。右端が最新。
        def map_x(i):
            if HIST_POINTS<=1: return rect.left()
            return rect.left() + (i/(HIST_POINTS-1.0))*rect.width()
        def map_y(v): return rect.bottom() - ( (v - vmin)/(vmax - vmin) )*rect.height()

        # 全銘柄描画
        for n in self.names:
            data = self.history[n]
            if len(data) < 2: continue
            path = QtGui.QPainterPath()
            for i, v in enumerate(data):
                x = map_x(i); y = map_y(v)
                path.moveTo(x,y) if i==0 else path.lineTo(x,y)
            p.setPen(QtGui.QPen(self.colors.get(n, QtCore.Qt.white), 2))
            p.drawPath(path)

        # 目盛/ラベル
        p.setPen(QtGui.QPen(QtGui.QColor("#aaaaaa")))
        font=p.font(); font.setPointSize(9); p.setFont(font)
        # Y軸 5段
        for i in range(5):
            val = vmin + i*(vmax-vmin)/4.0
            y = rect.bottom() - i*(rect.height()/4.0)
            p.drawText(4, y+4, fmt_yen(val))
        # X 軸：左=過去20ティック前 / 右=最新
        p.drawText(rect.left(), rect.bottom()+18, "← 古い（20ティック前）")
        right_label = "最新（0）"
        metrics = QtGui.QFontMetrics(p.font())
        p.drawText(rect.right()-metrics.width(right_label), rect.bottom()+18, right_label)

    def _draw_legend(self, p, legend_h):
        # 上帯に凡例（線 + 銘柄名）
        band = QtCore.QRect(self.rect().left()+8, self.rect().top()+4, self.rect().width()-16, legend_h)
        x = band.left(); y = band.top()+6
        for n in self.names:
            p.setPen(QtGui.QPen(self.colors.get(n, QtCore.Qt.white), 3))
            p.drawLine(x, y+6, x+22, y+6)
            p.setPen(QtGui.QPen(QtGui.QColor("#dddddd")))
            p.drawText(x+28, y+10, n)
            x += 180  # 1項目の横幅
            if x+160 > band.right():
                x = band.left()
                y += 18

    def _draw_grid(self, p, rect):
        p.save()
        p.setPen(QtGui.QPen(QtGui.QColor("#444"), 1)); p.drawRect(rect)
        p.setPen(QtGui.QPen(QtGui.QColor("#333"), 1, QtCore.Qt.DashLine))
        for i in range(1,4):
            y = rect.top()+i*(rect.height()/4.0); p.drawLine(rect.left(),y,rect.right(),y)
        for i in range(1,5):
            x = rect.left()+i*(rect.width()/5.0); p.drawLine(x,rect.top(),x,rect.bottom())
        p.restore()

# ===== メインウィンドウ =====
class YenStockWindow(QtWidgets.QWidget):
    _instance = None
    @classmethod
    def open_unique(cls):
        if cls._instance and cls._instance.isVisible():
            try:
                cls._instance.raise_(); cls._instance.activateWindow(); return cls._instance
            except Exception: pass
        cls._instance = cls(); cls._instance.show(); cls._instance.raise_(); cls._instance.activateWindow(); return cls._instance

    def __init__(self):
        super().__init__()
        self.setWindowTitle("円ギャグ銘柄 · 模擬トレード（20ティック固定・右端が最新・空売り不可）")
        self.resize(1180, 620)

        self.market = Market(self)
        self.account = Account(INIT_CASH)
        self.market.ticked.connect(self.on_tick)

        self.names = [e.name for e in self.market.engines]
        self._build_ui()

        # 初期20点を投入
        self.chart.seed_with_series(self.market.bootstrap_history)
        self._refresh(self.market.prices(), first=True)

        # 時計
        self.clockTimer = QtCore.QTimer(self)
        self.clockTimer.timeout.connect(lambda: self.lblClock.setText(datetime.now().strftime("時刻：%Y-%m-%d %H:%M:%S")))
        self.clockTimer.start(1000)
        self.lblClock.setText(datetime.now().strftime("時刻：%Y-%m-%d %H:%M:%S"))

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)

        # 上段
        top = QtWidgets.QHBoxLayout()
        self.lblClock  = QtWidgets.QLabel("")
        self.lblCash   = QtWidgets.QLabel("")
        self.lblEquity = QtWidgets.QLabel("")
        self.lblPnL    = QtWidgets.QLabel("")
        for w in (self.lblClock, self.lblCash, self.lblEquity, self.lblPnL):
            top.addWidget(w); top.addStretch(1)
        root.addLayout(top)

        # 中段：テーブル + 注文
        mid = QtWidgets.QHBoxLayout(); root.addLayout(mid, 1)
        self.tbl = QtWidgets.QTableWidget(5, 6)
        self.tbl.setHorizontalHeaderLabels(["銘柄名","価格","変動%（初期比）","保有数量","平均単価","評価損益"])
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tbl.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tbl.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        mid.addWidget(self.tbl, 6)

        for i, n in enumerate(self.names):
            self.tbl.setItem(i, 0, QtWidgets.QTableWidgetItem(n))

        box = QtWidgets.QGroupBox("注文（空売り不可）")
        form = QtWidgets.QFormLayout(box)
        self.cmbName = QtWidgets.QComboBox(); self.cmbName.addItems(self.names)
        self.spnQty  = QtWidgets.QDoubleSpinBox(); self.spnQty.setDecimals(0); self.spnQty.setRange(1, 10**9); self.spnQty.setValue(100)
        self.btnBuy  = QtWidgets.QPushButton("買い（＋）")
        self.btnSell = QtWidgets.QPushButton("売り（－/保有分まで）")
        self.btnBuy.clicked.connect(self._buy); self.btnSell.clicked.connect(self._sell)
        form.addRow("銘柄：", self.cmbName)
        form.addRow("数量：", self.spnQty)
        hb = QtWidgets.QHBoxLayout(); hb.addWidget(self.btnBuy); hb.addWidget(self.btnSell); hb.addStretch(1)
        form.addRow(hb)
        mid.addWidget(box, 4)

        # 下段：グラフ
        self.chart = LineChart(self.names)
        root.addWidget(self.chart, 1)

        self.status = QtWidgets.QLabel("準備完了。")
        root.addWidget(self.status)

    @QtCore.Slot(dict)
    def on_tick(self, prices):
        self.chart.append_prices(prices)
        self._refresh(prices)

    def _buy(self):
        n = self.cmbName.currentText(); q = int(self.spnQty.value()); px = self.market.prices()[n]
        self.account.ensure_open_px(n, px)
        done = self.account.trade_buy(n, px, q)
        self.status.setText(f"買い：{n} x {done} @ {fmt_yen(px)}")
        self._refresh(self.market.prices())

    def _sell(self):
        n = self.cmbName.currentText(); q = int(self.spnQty.value()); px = self.market.prices()[n]
        have = self.account.get_qty(n)
        if have <= 0:
            self.status.setText(f"売り不可：{n} の保有がありません。"); return
        self.account.ensure_open_px(n, px)
        done = self.account.trade_sell(n, px, q)
        self.status.setText(f"売り：{n} x {int(done)} @ {fmt_yen(px)}")
        self._refresh(self.market.prices())

    def _refresh(self, prices, first=False):
        for i, n in enumerate(self.names):
            px = prices[n]
            if first: self.account.ensure_open_px(n, px)
            base = self.account.open_px.get(n, px)
            pct = (px/base - 1.0) * 100.0 if base>0 else 0.0

            self._set(i, 1, fmt_yen(px))
            it_pct = QtWidgets.QTableWidgetItem(f"{pct:+.2f}%")
            it_pct.setForeground(QtGui.QBrush(QtGui.QColor("#d32f2f" if pct<0 else "#388e3c")))
            self.tbl.setItem(i, 2, it_pct)

            qty = self.account.get_qty(n)
            avg = self.account.get_avg(n)
            pnl = (px - avg) * qty if qty>0 else 0.0
            self._set(i, 3, f"{int(qty)}")
            self._set(i, 4, fmt_yen(avg) if qty>0 else "-")
            it_pnl = QtWidgets.QTableWidgetItem(fmt_yen(pnl))
            it_pnl.setForeground(QtGui.QBrush(QtGui.QColor("#d32f2f" if pnl<0 else "#388e3c")))
            self.tbl.setItem(i, 5, it_pnl)

        mv  = self.account.mkt_value(prices)
        pnl = self.account.unreal_pnl(prices)
        equity = self.account.cash + mv
        self.lblCash.setText(f"現金：{fmt_yen(self.account.cash)}")
        self.lblEquity.setText(f"総資産：{fmt_yen(equity)}")
        self.lblPnL.setText(f"評価損益：{fmt_yen(pnl)}")

        self.tbl.resizeColumnsToContents()
        self.tbl.horizontalHeader().setStretchLastSection(True)

    def _set(self, r, c, text):
        it = QtWidgets.QTableWidgetItem(str(text))
        it.setTextAlignment(QtCore.Qt.AlignRight if c>=1 else QtCore.Qt.AlignLeft)
        self.tbl.setItem(r, c, it)

# Maya 呼び出し口
def open_yen_stock_sim():
    return YenStockWindow.open_unique()

if __name__ == "__main__":
    open_yen_stock_sim()
