# -*- coding: utf-8 -*-
from pyfbsdk import *
from pyfbsdk_additions import *
import xml.etree.ElementTree as ET
import _winreg
from os import walk 
import os.path
import os
import glob
import re
#python api https://help.autodesk.com/view/MOBPRO/2019/ENU/?guid=__py_ref_index_html
#获取系统默认路径
def GetWindowsOSDesktopPath():
    key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    desktopFilepath = _winreg.QueryValueEx(key, 'Desktop')[0]  
    return  str(desktopFilepath)

class MotionBuilderTool:
    def __init__(self):
        self.tool = FBCreateUniqueTool('快速动画重定向插件')
        self.tool.StartSizeX = 650
        self.tool.StartSizeY = 650
        #窗口布局
        self.PopulateconfigLayout(self.tool)

        ShowTool(self.tool)
        #窗口销毁事件回调
        self.tool.OnUnbind.Add(self.OnToolDestroy)
        self.LoadConfigHistory()
    
    def LoadConfigHistory(self):
        self.modelFileEdit = 'C:\\Users\\26593\\Desktop\\demo\\SK_Mannequin.FBX'
        self.skeletonDefinitionTemplateEdit = 'C:\\Users\\26593\\Desktop\\demo\\template.xml'
        self.TPoseConfigEdit = ''
        self.animationRepositoryEdit = 'C:\Users\\26593\\Desktop\demo\\animationRepository'
        self.outputEdit = 'C:\Users\\26593\\Desktop\\demo\\outputEdit'
        self.MergeEdit = 'C:\\Users\\26593\\Desktop\\demo\\Ying6_Tpos.FBX'
    
    #窗口销毁事件回调
    def OnToolDestroy(self, control, event):
        FBSystem().Scene.OnChange.Remove(SceneChanged)

    #窗口布局
    def PopulateconfigLayout(self, mainLayout):
        #配置大小区域
        x = FBAddRegionParam(10, FBAttachType.kFBAttachLeft, '')
        y = FBAddRegionParam(20, FBAttachType.kFBAttachTop, '')
        w = FBAddRegionParam(-10, FBAttachType.kFBAttachRight, '')
        h = FBAddRegionParam(600, FBAttachType.kFBAttachNone, '')
        mainLayout.AddRegion('Config', '', x, y, w, h)
        #创建纵向布局
        configLayout = FBVBoxLayout()
        mainLayout.SetControl('Config', configLayout)
        mainLayout.SetBorder('Config', FBBorderStyle.kFBStandardBorder ,True, True,2,2,200,0)
        #打开路径
        Button_1 = FBButton()
        Button_1.Look = FBButtonLook.kFBLookColorChange
        Button_1.OnClick.Add(self.OpenModelFile)
        Button_1.Caption = '打开路径'
        configLayout.Add(Button_1, 50)
        #加载模型
        Button_2 = FBButton()
        Button_2.Look = FBButtonLook.kFBLookColorChange
        Button_2.OnClick.Add(self.LoadModelFile)
        Button_2.Caption = '加载模型'
        configLayout.Add(Button_2, 50)
        #定义骨架
        Button_3 = FBButton()
        Button_3.Look = FBButtonLook.kFBLookColorChange
        Button_3.OnClick.Add(self.DefineSkeleton)
        Button_3.Caption = '定义骨架'
        configLayout.Add(Button_3, 50)
        #把骨架映射到motion默认的系统上
        Button_4 = FBButton()
        Button_4.Look = FBButtonLook.kFBLookColorChange
        Button_4.OnClick.Add(self.Characterize)
        Button_4.Caption = '映射'
        configLayout.Add(Button_4, 50)
        """
        #跳转到控制面板
        Button_5 = FBButton()
        Button_5.Look = FBButtonLook.kFBLookColorChange
        Button_5.OnClick.Add(self.PlotToControlRig)
        Button_5.Caption = '跳转到控制面板'
        configLayout.Add(Button_5, 50)
        #加载动画到重定向目标
        Button_6 = FBButton()
        Button_6.Look = FBButtonLook.kFBLookColorChange
        Button_6.OnClick.Add(self.LoadAnimationForRetargeting)
        Button_6.Caption = '加载动画到重定向目标'
        configLayout.Add(Button_6, 50)
        """
        #打开Merge
        Button_7 = FBButton()
        Button_7.Look = FBButtonLook.kFBLookColorChange
        Button_7.OnClick.Add(self.OpenMerge)
        Button_7.Caption = '打开Merge'
        configLayout.Add(Button_7, 50)
        #选source
        Button_8 = FBButton()
        Button_8.Look = FBButtonLook.kFBLookColorChange
        Button_8.OnClick.Add(self.SetSource)
        Button_8.Caption = '选Source'
        configLayout.Add(Button_8, 50)
        #添加角色动画轨道
        Button_10 = FBButton()
        Button_10.Look = FBButtonLook.kFBLookColorChange
        Button_10.OnClick.Add(self.AddCharacterAnimationTrack)
        Button_10.Caption = '添加角色动画轨道'
        configLayout.Add(Button_10, 50)
        #烘焙动画到新骨骼
        Button_9 = FBButton()
        Button_9.Look = FBButtonLook.kFBLookColorChange
        Button_9.OnClick.Add(self.PlotSkeleton)
        Button_9.Caption = '烘焙动画到新骨骼'
        configLayout.Add(Button_9, 50)
        #输出动画
        Button_11 = FBButton()
        Button_11.Look = FBButtonLook.kFBLookColorChange
        Button_11.OnClick.Add(self.SaveAnimationFile)
        Button_11.Caption = '输出动画'
        configLayout.Add(Button_11, 50)
        
    #打开模型文件
    def OpenModelFile(self, contorl, event):
        # 创建弹出窗口并设置必要的初始值
        filePopup = pyfbsdk.FBFilePopup()
        filePopup.Caption = '选择你的原始动画文件'
        filePopup.Style = pyfbsdk.FBFilePopupStyle.kFBFilePopupOpen
        filePopup.Filter = '*.fbx'
        # 设置默认路径(假设我们使用windows操作系统)
        filePopup.Path = GetWindowsOSDesktopPath()
        # 让GUI显示出来
        bResult = filePopup.Execute()
        if bResult:
            self.modelFileEdit = filePopup.FullFilename
    
    #打开骨骼定义映射表
    def OpenSkeletonDefinitionTemplateFile(self, contorl, event):
        # 创建弹出窗口并设置必要的初始值
        filePopup = pyfbsdk.FBFilePopup()
        filePopup.Caption = '选择您的骨骼定义映射表'
        filePopup.Style = pyfbsdk.FBFilePopupStyle.kFBFilePopupOpen
        filePopup.Filter = '*.xml'
        # 设置默认路径(假设我们使用windows操作系统)
        filePopup.Path = GetWindowsOSDesktopPath()
        # 让GUI显示出来
        bResult = filePopup.Execute()
        if bResult:
            self.skeletonDefinitionTemplateEdit= filePopup.FullFilename

    #打开动画存储文件夹
    def OpenAimationRepositoryFolder(self, contorl, event):
        # 创建弹出窗口并设置必要的初始值
        folderPopup = pyfbsdk.FBFolderPopup()
        folderPopup.Caption = '选择您的动画存储文件夹'
        # 设置默认路径(假设我们使用windows操作系统)
        folderPopup.Path = GetWindowsOSDesktopPath()
        # 让GUI显示出来
        result = folderPopup.Execute()
        if result:
            self.animationRepositoryEdit = folderPopup.Path
    
    #打开输出文件夹
    def OpenOutputFolder(self, contorl, event):
        # 创建弹出窗口并设置必要的初始值
        folderPopup = pyfbsdk.FBFolderPopup()
        folderPopup.Caption = '选择您的输出文件夹'
        # 设置默认路径(假设我们使用windows操作系统)
        folderPopup.Path = GetWindowsOSDesktopPath()
        # 让GUI显示出来
        result = folderPopup.Execute()
        if result:
            self.outputEdit = folderPopup.Path
    
    #加载模型文件
    def LoadModelFile(self, control, event):   
        targetFilepath = self.modelFileEdit
        if targetFilepath == '':
            FBMessageBox( 'Config','没有模型文件路径', 'OK', None, None )
            return
        app = FBApplication()
        app.FileNew()
        loadOption = FBFbxOptions(True)
        loadOption.NamespaceList = 'UE4'
        app.FileOpen(targetFilepath, True, loadOption)

    #定义骨架
    def DefineSkeleton(self, control, event):
        skeletonDefinitionTemplateFilepath = self.skeletonDefinitionTemplateEdit
        if skeletonDefinitionTemplateFilepath == '':
            FBMessageBox( 'Config', '无框架定义模板文件路径.', 'OK', None, None )
            return
        # 待办事项:在这里需要验证操作
        currentCharacter = FBApplication().CurrentCharacter
        # 如果没有角色，就创造一个
        if currentCharacter == None:     
            currentCharacter = FBCharacter('UE4:Character')
            FBApplication().CurrentCharacter = currentCharacter
        tree = ET.parse(skeletonDefinitionTemplateFilepath)
        root = tree.getroot()
        # 待办事项:现在这里没有匹配操作
        for elem in tree.iter(tag='item'):
            jointName = 'UE4:'+elem.attrib['value']
            targetLinkSlotName = elem.attrib['key'] + 'Link'
            if jointName == '':
                continue
            joint = FBFindModelByLabelName(jointName)
            if joint == None:
                print('骨架定义模板中的意外连接: %s' % (jointName))
            else:
                property = currentCharacter.PropertyList.Find(targetLinkSlotName)
                property.removeAll()
                property.append (joint)
    
    #动画文件是否存在
    def IsAnimationFileValid(self, animationFileFullFilename):
         # 获取目标网格文件名
        targetMeshFullFilename = self.modelFileEdit
        targetMeshBasename = os.path.basename(targetMeshFullFilename)
        targetMeshName,_ = os.path.splitext(targetMeshBasename)
        baseName = os.path.basename(animationFileFullFilename)
        fileNameWithoutExtention,_ = os.path.splitext(baseName)
        parttern = targetMeshName + r'_Ani_\w+'
        match = re.search(parttern, fileNameWithoutExtention ) 
        result = not match == None
        return  result
    
    #在存储库文件夹中找到动画
    def FindAnimationInRepositoryFolder(self, control, event):
        self.foundlAnimationFileList.Items.removeAll()
        animationRepositoryFolder = self.animationRepositoryEdit
        bValidFolderPath = os.path.isdir(animationRepositoryFolder)
        if not bValidFolderPath:
            FBMessageBox( 'Config','无效的动画存储库文件夹', 'OK', None, None )
            return
        foundFbxFiles = glob.glob(animationRepositoryFolder +'/*.fbx')
        for f in foundFbxFiles:
            if self.IsAnimationFileValid(f):
                self.foundlAnimationFileList.Items.append(f)
        # 如果没有找到动画文件就打印
        if self.foundlAnimationFileList.Items.len == 0:
            print('没有发现动画')
            return
    
    #描述-把骨架映射到motion默认的系统上
    def Characterize(self, control, event):
        currentCharacter = FBApplication().CurrentCharacter
        if currentCharacter == None:
            FBMessageBox( 'Config', '没有定义角色', 'OK', None, None )
            return 
        # 这里的True指的是两足动物的特征
        currentCharacter.SetCharacterizeOn(True)
        FBSystem().Scene.Evaluate()
    
    #跳转到控制面板
    def PlotToControlRig(self, control, event):
        currentCharacter = FBApplication().CurrentCharacter
        if currentCharacter == None:
            FBMessageBox( 'Config', '没有定义角色', 'OK', None, None )
            return 
        # 禁用并删除控制Rig
        currentCharacter.ActiveInput = False
        controlRig = currentCharacter.GetCurrentControlSet()
        # 如果没有控制Rig，就创建一个新的
        if not controlRig:
            # 使用“True”参数指定的正运动学和逆运动学创建一个控制Rig
            bCreationResult = currentCharacter.CreateControlRig(True)
            if not bCreationResult:
                print('在PlotToControlRig中创建新的控制rig失败，请检查')

        plotOptions = FBPlotOptions()
        plotOptions.ConstantKeyReducerKeepOneKey = False
        plotOptions.PlotAllTakes = True 
        plotOptions.PlotOnFrame = True
        plotOptions.PlotPeriod = FBTime( 0, 0, 0, 1 )
        plotOptions.PlotTranslationOnRootOnly = False
        plotOptions.PreciseTimeDiscontinuities = False
        plotOptions.RotationFilterToApply = FBRotationFilter.kFBRotationFilterUnroll
        plotOptions.UseConstantKeyReducer = False
        currentCharacter.PlotAnimation (FBCharacterPlotWhere.kFBCharacterPlotOnControlRig,plotOptions )
    
    #加载动画到重定向目标
    def LoadAnimationForRetargeting(self, control, event):
        fbxOptions = FBFbxOptions( True )
        fbxOptions.TransferMethod = FBCharacterLoadAnimationMethod.kFBCharacterLoadRetarget
        plotOptions = FBPlotOptions()
        animFile = 'C:\Users\26593\Desktop\demo\Bow_Run_Fwd_45_L.fbx'
        currentCharacter = FBApplication().CurrentCharacter
        if currentCharacter == None:
            FBMessageBox( 'Config', '没有定义角色', 'OK', None, None )
            return 
        FBApplication().LoadAnimationOnCharacter( animFile, currentCharacter, fbxOptions, plotOptions )
    
    #执行测试
    def ExecuteTest(self, control, event): 
        # 首先，清除场景并打开目标网格文件
        # 从框架模板定义
        # 描述
        # 控制Rig
        # 指定动画文件
        # 加载动画
        self.FindAnimationInRepositoryFolder() 

    #打开Merge
    def OpenMerge(self, control, event): 
        # 文件路径
        nativeFile = self.MergeEdit
        options = FBFbxOptions(True, nativeFile)
        options.SetAll(FBElementAction.kFBElementActionMerge, True)
        for takeIndex in range( 0, options.GetTakeCount() ):
            # 取消选择options
            options.SetTakeSelect( takeIndex, True )
        FBApplication().FileMerge( nativeFile, False, options )
    #选source
    def SetSource(self, control, event): 
        # 选character
        foundComponents = FBComponentList()
        # 选character
        FBFindObjectsByName('Character', foundComponents, True, False)
        Character = foundComponents[0]
        Character.Selected = True
        # 选source
        foundComponents = FBComponentList()
        FBFindObjectsByName('UE4:Character', foundComponents, True, False)
        OldCharacter = foundComponents[0]
        Character.InputCharacter = OldCharacter
        Character.InputType = FBCharacterInputType.kFBCharacterInputCharacter
        Character.ActiveInput = True
    
    #烘焙动画到新骨骼
    def PlotSkeleton(self, control, event): 
        myPlotOptions = FBPlotOptions ()
        myPlotOptions.ConstantKeyReducerKeepOneKey = False
        myPlotOptions.PlotAllTakes = False
        myPlotOptions.PlotOnFrame = True
        myPlotOptions.PlotPeriod = FBTime( 0, 0, 0, 1 )
        myPlotOptions.PlotTranslationOnRootOnly = False
        myPlotOptions.PreciseTimeDiscontinuities = False
        myPlotOptions.RotationFilterToApply = FBRotationFilter.kFBRotationFilterNone
        myPlotOptions.UseConstantKeyReducer = False
        TheChar = FBApplication().CurrentCharacter
        if TheChar.ActiveInput == True:
            TheChar.PlotAnimation(FBCharacterPlotWhere.kFBCharacterPlotOnSkeleton, myPlotOptions)
        else:
            TheChar.PlotAnimation(FBCharacterPlotWhere.kFBCharacterPlotOnControlRig, myPlotOptions)
    
    #添加角色动画轨道
    def AddCharacterAnimationTrack(self, control, event): 
        lParentTrack = FBStoryTrack(FBStoryTrackType.kFBStoryTrackCharacter)
        #把当前角色赋予轨道
        foundComponents = FBComponentList()
        FBFindObjectsByName('UE4:Character', foundComponents, True, False)
        Character = foundComponents[0]
        lParentTrack.Details.append(Character)
    
    #保存当前动画文件
    def SaveAnimationFile(self, control, event): 
        # 创建所有的类实例
        lSystem = FBSystem()
        lApp = FBApplication()
        lScene = lSystem.Scene
        #开始保存当前动画
        lOptions = FBFbxOptions(False)## 保存选项
        lOptions.SaveCharacter = False
        lOptions.SaveControlSet = True
        lOptions.SaveCharacterExtension = False
        if len( lScene.Characters ) > 0:
            lApp.SaveCharacterRigAndAnimation(self.animationRepositoryEdit + '\\Ying6_Bow_Run_Fwd_45_L.fbx', lScene.Characters[0], lOptions)

        

        
MotionBuilderTool()