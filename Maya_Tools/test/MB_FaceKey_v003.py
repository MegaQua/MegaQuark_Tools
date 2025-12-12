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
A2FfacsNames = [
    "browLowerL",
    "browLowerR",
    "innerBrowRaiserL",
    "innerBrowRaiserR",
    "outerBrowRaiserL",
    "outerBrowRaiserR",
    "eyesLookLeft",
    "eyesLookRight",
    "eyesLookUp",
    "eyesLookDown",
    "eyesCloseL",
    "eyesCloseR",
    "eyesUpperLidRaiserL",
    "eyesUpperLidRaiserR",
    "squintL",
    "squintR",
    "cheekRaiserL",
    "cheekRaiserR",
    "cheekPuffL",
    "cheekPuffR",
    "noseWrinklerL",
    "noseWrinklerR",
    "jawDrop",
    "jawDropLipTowards",
    "jawThrust",
    "jawSlideLeft",
    "jawSlideRight",
    "mouthSlideLeft",
    "mouthSlideRight",
    "dimplerL",
    "dimplerR",
    "lipCornerPullerL",
    "lipCornerPullerR",
    "lipCornerDepressorL",
    "lipCornerDepressorR",
    "lipStretcherL",
    "lipStretcherR",
    "upperLipRaiserL",
    "upperLipRaiserR",
    "lowerLipDepressorL",
    "lowerLipDepressorR",
    "chinRaiser",
    "lipPressor",
    "pucker",
    "funneler",
    "lipSuck"
            ]
CC4facsNames= [
        "V_Open",
        "V_Explosive",
        "V_Dental_Lip",
        "V_Tight_O",
        "V_Tight",
        "V_Wide",
        "V_Affricate",
        "V_Lip_Open",
        "Brow_Raise_Inner_L",
        "Brow_Raise_Inner_R",
        "Brow_Raise_Outer_L",
        "Brow_Raise_Outer_R",
        "Brow_Drop_L",
        "Brow_Drop_R",
        "Brow_Compress_L",
        "Brow_Compress_R",
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
        "Ear_Up_L",
        "Ear_Up_R",
        "Ear_Down_L",
        "Ear_Down_R",
        "Ear_Out_L",
        "Ear_Out_R",
        "Nose_Sneer_L",
        "Nose_Sneer_R",
        "Nose_Nostril_Raise_L",
        "Nose_Nostril_Raise_R",
        "Nose_Nostril_Dilate_L",
        "Nose_Nostril_Dilate_R",
        "Nose_Crease_L",
        "Nose_Crease_R",
        "Nose_Nostril_Down_L",
        "Nose_Nostril_Down_R",
        "Nose_Nostril_In_L",
        "Nose_Nostril_In_R",
        "Nose_Tip_L",
        "Nose_Tip_R",
        "Nose_Tip_Up",
        "Nose_Tip_Down",
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
        "Head_Turn_Up",
        "Head_Turn_Down",
        "Head_Turn_L",
        "Head_Turn_R",
        "Head_Tilt_L",
        "Head_Tilt_R",
        "Head_L",
        "Head_R",
        "Head_Forward",
        "Head_Backward"
        ]
A2Ffilder = "A2F"
CC4filder = "CC4"
Josnpathmark = A2Ffilder
mouthposes_dict ={
    "default":"K:\\shenron\\11_Users\\Q\\MB_FaceKey\\Json\\"+Josnpathmark+"\\mouth_poses\\"+Josnpathmark+"_default.json",
    "a":"K:\\shenron\\11_Users\\Q\\MB_FaceKey\\Json\\"+Josnpathmark+"\\mouth_poses\\"+Josnpathmark+"_mouthpose_a.json",
    "i":"K:\\shenron\\11_Users\\Q\\MB_FaceKey\\Json\\"+Josnpathmark+"\\mouth_poses\\"+Josnpathmark+"_mouthpose_i.json",
    "u":"K:\\shenron\\11_Users\\Q\\MB_FaceKey\\Json\\"+Josnpathmark+"\\mouth_poses\\"+Josnpathmark+"_mouthpose_u.json",
    "e":"K:\\shenron\\11_Users\\Q\\MB_FaceKey\\Json\\"+Josnpathmark+"\\mouth_poses\\"+Josnpathmark+"_mouthpose_e.json",
    "o":"K:\\shenron\\11_Users\\Q\\MB_FaceKey\\Json\\"+Josnpathmark+"\\mouth_poses\\"+Josnpathmark+"_mouthpose_o.json"
}
setcharlist=["None","pfc0000_00","mob0010_00"]
mouthposes = []
for key in mouthposes_dict:
    mouthposes.append(key)
