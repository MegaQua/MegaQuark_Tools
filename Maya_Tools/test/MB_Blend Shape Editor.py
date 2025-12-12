# Copyright 2009 Autodesk, Inc.  All rights reserved.
# Use of this software is subject to the terms of the Autodesk license agreement 
# provided at the time of installation or download, or which otherwise accompanies
# this software in either electronic or hard copy form.
#
# Script description:
# Blend shaped editor.
# Press Attach and it will grab all BlendShape Model in the scene and create an editor for them.
# Press Detach and it will release all BlendShape and clears all UI
#
# Topic: FBEventName, FBSlider
# 

from pyfbsdk import *
from pyfbsdk_additions import *

class SliderControl(FBVBoxLayout):
    def _sliderCallback(self,control,event):
        if event.Type == FBEventName.kFBEventChange:
            self.value.Text = "%3.2f" % self.slider.Value
            self._linkedproperty.Data=self.slider.Value
        if self.key.State==1:
            self._isCandidate=True
        elif event.Type ==FBEventName.kFBEventOnClick:
            self._onChange=True
        elif event.Type ==FBEventName.kFBEventExit:
            self._onChange=False                 
        
    def _valueCallback(self, control, event):
        self._onChange=True
        self.slider.Value = float(self.value.Text)
        self._linkedproperty.Data = float(self.value.Text)
        self.value.Text = "%3.2f" % float(self.value.Text)
        self._onChange=False
        if self.key.State==1:
            self._isCandidate=True

    def _nameCallback(self, control, event):
        print ("NameChanged")
    
    def _keyCallback(self, control, event):
        self.Key()
    
    def _clearCallback(self, control, event):
        self.ClearAnimation()
    
    def _IdleCallback(self, control, event):
        if not self._onChange:
            self.updateView()
                        
    def __init__(self, Aproperty):
        from pyfbsdk import FBAddRegionParam
        from pyfbsdk import FBAttachType        
        
        FBVBoxLayout.__init__(self)
        self._linkedproperty = Aproperty
        self._onChange = False
        self._isCandidate = False
        self.slider = pyfbsdk.FBSlider()
        self.value = pyfbsdk.FBEdit()
        self.name = pyfbsdk.FBLabel()
        self.name.Justify = FBTextJustify.kFBTextJustifyRight
        self.key = pyfbsdk.FBButton()
        self.key.State=1
        self.key.Caption = "Key"
        self.clear = pyfbsdk.FBButton()
        self.clear.Caption = "Clear"
        
        if Aproperty.IsAnimatable() and Aproperty.GetDataTypeName().lower()=="shape": ##check that we have an animatable shape property
            self.slider.Min = Aproperty.GetMin()
            self.slider.Max = Aproperty.GetMax()
            self.slider.Value = Aproperty.Data
            self.value.Text = "%3.2f" % Aproperty.Data
            self.name.Caption = Aproperty.GetName()
        else:
            print ("notAdouble")
        
        self.slider.OnChange.Add(self._sliderCallback)
        self.value.OnChange.Add(self._valueCallback)
        self.key.OnClick.Add(self._keyCallback)
        self.OnIdle.Add(self._IdleCallback)
        self.clear.OnClick.Add(self._clearCallback)

        ##add the slider view        
        self.Add(self.slider, 150, width = 35)
        
        ## add the button clear
        self.Add(self.clear, 25)
        
        ## add the button key
        self.Add(self.key, 25)

        ## add the name
        self.Add(self.name, 25)


        ##add the Value
        self.Add(self.value, 25)
        
                        
    def add(self,name,content):
        self.tabpanel.Items.append(name)
        self.tabcontents.append(content)
        self.setContent(len(self.tabpanel.Items) - 1)

    def setContent(self,index):
        self.tabpanel.ItemIndex = index
        self.SetControl("mainlyt",self.tabcontents[index])
    
    def Key(self):
        self._linkedproperty.Key()
        self._isCandidate=False
        
    def Reset(self):
        self._isCandidate=True
        self.value.Text="0.0"
        self._valueCallback(None,FBEventChange())
    
    def ClearAnimation(self):
        self._isCandidate=True
        self._linkedproperty.GetAnimationNode().FCurve.EditClear()

    
    def Clear(self):
        self._linkedproperty.GetAnimationNode().KeyRemove()

    def updateView(self):
        if not self._onChange: 
            precision = 0.005
            currentvalue = float(self.value.Text)
            if currentvalue < self._linkedproperty.Data-precision or currentvalue > self._linkedproperty.Data+precision:
                self.value.Text="%3.2f" %self._linkedproperty.Data
                self.slider.Value = self._linkedproperty.Data
            if not self._isCandidate and self._linkedproperty.GetAnimationNode().IsKey():
                    if self.key.State!=1:
                        self.key.State=1
            else:
                if self.key.State!=0:
                    self.key.State=0
            if self._linkedproperty.IsAnimatable() and self._linkedproperty.GetAnimationNode().KeyCount>0:
                self.key.Caption="Key *"
            else:
                self.key.Caption="Key"

def GetBlendShapeProp(aModel):
    myproplist = list()
    for prop in aModel.PropertyList:
        if prop != None and prop.IsAnimatable() and prop.GetDataTypeName().lower()=="shape":
            myproplist.append(prop)
    return myproplist

