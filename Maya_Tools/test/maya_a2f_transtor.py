import json
import maya.cmds as mc

with open (r'K:\shenron\11_Users\Q\anyheadtest\a2f_cache_ba.json', "r") as f:
    facs_data = json.loads(f.read())
    facsNames = facs_data["facsNames"]
    numPoses = facs_data["numPoses"]
    numFrames = facs_data["numFrames"]
    weightMat = facs_data["weightMat"]

    bsnode = 'blendShape1'
    for fr in range(numFrames) :
        for i in range(numPoses):
            mc.setKeyframe(bsnode+'.'+facsNames[i], v=weightMat[fr][i], t=fr)