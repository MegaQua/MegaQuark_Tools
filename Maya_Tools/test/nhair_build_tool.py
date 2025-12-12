import maya.cmds as cmds
import maya.mel as mel

def get_all_child_joints(start_joint):
    """获取开始关节及其所有子关节的名称列表，从根关节到叶关节的顺序"""
    all_joints = []
    queue = [start_joint]

    while queue:
        current_joint = queue.pop(0)
        all_joints.append(current_joint)
        children = cmds.listRelatives(current_joint, c=True, type='joint') or []
        queue.extend(children)

    return all_joints

def duplicate_rename_joints(selected_joints, prefix):
    def select_first_level_joints_in_group(group_name):
        children = cmds.listRelatives(group_name, c=True, type='joint') or []
        cmds.select(children)

    copied_joints_to_select = []

    for start_joint in selected_joints:
        all_joints = get_all_child_joints(start_joint)
        group_name = "{}_joint_GP".format(prefix)
        if not cmds.objExists(group_name):
            cmds.group(em=True, name=group_name)
        copied_joint = cmds.duplicate(start_joint, rc=True)[0]
        cmds.parent(copied_joint, group_name)
        copied_all_joints = get_all_child_joints(copied_joint)
        for orig_joint, copy_joint in zip(all_joints, copied_all_joints):
            new_name = "{}_{}".format(prefix, orig_joint.split("|")[-1])
            cmds.rename(copy_joint, new_name)
            #cmds.orientConstraint(new_name, orig_joint, maintainOffset=True)
        copied_joints_to_select.append(copied_joint)

    # 选择前缀加 "_GP" 下面第一层的所有关节。
    select_first_level_joints_in_group("{}_joint_GP".format(prefix))


def is_single_chain(joint_name):
    """Check if the given joint has only one chain of children."""
    children = cmds.listRelatives(joint_name, children=True, type='joint') or []
    if not children:
        return True
    if len(children) > 1:
        return False
    return is_single_chain(children[0])


def get_joint_chain(joint_name):
    """Retrieve the entire chain of joints starting from the given joint."""
    chain = [joint_name]
    children = cmds.listRelatives(joint_name, children=True, type='joint') or []
    while children:
        chain.append(children[0])
        children = cmds.listRelatives(children[0], children=True, type='joint') or []
    return chain


def create_curve_from_joint_chain(joint_name):
    """Create a cubic curve from a joint chain if conditions are met."""
    if not is_single_chain(joint_name):
        return f"Error for '{joint_name}': Multiple chains of joints underneath."
    chain = get_joint_chain(joint_name)
    if len(chain) < 4:
        return f"Error for '{joint_name}': Not enough joints (minimum 4 required)."
    cvs = [cmds.xform(j, query=True, worldSpace=True, translation=True) for j in chain]
    curve = cmds.curve(d=3, p=cvs, name=f"{joint_name}_curve")
    return curve


def create_ik_spline(joint_name, curve):
    """Create an ikSpline handle using the joint chain and the provided curve."""
    chain = get_joint_chain(joint_name)
    start_joint = chain[0]
    end_joint = chain[-1]
    ik_handle, effector = cmds.ikHandle(name=f"{joint_name}_ikHandle", startJoint=start_joint, endEffector=end_joint, curve=curve,
                                        solver="ikSplineSolver", createCurve=False, parentCurve=False)
    return ik_handle


def group_curves(curve_list, group_name):
    """Group curves into a specified group."""
    if not cmds.objExists(group_name):
        cmds.group(empty=True, name=group_name)
    cmds.parent(curve_list, group_name)


def rename_follicle_and_shape(curve_name):
    # Getting the follicle and its shape node
    dynFollicle = cmds.listRelatives(curve_name, p=1)[0]
    dynFollicleShape = cmds.listRelatives(dynFollicle, s=1)[0]

    # Release the tip
    cmds.setAttr(dynFollicleShape + ".pointLock", 1)

    # Connect IK
    dynCurveConnections = cmds.listConnections(dynFollicleShape, sh=1)

    for dynCurve in dynCurveConnections:
        if "curveShape" in dynCurve:
            outputCurve = cmds.listRelatives(dynCurve, p=1)[0]

    newFollicleName = curve_name.replace("_curve_dy_start", "_follicle")
    newFollicleShapeName = curve_name.replace("_curve_dy_start", "_curve_dy")

    cmds.rename(dynFollicle, newFollicleName)
    cmds.rename(outputCurve, newFollicleShapeName)


