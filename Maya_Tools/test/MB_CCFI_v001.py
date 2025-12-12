from pyfbsdk import *
from pyfbsdk_additions import *
import xml.etree.ElementTree as ET
#import _winreg
from os import walk 
import os.path
import os
import glob
import re
import json


mouthposes_dict ={
    "default":"K:\\shenron\\11_Users\\Q\\MB_CCFI\\Json\\mouth_poses\\cc_default.json",
    "a":"K:\\shenron\\11_Users\\Q\\MB_CCFI\\Json\\mouth_poses\\cc_mouthpose_a.json",
    "i":"K:\\shenron\\11_Users\\Q\\MB_CCFI\\Json\\mouth_poses\\cc_mouthpose_i.json",
    "u":"K:\\shenron\\11_Users\\Q\\MB_CCFI\\Json\\mouth_poses\\cc_mouthpose_u.json",
    "e":"K:\\shenron\\11_Users\\Q\\MB_CCFI\\Json\\mouth_poses\\cc_mouthpose_e.json",
    "o":"K:\\shenron\\11_Users\\Q\\MB_CCFI\\Json\\mouth_poses\\cc_mouthpose_o.json"
}
mouthposes = []
for key in mouthposes_dict:
    mouthposes.append(key)
#print (mouthposes)
eyebrowposes_dict={
    "default":"K:\\shenron\\11_Users\\Q\\MB_CCFI\\Json\\eyebrow_poses\\cc_default.json",
    "angry":"K:\\shenron\\11_Users\\Q\\MB_CCFI\\Json\\eyebrow_poses\\cc_angry.json",
    "happy":"K:\\shenron\\11_Users\\Q\\MB_CCFI\\Json\\eyebrow_poses\\cc_happy.json",
    "sad":"K:\\shenron\\11_Users\\Q\\MB_CCFI\\Json\\eyebrow_poses\\cc_sad.json",
    "surprise":"K:\\shenron\\11_Users\\Q\\MB_CCFI\\Json\\eyebrow_poses\\cc_surprise.json",
    "pain":"K:\\shenron\\11_Users\\Q\\MB_CCFI\\Json\\eyebrow_poses\\cc_pain.json"
}

eyebrowposes = []
for key in eyebrowposes_dict:
    eyebrowposes.append(key)
eyeposes_dict ={
    "default":"K:\\shenron\\11_Users\\Q\\MB_CCFI\\Json\\eye_poses\\cc_default.json",
    "close":"K:\\shenron\\11_Users\\Q\\MB_CCFI\\Json\\eye_poses\\cc_close.json"
}
eyeposes = []
for key in eyeposes_dict:
    eyeposes.append(key)
    
