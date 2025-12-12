# -*- coding: utf-8 -*-
import os, json, random, time, getpass
from datetime import datetime
try:
    from PySide6 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide2 import QtWidgets, QtCore, QtGui

NUM_COLORS = {
    1: "#1976d2",
    2: "#388e3c",
    3: "#d32f2f",
    4: "#7b1fa2",
    5: "#6d4c41",
    6: "#00838f",
    7: "#455a64",
    8: "#000000"
}

DEFAULT_RATIO = 0.15
RANK_FILENAME = "JCQ_Minesweeper_ranks.json"


def mines_for(w, h, ratio=DEFAULT_RATIO):
    return max(1, int(round(w * h * ratio)))


def ensure_data_dir():
    primary = r"S:\Public\qiu_yi\JCQ_Tool\data"
    if os.path.isdir(primary):
        try:
            os.makedirs(primary, exist_ok=True)
            test_path = os.path.join(primary, "_w.test")
            with open(test_path, "w", encoding="utf-8") as f:
                f.write("ok")
            os.remove(test_path)
            return primary
        except Exception:
            pass

    home = os.path.expanduser("~")
    doc = os.path.join(home, "Documents")
    fallback = os.path.join(doc, "JCQ_Minesweeper")
    os.makedirs(fallback, exist_ok=True)
    return fallback


def rank_path():
    d = ensure_data_dir()
    p = os.path.join(d, RANK_FILENAME)
    if not os.path.exists(p):
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"easy": [], "normal": [], "hard": []}, f, indent=2)
    return p


def load_ranks():
    p = rank_path()
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {"easy": [], "normal": [], "hard": []}
    for k in ("easy", "normal", "hard"):
        data.setdefault(k, [])
        data[k] = sorted(data[k], key=lambda x: x.get("time", 9e9))[:100]
    return data


