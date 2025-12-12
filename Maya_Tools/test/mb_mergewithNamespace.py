from pyfbsdk import *


def namespace_exists(namespace):
    for ns in FBSystem().Scene.Namespaces:
        if ns.Name == namespace:
            return True
    return False


def import_fbx_with_namespace(file_path, namespace):
    if namespace_exists(namespace):
        print(f"Namespace '{namespace}' already exists in the scene. Skipping import.")
        return

    app = FBApplication()
    options = FBFbxOptions(False)  # False indicates OPTIONS_FOR_LOAD is not used
    options.NamespaceList = namespace
    options.SetAll(FBElementAction.kFBElementActionMerge, True)
    app.FileAppend(file_path, False, options)  # False indicates NO_LOAD_UI_DIALOG
    print(f"Imported '{file_path}' with namespace '{namespace}'.")


# Example usage
file_path = "D:/export/_fbx/test.fbx"
namespace = "your_namespace2"
import_fbx_with_namespace(file_path, namespace)