mouthshapes = [
        "V_Open",
        "V_Explosive",
        "V_Dental_Lip",
        "V_Tight_O",
        "V_Tight",
        "V_Wide",
        "V_Affricate",
        "V_Lip_Open",
        "Nose_Sneer_L",
        "Nose_Sneer_R",
        "Cheek_Raise_L",
        "Cheek_Raise_R",
        "Cheek_Suck_L",
        "Cheek_Suck_R",
        "Cheek_Puff_L",
        "Cheek_Puff_R",
        "Mouth_Smile_L",
        "Mouth_Smile_R",
        "Mouth_Smile_Sharp_L",
        "Mouth_Smile_Sharp_R",
        "Mouth_Frown_L",
        "Mouth_Frown_R",
        "Mouth_Stretch_L",
        "Mouth_Stretch_R",
        "Mouth_Dimple_L",
        "Mouth_Dimple_R",
        "Mouth_Press_L",
        "Mouth_Press_R",
        "Mouth_Tighten_L",
        "Mouth_Tighten_R",
        "Mouth_Blow_L",
        "Mouth_Blow_R",
        "Mouth_Pucker_Up_L",
        "Mouth_Pucker_Up_R",
        "Mouth_Pucker_Down_L",
        "Mouth_Pucker_Down_R",
        "Mouth_Funnel_Up_L",
        "Mouth_Funnel_Up_R",
        "Mouth_Funnel_Down_L",
        "Mouth_Funnel_Down_R",
        "Mouth_Roll_In_Upper_L",
        "Mouth_Roll_In_Upper_R",
        "Mouth_Roll_In_Lower_L",
        "Mouth_Roll_In_Lower_R",
        "Mouth_Roll_Out_Upper_L",
        "Mouth_Roll_Out_Upper_R",
        "Mouth_Roll_Out_Lower_L",
        "Mouth_Roll_Out_Lower_R",
        "Mouth_Push_Upper_L",
        "Mouth_Push_Upper_R",
        "Mouth_Push_Lower_L",
        "Mouth_Push_Lower_R",
        "Mouth_Pull_Upper_L",
        "Mouth_Pull_Upper_R",
        "Mouth_Pull_Lower_L",
        "Mouth_Pull_Lower_R",
        "Mouth_Up",
        "Mouth_Down",
        "Mouth_L",
        "Mouth_R",
        "Mouth_Upper_L",
        "Mouth_Upper_R",
        "Mouth_Lower_L",
        "Mouth_Lower_R",
        "Mouth_Shrug_Upper",
        "Mouth_Shrug_Lower",
        "Mouth_Drop_Upper",
        "Mouth_Drop_Lower",
        "Mouth_Up_Upper_L",
        "Mouth_Up_Upper_R",
        "Mouth_Down_Lower_L",
        "Mouth_Down_Lower_R",
        "Mouth_Chin_Up",
        "Mouth_Close",
        "Mouth_Contract",
        "Tongue_Bulge_L",
        "Tongue_Bulge_R",
        "Jaw_Open",
        "Jaw_Forward",
        "Jaw_Backward",
        "Jaw_L",
        "Jaw_R",
        "Jaw_Up",
        "Jaw_Down",
        "Neck_Swallow_Up",
        "Neck_Swallow_Down",
        "Neck_Tighten_L",
        "Neck_Tighten_R",
    ]
eyebrowshapes= [
        "Brow_Raise_Inner_L",
        "Brow_Raise_Inner_R",
        "Brow_Raise_Outer_L",
        "Brow_Raise_Outer_R",
        "Brow_Drop_L",
        "Brow_Drop_R",
        "Brow_Compress_L",
        "Brow_Compress_R",
]
eyeshapes= [
        "Eye_Blink_L",
        "Eye_Blink_R",
        "Eye_Squint_L",
        "Eye_Squint_R",
        "Eye_Wide_L",
        "Eye_Wide_R",
        "Eye_L_Look_L",
        "Eye_R_Look_L",
        "Eye_L_Look_R",
        "Eye_R_Look_R",
        "Eye_L_Look_Up",
        "Eye_R_Look_Up",
        "Eye_L_Look_Down",
        "Eye_R_Look_Down",
        "Eyelash_Upper_Up_L",
        "Eyelash_Upper_Down_L",
        "Eyelash_Upper_Up_R",
        "Eyelash_Upper_Down_R",
        "Eyelash_Lower_Up_L",
        "Eyelash_Lower_Down_L",
        "Eyelash_Lower_Up_R",
        "Eyelash_Lower_Down_R",
]


#def BtnCallback(control, event):
#    print (control.Caption, " has been clicked!")
def ListCallback(control, event):
    
    importjsonpath = mouthposes_dict[control.Items[control.ItemIndex]]
    print (control.Items[control.ItemIndex], "has been selected!set path at "+ importjsonpath)
def ListCallback2(control, event):
    
    importjsonpath = eyebrowposes_dict[control.Items[control.ItemIndex]]
    print (control.Items[control.ItemIndex], "has been selected!set path at "+ importjsonpath)
def ListCallback3(control, event):
    
    importjsonpath = eyeposes_dict[control.Items[control.ItemIndex]]
    print (control.Items[control.ItemIndex], "has been selected!set path at "+ importjsonpath)
   