#print (mouthposes)
eyebrowposes_dict={
    "default":"K:\\shenron\\11_Users\\Q\\MB_FaceKey\\Json\\"+Josnpathmark+"\\eyebrow_poses\\"+Josnpathmark+"_default.json",
    "angry":"K:\\shenron\\11_Users\\Q\\MB_FaceKey\\Json\\"+Josnpathmark+"\\eyebrow_poses\\"+Josnpathmark+"_angry.json",
    "happy":"K:\\shenron\\11_Users\\Q\\MB_FaceKey\\Json\\"+Josnpathmark+"\\eyebrow_poses\\"+Josnpathmark+"_happy.json",
    "sad":"K:\\shenron\\11_Users\\Q\\MB_FaceKey\\Json\\"+Josnpathmark+"\\eyebrow_poses\\"+Josnpathmark+"_sad.json",
    "surprise":"K:\\shenron\\11_Users\\Q\\MB_FaceKey\\Json\\"+Josnpathmark+"\\eyebrow_poses\\"+Josnpathmark+"_surprise.json",
    "pain":"K:\\shenron\\11_Users\\Q\\MB_FaceKey\\Json\\"+Josnpathmark+"\\eyebrow_poses\\"+Josnpathmark+"_pain.json"
}

eyebrowposes = []
for key in eyebrowposes_dict:
    eyebrowposes.append(key)
eyeposes_dict ={
    "default":"K:\\shenron\\11_Users\\Q\\MB_FaceKey\\Json\\"+Josnpathmark+"\\eye_poses\\"+Josnpathmark+"_default.json",
    "close":"K:\\shenron\\11_Users\\Q\\MB_FaceKey\\Json\\"+Josnpathmark+"\\eye_poses\\"+Josnpathmark+"_close.json"
}
eyeposes = []
for key in eyeposes_dict:
    eyeposes.append(key)
    
