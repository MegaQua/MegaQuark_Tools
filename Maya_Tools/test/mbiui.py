from pyfbsdk import *
from pyfbsdk_additions import *

mouthposes = [
    "default",
    "a",
    "i",
    "u",
    "e",
    "o"
]  
eyebrowposes = [
    "default",
    "angry",
    "happy",
    "sad",
    "surprise",
    "pain"
]  
eyeposes = [
    "default",
    "close"
]  


def ListCallback(control, event):
    #print control.Items[control.ItemIndex], "has been selected!"
    print("selected")

    
def PopulateLayout(mainLyt):
    
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
    ed = FBEdit()
    namespace = ""
    ed.Text = namespace
    mainLyt.SetControl(name,ed) 
    
    name = "Label:"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachRight,"namespace")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(300,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    lb = FBLabel()
    lb.Caption = ":  ( none and no select for no namespace )"
    mainLyt.SetControl(name,lb)   
        
    name = "startflame"
    x = FBAddRegionParam(10,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label_select...")
    w = FBAddRegionParam(70,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    lb = FBLabel()
    lb.Caption = "start flame :"
    mainLyt.SetControl(name,lb)   
    
    name = "theflame"
    x = FBAddRegionParam(20,FBAttachType.kFBAttachRight,"startflame")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label_select...")
    w = FBAddRegionParam(60,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    ed = FBEdit()
    ed.Text = "0"
    mainLyt.SetControl(name,ed)
    
    name = "jsonkeymultiply"
    x = FBAddRegionParam(20,FBAttachType.kFBAttachRight,"theflame")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label_select...")
    w = FBAddRegionParam(60,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    lb = FBLabel()
    lb.Caption = "   multiply :"
    mainLyt.SetControl(name,lb)   
    
    name = "jsonkeymultiplication"
    x = FBAddRegionParam(20,FBAttachType.kFBAttachRight,"jsonkeymultiply")
    y = FBAddRegionParam(10,FBAttachType.kFBAttachBottom,"Label_select...")
    w = FBAddRegionParam(60,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion(name,name, x, y, w, h)
    ed = FBEdit()
    multiplication = "1"
    ed.Text = multiplication
    #pathtext = ed.Text
    mainLyt.SetControl(name,ed)
    
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
    ed = FBEdit()
    pathtext = ""
    ed.Text = pathtext
    #pathtext = ed.Text
    l.SetControl(name,ed)
    

    


   
     
    
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
    global controls
    controls = [FBList(), FBList()]
    for ll in controls:
        ll.OnChange.Add(ListCallback)
        for i in mouthposes:
            name = i
            ll.Items.append(name)
    
    controls[0].Style = FBListStyle.kFBDropDownList
    lyt.Add(controls[0], 25)
    controls[0].Selected(0, True)
    
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
    global controls2
    controls2 = [FBList(), FBList()]
    for ll in controls2:
        ll.OnChange.Add(ListCallback)
        for i in eyebrowposes:
            name = i
            ll.Items.append(name)
    
    controls2[0].Style = FBListStyle.kFBDropDownList
    lyt.Add(controls2[0], 25)
    controls2[0].Selected(0, True)
    
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
    global controls3
    controls3 = [FBList(), FBList()]
    for ll in controls3:
        ll.OnChange.Add(ListCallback)
        for i in eyeposes:
            name = i
            ll.Items.append(name)
    
    controls3[0].Style = FBListStyle.kFBDropDownList
    lyt.Add(controls3[0], 25)
    controls3[0].Selected(0, True)
    
    
    
#set defuelt tab at 0
    tab.SetContent(0)
    tab.TabPanel.TabStyle = 0 # normal tabs
    #tab.TabPanel.TabStyle = 1 # tabs are activated with buttons
    
def CreateTool():
    # Tool creation will serve as the hub for all other controls
    t = FBCreateUniqueTool("LY")
    t.StartSizeX = 640
    t.StartSizeY = 300
    PopulateLayout(t)  
    ShowTool(t)

CreateTool()