def create_clusters_and_ctrls_for_curve(curve_name, ctrl_prefix):
    """
    Create clusters for each CV of a curve and create controllers which will be parented to clusters.
    Cluster handles will be hidden after creation. Controllers will be parented under a group.

    Parameters:
    - curve_name (str): The name of the curve.
    - ctrl_prefix (str): A prefix for the controller names.
    """
    # Get number of CVs on the curve.
    curve_cvs = cmds.getAttr(curve_name + ".cp", s=1)

    # Create a group and position it to the first cluster handle.
    #ctrl_group = cmds.group(em=True, n=curve_name+ "_cluster_con_GP")
    #first_cluster, first_cluster_handle = cmds.cluster(curve_name + ".cv[0]", n=curve_name + "_cluster_0")
    #cmds.matchTransform(ctrl_group, first_cluster_handle)

    # Delete the first cluster and handle as they are not needed.
    #cmds.delete(first_cluster, first_cluster_handle)
    cluster_group = cmds.group(em=True, n=ctrl_prefix + curve_name + "cluster_GP")
    #cmds.parent(cluster_group, all_cluster_group)
    # Create controllers, parent the cluster handles to them, and parent controllers to the group.
    for i in range(curve_cvs):
        cluster, cluster_handle = cmds.cluster(curve_name + ".cv[" + str(i) + "]", n=curve_name + "_cluster_" + str(i))

        # Hide the cluster handle.
        cmds.setAttr(cluster_handle + ".visibility", 0)

        # Create a NURBS circle as controller.
        ctrl = cmds.circle(n=curve_name+"_con_curve_" + str(i), ch=False, o=True)[0]

        # Move the controller to the position of the cluster handle.
        cmds.matchTransform(ctrl, cluster_handle)
        cmds.makeIdentity(ctrl, apply=True, translate=True, rotate=True, scale=True)
        cmds.parent(cluster_handle, ctrl)

        # Create an offset group for the controller.
        if i == 0:
            cmds.matchTransform(cluster_group, ctrl)
        cmds.parent(ctrl, cluster_group)



selected_joints = cmds.ls(selection=True, type='joint')
prefix = "ep3skirtSim"

if selected_joints:
    duplicate_rename_joints(selected_joints, prefix)

selected_joints = cmds.ls(selection=True, type='joint')

if selected_joints:
    # Creating or finding groups for organization
    curves_group = prefix+"_ik_curve_GP"
    follicle_group = prefix+"_follicle_GP"
    ik_handles_group = prefix+"_ikHandle_GP"
    dy_start_GP_group = prefix + "_dy_start_GP"
    all_cluster_group = prefix + "_cluster_GP"

    if not cmds.objExists(curves_group):
        curves_group = cmds.group(empty=True, name=curves_group)
    if not cmds.objExists(follicle_group):
        follicle_group = cmds.group(empty=True, name=follicle_group)
    if not cmds.objExists(ik_handles_group):
        ik_handles_group = cmds.group(empty=True, name=ik_handles_group)
    if not cmds.objExists(dy_start_GP_group):
        dy_start_GP_group = cmds.group(empty=True, name=dy_start_GP_group)
    if not cmds.objExists(all_cluster_group):
        dy_start_GP_group = cmds.group(empty=True, name=all_cluster_group)

    backup_curves_to_make_dynamic = []  # 存储_dy_start曲线的列表

    # Processing selected joints
    for joint in selected_joints:
        curve_result = create_curve_from_joint_chain(joint)

        if "Error" not in curve_result:
            # Duplicate the curve and rename it
            backup_curve = cmds.duplicate(curve_result, name=f"{joint}_curve_dy_start")[0]
            backup_curves_to_make_dynamic.append(backup_curve)  # 添加曲线到列表
            print(f"Backup curve '{backup_curve}' created.")

            # Create the ikSpline handle with the original curve
            ik_handle = create_ik_spline(joint, curve_result)
            print(f"For joint '{joint}', ikSpline handle '{ik_handle}' created with curve '{curve_result}'.")

            # Organizing objects in respective groups
            cmds.parent(curve_result, curves_group)
            cmds.parent(backup_curve, follicle_group)
            cmds.parent(ik_handle, ik_handles_group)
        else:
            #print(curve_result)
            pass

    # Making all _dy_start curves dynamic after processing all joints
    if backup_curves_to_make_dynamic:
        cmds.select(backup_curves_to_make_dynamic)
        mel.eval('makeCurvesDynamic 2 { "1", "0", "1", "1", "0"};')
        cmds.select(clear=True)  # 清除选择，以防干扰后续的操作

    for curve in backup_curves_to_make_dynamic:
        rename_follicle_and_shape(curve)  # Rename follicle and shape for each curve
        basename = curve.replace("_curve_dy_start", "")
        cmds.blendShape(basename + "_curve_dy", basename + "_curve", n=basename + "_bshape")
        cmds.setAttr(basename + "_bshape" + "."+basename+"_curve_dy", 1.0)
        cmds.parent(curve, dy_start_GP_group)

    dy_start = cmds.listRelatives(dy_start_GP_group, c=True) or []
    print(dy_start)

    for curve in dy_start:
        print(curve)
        create_clusters_and_ctrls_for_curve(curve,prefix)

else:
    print("Please select one or more joints and try again.")