CC4mouthshapes = [
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
A2Fmouthshapes = [
    "cheekRaiserL",
    "cheekRaiserR",
    "cheekPuffL",
    "cheekPuffR",
    "noseWrinklerL",
    "noseWrinklerR",
    "jawDrop",
    "jawDropLipTowards",
    "jawThrust",
    "jawSlideLeft",
    "jawSlideRight",
    "mouthSlideLeft",
    "mouthSlideRight",
    "dimplerL",
    "dimplerR",
    "lipCornerPullerL",
    "lipCornerPullerR",
    "lipCornerDepressorL",
    "lipCornerDepressorR",
    "lipStretcherL",
    "lipStretcherR",
    "upperLipRaiserL",
    "upperLipRaiserR",
    "lowerLipDepressorL",
    "lowerLipDepressorR",
    "chinRaiser",
    "lipPressor",
    "pucker",
    "funneler",
    "lipSuck"
    ]
A2Feyebrowshapes= [
    "browLowerL",
    "browLowerR",
    "innerBrowRaiserL",
    "innerBrowRaiserR",
    "outerBrowRaiserL",
    "outerBrowRaiserR",
]

CC4eyebrowshapes= [
        "Brow_Raise_Inner_L",
        "Brow_Raise_Inner_R",
        "Brow_Raise_Outer_L",
        "Brow_Raise_Outer_R",
        "Brow_Drop_L",
        "Brow_Drop_R",
        "Brow_Compress_L",
        "Brow_Compress_R",
]
A2Feyeshapes= [
    "eyesLookLeft",
    "eyesLookRight",
    "eyesLookUp",
    "eyesLookDown",
    "eyesCloseL",
    "eyesCloseR",
    "eyesUpperLidRaiserL",
    "eyesUpperLidRaiserR",
    "squintL",
    "squintR",
]

CC4eyeshapes= [
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
mouthshapes = A2Fmouthshapes
eyebrowshapes = A2Feyebrowshapes
eyeshapes = A2Feyeshapes
jsontype = ""


pngnamegp =[
    "Neutral_",
    "00_Neutral",
    "01_browLowerL",
    "02_browLowerR",
    "03_innerBrowRaiserL",
    "04_innerBrowRaiserR",
    "05_outerBrowRaiserL",
    "06_outerBrowRaiserR",
    "07_eyesLookLeft",
    "08_eyesLookRight",
    "09_eyesLookUp",
    "10_eyesLookDown",
    "11_eyesCloseL",
    "12_eyesCloseR",
    "13_eyesUpperLidRaiserL",
    "14_eyesUpperLidRaiserR",
    "15_squintL",
    "16_squintR",
    "17_cheekRaiserL",
    "18_cheekRaiserR",
    "19_cheekPuffL",
    "20_cheekPuffR",
    "21_noseWrinklerL",
    "22_noseWrinklerR",
    "23_jawDrop",
    "24_jawDropLipTowards",
    "25_jawThrust",
    "26_jawSlideLeft",
    "27_jawSlideRight",
    "28_mouthSlideLeft",
    "29_mouthSlideRight",
    "30_dimplerL",
    "31_dimplerR",
    "32_lipCornerPullerL",
    "33_lipCornerPullerR",
    "34_lipCornerDepressorL",
    "35_lipCornerDepressorR",
    "36_lipStretcherL",
    "37_lipStretcherR",
    "38_upperLipRaiserL",
    "39_upperLipRaiserR",
    "40_lowerLipDepressorL",
    "41_lowerLipDepressorR",
    "42_chinRaiser",
    "43_lipPressor",
    "44_pucker",
    "45_funneler",
    "46_lipSuck",
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
        # Create the popup and set the necessary initial values
        filePopup = pyfbsdk.FBFilePopup()
        filePopup.Caption = 'select .json file'
        #filePopup.Style = pyfbsdk.FBFilePopupStyle.kFBFilePopupOpen
        filePopup.Filter = '*.json'

        #Set the default path (assuming we use windows operating system)
        filePopup.Path = "K:\\shenron\\11_Users\\Q\\MB_FaceKey\\Json\\A2F\\mouth_a2f"
        # Let the GUI show up
        bResult = filePopup.Execute()
        if bResult:
            self.modelFileEdit = filePopup.FullFilename
            ed_Jpath.Text  = filePopup.FullFilename
            ed_Jpathfullface.Text  = filePopup.FullFilename
            print ("the path is " + ed_Jpath.Text)
            #change dataframe lb
            with open (ed_Jpath.Text) as f:
                facs_data = json.loads(f.read())
                jsonframedata = str(facs_data["numFrames"])
                jsonframedata_lb.Caption = ".josn file frame length is : " + jsonframedata
                jsonframedatafullface_lb.Caption = ".josn file frame length is : " + jsonframedata

    def GetLastSelectetdModels():
        selectedModels = FBModelList()
        FBGetSelectedModels(selectedModels, None, True, True)
        return selectedModels[-1] if selectedModels else None
    
    def SetNameSpace(self,*args):
        ed_face_namespace.Text = ed_namespace.Text 
        ed_teeth_namespace.Text = ed_namespace.Text 
        ed_jawjoint_namespace.Text = ed_namespace.Text 
        
        print("Set Name Space Done")

    def CharListSelected(control, event):
        charname = control.Items[control.ItemIndex]
        if charname == "pfc0000_00":
            ed_face_namespace.Text = "pfc0000_00"
            ed_teeth_namespace.Text = "pfc0000_00"
            ed_jawjoint_namespace.Text = ""
            ed_facename.Text = "head_lod0"
            ed_teethname.Text = "mouth_lod0"
            ed_jawjoint_namespace.Text = ""
        elif charname == "mob0010_00":
            ed_face_namespace.Text = "mob0010_00"
            ed_teeth_namespace.Text = "mob0010_00"
            ed_jawjoint_namespace.Text = ""
            ed_facename.Text = "head_lod0"
            ed_teethname.Text = "teeth_lod0"
            ed_jawjoint_namespace.Text = ""
        elif charname == "None":
            ed_face_namespace.Text = ""
            ed_teeth_namespace.Text = ""
            ed_jawjoint_namespace.Text = ""
            ed_facename.Text = ""
            ed_teethname.Text = ""
            ed_jawjoint_namespace.Text = ""           
        else: 
            pass



    def setBSkey(self,*args):
        importjsonpath = ed_Jpath.Text
        #get bottom name
        bottom_name = self.Caption
        #print (self.Caption, " has been clicked!")
        global mouthshapes
        global eyebrowshapes
        global eyeshapes
        global pngnamegp
        #jug1 mouth
        if bottom_name == "import .json"or bottom_name == "set mouth pose":
            if bottom_name == "import .json":
                print (self.Caption, " has been clicked!,import a2f mouth animation")
                if importjsonpath == "":
                    print("no path")
                    return
            else :
                importjsonpath = mouthposes_dict[listtab_1.Items[listtab_1.ItemIndex]]
                print (self.Caption, " has been clicked!,set mouth pose in path "+importjsonpath)
                
            TargerShapes = mouthshapes
        #jug2 eyebrow
        elif bottom_name == "set eyebrow pose":
            importjsonpath = eyebrowposes_dict[listtab_2.Items[listtab_2.ItemIndex]]
            print (self.Caption, " has been clicked!,set mouth pose in path "+importjsonpath)
            TargerShapes = eyebrowshapes
        #jug3 eye
        elif bottom_name == "set eye pose":
            importjsonpath = eyeposes_dict[listtab_3.Items[listtab_3.ItemIndex]]
            print (self.Caption, " has been clicked!,set eye pose in path "+importjsonpath)
            TargerShapes = eyeshapes
        #jug4 shapes
        elif bottom_name in pngnamegp:
            TargerShapes = [bottom_name[3:]]
            print(self.Caption, " has been clicked!,set key on pose "+bottom_name[3:])
            importjsonpath = r"K:\shenron\11_Users\Q\MB_FaceKey\Json\A2F\others\all_1.json"
            ed_mp.Text = ed_shapesmultiply.Text
            ed_startframe.Text = ed_shapesframe.Text
        #jug5 fullface
        elif bottom_name == "import fullface .json":
            print (self.Caption, " has been clicked!,import a2f fullface animation")
            
            TargerShapes = A2FfacsNames

            
            
        #others    
        else:
            print (self.Caption, " has been clicked!,but not finished")
            return
        #print("import json to set mouth blendshapes key")
        setkeytimes = 0
        
        with open (importjsonpath) as f:
            startframe = ed_startframe.Text
            keyMp = ed_mp.Text
            
            facs_data = json.loads(f.read())
            facsNames = facs_data["facsNames"]
            numPoses = facs_data["numPoses"]
            numFrames = facs_data["numFrames"]
            weightMat = facs_data["weightMat"]
            selectM = GetLastSelectetdModels()
            global jsontype
            #judge face type
            """
            if facsNames == CC4facsNames :
                print("json type CC4")
                jsontype = "CC4"
                mouthshapes = CC4mouthshapes
                eyebrowshapes = CC4eyebrowshapes
                eyeshapes = CC4eyeshapes
            elif  facsNames == A2FfacsNames :
                print("json type A2F")
                jsontype = "A2F"
                mouthshapes = A2Fmouthshapes
                eyebrowshapes = A2Feyebrowshapes
                eyeshapes = A2Feyeshapes
            else:
                print("unknow type json")
                return  
            """    
                
            #set mesh list namespace
            if ed_face_namespace.Text ==  "":
                namespace = ""
            else :
                namespace =ed_face_namespace.Text+":"
            Face = FBFindModelByLabelName(namespace+ed_facename.Text)
            
            if ed_teeth_namespace.Text ==  "":
                namespace = ""
            else :
                namespace =ed_teeth_namespace.Text+":"
            Teeth = FBFindModelByLabelName(namespace+ed_teethname.Text)
            
            if ed_jawjoint_namespace.Text ==  "":
                namespace = ""
            else :
                namespace =ed_jawjoint_namespace.Text+":"
            Jaw = FBFindModelByLabelName(namespace+ed_jawjointname.Text)

            meshlist = (
                Jaw,
                Face,
                Teeth,
            )
            meshcount = int(len(meshlist))
            
            #set frame length
            if ed_mouthjsonframelength.Text != "":
                print(ed_mouthjsonframelength.Text)
           
                if int(ed_mouthjsonframelength.Text) != "" and int(ed_mouthjsonframelength.Text) >=  int(ed_startframe.Text)  and  numFrames > int(ed_mouthjsonframelength.Text) - int(ed_startframe.Text)+1:
                    numFrames = int(ed_mouthjsonframelength.Text) - int(ed_startframe.Text) + 1
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
                            selectM.PropertyList.Find(str(facsNames[i])).GetAnimationNode().FCurve.KeyAdd(FBTime(0, 0, 0,fr+int(startframe)), weightMat[fr][i]*100*float(keyMp))
                            setkeytimes = setkeytimes +1
                            if facsNames[i] == "Mouth_Down" :
                                selectM.PropertyList.Find(str(facsNames[i])).SetAnimated(True)
                                selectM.PropertyList.Find(str(facsNames[i])).GetAnimationNode().FCurve.KeyAdd(FBTime(0, 0, 0,fr+int(startframe)), weightMat[fr][i]*30*float(keyMp))
                                setkeytimes = setkeytimes +1

                            if facsNames[i] == "Mouth_Down_Lower_L" :
                                selectM.PropertyList.Find(str(facsNames[i])).SetAnimated(True)
                                selectM.PropertyList.Find(str(facsNames[i])).GetAnimationNode().FCurve.KeyAdd(FBTime(0, 0, 0,fr+int(startframe)), weightMat[fr][i]*30*float(keyMp))
                                setkeytimes = setkeytimes +1

                            if facsNames[i] == "Mouth_Down_Lower_R" :
                                selectM.PropertyList.Find(str(facsNames[i])).SetAnimated(True)
                                selectM.PropertyList.Find(str(facsNames[i])).GetAnimationNode().FCurve.KeyAdd(FBTime(0, 0, 0,fr+int(startframe)), weightMat[fr][i]*30*float(keyMp))
                                setkeytimes = setkeytimes +1
            else:
                print("key for name")
                nousemeshcount = 0
                for i in range (meshcount):
                    if  meshlist[i] is not None:
                        print(" "+str(meshlist[i].Name))
                    else :
                        nousemeshcount = nousemeshcount +1
                print("can'find "+str(nousemeshcount)+" meshes")
                print(str(meshcount-nousemeshcount)+" meshes selected")
                        
                #key namespace from Json
                #setting special int                
                #jugg if there is target shapes in faceNames
                for i in range(numPoses):
                    if  facsNames[i] in TargerShapes:
                        for j in range(meshcount):
                            if meshlist[j] is not None :
                                if  meshlist[j].PropertyList.Find(str(facsNames[i])) is not None:
                                    meshlist[j].PropertyList.Find(str(facsNames[i])).SetAnimated(True)
                                    #print(str(meshlist[j].Name)+" Fcurve set ")
                                else:
                                    #print(str(meshlist[j].Name)+" dont have "+str(facsNames[i])+" pass ")   
                                    pass  
                            else:
                                pass
                for fr in range(numFrames) :
                    for i in range(numPoses):
                        if  facsNames[i] in TargerShapes:
                            for j in range(meshcount):
                                if meshlist[j] is not None :
                                    if  meshlist[j].PropertyList.Find(str(facsNames[i])) is not None:
                                        meshlist[j].PropertyList.Find(str(facsNames[i])).GetAnimationNode().FCurve.KeyAdd(FBTime(0, 0, 0,fr+int(startframe)), weightMat[fr][i]*100*float(keyMp))
                                        setkeytimes = setkeytimes +1
                                else:
                                    pass
            
            onetimetime = FBTime(0,0,0,int(ed_startframe.Text),0)
            twotimetime = FBTime(0,0,0,int(ed_startframe.Text)+1,0)
            FBPlayerControl().Goto(twotimetime)
            FBPlayerControl().Goto(onetimetime)
            print ("Done, set key "+str(setkeytimes)+" times")
    #Shape Controll box
    def ShapeConLayout(ShapeConLyt):
        def GetSystemTime(*args):
            systime = FBSystem().LocalTime.GetFrame()
            ed_startframe.Text = str(systime)
            ed_shapesframe.Text = str(systime)

        x = FBAddRegionParam(0,FBAttachType.kFBAttachLeft,"")
        y = FBAddRegionParam(0,FBAttachType.kFBAttachTop,"")
        w = FBAddRegionParam(0,FBAttachType.kFBAttachRight,"")
        h = FBAddRegionParam(0,FBAttachType.kFBAttachBottom,"")
        ShapeConLyt.AddRegion("main","main", x, y, w, h)
        
        # create a scrollbox and set it as the main control in our tool
        scroll = FBScrollBox()
        ShapeConLyt.SetControl("main",scroll)
        # Content property is the scrollbox's layout: create a region in it
        scroll.Content.AddRegion( "content", "content", x, y, w, h )
        
        Glyt = FBGridLayout()
        Glyt.SetRowHeight(0, 40)
        for i in [2,4,6,8]:
            Glyt.SetRowHeight(i,40 )
            Glyt.SetRowHeight(i-1,128)
        # set our layout as the content of the scrollbox
        scroll.Content.SetControl("content", Glyt)
        
        # init the scrollbox content size. We will be able to scroll on this size.
        scroll.SetContentSize(1600, 750)

        # populate our grid with dummy buttons
        lb = FBLabel()
        lb.Caption = "Set Key frame start at"
        Glyt.Add(lb, 0, 1)
        
        #set at 824
        Glyt.Add(ed_shapesframe, 0, 2)
        
        b = FBButton()
        b.Caption = "get time slide frame"
        Glyt.Add(b, 0, 3)
        b.OnClick.Add(GetSystemTime)
        
        lb = FBLabel()
        lb.Caption = "key influence"
        Glyt.Add(lb, 0, 5)
        
        b = FBButton()
        
        #set at 822
        Glyt.Add(ed_shapesmultiply, 0, 7)
        
        Glyt.Add(hs,0,6)

        
        
        k = 0
        for i in range(4):
            for j in range(12):
                img = FBImageContainer()
                img.Filename = "K:\\shenron\\11_Users\\Q\MB_FaceKey\\png\\shenronply0000\\%s"%pngnamegp[k]+".png"
                b = FBButton()
                b.OnClick.Add(setBSkey)
                b.Caption=pngnamegp[k]
                k=k+1
                if i==0 and j==0 :
                    pass
                elif i == 0 and j == 1:
                    pass
                else:
                    Glyt.Add(img, 2*i+1, j)
                    Glyt.Add(b, 2*i+2, j,height=35)
            
    def frameonchange(self,*args):
        awsl = self.Text
        if awsl.isdigit():
            onetimetime = FBTime(0,0,0,int(awsl),0)
            FBPlayerControl().Goto(onetimetime)   
        else:
            pass


    def CreateSCTool(*args):
        # Tool creation will serve as the hub for all other controls
        t2 = FBCreateUniqueTool("Shape controller")
        t2.StartSizeX = 1650
        t2.StartSizeY = 800
        ShapeConLayout(t2)    
        ShowTool(t2)
        print("tool create Shape controller success")
    
    def GetSystemTime(*args):
        systime = FBSystem().LocalTime.GetFrame()
        ed_startframe.Text = str(systime)
        #ed_shapesframe.Text = str(systime)
    #for t2 window  
    def setsmultiplyvalue(self,*args):
        #print(hs.Value)
        hsv=self.Value
        ed_mp.Text = str("%.2f" % hsv)
        ed_shapesmultiply.Text = str("%.2f" % hsv)
         
    ed_shapesmultiply = FBEdit()
    ed_shapesmultiply.Text = "1"
    ed_shapesframe = FBEdit()
    ed_shapesframe.Text = "0" 
    ed_shapesframe.OnChange.Add(frameonchange) 
    
    hs = FBSlider()    
    hs.Orientation = FBOrientation.kFBHorizontal   
    hs.SmallStep = 10
    hs.LargeStep = 10 
    hs.OnChange.Add(setsmultiplyvalue)
    #hs.OnTransaction.Add(Transaction)


 #ui element
    name = "selectobj"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(100,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    lb = FBLabel()
    lb.Caption = "select target , or "
    mainLyt.SetControl(name,lb)  

    name = "charlist"
    x = FBAddRegionParam(-120,FBAttachType.kFBAttachRight,"")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(100,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)

    charlist = FBList()
    #charlist.OnChange.Add(ListCallback)
    for i in setcharlist:
        charlist.Items.append(i)
    
    charlist.Style = FBListStyle.kFBDropDownList
    charlist.OnChange.Add(CharListSelected)
    mainLyt.SetControl(name,charlist)
    charlist.Selected(0, True)

    
    name = "typeinnamespace"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"selectobj")
    w = FBAddRegionParam(100,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    lb = FBLabel()
    lb.Caption = "type in namespace :"
    mainLyt.SetControl(name,lb)  
    
    name = "namespace"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachRight,"typeinnamespace")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"selectobj")
    w = FBAddRegionParam(150,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    ed_namespace = FBEdit()
    ed_namespace.Text = ""
    mainLyt.SetControl(name,ed_namespace) 

    b = FBButton()
    name = "SetNameSpace"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachRight,"namespace")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"selectobj")
    w = FBAddRegionParam(200,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    b.OnClick.Add(SetNameSpace)
    b.Caption="Set Name Space"
    mainLyt.SetControl(name,b)
       
    #line 2
    name = "Label_facename"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"typeinnamespace")
    w = FBAddRegionParam(100,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    lb = FBLabel()
    lb.Caption = "face name : "
    mainLyt.SetControl(name,lb)  
    
    name = "facenamespace"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachRight,"Label_facename")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"typeinnamespace")
    w = FBAddRegionParam(150,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    ed_face_namespace = FBEdit()
    ed_face_namespace.Text =  ""
    mainLyt.SetControl(name,ed_face_namespace) 
 
    
    name = "facename"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachRight,"facenamespace")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"typeinnamespace")
    w = FBAddRegionParam(-20,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    ed_facename = FBEdit()
    ed_facename.Text = ""
    mainLyt.SetControl(name,ed_facename)
    #  
    name = "Label_teethname"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label_facename")
    w = FBAddRegionParam(100,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    lb = FBLabel()
    lb.Caption = "teeth name : "
    mainLyt.SetControl(name,lb) 
    
    name = "teethnamespace"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachRight,"Label_teethname")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label_facename")
    w = FBAddRegionParam(150,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    ed_teeth_namespace = FBEdit()
    ed_teeth_namespace.Text = ""
    mainLyt.SetControl(name,ed_teeth_namespace) 

    
    name = "teethname"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachRight,"teethnamespace")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label_facename")
    w = FBAddRegionParam(-20,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    ed_teethname = FBEdit()
    ed_teethname.Text = ""
    mainLyt.SetControl(name,ed_teethname)   
    #
    name = "Label_jawjointname"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"teethname")
    w = FBAddRegionParam(100,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    lb = FBLabel()
    lb.Caption = "jaw name : "
    mainLyt.SetControl(name,lb) 
    
    name = "jawjointnamespace"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachRight,"Label_jawjointname")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"teethname")
    w = FBAddRegionParam(150,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    ed_jawjoint_namespace = FBEdit()
    ed_jawjoint_namespace.Text = ""
    mainLyt.SetControl(name,ed_jawjoint_namespace) 
  
    
    name = "jawjointname"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachRight,"jawjointnamespace")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"teethname")
    w = FBAddRegionParam(-20,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    ed_jawjointname = FBEdit()
    ed_jawjointname.Text = ""
    mainLyt.SetControl(name,ed_jawjointname)   

        
    name = "startframe"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label_jawjointname")
    w = FBAddRegionParam(100,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    lb = FBLabel()
    lb.Caption = "Set Key frame start at :"
    mainLyt.SetControl(name,lb)   
    
    name = "theframe"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachRight,"startframe")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label_jawjointname")
    w = FBAddRegionParam(60,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    ed_startframe = FBEdit()
    ed_startframe.Text = "0"
    ed_startframe.OnChange.Add(frameonchange)
    mainLyt.SetControl(name,ed_startframe)
    
    b = FBButton()
    name = "B_GetSystemTime"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachRight,"theframe")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label_jawjointname")
    w = FBAddRegionParam(150,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    b.OnClick.Add(GetSystemTime)
    b.Caption="get time slide frame"
    mainLyt.SetControl(name,b)
    
    name = "jsonkeymultiply"
    x = FBAddRegionParam(40,FBAttachType.kFBAttachRight,"B_GetSystemTime")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label_jawjointname")
    w = FBAddRegionParam(70,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    lb = FBLabel()
    lb.Caption = "key influence :"
    mainLyt.SetControl(name,lb)   
    
    name = "jsonkeymultiplication"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachRight,"jsonkeymultiply")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label_jawjointname")
    w = FBAddRegionParam(60,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    ed_mp = FBEdit()
    ed_mp.Text = "1"
    mainLyt.SetControl(name,ed_mp)
    
    name = "hs"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachRight,"jsonkeymultiplication")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label_jawjointname")
    w = FBAddRegionParam(-20,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    hs0 = FBSlider()
    hs0.Orientation = FBOrientation.kFBHorizontal   
    hs0.SmallStep = 10
    hs0.LargeStep = 10 
    hs0.OnChange.Add(setsmultiplyvalue)
  
    mainLyt.AddRegion(name,name, x, y, w, h)
    mainLyt.SetControl(name,hs0)
    
    # insert tab control
    
    tab = FBTabControl()
    
    x = FBAddRegionParam(10,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"startframe")
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
    x = FBAddRegionParam(5,FBAttachType.kFBAttachLeft,"")
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
    x = FBAddRegionParam(10,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"selectpath")
    w = FBAddRegionParam(55,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    lb = FBLabel()
    lb.Caption = "json path : "
    l.SetControl(name,lb)   
    
    name = "thepath"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachRight,"Label_.josn_path")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"selectpath")
    w = FBAddRegionParam(-20,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    ed_Jpath = FBEdit()
    ed_Jpath.Text = ""
    l.SetControl(name,ed_Jpath)
    
    name = ".josnfileframelengthis"
    x = FBAddRegionParam(-55,FBAttachType.kFBAttachRight,"Label_.josn_path")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label_.josn_path")
    w = FBAddRegionParam(200,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    jsonframedata_lb = FBLabel()
    jsonframedata_lb.Caption = ".josn file frame length is : no data read" 
    l.SetControl(name,jsonframedata_lb)   
    
    name = "loadframelength"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,".josnfileframelengthis")
    w = FBAddRegionParam(190,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    loadframelength_lb = FBLabel()
    loadframelength_lb.Caption = "stop import at(none for import all) : " 
    l.SetControl(name,loadframelength_lb)
    
    name = "mouthjsonframelength"
    x = FBAddRegionParam(0,FBAttachType.kFBAttachRight,"loadframelength")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,".josnfileframelengthis")
    w = FBAddRegionParam(70,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    ed_mouthjsonframelength = FBEdit()
    ed_mouthjsonframelength.Text = ""
    l.SetControl(name,ed_mouthjsonframelength)
    
 #tab 1.5 
    name = "Shape Crl" 
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
    x = FBAddRegionParam(-160,FBAttachType.kFBAttachRight,"")
    y = FBAddRegionParam(-40,FBAttachType.kFBAttachBottom,"")
    w = FBAddRegionParam(150,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    b.Caption="open Shape controller"
    b.OnClick.Add(CreateSCTool)
    l.SetControl(name,b) 
  
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
    lb.Caption = "select eyebrow pose"
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

    
    


 #tab 5   

    l = FBLayout()    
    name = "full face animation"        
    x = FBAddRegionParam(1,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(1,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(-1,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(-1,FBAttachType.kFBAttachBottom,"")
    l.AddRegion(name,name, x, y, w, h)
    # each layout will have a visible border
    l.SetBorder(name,FBBorderStyle.kFBStandardBorder,False, True,1,0,90,0)
    
    tab.Add(name,l)
    
    b = FBButton()
    name = "selectpathfullface"
    x = FBAddRegionParam(5,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(15,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(95,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    b.OnClick.Add(OpenJsonFile)
    b.Caption="select .json file"
    l.SetControl(name,b) 
 
    b = FBButton()
    name = "importjsonfullface"
    x = FBAddRegionParam(-180,FBAttachType.kFBAttachRight,"")
    y = FBAddRegionParam(-40,FBAttachType.kFBAttachBottom,"")
    w = FBAddRegionParam(160,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    b.Caption="import fullface .json"
    b.OnClick.Add(setBSkey)
    l.SetControl(name,b)
    
    name = "Label_.josn_pathfullface"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"selectpathfullface")
    w = FBAddRegionParam(55,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    lb = FBLabel()
    lb.Caption = "json path : "
    l.SetControl(name,lb)   
    
    name = "thepathfullface"
    x = FBAddRegionParam(15,FBAttachType.kFBAttachRight,"Label_.josn_pathfullface")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"selectpathfullface")
    w = FBAddRegionParam(-20,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    ed_Jpathfullface = FBEdit()
    ed_Jpathfullface.Text = ""
    l.SetControl(name,ed_Jpathfullface)
    
    name = ".josnfileframelengthis"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label_.josn_pathfullface")
    w = FBAddRegionParam(200,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    jsonframedatafullface_lb = FBLabel()
    jsonframedatafullface_lb.Caption = ".josn file frame length is : no data read" 
    l.SetControl(name,jsonframedatafullface_lb)   
    
    name = "loadframelengthfullface"
    x = FBAddRegionParam(0,FBAttachType.kFBAttachLeft,".josnfileframelengthis")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,".josnfileframelengthis")
    w = FBAddRegionParam(190,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    loadframelengthfullface_lb = FBLabel()
    loadframelengthfullface_lb.Caption = "stop import at(none for import all) : " 
    l.SetControl(name,loadframelengthfullface_lb)
    
    name = "mouthjsonframelength"
    x = FBAddRegionParam(0,FBAttachType.kFBAttachRight,"loadframelengthfullface")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,".josnfileframelengthis")
    w = FBAddRegionParam(70,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    l.AddRegion(name,name, x, y, w, h)
    ed_mouthjsonframelength = FBEdit()
    ed_mouthjsonframelength.Text = ""
    l.SetControl(name,ed_mouthjsonframelength)

    #set defuelt tab at 0
    tab.SetContent(0)
    tab.TabPanel.TabStyle = 0 # normal tabs



   
def CreateTool(*args):
    # Tool creation will serve as the hub for all other controls
    t = FBCreateUniqueTool("MB_FaceKey_By_Jc.Q_v002")
    t.StartSizeX = 640
    t.StartSizeY = 440
    PopulateLayout(t)  
    ShowTool(t)
    print("tool create success")


CreateTool()