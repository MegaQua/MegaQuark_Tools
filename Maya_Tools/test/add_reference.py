import maya.cmds as cmds

def add_reference_with_namespace(name, namespace, path):
    """
    Add a file as a reference to the current Maya scene with a given namespace
    :param name: (str) Name of the reference node
    :param namespace: (str) Namespace for the reference node
    :param path: (str) File path to the reference file
    :return: (str) Full path to the reference node created
    """
    # Check if the file exists
    if not os.path.exists(path):
        raise ValueError("File not found: {}".format(path))

    # Add the reference
    ref_node = cmds.file(path, reference=True, namespace=namespace, returnNewNodes=True, groupName=name)
    if not ref_node:
        raise RuntimeError("Failed to create reference: {}".format(path))

    # Rename the reference node to the specified name
    ref_node = cmds.rename(ref_node[0], name)

    # Return the full path to the reference node
    return ref_node
