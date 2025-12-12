import json
import maya.cmds as mc
import maya.cmds as cmds



    
class MR_Window(object):

     
#constructor
    def __init__(self):
        self.window = "MR_Window"
        self.title = "Json Importer For BS46 0.0.1 by jc.Q"
        self.size = (400, 100)
        
        
        #delete old window is open
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)
        #creat new window
        self.window = cmds.window(self.window, title=self.title, widthHeight=self.size)
        
        cmds.columnLayout(adjustableColumn = True)
        
        cmds.text(self.title)
        cmds.separator(height=20)
        
        self.blendshapename = str(cmds.textFieldGrp( label="blendshape name:" , text = "A2F46"))
        self.pathname = str(cmds.textFieldGrp( label="A2F BS Json Path Name:" , text = r"K:\shenron\11_Users\Q\MB_FaceKey\Json\A2F\mouth_a2f\shenron_vs_ct00020"))
        self.filename = str(cmds.textFieldGrp( label="A2F BS Json File Name:" , text = "shenron_vs_ct00020_cut_00_Wilgrim"))
        self.startFlame = str(cmds.textFieldGrp( label="startFlame at:" , text = 0))  
            
        
        self.cubeCreatebtn = cmds.button(label="Import Json", command=self.printpathname)
       
        
        #display new window
        cmds.showWindow()
    #@staticmethod
    def printpathname(self,*args):   
        pathname = cmds.textFieldGrp(self.pathname, query=True, text=True)
        filename = cmds.textFieldGrp(self.filename, query=True, text=True)
        startFlame = cmds.textFieldGrp(self.startFlame, query=True, text=True)
        blendshapename = cmds.textFieldGrp(self.blendshapename, query=True, text=True)
        fullpath = pathname + "\\" + filename + ".json"
        print("path name is " + fullpath)
        
        with open (fullpath,"r") as f:
         facs_data = json.loads(f.read())
         facsNames = facs_data["facsNames"]
         numPoses = facs_data["numPoses"]
         numFrames = facs_data["numFrames"]
         weightMat = facs_data["weightMat"]
         startFlame = cmds.textFieldGrp(self.startFlame, query=True, text=True)
         startFlame = float(startFlame)
         #print(startFlame,type(startFlame))
         #startFlame = float(startFlame)
         
         bsnode = blendshapename
         for fr in range(numFrames) :
            for i in range(numPoses):
               mc.setKeyframe(bsnode+'.'+(facsNames[i]), v=weightMat[fr][i], t=fr + startFlame)
        
        
     

myWindow = MR_Window()