def PopulateLayout(mainLyt,*args):
    
    def OpenJsonFile(self,*args):
        # 创建弹出窗口并设置必要的初始值
        filePopup = pyfbsdk.FBFilePopup()
        filePopup.Caption = 'select .json file'
        #filePopup.Style = pyfbsdk.FBFilePopupStyle.kFBFilePopupOpen
        filePopup.Filter = '*.json'
        # 设置默认路径(假设我们使用windows操作系统)
        filePopup.Path = "K:\\shenron\\11_Users\\Q\MB_CCFI\\Json\\mouth_a2f"
        # 让GUI显示出来
        bResult = filePopup.Execute()
        if bResult:
            self.modelFileEdit = filePopup.FullFilename
            ed_Jpath.Text  = filePopup.FullFilename
            print ("the path is " + ed_Jpath.Text)
            #change dataflame lb
            with open (ed_Jpath.Text) as f:
                facs_data = json.loads(f.read())
                jsonflamedata = str(facs_data["numFrames"])
                jsonflamedata_lb.Caption = ".josn file flame length is : " + jsonflamedata


    def GetLastSelectetdModels():
        selectedModels = FBModelList()
        FBGetSelectedModels(selectedModels, None, True, True)
        return selectedModels[-1] if selectedModels else None



    def setBSkey(self,*args):
        importjsonpath = ed_Jpath.Text
        #get bottom name
        bottom_name = self.Caption
        #print (self.Caption, " has been clicked!")
        if bottom_name == "import .json":
            print (self.Caption, " has been clicked!,import a2f mouth animation")
            blendshapetype = mouthshapes
        elif bottom_name == "set mouth pose":
            print (self.Caption, " has been clicked!,import mouthpose animation")
            blendshapetype =  mouthshapes
            importjsonpath = mouthposes_dict[listtab_1.Items[listtab_1.ItemIndex]]
            print("set mouth pose in path "+importjsonpath)
        elif bottom_name == "set eyebrow pose":
            print (self.Caption, " has been clicked!,import eyebrow pose animation")
            blendshapetype = eyebrowshapes
            importjsonpath = eyebrowposes_dict[listtab_2.Items[listtab_2.ItemIndex]]
            print("set mouth pose in path "+importjsonpath)            
        elif bottom_name == "set eye pose":
            print (self.Caption, " has been clicked!,import eye pose animation")
            blendshapetype = eyeshapes
            importjsonpath = eyeposes_dict[listtab_3.Items[listtab_3.ItemIndex]]
            print("set eye pose in path "+importjsonpath)         
        else:
            print (self.Caption, " has been clicked!,but not finished")
            return
        #print("import json to set mouth blendshapes key")
        setkeytimes = 0
        
        with open (importjsonpath) as f:
            startFlame = ed_startflame.Text
            keyMp = ed_mp.Text
            facs_data = json.loads(f.read())
            facsNames = facs_data["facsNames"]
            numPoses = facs_data["numPoses"]
            numFrames = facs_data["numFrames"]
            weightMat = facs_data["weightMat"]
            selectM = GetLastSelectetdModels()
            #set mesh list namespace
            if (ed_namespace.Text+"") == "":
                namespaceplus = ""
            else:
                namespaceplus = ed_namespace.Text+":"
            
            JawRoot = FBFindModelByLabelName(namespaceplus+"CC_Base_JawRoot")
            Teeth = FBFindModelByLabelName(namespaceplus+"CC_Base_Teeth02")
            Tongue = FBFindModelByLabelName(namespaceplus+"CC_Base_Tongue01")
            Base_body = FBFindModelByLabelName(namespaceplus+"CC_Base_Body")
            Base_EyeOc = FBFindModelByLabelName(namespaceplus+"CC_Base_EyeOcclusion")
            Base_TearLine = FBFindModelByLabelName(namespaceplus+"CC_Base_TearLine")
            CC_brow = FBFindModelByLabelName(namespaceplus+ed_eyebrowname.Text)

            meshlist = (
                Base_body,
                Base_EyeOc,
                Base_TearLine,
                CC_brow 
            )
            meshcount = int(len(meshlist))
            
            #set flame length
            if ed_mouthjsonflamelength.Text != "":
                print(ed_mouthjsonflamelength.Text)
           
                if int(ed_mouthjsonflamelength.Text) != "" and int(ed_mouthjsonflamelength.Text) >=  int(ed_startflame.Text)  and  numFrames > int(ed_mouthjsonflamelength.Text) - int(ed_startflame.Text)+1:
                    numFrames = int(ed_mouthjsonflamelength.Text) - int(ed_startflame.Text) + 1
                    print("set numFrames as "+ str(numFrames) )
                else :
                    print("use default numFrames")
                
            
            
            
            #key slelct mesh from Json
            if selectM != None :
                print ("key on select")
                for fr in range(numFrames) :
                    for i in range(numPoses):
                        if  selectM.PropertyList.Find(str(facsNames[i])) is not None:
                            selectM.PropertyList.Find(str(facsNames[i])).SetAnimated(True)
                            selectM.PropertyList.Find(str(facsNames[i])).GetAnimationNode().FCurve.KeyAdd(FBTime(0, 0, 0,fr+int(startFlame)), weightMat[fr][i]*100*float(keyMp))
                            setkeytimes = setkeytimes +1
                            if facsNames[i] == "Mouth_Down" :
                                selectM.PropertyList.Find(str(facsNames[i])).SetAnimated(True)
                                selectM.PropertyList.Find(str(facsNames[i])).GetAnimationNode().FCurve.KeyAdd(FBTime(0, 0, 0,fr+int(startFlame)), weightMat[fr][i]*30*float(keyMp))
                                setkeytimes = setkeytimes +1

                            if facsNames[i] == "Mouth_Down_Lower_L" :
                                selectM.PropertyList.Find(str(facsNames[i])).SetAnimated(True)
                                selectM.PropertyList.Find(str(facsNames[i])).GetAnimationNode().FCurve.KeyAdd(FBTime(0, 0, 0,fr+int(startFlame)), weightMat[fr][i]*30*float(keyMp))
                                setkeytimes = setkeytimes +1

                            if facsNames[i] == "Mouth_Down_Lower_R" :
                                selectM.PropertyList.Find(str(facsNames[i])).SetAnimated(True)
                                selectM.PropertyList.Find(str(facsNames[i])).GetAnimationNode().FCurve.KeyAdd(FBTime(0, 0, 0,fr+int(startFlame)), weightMat[fr][i]*30*float(keyMp))
                                setkeytimes = setkeytimes +1
            else:
                print("key for namespace")
                if namespaceplus == "":
                    print ("no namespace")
                else:
                    print("namespace is ----- "+namespaceplus)
                print("mesh name is")
                #print (meshcount)
                nousemeshcount = 0
                for i in range (meshcount):
                    if  meshlist[i] is not None:
                        print(" "+namespaceplus+str(meshlist[i].Name))
                    else :
                        nousemeshcount = nousemeshcount +1
                        print("can'find "+str(nousemeshcount)+" meshes")
                print(str(meshcount-nousemeshcount)+" meshes selected")
                        
                #key namespace from Json
                #setting special int
                Mouth_Down_Lower_L_Num = 30
                Mouth_Down_Lower_R_Num = 20
                Mouth_Down_Num = 30
                JawRoot_Num = 10
                Teeth_Num = 5
                Tongue_Num = 5
                
                #判断对象有没有对应脸 有satfcurve 无 print
                
                for i in range(numPoses):
                    if  facsNames[i] in blendshapetype:
                        for j in range(meshcount):
                            if meshlist[j] is not None :
                                if  meshlist[j].PropertyList.Find(str(facsNames[i])) is not None:
                                    meshlist[j].PropertyList.Find(str(facsNames[i])).SetAnimated(True)
                                    #print(str(meshlist[j].Name)+" Fcurve set ")
                                #else:
                                    #print(str(meshlist[j].Name)+" dont have "+str(facsNames[i])+" pass ")     
                            else:
                                pass
                for fr in range(numFrames) :
                    for i in range(numPoses):
                        if  facsNames[i] in blendshapetype:
                            for j in range(meshcount):
                                if meshlist[j] is not None :
                                    if  meshlist[j].PropertyList.Find(str(facsNames[i])) is not None:
                                        meshlist[j].PropertyList.Find(str(facsNames[i])).GetAnimationNode().FCurve.KeyAdd(FBTime(0, 0, 0,fr+int(startFlame)), weightMat[fr][i]*100*float(keyMp))
                                        setkeytimes = setkeytimes +1
                                        if facsNames[i] == "Mouth_Down_Lower_L" :
                                            meshlist[j].PropertyList.Find(str(facsNames[i])).SetAnimated(True)
                                            meshlist[j].PropertyList.Find(str(facsNames[i])).GetAnimationNode().FCurve.KeyAdd(FBTime(0, 0, 0,fr+int(startFlame)), weightMat[fr][i]*Mouth_Down_Lower_L_Num*float(keyMp))
                                            setkeytimes = setkeytimes +1
                                        if facsNames[i] == "Mouth_Down_Lower_R" :
                                            meshlist[j].PropertyList.Find(str(facsNames[i])).SetAnimated(True)
                                            meshlist[j].PropertyList.Find(str(facsNames[i])).GetAnimationNode().FCurve.KeyAdd(FBTime(0, 0, 0,fr+int(startFlame)), weightMat[fr][i]*Mouth_Down_Lower_R_Num*float(keyMp))
                                            setkeytimes = setkeytimes +1
                                        if facsNames[i] == "Mouth_Down" :
                                            meshlist[j].PropertyList.Find(str(facsNames[i])).SetAnimated(True)
                                            meshlist[j].PropertyList.Find(str(facsNames[i])).GetAnimationNode().FCurve.KeyAdd(FBTime(0, 0, 0,fr+int(startFlame)), weightMat[fr][i]*Mouth_Down_Num*float(keyMp))
                                            setkeytimes = setkeytimes +1
                                else:
                                    pass
                        if facsNames[i] == "Mouth_Down_Lower_R" :
                            if JawRoot is not None:
                                JawRoot.Rotation.SetAnimated(True)
                                JawRoot.Rotation.GetAnimationNode().KeyAdd(FBTime(0,0,0,fr+int(startFlame)), [0, 0, 90+weightMat[fr][i]*JawRoot_Num*float(keyMp)])
                                setkeytimes = setkeytimes +1
                        if facsNames[i] == "Mouth_Down" :
                            if Teeth is not None:
                                Teeth.Rotation.SetAnimated(True)
                                Teeth.Rotation.GetAnimationNode().KeyAdd(FBTime(0,0,0,fr+int(startFlame)), [-179.99, -0.01, weightMat[fr][i]*Teeth_Num*float(keyMp)])
                                setkeytimes = setkeytimes +1
                            if Tongue is not None:
                                Tongue.Rotation.SetAnimated(True)
                                Tongue.Rotation.GetAnimationNode().KeyAdd(FBTime(0,0,0,fr+int(startFlame)), [0.04, 1.2, 5.3+weightMat[fr][i]*Tongue_Num*float(keyMp)])
                                setkeytimes = setkeytimes +1
            print ("Done, set key "+str(setkeytimes)+" times")

 #ui element
    
    name = "Label_select..."
    x = FBAddRegionParam(10,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(190,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    lb = FBLabel()
    lb.Caption = "select mesh, or type in namespace :"
    mainLyt.SetControl(name,lb)  
    
    name = "namespace"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachRight,"Label_select...")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(100,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    ed_namespace = FBEdit()
    ed_namespace.Text = ""
    mainLyt.SetControl(name,ed_namespace) 
    
    name = "Label:"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachRight,"namespace")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(300,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    lb = FBLabel()
    lb.Caption = ":  ( none and no select for no namespace )"
    mainLyt.SetControl(name,lb)   
    #line 2
    name = "Label_eyebrowname"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label_select...")
    w = FBAddRegionParam(220,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    lb = FBLabel()
    lb.Caption = "eyebrow mesh name(without namespace) : "
    mainLyt.SetControl(name,lb)   
    
    name = "eyebrowname"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachRight,"Label_eyebrowname")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label:")
    w = FBAddRegionParam(-20,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    ed_eyebrowname = FBEdit()
    ed_eyebrowname.Text = "CC_brow"
    mainLyt.SetControl(name,ed_eyebrowname)   
        
    name = "startflame"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label_eyebrowname")
    w = FBAddRegionParam(70,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    lb = FBLabel()
    lb.Caption = "start flame :"
    mainLyt.SetControl(name,lb)   
    
    name = "theflame"
    x = FBAddRegionParam(20,FBAttachType.kFBAttachRight,"startflame")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label_eyebrowname")
    w = FBAddRegionParam(60,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    ed_startflame = FBEdit()
    ed_startflame.Text = "0"
    mainLyt.SetControl(name,ed_startflame)
    
    name = "jsonkeymultiply"
    x = FBAddRegionParam(20,FBAttachType.kFBAttachRight,"theflame")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label_eyebrowname")
    w = FBAddRegionParam(65,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    lb = FBLabel()
    lb.Caption = "key multiply :"
    mainLyt.SetControl(name,lb)   
    
    name = "jsonkeymultiplication"
    x = FBAddRegionParam(20,FBAttachType.kFBAttachRight,"jsonkeymultiply")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label_eyebrowname")
    w = FBAddRegionParam(60,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    ed_mp = FBEdit()
    ed_mp.Text = "1"
    mainLyt.SetControl(name,ed_mp)
    
    # insert tab control
    
    tab = FBTabControl()
    
    x = FBAddRegionParam(10,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"startflame")
    w = FBAddRegionParam(-10,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(-10,FBAttachType.kFBAttachBottom,"")
    tab = FBTabControl()
    mainLyt.AddRegion("tab", "tab",x,y,w,h)
    mainLyt.SetControl("tab", tab)

    
 # Create dummy layout that will be "tabbable"
 #tab 1   

    l = FBLayout()    
    name = "mouth animation"        
    x = FBAddRegionParam(1,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(1,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(-1,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(-1,FBAttachType.kFBAttachBottom,"")
    l.AddRegion(name,name, x, y, w, h)
    # each layout will have a visible border
    l.SetBorder(name,FBBorderStyle.kFBStandardBorder,False, True,1,0,90,0)
    
    tab.Add(name,l)
    
    b = FBButton()
    name = "selectpath"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(15,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(95,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    b.OnClick.Add(OpenJsonFile)
    b.Caption="select .json file"
    l.SetControl(name,b) 
 
    b = FBButton()
    name = "importjson"
    x = FBAddRegionParam(-120,FBAttachType.kFBAttachRight,"")
    y = FBAddRegionParam(-40,FBAttachType.kFBAttachBottom,"")
    w = FBAddRegionParam(100,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    b.Caption="import .json"
    b.OnClick.Add(setBSkey)
    l.SetControl(name,b)
    
    name = "Label_.josn_path"
    x = FBAddRegionParam(-55,FBAttachType.kFBAttachRight,"selectpath")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"selectpath")
    w = FBAddRegionParam(55,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    lb = FBLabel()
    lb.Caption = "json path : "
    l.SetControl(name,lb)   
    
    name = "thepath"
    x = FBAddRegionParam(15,FBAttachType.kFBAttachRight,"selectpath")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"selectpath")
    w = FBAddRegionParam(-20,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    ed_Jpath = FBEdit()
    ed_Jpath.Text = ""
    l.SetControl(name,ed_Jpath)
    
    name = ".josnfileflamelengthis"
    x = FBAddRegionParam(-55,FBAttachType.kFBAttachRight,"Label_.josn_path")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label_.josn_path")
    w = FBAddRegionParam(200,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    jsonflamedata_lb = FBLabel()
    jsonflamedata_lb.Caption = ".josn file flame length is : no data read" 
    l.SetControl(name,jsonflamedata_lb)   
    
    name = "loadflamelength"
    x = FBAddRegionParam(0,FBAttachType.kFBAttachLeft,".josnfileflamelengthis")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,".josnfileflamelengthis")
    w = FBAddRegionParam(190,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    loadflamelength_lb = FBLabel()
    loadflamelength_lb.Caption = "stop import at(none for import all) : " 
    l.SetControl(name,loadflamelength_lb)
    
    name = "mouthjsonflamelength"
    x = FBAddRegionParam(0,FBAttachType.kFBAttachRight,"loadflamelength")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,".josnfileflamelengthis")
    w = FBAddRegionParam(70,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    ed_mouthjsonflamelength = FBEdit()
    ed_mouthjsonflamelength.Text = ""
    l.SetControl(name,ed_mouthjsonflamelength)
    
    
 #tab 2 
    name = "mouth pose" 
    l = FBLayout()    
            
    x = FBAddRegionParam(1,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(1,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(-1,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(-1,FBAttachType.kFBAttachBottom,"")
    l.AddRegion(name,name, x, y, w, h)
    # each layout will have a visible border
    l.SetBorder(name,FBBorderStyle.kFBStandardBorder,False, True,1,0,90,0)
    
    tab.Add(name,l)
    
    b = FBButton()
    name = "setmouthposebt"
    x = FBAddRegionParam(-120,FBAttachType.kFBAttachRight,"")
    y = FBAddRegionParam(-40,FBAttachType.kFBAttachBottom,"")
    w = FBAddRegionParam(100,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    b.Caption="set mouth pose"
    b.OnClick.Add(setBSkey)
    l.SetControl(name,b) 
    
    name = "mouthposelist"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(100,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(50,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)

    lyt = FBVBoxLayout()
    l.SetControl(name,lyt)
    
    # List creation
    listtab_1 = FBList()
    listtab_1.OnChange.Add(ListCallback)
    for i in mouthposes:
        listtab_1.Items.append(i)
    
    listtab_1.Style = FBListStyle.kFBDropDownList
    lyt.Add(listtab_1, 25)
    listtab_1.Selected(0, True)
    
    name = "selectmouth pose"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachRight,"mouthposelist")
    y = FBAddRegionParam(15,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(100,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    lb = FBLabel()
    lb.Caption = "select mouth pose"
    l.SetControl(name,lb)      
 #tab3    
    name = "eyebrow pose" 
    l = FBLayout()    
            
    x = FBAddRegionParam(1,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(1,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(-1,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(-1,FBAttachType.kFBAttachBottom,"")
    l.AddRegion(name,name, x, y, w, h)
    # each layout will have a visible border
    l.SetBorder(name,FBBorderStyle.kFBStandardBorder,False, True,1,0,90,0)
    
    tab.Add(name,l)
    
    
    
    b = FBButton()
    name = "seteyebrowpose"
    x = FBAddRegionParam(-120,FBAttachType.kFBAttachRight,"")
    y = FBAddRegionParam(-40,FBAttachType.kFBAttachBottom,"")
    w = FBAddRegionParam(100,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    b.Caption="set eyebrow pose"
    b.OnClick.Add(setBSkey)
    l.SetControl(name,b)    
        

    
    name = "eyebrowposelist"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(100,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(50,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)

    lyt = FBVBoxLayout()
    l.SetControl(name,lyt)
    
    # List creation
    listtab_2 = FBList()
    listtab_2.OnChange.Add(ListCallback2)
    for i in eyebrowposes:
        listtab_2.Items.append(i)
    
    listtab_2.Style = FBListStyle.kFBDropDownList
    lyt.Add(listtab_2, 25)
    listtab_2.Selected(0, True)
    
    name = "selectmouth pose"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachRight,"eyebrowposelist")
    y = FBAddRegionParam(15,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(-20,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    lb = FBLabel()
    lb.Caption = "select eyebrow pose, and select brow mesh"
    l.SetControl(name,lb) 
    

    
 #tab 4
    
    name = "eye pose" 
    l = FBLayout()    
            
    x = FBAddRegionParam(1,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(1,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(-1,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(-1,FBAttachType.kFBAttachBottom,"")
    l.AddRegion(name,name, x, y, w, h)
    # each layout will have a visible border
    l.SetBorder(name,FBBorderStyle.kFBStandardBorder,False, True,1,0,90,0)
    
    tab.Add(name,l)
    
    
    
    b = FBButton()
    name = "seteyepose"
    x = FBAddRegionParam(-120,FBAttachType.kFBAttachRight,"")
    y = FBAddRegionParam(-40,FBAttachType.kFBAttachBottom,"")
    w = FBAddRegionParam(100,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    b.Caption="set eye pose"
    b.OnClick.Add(setBSkey)
    l.SetControl(name,b)    
        

    
    name = "eyebrowposelist"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(100,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(50,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)

    lyt = FBVBoxLayout()
    l.SetControl(name,lyt)
    
    # List creation
    listtab_3 = FBList()
    listtab_3.OnChange.Add(ListCallback3)
    for i in eyeposes:
        listtab_3.Items.append(i)
    
    listtab_3.Style = FBListStyle.kFBDropDownList
    lyt.Add(listtab_3, 25)
    listtab_3.Selected(0, True)

    
    
    #set defuelt tab at 0
    tab.SetContent(0)
    tab.TabPanel.TabStyle = 0 # normal tabs
    
def CreateTool(*args):
    # Tool creation will serve as the hub for all other controls
    t = FBCreateUniqueTool("MB_CCFI_By_Jc.Q_v001")
    t.StartSizeX = 640
    t.StartSizeY = 340
    PopulateLayout(t)  
    ShowTool(t)
    print("tool create success")


CreateTool()