import maya.cmds as cmds


class MR_Window(object):
    # constructor
    def __init__(self):
        self.window = "MR_Window"
        self.title = "Cube Creator"
        self.size = (400, 400)
        # delete old window is open
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)
        # creat new window
        self.window = cmds.window(self.window, title=self.title, widthHeight=self.size)

        cmds.columnLayout(adjustableColumn=True)

        cmds.text(self.title)
        cmds.separator(height=20)

        self.cubeName = cmds.textFieldGrp(label="Cube Name:")
        self.cubeSize = cmds.floatFieldGrp(numberOfFields=3, label="Size:",
                                           value1=1, value2=1, value3=1)
        self.cubeSubdives = cmds.intSliderGrp(field=True, label="Subdivs",
                                              minValue=1, maxValue=10, value=1)

        self.cubeCreatebtn = cmds.button(label="Create Cube", command=self.createCube)

        # display new window
        cmds.showWindow()

    def createCube(self, *args):
        name = cmds.textFieldGrp(self.cubeName, query=True, text=True)
        width = cmds.floatFieldGrp(self.cubeSize, query=True, value1=True)
        height = cmds.floatFieldGrp(self.cubeSize, query=True, value2=True)
        depth = cmds.floatFieldGrp(self.cubeSize, query=True, value3=True)

        subdivs = cmds.intSliderGrp(self.cubeSubdives, query=True, value=True)

        cmds.polyCube(name=name, width=width, height=height, depth=depth,
                      subdivisionsWidth=subdivs, subdivisionsHeight=subdivs, subdivisionsDepth=subdivs)


myWindow = MR_Window()