# -*- coding: utf-8 -*-
import maya.cmds as cmds
import os, re

import json
# ===== PySide =====
from maya import OpenMayaUI as omui
try:
    from PySide2 import QtWidgets, QtCore
except Exception:
    from PySide6 import QtWidgets, QtCore

# --------------------------------------
# 迷你工具窗口
# --------------------------------------
class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MyWindow, self).__init__(None)
        self.setObjectName("mini_tools_win")
        self.setWindowTitle("mini tools")

        # 按钮
        btn1  = QtWidgets.QPushButton("con offset creater tool")
        btn2  = QtWidgets.QPushButton("delete unknown plugin")
        btn3  = QtWidgets.QPushButton("delete all bindposes")
        btn4  = QtWidgets.QPushButton("save bindpose selection")
        btn5  = QtWidgets.QPushButton(" joint weight i/0")
        btn6  = QtWidgets.QPushButton("cam poly mask")
        btn7  = QtWidgets.QPushButton("file sequence tool")
        btn8  = QtWidgets.QPushButton("")
        btn9  = QtWidgets.QPushButton("")
        btn10 = QtWidgets.QPushButton("")

        # 绑定
        btn1.clicked.connect(self.offset_creater_tool)
        btn2.clicked.connect(self.delete_unknown_plugin)
        btn3.clicked.connect(self.delete_all_bindposes)
        btn4.clicked.connect(self.save_bindpose_selection)
        btn5.clicked.connect(self.build_joint_weight_io_tool)
        btn6.clicked.connect(self.cam_poly_mask)
        btn7.clicked.connect(self.file_sequence_tool)
        btn8.clicked.connect(self.button_clicked)
        btn9.clicked.connect(self.button_clicked)
        btn10.clicked.connect(self.button_clicked)

        # 布局
        g = QtWidgets.QGridLayout(self)
        g.addWidget(btn1,  0, 0); g.addWidget(btn2,  0, 1)
        g.addWidget(btn3,  1, 0); g.addWidget(btn4,  1, 1)
        g.addWidget(btn5,  2, 0); g.addWidget(btn6,  2, 1)
        g.addWidget(btn7,  3, 0); g.addWidget(btn8,  3, 1)
        g.addWidget(btn9,  4, 0); g.addWidget(btn10, 4, 1)

        self.resize(400, 300)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def button_clicked(self):
        btn = self.sender()
        print(u"[mini tools] 点击：{}".format(btn.text() if btn else ""))

    def offset_creater_tool(self):
        # 防重复
        for w in QtWidgets.QApplication.topLevelWidgets():
            if w.objectName() == "offset_creater_win":
                w.close()

        class Win(QtWidgets.QWidget):
            def __init__(self):
                super(Win, self).__init__(None)
                self.setObjectName("offset_creater_win")
                self.setWindowTitle("offset creater")
                self.setMinimumWidth(420)

                self.suffix_offset = QtWidgets.QLineEdit("_offset")
                self.suffix_ctrl   = QtWidgets.QLineEdit("_Con")

                self.btn_only_offset = QtWidgets.QPushButton("Create Offset Only")
                self.btn_ctrl_stack  = QtWidgets.QPushButton("Create Offset + Controller (Constrain TRS)")

                form = QtWidgets.QFormLayout()
                form.addRow(u"Offset suffix：", self.suffix_offset)
                form.addRow(u"Controller suffix：", self.suffix_ctrl)

                lay = QtWidgets.QVBoxLayout(self)
                lay.addLayout(form)
                lay.addWidget(self.btn_only_offset)
                lay.addWidget(self.btn_ctrl_stack)

                self.btn_only_offset.clicked.connect(self._create_offset_only)
                self.btn_ctrl_stack.clicked.connect(self._create_offset_and_controller_constrain)

            # ---------- helpers ----------
            def _as_transform(self, n):
                if cmds.objectType(n, isAType='transform'):
                    return n
                p = cmds.listRelatives(n, p=True, f=True) or []
                return p[0] if p and cmds.objectType(p[0], isAType='transform') else None

            def _unique_name(self, base):
                name, i = base, 1
                while cmds.objExists(name):
                    i += 1
                    name = "{}_{}".format(base, i)
                return name

            def _short_no_ns(self, long_name):
                return long_name.split('|')[-1].split(':')[-1]

            def _selected_transforms(self):
                sel = cmds.ls(sl=True, long=True) or []
                trans = []
                for s in sel:
                    t = self._as_transform(s)
                    if t:
                        trans.append(t)
                # 深层优先，便于后面父子处理
                return sorted(set(trans), key=lambda x: x.count('|'), reverse=True)

            def _uuid(self, node):
                return (cmds.ls(node, uuid=True) or [None])[0]

            def _from_uuid(self, uid):
                if not uid:
                    return None
                n = cmds.ls(uid, l=True) or []
                return n[0] if n else None

            def _world_matrix(self, node):
                return cmds.xform(node, q=True, m=True, ws=True)

            def _set_world_matrix(self, node_or_uuid, mat):
                n = node_or_uuid if ('|' in str(node_or_uuid) or ':' in str(node_or_uuid)) else self._from_uuid(node_or_uuid)
                if n and cmds.objExists(n):
                    cmds.xform(n, m=mat, ws=True)

            def _parent_keep_ws(self, child, new_parent):
                wm = self._world_matrix(child)
                cmds.parent(child, new_parent)
                self._set_world_matrix(child, wm)

            # ---------- 按钮1 ----------
            def _create_offset_only(self):
                suffix = self.suffix_offset.text().strip() or "_offset"
                trans = self._selected_transforms()
                if not trans:
                    cmds.warning("[offset creater] 请选择至少一个 transform/joint/shape")
                    return

                created = []
                for t in trans:
                    if not cmds.objExists(t):
                        continue
                    t_uid = self._uuid(t)
                    t_now = self._from_uuid(t_uid)
                    if not t_now:
                        continue

                    obj_wm = self._world_matrix(t_now)
                    parent = (cmds.listRelatives(t_now, p=True, f=True) or [None])[0]

                    off = cmds.createNode("transform", name=self._unique_name(self._short_no_ns(t_now) + suffix))
                    self._set_world_matrix(off, obj_wm)
                    if parent:
                        self._parent_keep_ws(off, parent)

                    t_now = self._from_uuid(t_uid)
                    if not t_now:
                        continue
                    self._parent_keep_ws(t_now, off)
                    created.append(off)

                if created:
                    cmds.select(created, r=True)
                    print("[offset creater] Offset 组创建数: {}".format(len(created)))

            # ---------- 按钮2：保持 TRS 约束 + 层级联动 ----------
            def _create_offset_and_controller_constrain(self):
                off_suffix = self.suffix_offset.text().strip() or "_offset"
                con_suffix = self.suffix_ctrl.text().strip() or "_Con"
                trans = self._selected_transforms()
                if not trans:
                    cmds.warning("[offset creater] 请选择至少一个 transform/joint/shape")
                    return

                # 第1遍：创建 offset / ctrl 并暂回原父
                items = {}
                for t in trans:
                    if not cmds.objExists(t):
                        continue
                    obj_uid = self._uuid(t)
                    obj_now = self._from_uuid(obj_uid)
                    if not obj_now:
                        continue

                    obj_wm  = self._world_matrix(obj_now)
                    par_now = (cmds.listRelatives(obj_now, p=True, f=True) or [None])[0]
                    par_uid = self._uuid(par_now) if par_now else None
                    short   = self._short_no_ns(obj_now)

                    off = cmds.createNode("transform", name=self._unique_name(short + off_suffix))
                    self._set_world_matrix(off, obj_wm)
                    if par_now:
                        self._parent_keep_ws(off, par_now)

                    ctrl = cmds.circle(name=self._unique_name(short + con_suffix), ch=False, nr=(0, 1, 0), r=1.0)[0]
                    cmds.delete(ctrl, ch=True)
                    self._set_world_matrix(ctrl, obj_wm)
                    self._parent_keep_ws(ctrl, off)

                    items[obj_uid] = {
                        'parent_uid': par_uid,
                        'offset': off,
                        'ctrl': ctrl,
                        'wm': obj_wm,
                    }

                # 第2遍：父子联动（子.offset 归到 父.ctrl）
                for uid, info in items.items():
                    par_uid = info['parent_uid']
                    if par_uid and par_uid in items:
                        self._parent_keep_ws(info['offset'], items[par_uid]['ctrl'])

                # 第3遍：TRS 约束（对象不放进 ctrl）
                created_ctrls = []
                for t in trans:
                    uid   = self._uuid(t)
                    t_now = self._from_uuid(uid)
                    if not t_now:
                        continue
                    ctrl  = items[uid]['ctrl']
                    short = self._short_no_ns(t_now)

                    if cmds.nodeType(t_now) == 'joint':
                        cmds.pointConstraint (ctrl, t_now, mo=False, n=self._unique_name(short + "_ptConst"))
                        cmds.orientConstraint(ctrl, t_now, mo=False, n=self._unique_name(short + "_orConst"))
                        try:
                            cmds.scaleConstraint (ctrl, t_now, mo=False, n=self._unique_name(short + "_scConst"))
                        except Exception:
                            pass
                    else:
                        cmds.parentConstraint(ctrl, t_now, mo=False, n=self._unique_name(short + "_prConst"))
                        try:
                            cmds.scaleConstraint (ctrl, t_now, mo=False, n=self._unique_name(short + "_scConst"))
                        except Exception:
                            pass

                    created_ctrls.append(ctrl)

                if created_ctrls:
                    cmds.select(created_ctrls, r=True)
                    print("[offset creater] 已创建 Offset+Controller(约束 TRS) 数: {}".format(len(created_ctrls)))

        # 弹窗
        self._offset_creater_win = Win()
        self._offset_creater_win.show()

    def delete_unknown_plugin(self):
        # 删除 unknown 类型的节点
        unknown_nodes = cmds.ls(type="unknown") or []
        if unknown_nodes:
            cmds.delete(unknown_nodes)

        # 删除 unknown 插件
        plugins_list = cmds.unknownPlugin(q=True, l=True)
        if plugins_list:
            for plugin in plugins_list:
                print(u"無効なプラグイン発見、削除します…: {0}".format(plugin))
                cmds.unknownPlugin(plugin, r=True)

    def delete_all_bindposes(self):
        nodes = cmds.ls(type="dagPose") or []
        if not nodes:
            cmds.warning("[BindPose Tool] 场景中没有 bindPose 节点")
            return
        cmds.delete(nodes)
        print("[BindPose Tool] 已删除 {} 个 bindPose 节点".format(len(nodes)))

    def save_bindpose_selection(self):
        sel = cmds.ls(sl=True) or []
        if not sel:
            cmds.warning("[BindPose Tool] 请先选择对象")
            return
        try:
            cmds.dagPose(sel, bindPose=True, save=True)
            print("[BindPose Tool] 已保存 BindPose for: {}".format(sel))
        except Exception as e:
            cmds.warning("[BindPose Tool] 失败: {}".format(e))

        def build_joint_weight_io_tool():
            """两按钮：导出/导入所选joint的权重（导出前先选路径；导入含歧义选择与缺失影响处理）"""

            # ===== 基础工具 =====
            def _short_no_ns(n):
                s = n.split('|')[-1]; return s.split(':')[-1]

            def _strip_ns_vtx_key(obj, idx):
                return f'{_short_no_ns(obj)}.vtx[{idx}]'

            def _choose_path(save=True):
                dlg = cmds.fileDialog2(fileFilter='JSON (*.json)', dialogStyle=2,
                                       fileMode=0 if save else 1)
                return dlg[0] if dlg else None

            # --- 选择器（用于同名短名多候选时让用户挑一个） ---
            def _pick_from_list(title, items):
                """返回用户选择的字符串；取消返回None"""
                if not items: return None
                sel_holder = {"value": None}

                def _ui():
                    form = cmds.setParent(q=True)
                    cmds.formLayout(form, e=True, width=480, height=300)
                    txt = cmds.text(l=title, align='left')
                    lst = cmds.textScrollList(numberOfRows=12, allowMultiSelection=False, append=items)
                    okb = cmds.button(l=u'确定', c=lambda *_: _store_and_dismiss())
                    cab = cmds.button(l=u'取消', c=lambda *_: cmds.layoutDialog(dismiss='cancel'))

                    def _store_and_dismiss():
                        ss = cmds.textScrollList(lst, q=True, si=True) or []
                        if ss:
                            sel_holder["value"] = ss[0]
                            cmds.layoutDialog(dismiss='ok')
                        else:
                            cmds.layoutDialog(dismiss='cancel')

                    cmds.formLayout(form, e=True,
                        attachForm=[(txt,'top',8),(txt,'left',8),
                                    (lst,'left',8),(lst,'right',8),
                                    (okb,'left',8),(cab,'right',8),
                                    (okb,'bottom',8),(cab,'bottom',8)],
                        attachControl=[(lst,'top',8,txt),(lst,'bottom',8,okb)],
                        attachPosition=[(okb,'right',2,50),(cab,'left',2,50)])
                res = cmds.layoutDialog(ui=_ui)
                return sel_holder["value"] if res == 'ok' else None

            def _resolve_unique_by_short(type_name, short_name):
                """在全场景按短名找唯一节点；多于1个则弹窗让用户选；返回全名或None"""
                cands = [n for n in (cmds.ls(type=type_name) or []) if _short_no_ns(n) == short_name]
                if not cands: return None
                if len(cands) == 1: return cands[0]
                pick = _pick_from_list(u'存在多个同名%s：请选择' % type_name, cands)
                return pick

            def _resolve_from_list_by_short(cands, short_name, title):
                """在给定候选列表里按短名筛选；多于1个弹窗选择"""
                hits = [n for n in cands if _short_no_ns(n) == short_name]
                if not hits: return None
                if len(hits) == 1: return hits[0]
                pick = _pick_from_list(title, hits)
                return pick

            # ===== 导出（先选路径，取消即中止） =====
            def _export_selected_joints_weights(*_):
                path = _choose_path(save=True)
                if not path:
                    print(u'[取消] 未选择保存路径'); return

                sel = cmds.ls(sl=True, type='joint') or []
                if not sel:
                    cmds.warning('请选择一个或多个 joint'); return

                data = {"items": []}
                for j in sel:
                    j_short = _short_no_ns(j)
                    skcs = cmds.listConnections(j, s=False, d=True, type='skinCluster') or []
                    if not skcs:
                        skcs = cmds.listConnections(j, s=True, d=True, type='skinCluster') or []

                    for skc in skcs:
                        infs = cmds.skinCluster(skc, q=True, inf=True) or []
                        inf_match = None
                        for inf in infs:
                            if _short_no_ns(inf) == j_short:
                                inf_match = inf; break
                        if not inf_match:
                            continue

                        geos = cmds.skinCluster(skc, q=True, geometry=True) or []
                        for geo in geos:
                            vtx_count = cmds.polyEvaluate(geo, v=True)
                            weight_dict = {}
                            for i in range(vtx_count):
                                vtx = f'{geo}.vtx[{i}]'
                                w = cmds.skinPercent(skc, vtx, q=True, t=inf_match)
                                if w and w > 0.0:
                                    weight_dict[_strip_ns_vtx_key(geo, i)] = float('%.6f' % w)
                            if weight_dict:
                                data["items"].append({
                                    "joint": _short_no_ns(j),
                                    "skinCluster": _short_no_ns(skc),
                                    "geo": _short_no_ns(geo),
                                    "weights": weight_dict
                                })

                if not data["items"]:
                    cmds.warning('未采集到任何权重，未写入文件'); return

                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print(u'[OK] 导出完成: %s  条目: %d' % (path, len(data["items"])))
                except Exception as e:
                    cmds.warning('写入失败: %s' % e)

            # ===== 导入（同名选择 & 缺失影响可添加） =====
            def _apply_weights_from_json(*_):
                path = _choose_path(save=False)
                if not path:
                    print(u'[取消] 未选择JSON'); return
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except Exception as e:
                    cmds.warning('读取JSON失败: %s' % e); return

                items = data.get("items", [])
                if not items:
                    cmds.warning('JSON无items'); return

                total_applied = 0
                for it in items:
                    j_short   = it.get("joint")
                    skc_short = it.get("skinCluster")
                    geo_short = it.get("geo")
                    wdict     = it.get("weights", {})

                    # 解析 skinCluster（全场景）
                    skc = _resolve_unique_by_short('skinCluster', skc_short)
                    if not skc:
                        print(u'[跳过] 找不到 skinCluster: %s' % skc_short); continue

                    # 解析 绑定几何（仅在该skinCluster几何里挑）
                    geos = cmds.skinCluster(skc, q=True, geometry=True) or []
                    geo = _resolve_from_list_by_short(geos, geo_short, u'存在多个同名几何：请选择')
                    if not geo:
                        print(u'[跳过] %s 未绑定几何 %s' % (skc_short, geo_short)); continue

                    # 解析 joint（全场景）
                    joint_node = _resolve_unique_by_short('joint', j_short)
                    if not joint_node:
                        print(u'[跳过] 找不到 joint: %s' % j_short); continue

                    # 确保 joint 在 skinCluster 影响中；不在则询问并可添加
                    infs = cmds.skinCluster(skc, q=True, inf=True) or []
                    inf_match = None
                    for inf in infs:
                        if _short_no_ns(inf) == j_short:
                            inf_match = inf; break

                    if not inf_match:
                        ans = cmds.confirmDialog(
                            t=u'添加影响？',
                            m=u'joint "%s" 不在 skinCluster "%s" 的影响中。\n是否将其作为权重初始为0的影响添加？' % (joint_node, skc),
                            b=[u'是', u'否'], db=u'是', cb=u'否', ds=u'否')
                        if ans == u'是':
                            try:
                                # 作为影响添加，初始权重0，不锁权重
                                cmds.skinCluster(skc, e=True, ai=joint_node, lw=False, wt=0.0)
                                inf_match = joint_node
                                print(u'[OK] 已添加影响: %s -> %s' % (joint_node, skc))
                            except Exception as e:
                                print(u'[失败] 添加影响出错: %s' % e)
                                continue
                        else:
                            print(u'[跳过] 未添加影响：%s' % j_short)
                            continue

                    vtx_max = cmds.polyEvaluate(geo, v=True)
                    applied = 0
                    for k, w in wdict.items():
                        try:
                            obj, rest = k.split('.vtx[')
                            if obj != geo_short:  # 键是无NS短名
                                continue
                            idx = int(rest[:-1])
                            if not (0 <= idx < vtx_max):
                                continue
                        except:
                            continue

                        vtx_comp = '%s.vtx[%d]' % (geo, idx)
                        cmds.skinPercent(skc, vtx_comp,
                                         transformValue=[(inf_match, float(w))],
                                         normalize=True)
                        applied += 1

                    total_applied += applied
                    print(u'[OK] 应用: skc=%s geo=%s joint=%s 顶点=%d'
                          % (_short_no_ns(skc), geo_short, j_short, applied))

                print(u'[DONE] 总计应用顶点: %d' % total_applied)

            # ===== UI =====
            win = 'JointWeightIOWin'
            if cmds.window(win, exists=True):
                cmds.deleteUI(win)
            cmds.window(win, t=u'Joint Weights I/O (NS安全+歧义选择+缺失影响添加)', mnb=False, mxb=False)
            cmds.columnLayout(adj=True, rs=6)
            cmds.button(l=u'导出所选Joint权重 → JSON（先选路径，取消中止）', h=36, c=_export_selected_joints_weights)
            cmds.button(l=u'从JSON应用权重（同名可选；缺失影响可添加）',             h=36, c=_apply_weights_from_json)
            cmds.separator(h=6, st='none')
            cmds.text(l=u'导入时：\n- 同名节点会弹窗让你选。\n- 若joint不在skinCluster影响中，可选择添加为0权重后再应用。', al='left')
            cmds.showWindow(win)
            return win

    def build_joint_weight_io_tool(self):
        """导出/导入关节权重；可选择是否保留命名空间"""

        # ===== 基础工具 =====
        def _short_no_ns(n):
            s = n.split('|')[-1];
            return s.split(':')[-1]

        def _strip_ns_vtx_key(obj, idx):
            return f'{_short_no_ns(obj)}.vtx[{idx}]'

        def _choose_path(save=True):
            dlg = cmds.fileDialog2(fileFilter='JSON (*.json)', dialogStyle=2,
                                   fileMode=0 if save else 1)
            return dlg[0] if dlg else None

        def _dlg_info(msg, title=u'完成'):
            cmds.confirmDialog(t=title, m=msg, b=[u'确定'])

        def _dlg_warn(msg, title=u'提示'):
            cmds.confirmDialog(t=title, m=msg, b=[u'确定'])

        def _pick_from_list(title, items):
            if not items: return None
            holder = {"val": None}

            def _ui():
                form = cmds.setParent(q=True)
                cmds.formLayout(form, e=True, width=520, height=320)
                txt = cmds.text(l=title, align='left')
                lst = cmds.textScrollList(numberOfRows=12, allowMultiSelection=False, append=items)

                def _ok(*_):
                    sel = cmds.textScrollList(lst, q=True, si=True) or []
                    if sel: holder["val"] = sel[0]; cmds.layoutDialog(dismiss='ok')

                def _cancel(*_): cmds.layoutDialog(dismiss='cancel')

                okb = cmds.button(l=u'确定', c=_ok)
                cab = cmds.button(l=u'取消', c=_cancel)
                cmds.formLayout(form, e=True,
                                attachForm=[(txt, 'top', 8), (txt, 'left', 8),
                                            (lst, 'left', 8), (lst, 'right', 8),
                                            (okb, 'left', 8), (cab, 'right', 8),
                                            (okb, 'bottom', 8), (cab, 'bottom', 8)],
                                attachControl=[(lst, 'top', 8, txt), (lst, 'bottom', 8, okb)],
                                attachPosition=[(okb, 'right', 2, 50), (cab, 'left', 2, 50)])

            res = cmds.layoutDialog(ui=_ui)
            return holder["val"] if res == 'ok' else None

        # --- 缓存 ---
        joint_cache = {}
        skincluster_cache = {}
        geo_cache = {}

        def _resolve_unique_by_short(type_name, short_name):
            if type_name == 'joint' and short_name in joint_cache:
                return joint_cache[short_name]
            if type_name == 'skinCluster' and short_name in skincluster_cache:
                return skincluster_cache[short_name]
            cands = [n for n in (cmds.ls(type=type_name) or []) if _short_no_ns(n) == short_name]
            if not cands: return None
            full = cands[0] if len(cands) == 1 else _pick_from_list(
                u'存在多个同名 %s 节点 "%s"，请选择要使用的一个：' % (type_name, short_name), cands)
            if not full: return None
            if type_name == 'joint':
                joint_cache[short_name] = full
            elif type_name == 'skinCluster':
                skincluster_cache[short_name] = full
            return full

        def _resolve_geo_in_skc(skc_full, geo_short):
            key = (skc_full, geo_short)
            if key in geo_cache: return geo_cache[key]
            geos = cmds.skinCluster(skc_full, q=True, geometry=True) or []
            hits = [g for g in geos if _short_no_ns(g) == geo_short]
            if not hits: return None
            full = hits[0] if len(hits) == 1 else _pick_from_list(
                u'在 skinCluster "%s" 中存在多个同名几何 "%s"，请选择：' % (_short_no_ns(skc_full), geo_short), hits)
            if full: geo_cache[key] = full
            return full

        # ===== 导出（批量 skinPercent 版） =====
        def _export_selected_joints_weights(*_):
            path = _choose_path(save=True)
            if not path:
                _dlg_info(u'已取消导出。', title=u'已取消')
                return

            sel = cmds.ls(sl=True, type='joint') or []
            if not sel:
                _dlg_warn(u'请选择一个或多个 joint 后再导出。', title=u'无选择')
                return

            keep_ns = cmds.checkBox('keepNSChk', q=True, v=True)
            data = {"items": [], "keep_namespace": keep_ns}

            for j in sel:
                j_name = j if keep_ns else _short_no_ns(j)

                # 找 joint 相关的 skinCluster
                skcs = cmds.listConnections(j, s=False, d=True, type='skinCluster') or []
                if not skcs:
                    skcs = cmds.listConnections(j, s=True, d=True, type='skinCluster') or []

                for skc in skcs:
                    # 先匹配这个 joint 在当前 skinCluster 里的实际影响名
                    infs = cmds.skinCluster(skc, q=True, inf=True) or []
                    inf_match = None
                    j_short = _short_no_ns(j)
                    for inf in infs:
                        if keep_ns:
                            if inf == j:
                                inf_match = inf
                                break
                        else:
                            if _short_no_ns(inf) == j_short:
                                inf_match = inf
                                break
                    if not inf_match:
                        continue

                    # 对每个 geo，一次性查询所有顶点的权重
                    geos = cmds.skinCluster(skc, q=True, geometry=True) or []
                    for geo in geos:
                        vtx_count = cmds.polyEvaluate(geo, v=True)
                        if not vtx_count:
                            continue

                        # 批量查询：geo.vtx[0:count-1]
                        comp = f'{geo}.vtx[0:{vtx_count - 1}]'
                        try:
                            # 注意：有的 Maya 版本需要显式写 value=True
                            wt_list = cmds.skinPercent(
                                skc, comp,
                                q=True, t=inf_match, value=True
                            )
                        except TypeError:
                            # 回退：有的版本 q=True,t=xxx 默认返回值列表
                            wt_list = cmds.skinPercent(
                                skc, comp,
                                q=True, t=inf_match
                            )

                        if not wt_list:
                            continue

                        weight_dict = {}
                        geo_short = _short_no_ns(geo)
                        # 遍历列表，只对非零权重记录
                        for i, w in enumerate(wt_list):
                            if not w or w <= 0.0:
                                continue
                            k = f'{geo}.vtx[{i}]' if keep_ns else _strip_ns_vtx_key(geo, i)
                            # 保持原来 6 位小数的输出
                            weight_dict[k] = float('%.6f' % w)

                        if weight_dict:
                            data["items"].append({
                                "joint": j_name,
                                "skinCluster": skc if keep_ns else _short_no_ns(skc),
                                "geo": geo if keep_ns else geo_short,
                                "weights": weight_dict
                            })

            if not data["items"]:
                _dlg_warn(u'未采集到任何权重，未写入文件。', title=u'无数据')
                return

            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                _dlg_info(u'导出成功：\n%s\n条目：%d\n保留命名空间：%s' %
                          (path, len(data["items"]), keep_ns))
            except Exception as e:
                _dlg_warn(u'写入失败：%s' % e, title=u'失败')

        # ===== 导入（去掉逐点 normalize，最后整体 normalize） =====
        def _apply_weights_from_json(*_):
            path = _choose_path(save=False)
            if not path:
                _dlg_info(u'已取消导入。', title=u'已取消')
                return
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                _dlg_warn(u'读取JSON失败：%s' % e, title=u'失败')
                return

            items = data.get("items", [])
            if not items:
                _dlg_warn(u'JSON 内无 items。', title=u'无数据')
                return

            # 记录哪些 (skinCluster, geo) 被改过，最后统一 normalize
            touched_pairs = set()

            total_applied = 0
            for it in items:
                j_short   = _short_no_ns(it.get("joint"))
                skc_short = _short_no_ns(it.get("skinCluster"))
                geo_short = _short_no_ns(it.get("geo"))
                wdict     = it.get("weights", {})

                skc = _resolve_unique_by_short('skinCluster', skc_short)
                if not skc:
                    print(f'[跳过] 找不到 skinCluster: {skc_short}')
                    continue

                geo = _resolve_geo_in_skc(skc, geo_short)
                if not geo:
                    print(f'[跳过] {skc_short} 未绑定几何 {geo_short}')
                    continue

                joint_node = _resolve_unique_by_short('joint', j_short)
                if not joint_node:
                    print(f'[跳过] 找不到 joint: {j_short}')
                    continue

                # 确保 joint 在影响列表里
                infs = cmds.skinCluster(skc, q=True, inf=True) or []
                inf_match = None
                for inf in infs:
                    if _short_no_ns(inf) == j_short:
                        inf_match = inf
                        break

                if not inf_match:
                    ans = cmds.confirmDialog(
                        t=u'添加影响？',
                        m=u'joint "%s" 不在 skinCluster "%s" 的影响中。\n是否添加为0权重？' % (joint_node, _short_no_ns(skc)),
                        b=[u'是', u'否'], db=u'是', cb=u'否', ds=u'否')
                    if ans == u'是':
                        try:
                            cmds.skinCluster(skc, e=True, ai=joint_node, lw=False, wt=0.0)
                            inf_match = joint_node
                            print(f'[OK] 已添加影响: {joint_node} -> {skc}')
                        except Exception as e:
                            print(f'[失败] 添加影响出错: {e}')
                            continue
                    else:
                        continue

                vtx_max = cmds.polyEvaluate(geo, v=True)
                applied = 0

                for k, w in wdict.items():
                    try:
                        obj, rest = k.split('.vtx[')
                        if _short_no_ns(obj) != geo_short:
                            continue
                        idx = int(rest[:-1])
                        if not (0 <= idx < vtx_max):
                            continue
                    except Exception:
                        continue

                    vtx_comp = f'{geo}.vtx[{idx}]'
                    # 关键改动：逐点写时不做 normalize
                    cmds.skinPercent(
                        skc, vtx_comp,
                        transformValue=[(inf_match, float(w))],
                        normalize=False
                    )
                    applied += 1

                if applied:
                    touched_pairs.add((skc, geo))
                total_applied += applied

            # 统一归一化：每个 (skinCluster, geo) 只做一次
            for skc, geo in touched_pairs:
                try:
                    vtx_max = cmds.polyEvaluate(geo, v=True)
                    if vtx_max:
                        comp = f'{geo}.vtx[0:{vtx_max - 1}]'
                        cmds.skinPercent(skc, comp, normalize=True)
                        print(f'[Normalize] {skc} / {geo} -> {vtx_max} verts')
                except Exception as e:
                    print(f'[警告] 归一化失败 {skc}, {geo}: {e}')

            _dlg_info(u'导入完成：\n文件：%s\n应用顶点：%d' % (path, total_applied))

        # ===== UI =====
        win = 'JointWeightIOWin'
        if cmds.window(win, exists=True): cmds.deleteUI(win)
        cmds.window(win, t=u'Joint Weights I/O', mnb=False, mxb=False)
        cmds.columnLayout(adj=True, rs=6)
        cmds.checkBox('keepNSChk', l=u'保留命名空间 (导出时记录完整路径)', v=False)
        cmds.button(l=u'导出所选Joint权重 → JSON', h=36, c=_export_selected_joints_weights)
        cmds.button(l=u'从JSON应用权重（同名缓存选择；缺失影响可添加）', h=36, c=_apply_weights_from_json)
        cmds.separator(h=6, st='none')
        cmds.text(l=u'导出时如勾选“保留命名空间”，会记录完整节点名。\n未勾选则自动截断为短名。', al='left')
        cmds.showWindow(win)
        return win

    def cam_poly_mask(self,name_token="polyImagePlane", focal_mul=-0.0277):
        """Single-call tool. All helpers + main() inside.
        Args:
            name_token (str): naming token used in created nodes, e.g. "polyImagePlane"
            focal_mul (float): multiplier applied to camera focalLength (connect) -> translateZ
        """

        # ---------- helpers ----------
        def undo_chunk(name="PolyMask"):
            class _U:
                def __enter__(self):
                    try:
                        cmds.undoInfo(ock=True, cn=name)
                    except:
                        pass

                def __exit__(self, *_):
                    try:
                        cmds.undoInfo(cck=True)
                    except:
                        pass

            return _U()

        def cameras():
            out = []
            for s in cmds.ls(type="camera") or []:
                p = cmds.listRelatives(s, p=True, f=False) or []
                if p: out.append(p[0])
            return sorted(list(set(out)))

        def build_ui():
            """FormLayout，自适应宽度；返回(menu控件, run回调)"""
            win = "CamPolyMask_UI"
            if cmds.window(win, exists=True): cmds.deleteUI(win)
            cmds.window(win, t="Camera Poly Mask", s=True)

            form = cmds.formLayout(nd=100)
            lab = cmds.text(l="Camera:", al="left")
            menu = cmds.optionMenu()
            sep = cmds.separator(style="none", h=6)
            btnR = cmds.button(l="↻", c=lambda *_: fill_menu(menu))  # 小刷新
            btnC = cmds.button(l="Create Mask", c=lambda *_: main())  # 自动拉伸

            # Attachments (自适应)
            m = 8
            cmds.formLayout(form, e=True,
                            attachForm=[
                                (lab, 'top', m), (lab, 'left', m),
                                (menu, 'top', m), (menu, 'right', m),
                                (sep, 'left', m), (sep, 'right', m),
                                (btnR, 'left', m), (btnC, 'right', m), (btnR, 'bottom', m), (btnC, 'bottom', m)
                            ],
                            attachControl=[
                                (menu, 'left', 6, lab),
                                (sep, 'top', 6, menu),
                                (btnR, 'top', 6, sep),
                                (btnC, 'top', 6, sep),
                            ],
                            attachPosition=[
                                (btnR, 'right', 6, 20),  # 刷新按钮占左侧~20%
                                (btnC, 'left', 6, 22),  # Create 占余下区域
                            ]
                            )

            cmds.showWindow(win)
            return menu

        def fill_menu(menu):
            for mi in cmds.optionMenu(menu, q=True, ill=True) or []:
                cmds.deleteUI(mi)
            items = cameras() or ["(No cameras)"]
            for c in items:
                cmds.menuItem(l=c, p=menu)

        def current_cam(menu):
            v = cmds.optionMenu(menu, q=True, v=True)
            return None if v == "(No cameras)" else v

        # ---------- main ----------
        def main():
            cam = current_cam(menu)
            if not cam:
                cmds.warning("Pick a camera.");
                return
            with undo_chunk():
                # validate
                if not cmds.objExists(cam): cmds.warning("Camera not found."); return
                cam_shape = (cmds.listRelatives(cam, s=True, type="camera") or [None])[0]
                if not cam_shape: cmds.warning("No camera shape."); return

                # names
                base = cam
                gp = f"{base}_{name_token}_GP"  # container only
                off = f"{base}_{name_token}_offset"  # constrained to camera (T+R+S)
                xfm = f"{base}_{name_token}_transfrom"  # aspect (scaleY) + focal (tz) connections
                ply = f"{base}_{name_token}"  # plain mesh; keep clean
                div = f"{base}_{name_token}_hwRatio"  # height/width
                mlin = f"{base}_{name_token}_flenMul"  # multDoubleLinear

                ss = f"{base}_{name_token}_SS"
                sg = f"{base}_{name_token}_SG"

                # cleanup
                for n in (gp, off, xfm, ply, div, mlin, ss, sg):
                    if cmds.objExists(n):
                        try:
                            cmds.delete(n)
                        except:
                            pass

                # hierarchy: GP -> offset -> transfrom -> plane
                gp = cmds.createNode("transform", n=gp)
                off = cmds.createNode("transform", n=off, p=gp)
                xfm = cmds.createNode("transform", n=xfm, p=off)
                ply = cmds.polyPlane(name=ply, sx=1, sy=1, ch=False)[0]
                cmds.parent(ply, xfm)

                # rotate then freeze rotation on the plane
                cmds.setAttr(ply + ".rx", 90)
                cmds.makeIdentity(ply, apply=True, t=False, r=True, s=False, n=False)

                # aspect: connect (height/width) -> xfm.scaleY
                div = cmds.shadingNode("multiplyDivide", au=True, n=div)
                cmds.setAttr(div + ".operation", 2)  # Divide
                try:
                    cmds.connectAttr("defaultResolution.height", div + ".input1X", f=True)
                    cmds.connectAttr("defaultResolution.width", div + ".input2X", f=True)
                except:
                    # fallback: set constant ratio
                    h = cmds.getAttr("defaultResolution.height")
                    w = cmds.getAttr("defaultResolution.width")
                    cmds.setAttr(div + ".input1X", h)
                    cmds.setAttr(div + ".input2X", w)
                cmds.connectAttr(div + ".outputX", xfm + ".scaleY", f=True)

                # focal: live connect focalLength * focal_mul -> xfm.translateZ
                mlin = cmds.shadingNode("multDoubleLinear", au=True, n=mlin)
                cmds.connectAttr(cam_shape + ".focalLength", mlin + ".input1", f=True)
                cmds.setAttr(mlin + ".input2", float(focal_mul))
                cmds.connectAttr(mlin + ".output", xfm + ".tz", f=True)

                # align & constraints ON offset (parent + scale)
                m = cmds.xform(cam, q=True, ws=True, m=True)
                cmds.xform(off, ws=True, m=m)
                cmds.parentConstraint(cam, off, mo=True)
                cmds.scaleConstraint(cam, off, mo=True)

                # shader
                ss = cmds.shadingNode("surfaceShader", asShader=True, n=ss)
                sg = cmds.sets(r=True, nss=True, empty=True, n=sg)
                cmds.connectAttr(ss + ".outColor", sg + ".surfaceShader", f=True)
                cmds.sets(ply, e=True, forceElement=sg)

                # done
                cmds.select(ply)
                try:
                    cmds.inViewMessage(
                        amg=f"<hl>Done:</hl> Mask for <hl>{base}</hl>  (token='{name_token}', mul={focal_mul})",
                        pos="midCenter", fade=True
                    )
                except:
                    pass

        # ---------- setup & exec ----------
        menu = build_ui()
        fill_menu(menu)

        # auto-pick selected camera if any
        sel = cmds.ls(sl=True, type="transform") or []
        for t in sel:
            if cmds.listRelatives(t, s=True, type="camera"):
                cmds.optionMenu(menu, e=True, v=t)
                break

    def file_sequence_tool(self,name_token="imageSeq", tag_attr="JCQImageSeqCtrl", tool_tag="ImageSeqClamper_v2"):
        """Single-call UI tool. English UI. Logs to Script Editor.
        - Lists eligible file nodes (useFrameExtension=1, numeric filename, NOT tagged).
        - Builds controller null (seqMin/seqMax/seqOffset/flipAlpha) with recognizable tags.
        - frameExtension = clamp(time1.outTime + seqOffset, seqMin, seqMax)
        - flipAlpha (0/1) -> (-1/+1) drives file.alphaGain (fallback colorBalance.alphaGain).
        """

        # ---------------- helpers ----------------
        def undo_chunk(name="ImageSeqClamper"):
            class _U:
                def __enter__(self):
                    try: cmds.undoInfo(ock=True, cn=name)
                    except: pass
                def __exit__(self, *_):
                    try: cmds.undoInfo(cck=True)
                    except: pass
            return _U()

        def _scan_seq_range(tex_path):
            if not tex_path:
                raise RuntimeError("fileTextureName is empty.")
            fname = os.path.basename(tex_path)
            dname = os.path.dirname(tex_path)
            m = re.search(r"^(.*?)(\d+)(\.[^.]+)$", fname)
            if not m:
                raise RuntimeError("Cannot parse frame digits from filename: %s" % fname)
            prefix, digits, suffix = m.groups()
            pad = len(digits)
            if not os.path.isdir(dname):
                raise RuntimeError("Directory does not exist: %s" % dname)
            rgx = re.compile(r"^" + re.escape(prefix) + r"(\d+)" + re.escape(suffix) + r"$")
            frames = []
            for f in os.listdir(dname):
                mm = rgx.match(f)
                if not mm: continue
                s = mm.group(1)
                if len(s) != pad: continue
                try: frames.append(int(s))
                except: pass
            if not frames:
                raise RuntimeError("No matching sequence found: %s[%%0%dd]%s" % (pad, suffix))
            return min(frames), max(frames)

        def _disconnect_all_inputs(attr):
            # expressions
            for e in cmds.ls(type='expression') or []:
                try:
                    s = cmds.getAttr(e + ".expression") or ""
                    if attr in s:
                        cmds.delete(e)
                except: pass
            # anim curves
            conns = cmds.listConnections(attr, s=True, d=False, plugs=True) or []
            for p in conns:
                node = p.split(".", 1)[0]
                t = cmds.nodeType(node)
                if t and (t.startswith("animCurve") or t in ("animCurveUU","animCurveUA","animCurveUL","animCurveTU","animCurveTA","animCurveTL")):
                    try: cmds.delete(node)
                    except: pass
            # other connections
            pair = cmds.listConnections(attr, s=True, d=False, plugs=True, connections=True) or []
            for i in range(0, len(pair), 2):
                src, dst = pair[i], pair[i+1]
                try: cmds.disconnectAttr(src, dst)
                except: pass

        def _ensure_time1():
            if not cmds.objExists("time1"):
                cmds.createNode("time", n="time1")
            return "time1"

        def _add_attr(node, name, at, dv=None, **kw):
            if not cmds.attributeQuery(name, n=node, ex=True):
                cmds.addAttr(node, ln=name, at=at, **kw)
                try: cmds.setAttr("%s.%s"%(node,name), e=True, k=True)
                except: pass
            if dv is not None:
                try: cmds.setAttr("%s.%s"%(node,name), dv)
                except: pass

        def _is_file_tagged(file_node):
            if not cmds.objExists(file_node):
                return False
            if not cmds.attributeQuery(tag_attr, n=file_node, ex=True):
                return False
            conns = cmds.listConnections("%s.%s"%(file_node, tag_attr), s=True, d=False) or []
            return len(conns) > 0

        def _eligible_file_nodes():
            res = []
            for n in cmds.ls(type="file") or []:
                try:
                    if not cmds.getAttr(n + ".useFrameExtension"): continue
                    tex = cmds.getAttr(n + ".fileTextureName")
                    if not tex: continue
                    if not re.search(r"\d+(?=\.[^.]+$)", os.path.basename(tex)): continue
                    if _is_file_tagged(n): continue
                    res.append(n)
                except: pass
            return sorted(res)

        def _lock_trs(x):
            for a in ("t","r","s"):
                for ax in ("x","y","z"):
                    try:
                        cmds.setAttr(f"{x}.{a}{ax}", e=True, k=False, l=True)
                    except: pass

        # ---------------- build logic ----------------
        def build_for_file(file_node):
            if not cmds.objExists(file_node) or cmds.nodeType(file_node) != "file":
                raise RuntimeError("File node not found: %s" % file_node)

            # enable frame extension
            if cmds.attributeQuery("useFrameExtension", n=file_node, ex=True):
                cmds.setAttr(file_node + ".useFrameExtension", 1)

            # seq range
            tex = cmds.getAttr(file_node + ".fileTextureName")
            fmin, fmax = _scan_seq_range(tex)

            # controller & cleanup
            ctrl = f"{file_node}_{name_token}_CTRL"
            for n in (ctrl, f"PMA_{file_node}_frame", f"CLP_{file_node}_frame",
                      f"MD_{file_node}_alpha2x", f"PMA_{file_node}_alphaShift"):
                if cmds.objExists(n):
                    try: cmds.delete(n)
                    except: pass
            ctrl = cmds.createNode("transform", n=ctrl)
            _lock_trs(ctrl)

            # controller attrs
            _add_attr(ctrl, "seqMin", "long", int(fmin))
            _add_attr(ctrl, "seqMax", "long", int(fmax))
            _add_attr(ctrl, "seqOffset", "long", 0)
            _add_attr(ctrl, "flipAlpha", "bool", 1)
            _add_attr(ctrl, "toolTag", "enum", None, en=tool_tag)  # recognizable mark
            _add_attr(ctrl, tag_attr, "message")                   # message tag

            # tag file (message attr)
            if not cmds.attributeQuery(tag_attr, n=file_node, ex=True):
                cmds.addAttr(file_node, ln=tag_attr, at="message")
            try:
                cmds.connectAttr(f"{ctrl}.{tag_attr}", f"{file_node}.{tag_attr}", f=True)
            except: pass

            # clamp network for frameExtension
            target_attr = file_node + ".frameExtension"
            _disconnect_all_inputs(target_attr)
            time1 = _ensure_time1()

            pma = cmds.shadingNode("plusMinusAverage", asUtility=True, n=f"PMA_{file_node}_frame")
            cmds.setAttr(pma + ".operation", 1)  # sum
            cmds.connectAttr(time1 + ".outTime",   pma + ".input1D[0]", f=True)
            cmds.connectAttr(ctrl  + ".seqOffset", pma + ".input1D[1]", f=True)

            clp = cmds.shadingNode("clamp", asUtility=True, n=f"CLP_{file_node}_frame")
            cmds.connectAttr(pma + ".output1D", clp + ".inputR", f=True)
            cmds.connectAttr(ctrl + ".seqMin",  clp + ".minR",   f=True)
            cmds.connectAttr(ctrl + ".seqMax",  clp + ".maxR",   f=True)
            cmds.connectAttr(clp + ".outputR",  target_attr,     f=True)

            # flipAlpha (0/1) -> (-1/+1) -> alphaGain
            target_alpha = (file_node + ".alphaGain"
                            if cmds.attributeQuery("alphaGain", n=file_node, ex=True)
                            else file_node + ".colorBalance.alphaGain")

            if "." in target_alpha:
                attr_short = target_alpha.split(".")[-1]
            else:
                attr_short = target_alpha

            if not cmds.attributeQuery(attr_short, n=file_node, ex=True):
                cmds.warning("Alpha Gain attribute not found on file node (checked alphaGain and colorBalance.alphaGain).")
            else:
                md = cmds.shadingNode("multiplyDivide", asUtility=True, n=f"MD_{file_node}_alpha2x")
                cmds.setAttr(md + ".operation", 1)  # multiply
                cmds.connectAttr(ctrl + ".flipAlpha", md + ".input1X", f=True)
                cmds.setAttr(md + ".input2X", 2)

                pma2 = cmds.shadingNode("plusMinusAverage", asUtility=True, n=f"PMA_{file_node}_alphaShift")
                cmds.setAttr(pma2 + ".operation", 2)  # subtract
                cmds.connectAttr(md + ".outputX",   pma2 + ".input1D[0]", f=True)  # 2*x
                cmds.setAttr(    pma2 + ".input1D[1]", 1)                           # -1
                # result: 2*flipAlpha - 1  => {0->-1, 1->+1}
                cmds.connectAttr(pma2 + ".output1D", target_alpha, f=True)

            # prime value
            cur = int(cmds.currentTime(q=True))
            try:
                cmds.setAttr(target_attr, max(int(fmin), min(int(fmax), cur)))
            except: pass

            print("[OK] Built controller for %s  range=[%d,%d]  tag=%s" % (file_node, fmin, fmax, tool_tag))
            return ctrl

        # ---------------- UI ----------------
        def build_ui():
            win = "ImageSeqClamper_UI"
            if cmds.window(win, exists=True): cmds.deleteUI(win)
            cmds.window(win, t="Image Sequence Clamper", s=True)
            form = cmds.formLayout(nd=100)
            lab  = cmds.text(l="File node:", al="left")
            menu = cmds.optionMenu()
            btnR = cmds.button(l="Refresh", c=lambda *_: fill_menu(menu))
            btnC = cmds.button(l="Create",  c=lambda *_: run_create(menu))
            m = 8
            cmds.formLayout(form, e=True,
                attachForm=[(lab,'top',m),(lab,'left',m),(menu,'top',m),(menu,'right',m),
                            (btnR,'left',m),(btnC,'right',m),(btnR,'bottom',m),(btnC,'bottom',m)],
                attachControl=[(menu,'left',6,lab),(btnR,'top',6,menu),(btnC,'top',6,menu)],
                attachPosition=[(btnR,'right',6,30),(btnC,'left',6,32)]
            )
            cmds.showWindow(win)
            return menu

        def fill_menu(menu):
            for mi in cmds.optionMenu(menu, q=True, ill=True) or []:
                cmds.deleteUI(mi)
            items = _eligible_file_nodes() or ["(No eligible file nodes)"]
            for it in items:
                cmds.menuItem(l=it, p=menu)
            print("[Info] Eligible files:", items)

        def current_file(menu):
            v = cmds.optionMenu(menu, q=True, v=True)
            return None if v == "(No eligible file nodes)" else v

        def run_create(menu):
            node = current_file(menu)
            if not node:
                cmds.warning("Pick a valid file node.")
                return
            with undo_chunk():
                try:
                    build_for_file(node)
                except Exception as e:
                    cmds.warning("Failed: %s" % e)

        # ---------- exec ----------
        menu = build_ui()
        fill_menu(menu)

        # auto-pick selected eligible file
        elig = set(_eligible_file_nodes())
        for s in cmds.ls(sl=True) or []:
            if s in elig:
                try: cmds.optionMenu(menu, e=True, v=s); break
                except: pass

# --------------------------------------
# 单例：避免重复打开
# --------------------------------------
def minitools():
    app = QtWidgets.QApplication.instance()
    for w in app.topLevelWidgets():
        if w.objectName() == "mini_tools_win":
            try:
                w.close()
            except Exception:
                pass
    return MyWindow()

# 运行
win = minitools()