class ModelBlendShapeUI (FBHBoxLayout):
    def _KeyAllCallBack(self,control, event):
        for each in self._mySliderList:
            each.Key()

    def _ResetAllCallBack(self,control, event):
        for each in self._mySliderList:
            each.Reset()

    def _ClearAllCallBack(self,control, event):
        for each in self._mySliderList:
            each.ClearAnimation()
            
    def __init__(self, Amodel):
        from pyfbsdk import FBAddRegionParam
        from pyfbsdk import FBAttachType        
        
        FBHBoxLayout.__init__(self)
        self._linkedModel = Amodel
        self._mySliderList=list()
        ## populate the propertylist
        self.bkeyall=FBButton()
        self.bkeyall.Caption="Key All"
        self.brstall=FBButton()
        self.brstall.Caption="Reset All"
        self.bclrall=FBButton()
        self.bclrall.Caption="Clear All"
        
        ## Creation of the buttonLayout 
        self._myButtonsLay = FBVBoxLayout()
        self.Add(self._myButtonsLay, 75)
                
        self.bkeyall.OnClick.Add(self._KeyAllCallBack)
        self._myButtonsLay.Add(self.bkeyall, 25)

        ##brstall
        self.brstall.OnClick.Add(self._ResetAllCallBack)
        self._myButtonsLay.Add(self.brstall, 25)

        ##bclrall
        self.bclrall.OnClick.Add(self._ClearAllCallBack)
        self._myButtonsLay.Add(self.bclrall, 25)
        
        # add all the slider ctrl
        for prop in GetBlendShapeProp(self._linkedModel):
            slider = SliderControl(prop)
            self._mySliderList.append(slider)
            self.Add(slider, 75, space = 10)
            


def GetBlendShapeModel():    
    modelslist = list()
    for component in FBSystem().Scene.Components:
        if str(type(component)).lower().find("fbmodel")>-1:
            bblend=False
            for prop in component.PropertyList:
                if not prop==None and  prop.IsAnimatable() and prop.GetDataTypeName().lower()=="shape":
                    bblend=True
                    break
            if bblend:
                modelslist.append(component)
    return modelslist


def DetachFromBlendShape(control, event):
    global regions
    global models
    
    for region in regions.itervalues():
        lyt.RemoveRegion(region)
    regions = {}
    models = []
    
def AttachToBlendShape(control, event):
    DetachFromBlendShape(None, None)
    
    global models
    models = GetBlendShapeModel()
    
    anchor = FBAttachType.kFBAttachTop
    anchorRegion = ""
    for i, model in enumerate(models):
        lytName = model.Name
        blendShapeEditor = ModelBlendShapeUI(model)
            
        arrowName = "ArrowName" + str( i )
        x = FBAddRegionParam(0,FBAttachType.kFBAttachLeft,"")
        y = FBAddRegionParam(0,anchor,anchorRegion)
        w = FBAddRegionParam(2000,FBAttachType.kFBAttachNone,"")
        h = FBAddRegionParam(0,FBAttachType.kFBAttachNone,"")
        lyt.AddRegion(arrowName ,arrowName , x, y, w, h)
    
        b = FBArrowButton()
        regions[model] = arrowName
        lyt.SetControl(arrowName ,b)
    
        # important : we set the content AFTER having added the button arrow
        # to its parent layout
        b.SetContent( model.Name, blendShapeEditor, 2000, 300 )
        blendShapeEditor.Restructure(True)

        anchor = FBAttachType.kFBAttachBottom
        anchorRegion = arrowName
        

def SceneChanged(scene, event):
    if event.Type == FBSceneChangeType.kFBSceneChangeDetach  and \
        event.ChildComponent in models:
        lyt.RemoveRegion(regions[event.ChildComponent])
        models.remove(event.ChildComponent)

    
def OnToolDestroy(control,event):
    # Important: each time we run this script we need to remove
    # the SceneChanged from the Scene else they will accumulate
    FBSystem().Scene.OnChange.Remove(SceneChanged)


models = []
regions = {}
  
# Tool creation will serve as the hub for all other controls
tool = FBCreateUniqueTool("Blend Shape Editor")

tool.StartSizeX = 400
tool.StartSizeY = 200

scroll = FBScrollBox()
scroll.SetContentSize(2000,10000)

mainLyt = FBVBoxLayout()
x = FBAddRegionParam(0,FBAttachType.kFBAttachLeft,"")
y = FBAddRegionParam(0,FBAttachType.kFBAttachTop,"")
w = FBAddRegionParam(0,FBAttachType.kFBAttachRight,"")
h = FBAddRegionParam(0,FBAttachType.kFBAttachBottom,"")
tool.AddRegion("main","main", x, y, w, h)
tool.SetControl("main",mainLyt)

btnbar = FBHBoxLayout()
btn = FBButton()
btn.Caption = "Attach"
btn.OnClick.Add(AttachToBlendShape)
btnbar.Add(btn, 75)

btn = FBButton()
btn.Caption = "Detach"
btn.OnClick.Add(DetachFromBlendShape)
btnbar.Add(btn, 75)

mainLyt.Add(btnbar, 30)

mainLyt.AddRelative(scroll)

lyt = scroll.Content

# Register for scene event
FBSystem().Scene.OnChange.Add(SceneChanged)
    
# register when this tool is destroyed.
tool.OnUnbind.Add(OnToolDestroy)

ShowTool(tool)
