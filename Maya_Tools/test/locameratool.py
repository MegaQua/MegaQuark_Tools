from pyfbsdk import *
from pyfbsdk_additions import *
from PySide2 import QtCore, QtWidgets, QtGui

class CameraTransferTool(QtWidgets.QWidget):
    def __init__(self):
        super(CameraTransferTool, self).__init__()

        self.setWindowTitle("Camera Transfer Tool")

        self.vcam_list = []
        self.rigcam_list = []

        self.populate_cameras()
        layout = QtWidgets.QGridLayout(self)

        # 第一行
        vcam_label = QtWidgets.QLabel("Vcam List")
        self.vcam_combo = QtWidgets.QComboBox()
        for vcam in self.vcam_list:
            self.vcam_combo.addItem(vcam)
        layout.addWidget(vcam_label, 0, 0)
        layout.addWidget(self.vcam_combo, 0, 1, 1, 3)

        # 第二行
        rigcam_label = QtWidgets.QLabel("Rig Cam List")
        self.rigcam_combo = QtWidgets.QComboBox()
        for rigcam in self.rigcam_list:
            self.rigcam_combo.addItem(rigcam)
        layout.addWidget(rigcam_label, 1, 0)
        layout.addWidget(self.rigcam_combo, 1, 1, 1, 3)

        # 第三行
        self.step1_button = QtWidgets.QPushButton("Step 1")
        self.step2_button = QtWidgets.QPushButton("Step 2")
        layout.addWidget(self.step1_button, 2, 1)
        layout.addWidget(self.step2_button, 2, 2)

        # 连接按钮到相应的函数
        self.step1_button.clicked.connect(self.step1)
        self.step2_button.clicked.connect(self.step2)

        self.setLayout(layout)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def populate_cameras(self):
        # 遍历所有模型，寻找以vcam_开头的camera对象
        for model in FBSystem().Scene.Components:
            try:
                model_name = model.Name
            except:
                continue
            if isinstance(model, FBCamera):
                if model.Name.startswith("vcam_"):
                    self.vcam_list.append(model.LongName)
            elif isinstance(model, FBModel):
                if "Cam_Rig" in model.Name.encode('utf-8').decode('utf-8'):
                    self.rigcam_list.append(model.LongName)

    def Align(self, pModel, pAlignTo, pAlignTransX=True, pAlignTransY=True, pAlignTransZ=True, pAlignRotX=True, pAlignRotY=True, pAlignRotZ=True):
        lAlignTransPos = FBVector3d()
        lModelTransPos = FBVector3d()
        lAlignRotPos = FBVector3d()
        lModelRotPos = FBVector3d()

        pAlignTo.GetVector(lAlignTransPos)
        pModel.GetVector(lModelTransPos)

        pAlignTo.GetVector(lAlignRotPos, FBModelTransformationType.kModelRotation)
        pModel.GetVector(lModelRotPos, FBModelTransformationType.kModelRotation)

        if pAlignTransX:
            lModelTransPos[0] = lAlignTransPos[0]
        if pAlignTransY:
            lModelTransPos[1] = lAlignTransPos[1]
        if pAlignTransZ:
            lModelTransPos[2] = lAlignTransPos[2]

        if pAlignRotX:
            lModelRotPos[0] = lAlignRotPos[0]
        if pAlignRotY:
            lModelRotPos[1] = lAlignRotPos[1]
        if pAlignRotZ:
            lModelRotPos[2] = lAlignRotPos[2]

        pModel.SetVector(lModelTransPos)
        pModel.SetVector(lModelRotPos, FBModelTransformationType.kModelRotation)

    def step1(self):
        # 获取选中的vcam和rigcam
        vcam_name = self.vcam_combo.currentText()
        rigcam_namespace = self.rigcam_combo.currentText().split(':')[0]

        # 获取对象
        vcam = FBFindModelByLabelName(vcam_name)
        camera = FBFindModelByLabelName(f"{rigcam_namespace}:camera")
        cam_move = FBFindModelByLabelName(f"{rigcam_namespace}:Cam_Move")
        Cam_Interest = FBFindModelByLabelName(f"{rigcam_namespace}:Cam_Interest")
        aim_null = FBModelNull(f"{vcam_name}_aim")

        if not vcam or not cam_move or not Cam_Interest:
            FBMessageBox("Error", "Selected cameras or rig not found!", "OK")
            return

        self.Align(vcam, camera)
        self.Align(aim_null, Cam_Interest)
        aim_null.Parent = vcam

        QtWidgets.QApplication.processEvents()

    def step2(self):
        def Find_AnimationNode(pParent, pName):
            # Boxが指定された名前のノードを持っているかを調べる。
            lResult = None
            for lNode in pParent.Nodes:
                if lNode.Name == pName:
                    lResult = lNode
                    break
            return lResult

        # 获取选中的vcam和rigcam
        vcam_name = self.vcam_combo.currentText()
        rigcam_namespace = self.rigcam_combo.currentText().split(':')[0]

        # 获取对象
        vcam = FBFindModelByLabelName(vcam_name)
        cam_move = FBFindModelByLabelName(f"{rigcam_namespace}:Cam_Move")
        Cam_Interest = FBFindModelByLabelName(f"{rigcam_namespace}:Cam_Interest")
        aim_null = FBFindModelByLabelName(f"{vcam_name}_aim")
        camera = FBFindModelByLabelName(f"{rigcam_namespace}:camera")

        if not vcam or not cam_move or not Cam_Interest or not aim_null:
            FBMessageBox("Error", "Selected cameras or rig not found!", "OK")
            return

        # 创建parent约束并跳过旋转的X和Y轴
        vcam_constraint = FBConstraintManager().TypeCreateConstraint("Position")
        vcam_constraint.Name = f"{vcam_name}_Position"
        vcam_constraint.ReferenceAdd(0, cam_move)
        vcam_constraint.ReferenceAdd(1, vcam)
        vcam_constraint.Active = True

        # aim_null对Cam_Interest position约束
        aim_constraint = FBConstraintManager().TypeCreateConstraint("Position")
        aim_constraint.Name = f"{vcam_name}_AimNull_Position"
        aim_constraint.ReferenceAdd(0, Cam_Interest)
        aim_constraint.ReferenceAdd(1, aim_null)
        aim_constraint.Active = True
        #aim_constraint.Lock  = True

        FocusAngle = vcam.PropertyList.Find('FocusAngle')
        FieldOfView = vcam.PropertyList.Find('FieldOfView')
        Roll = vcam.PropertyList.Find('Roll')
        FocusAngle.SetAnimated(True)
        FieldOfView.SetAnimated(True)
        Roll.SetAnimated(True)

        Relation = FBConstraintRelation(vcam_name + "_Relation")
        Sender1 = Relation.SetAsSource(vcam)
        Sender1_Rotation = Find_AnimationNode(Sender1.AnimationNodeOutGet(), 'Rotation')
        Sender1_FieldOfView = Find_AnimationNode(Sender1.AnimationNodeOutGet(), 'FieldOfView')
        Sender1_FocusAngle = Find_AnimationNode(Sender1.AnimationNodeOutGet(), 'FocusAngle')
        Sender1_Roll = Find_AnimationNode(Sender1.AnimationNodeOutGet(), 'Roll')
        Sender2 = Relation.SetAsSource(camera)
        Sender2_Rotation = Find_AnimationNode(Sender2.AnimationNodeOutGet(), 'Rotation')
        Vector_to_Number1 = Relation.CreateFunctionBox('Converters', 'Vector to Number')
        Vector_to_Number1_V = Find_AnimationNode(Vector_to_Number1.AnimationNodeInGet(), 'V')
        Vector_to_Number1_X = Find_AnimationNode(Vector_to_Number1.AnimationNodeOutGet(), 'X')
        Vector_to_Number2 = Relation.CreateFunctionBox('Converters', 'Vector to Number')
        Vector_to_Number2_V = Find_AnimationNode(Vector_to_Number2.AnimationNodeInGet(), 'V')
        Vector_to_Number2_X = Find_AnimationNode(Vector_to_Number2.AnimationNodeOutGet(), 'X')
        Subtract = Relation.CreateFunctionBox("Number", "Subtract (a - b)")
        Subtract_a = Find_AnimationNode(Subtract.AnimationNodeInGet(), 'a')
        Subtract_b = Find_AnimationNode(Subtract.AnimationNodeInGet(), 'b')
        Subtract_Result = Find_AnimationNode(Subtract.AnimationNodeOutGet(), 'Result')
        receiver1 = Relation.ConstrainObject(camera)

        ADD = Relation.CreateFunctionBox("Number", "Add (a + b)")
        ADD_a = Find_AnimationNode(ADD.AnimationNodeInGet(), 'a')
        ADD_b = Find_AnimationNode(ADD.AnimationNodeInGet(), 'b')
        ADD_Result = Find_AnimationNode(ADD.AnimationNodeOutGet(), 'Result')

        receiver1_roll = Find_AnimationNode(receiver1.AnimationNodeInGet(), 'Roll')
        receiver1_FieldOfView = Find_AnimationNode(receiver1.AnimationNodeInGet(), 'FieldOfView')
        receiver1_FocusAngle = Find_AnimationNode(receiver1.AnimationNodeInGet(), 'FocusAngle')
        FBConnect(Sender1_Rotation, Vector_to_Number1_V)
        FBConnect(Sender2_Rotation, Vector_to_Number2_V)
        FBConnect(Vector_to_Number1_X, Subtract_a)
        FBConnect(Vector_to_Number2_X, Subtract_b)
        #FBConnect(Subtract_Result, receiver1_roll)
        FBConnect(Subtract_Result, ADD_a)
        FBConnect(Sender1_Roll, ADD_b)
        FBConnect(ADD_Result, receiver1_roll)
        FBConnect(Sender1_FieldOfView, receiver1_FieldOfView)
        FBConnect(Sender1_FocusAngle, receiver1_FocusAngle)

        Relation.SetBoxPosition(Sender1, 0, -300)
        Relation.SetBoxPosition(Sender2, 0, 0)
        Relation.SetBoxPosition(Vector_to_Number1, 300, -300)
        Relation.SetBoxPosition(Vector_to_Number2, 300, 0)
        Relation.SetBoxPosition(Subtract, 600, -200)
        Relation.SetBoxPosition(receiver1, 900, -200)

        Relation.Active = True

        QtWidgets.QApplication.processEvents()

# 显示工具窗口
LO_camera = CameraTransferTool()