def save_rank_entry(diff_key, name, tsec):
    p = rank_path()
    data = load_ranks()
    data.setdefault(diff_key, []).append(
        {
            "name": name,
            "time": float(tsec),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    data[diff_key] = sorted(data[diff_key], key=lambda x: x["time"])[:100]
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


class DifficultyDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Difficulty")
        self.setModal(True)

        self.sel = QtWidgets.QButtonGroup(self)

        r_easy = QtWidgets.QRadioButton("Easy  5 × 5")
        r_norm = QtWidgets.QRadioButton("Normal 10 × 10")
        r_norm.setChecked(True)
        r_hard = QtWidgets.QRadioButton("Hard  20 × 20")

        self.sel.addButton(r_easy, 0)
        self.sel.addButton(r_norm, 1)
        self.sel.addButton(r_hard, 2)

        okb = QtWidgets.QPushButton("OK")
        okb.clicked.connect(self.accept)
        cb = QtWidgets.QPushButton("Cancel")
        cb.clicked.connect(self.reject)

        lay = QtWidgets.QVBoxLayout(self)
        for w in (r_easy, r_norm, r_hard):
            lay.addWidget(w)
        hl = QtWidgets.QHBoxLayout()
        hl.addStretch(1)
        hl.addWidget(cb)
        hl.addWidget(okb)
        lay.addLayout(hl)

    def get_result(self):
        i = self.sel.checkedId()
        if i == 0:
            return (5, 5, mines_for(5, 5), "easy")
        if i == 2:
            return (20, 20, mines_for(20, 20), "hard")
        return (10, 10, mines_for(10, 10), "normal")


class NameSaveDialog(QtWidgets.QDialog):
    def __init__(self, time_sec, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Success")
        self.setModal(True)

        v = QtWidgets.QVBoxLayout(self)
        v.addWidget(
            QtWidgets.QLabel(
                f"Success! Time: {time_sec:.2f}s\nDo you want to save your score?"
            )
        )
        form = QtWidgets.QFormLayout()
        self.edit = QtWidgets.QLineEdit(getpass.getuser() or "Player")
        form.addRow("Name:", self.edit)
        v.addLayout(form)
        btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Yes | QtWidgets.QDialogButtonBox.No
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        v.addWidget(btns)

    def get_name_if_accept(self):
        return (
            self.result() == QtWidgets.QDialog.Accepted,
            self.edit.text().strip() or "Player",
        )


class LeaderboardDialog(QtWidgets.QDialog):
    def __init__(self, default_key="normal", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Leaderboard")
        self.resize(520, 440)

        h = QtWidgets.QHBoxLayout(self)

        left = QtWidgets.QVBoxLayout()
        left.addWidget(QtWidgets.QLabel("Difficulties"))
        self.list = QtWidgets.QListWidget()
        self.list.addItems(["easy", "normal", "hard"])
        self.list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.list.currentTextChanged.connect(self.refresh)
        left.addWidget(self.list, 1)
        h.addLayout(left, 1)

        right = QtWidgets.QVBoxLayout()
        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Rank", "Name", "Time (s)"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        right.addWidget(self.table, 1)
        h.addLayout(right, 3)

        items = self.list.findItems(default_key, QtCore.Qt.MatchExactly)
        self.list.setCurrentItem(items[0] if items else self.list.item(1))
        self.refresh()

    def refresh(self):
        data = load_ranks()
        key = self.list.currentItem().text() if self.list.currentItem() else "normal"
        rows = data.get(key, [])
        self.table.setRowCount(len(rows))
        for i, rec in enumerate(rows):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(i + 1)))
            self.table.setItem(
                i, 1, QtWidgets.QTableWidgetItem(rec.get("name", ""))
            )
            self.table.setItem(
                i,
                2,
                QtWidgets.QTableWidgetItem(f'{rec.get("time", 0.0):.2f}'),
            )
        self.table.resizeColumnsToContents()


class CellButton(QtWidgets.QPushButton):
    leftClicked = QtCore.Signal(int, int)
    rightClicked = QtCore.Signal(int, int)

    def __init__(self, r, c, parent=None):
        super().__init__(parent)
        self.r, self.c = r, c
        self.is_mine = False
        self.is_open = False
        self.is_flag = False
        self.adj = 0
        self.setFixedSize(30, 30)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setStyleSheet(
            "font-weight:bold; border:1px solid #bdbdbd; padding:0; margin:0;"
        )

    def mousePressEvent(self, e):
        if e.button() == QtCore.Qt.RightButton:
            self.rightClicked.emit(self.r, self.c)
            return
        if e.button() == QtCore.Qt.LeftButton:
            self.leftClicked.emit(self.r, self.c)
            return
        super().mousePressEvent(e)

    def paintEvent(self, e):
        opt = QtWidgets.QStyleOptionButton()
        self.initStyleOption(opt)
        if self.is_open:
            opt.state &= ~QtWidgets.QStyle.State_Raised
            opt.state |= QtWidgets.QStyle.State_Sunken
        QtWidgets.QPushButton.paintEvent(self, e)


class Minesweeper(QtWidgets.QWidget):
    def __init__(self):
        super().__init__(None)
        self.setWindowTitle("JCQ_Minesweeper")

        dlg = DifficultyDialog(self)
        if dlg.exec_() != QtWidgets.QDialog.Accepted:
            self.W, self.H, self.M, self.diff_key = (
                10,
                10,
                mines_for(10, 10),
                "normal",
            )
        else:
            self.W, self.H, self.M, self.diff_key = dlg.get_result()

        self.grid = []
        self.alive = True
        self.cells_to_open = 0
        self.start_time = None

        self.elapsed_timer = QtCore.QTimer(self)
        self.elapsed_timer.setInterval(100)
        self.elapsed_timer.timeout.connect(self.update_status)

        top_main = QtWidgets.QVBoxLayout()

        self.status_lbl = QtWidgets.QLabel("")
        self.status_lbl.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByMouse
        )
        self.status_lbl.setAlignment(QtCore.Qt.AlignLeft)
        self.status_lbl.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        top_main.addWidget(self.status_lbl, alignment=QtCore.Qt.AlignLeft)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.setSpacing(4)

        self.btn_board = QtWidgets.QPushButton("Leaderboard")
        self.btn_board.clicked.connect(self.show_leaderboard)
        self.btn_change = QtWidgets.QPushButton("Change…")
        self.btn_change.clicked.connect(self.change_difficulty)
        self.btn_reset = QtWidgets.QPushButton("Reset")
        self.btn_reset.clicked.connect(self.reset)

        for b in (self.btn_board, self.btn_change, self.btn_reset):
            b.setFixedHeight(24)
            btn_row.addWidget(b)

        btn_row.addStretch(1)
        top_main.addLayout(btn_row)

        self.field = QtWidgets.QWidget()
        self.field_layout = QtWidgets.QGridLayout(self.field)
        self.field_layout.setSpacing(0)
        self.field_layout.setContentsMargins(0, 0, 0, 0)

        center_h = QtWidgets.QHBoxLayout()
        center_h.addStretch(1)
        center_h.addWidget(self.field, 0, QtCore.Qt.AlignCenter)
        center_h.addStretch(1)

        center_v = QtWidgets.QVBoxLayout()
        center_v.addStretch(1)
        center_v.addLayout(center_h)
        center_v.addStretch(1)

        main = QtWidgets.QVBoxLayout(self)
        main.setSpacing(6)
        main.addLayout(top_main)
        main.addLayout(center_v, 1)

        self.build_board(self.W, self.H)
        self.reset()
        self.show()

    def build_board(self, W, H):
        for i in reversed(range(self.field_layout.count())):
            w = self.field_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        self.grid = []

        for r in range(H):
            row = []
            for c in range(W):
                b = CellButton(r, c)
                b.leftClicked.connect(self.on_left)
                b.rightClicked.connect(self.on_right)
                self.field_layout.addWidget(b, r, c)
                row.append(b)
            self.grid.append(row)

        cell_w = self.grid[0][0].width() if self.grid and self.grid[0] else 30
        cell_h = self.grid[0][0].height() if self.grid and self.grid[0] else 30
        self.field.setMinimumSize(cell_w * W, cell_h * H)
        self.field.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )

    def change_difficulty(self):
        dlg = DifficultyDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.W, self.H, self.M, self.diff_key = dlg.get_result()
            self.build_board(self.W, self.H)
            self.reset()

    def reset(self):
        self.alive = True

        for r in range(self.H):
            for c in range(self.W):
                b = self.grid[r][c]
                b.is_mine = False
                b.is_open = False
                b.is_flag = False
                b.adj = 0
                b.setEnabled(True)
                b.setText("")
                b.setStyleSheet(
                    "font-weight:bold; border:1px solid #bdbdbd; padding:0; margin:0;"
                )

        all_idx = [(r, c) for r in range(self.H) for c in range(self.W)]
        for (r, c) in random.sample(all_idx, self.M):
            self.grid[r][c].is_mine = True

        for r in range(self.H):
            for c in range(self.W):
                if self.grid[r][c].is_mine:
                    continue
                cnt = 0
                for nr, nc in self.neighbors(r, c):
                    if self.grid[nr][nc].is_mine:
                        cnt += 1
                self.grid[r][c].adj = cnt

        self.cells_to_open = self.W * self.H - self.M
        self.start_time = time.time()
        self.elapsed_timer.start()
        self.update_status()

    def neighbors(self, r, c):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.H and 0 <= nc < self.W:
                    yield nr, nc

    def on_left(self, r, c):
        if not self.alive:
            return
        cell = self.grid[r][c]
        if cell.is_open or cell.is_flag:
            return
        if cell.is_mine:
            self.reveal_mines(exploded=(r, c))
            self.game_over(False)
            return
        self.open_cell(r, c)
        if self.cells_to_open == 0:
            self.game_over(True)

    def on_right(self, r, c):
        if not self.alive:
            return
        cell = self.grid[r][c]
        if cell.is_open:
            return
        cell.is_flag = not cell.is_flag
        cell.setText("⚑" if cell.is_flag else "")
        if cell.is_flag:
            cell.setStyleSheet(
                "font-weight:bold; border:1px solid #bdbdbd; padding:0; margin:0; color:#f57c00;"
            )
        else:
            cell.setStyleSheet(
                "font-weight:bold; border:1px solid #bdbdbd; padding:0; margin:0;"
            )
        self.update_status()

    def open_cell(self, r, c):
        stack = [(r, c)]
        visited = set()
        while stack:
            rr, cc = stack.pop()
            if (rr, cc) in visited:
                continue
            visited.add((rr, cc))
            cell = self.grid[rr][cc]
            if cell.is_open or cell.is_flag or cell.is_mine:
                continue
            cell.is_open = True
            cell.setEnabled(False)
            self.cells_to_open -= 1
            if cell.adj == 0:
                cell.setText("")
                cell.setStyleSheet(
                    "background:#e0e0e0; font-weight:bold; border:1px solid #bdbdbd; padding:0; margin:0;"
                )
                for nr, nc in self.neighbors(rr, cc):
                    if (nr, nc) not in visited:
                        stack.append((nr, nc))
            else:
                cell.setText(str(cell.adj))
                color = NUM_COLORS.get(cell.adj, "#000")
                cell.setStyleSheet(
                    "background:#f5f5f5; font-weight:bold; color:%s; border:1px solid #bdbdbd; padding:0; margin:0;"
                    % color
                )
        self.update_status()

    def reveal_mines(self, exploded=None):
        for r in range(self.H):
            for c in range(self.W):
                cell = self.grid[r][c]
                if cell.is_mine:
                    cell.setText("✹")
                    if exploded and (r, c) == exploded:
                        cell.setStyleSheet(
                            "background:#ff5252; color:#000; font-weight:bold; border:1px solid #bdbdbd; padding:0; margin:0;"
                        )
                    else:
                        cell.setStyleSheet(
                            "background:#ef9a9a; color:#000; font-weight:bold; border:1px solid #bdbdbd; padding:0; margin:0;"
                        )
                cell.setEnabled(False)

    def game_over(self, win):
        self.alive = False
        self.elapsed_timer.stop()
        if win:
            elapsed = self.current_elapsed()
            dlg = NameSaveDialog(elapsed, self)
            dlg.exec_()
            accepted, name = dlg.get_name_if_accept()
            if accepted:
                try:
                    save_rank_entry(self.diff_key, name, elapsed)
                except Exception:
                    pass
            self.setWindowTitle("JCQ_Minesweeper — You win! ✅")
        else:
            self.setWindowTitle("JCQ_Minesweeper — You lose ☠")

        for r in range(self.H):
            for c in range(self.W):
                self.grid[r][c].setEnabled(False)
        self.update_status()

    def current_elapsed(self):
        if self.start_time is None:
            return 0.0
        return max(0.0, time.time() - self.start_time)

    def mines_left_est(self):
        flags = sum(
            1
            for r in range(self.H)
            for c in range(self.W)
            if self.grid[r][c].is_flag
        )
        return max(self.M - flags, 0)

    def opened_count(self):
        return (self.W * self.H - self.M) - self.cells_to_open

    def update_status(self):
        t = self.current_elapsed()
        txt = (
            f"Diff:{self.diff_key} | Size:{self.W}×{self.H} | "
            f"MinesLeft:{self.mines_left_est()} | "
            f"Opened:{self.opened_count()}/{self.W * self.H - self.M} | "
            f"Time:{t:.2f}s"
        )
        self.status_lbl.setText(txt)
        self.status_lbl.setToolTip(txt)

    def show_leaderboard(self, default_key=None):
        dlg = LeaderboardDialog(default_key or self.diff_key, self)
        dlg.exec_()


window = Minesweeper()
