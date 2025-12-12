import maya.cmds as cmds

cmds.window( widthHeight=(200, 150) )

cmds.gridLayout( numberOfColumns=2, cellWidthHeight=(50, 50) )
cmds.button()
cmds.button()
cmds.button()
cmds.button()
cmds.button()
cmds.button()
cmds.button()
cmds.setParent( '..' )
form = cmds.formLayout()
tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
cmds.formLayout( form, edit=True, attachForm=((tabs, 'top', 0), (tabs, 'left', 0), (tabs, 'bottom', 0), (tabs, 'right', 0)) )

child1 = cmds.rowColumnLayout(numberOfColumns=2)
cmds.button()
cmds.button()
cmds.button()
cmds.setParent( '..' )

child2 = cmds.rowColumnLayout(numberOfColumns=2)
cmds.button()
cmds.button()
cmds.button()
cmds.setParent( '..' )

cmds.tabLayout( tabs, edit=True, tabLabel=((child1, 'One'), (child2, 'Two')) )

cmds.showWindow()