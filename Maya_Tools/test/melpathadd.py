import os
custom_path = r"S:\Public\qiu_yi\JCQ_Tool\mel"
os.environ["MAYA_SCRIPT_PATH"] = custom_path + os.pathsep + os.environ.get("MAYA_SCRIPT_PATH", "")
