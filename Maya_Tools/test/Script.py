# Copyright 2009 Autodesk, Inc.  All rights reserved.
# Use of this software is subject to the terms of the Autodesk license agreement 
# provided at the time of installation or download, or which otherwise accompanies
# this software in either electronic or hard copy form.
#
# Script description:
# Create a tool that show how to specify an Image in a container
#
# Topic: FBImageContainer
# 

from pyfbsdk import *
from pyfbsdk_additions import *


def PopulateLayout(mainLyt):
    x = FBAddRegionParam(0,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(0,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(50,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(50,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion("main","main", x, y, w, h)
    
    
    img = FBImageContainer()
    s="AriCopySkin"
    p=r"C:\Users\justcause\Desktop\%s.png"%s
    print(p)
    img.Filename = p
    
    mainLyt.SetControl("main",img)

def CreateTool():
    # Tool creation will serve as the hub for all other controls
    t = FBCreateUniqueTool("Image Container Example")
    
    PopulateLayout(t)
    
    t.StartSizeX = 400
    t.StartSizeY = 400
    
    ShowTool(t)

CreateTool()