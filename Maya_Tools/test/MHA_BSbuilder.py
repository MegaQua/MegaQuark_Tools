import pymel.core as pm
import metahuman_api as mh_api


def create_expression_shapes(selected_objects, expression_names, namespace=":"):
    """
    为多个选中对象创建指定表情形态，并将每组复制放入以表情名命名的组下

    参数:
        selected_objects (List[pm.nt.Transform]): 被控制的多边形列表
        expression_names (List[str]): 表情名称列表（带前缀，如 'ctrl_expressions_jawopen'）
        namespace (str): MetaHuman 命名空间（如 'mh_001:'，空字符串则不加）
    """
    if not selected_objects:
        raise RuntimeError("未选择任何对象")

    ns_prefix = namespace if namespace else ""

    # 获取 controllers
    controllers, err = mh_api.get_controllers(ns_prefix)
    if err:
        raise RuntimeError(err)

    # 构建完整表达式名 → 控制器通道映射（统一小写）
    expression_to_controller = {}
    for ctrl_obj in controllers:
        for ctrl_attr, expr_mappings in ctrl_obj.control_mapping.items():
            for full_expr_name, driver_val in expr_mappings:
                key = full_expr_name.lower()
                if key not in expression_to_controller:
                    expression_to_controller[key] = []
                expression_to_controller[key].append((ctrl_attr, driver_val))

    for expr in expression_names:
        expr_key = expr.lower()
        if expr_key not in expression_to_controller:
            pm.warning(f"未找到表情 '{expr}' 对应的控制器，跳过")
            continue

        print(f"\n🟡 处理表情: {expr}")
        controller_values = []

        # 设置控制器通道
        for ctrl_attr, val in expression_to_controller[expr_key]:
            ctrl_name = ctrl_attr.node().name()
            print(f"  → 控制器: {ctrl_name}, 属性: {ctrl_attr.longName()}, 设置值: {val}")
            controller_values.append((ctrl_attr, ctrl_attr.get()))
            ctrl_attr.set(val)

        # 创建空组（世界根节点下）
        group = pm.group(empty=True, name=expr)

        # 复制所有对象并添加到组下
        for obj in selected_objects:
            dup = pm.duplicate(obj, name=obj.name())[0]
            pm.parent(dup, group)

        # 恢复控制器通道
        for ctrl_attr, original in controller_values:
            ctrl_attr.set(original)

    print("\n✅ 所有表情形态已创建完成！")


selected = [pm.PyNode(x) for x in cmds.ls(selection=True)]


def get_all_expression_names(namespace=":"):
    """
    自动获取 CTRL_expressions 节点上所有表达式名称（带 ctrl_expressions_ 前缀）

    参数:
        namespace (str): 命名空间（可为空字符串）

    返回:
        List[str]: 所有表达式通道的全名
    """
    ns_prefix = namespace if namespace else ""
    expr_node_name = f"{ns_prefix}CTRL_expressions"

    if not pm.objExists(expr_node_name):
        raise RuntimeError(f"未找到 {expr_node_name} 节点")

    expr_node = pm.PyNode(expr_node_name)
    expression_attrs = expr_node.listAttr(userDefined=True, scalar=True)

    return [f"ctrl_expressions_{attr.attrName()}" for attr in expression_attrs]


expression_list = get_all_expression_names()
float_curve_names = [
    "ctrl_expressions_browdownl",
    "ctrl_expressions_browdownr",
    "ctrl_expressions_browlaterall",
    "ctrl_expressions_browlateralr",
    "ctrl_expressions_browraiseinl",
    "ctrl_expressions_browraiseinr",
    "ctrl_expressions_browraiseouterl",
    "ctrl_expressions_browraiseouterr",
    "ctrl_expressions_earupl",
    "ctrl_expressions_earupr",
    "ctrl_expressions_eyeblinkl",
    "ctrl_expressions_eyeblinkr",
    "ctrl_expressions_eyelidpressl",
    "ctrl_expressions_eyelidpressr",
    "ctrl_expressions_eyewidenl",
    "ctrl_expressions_eyewidenr",
    "ctrl_expressions_eyesquintinnerl",
    "ctrl_expressions_eyesquintinnerr",
    "ctrl_expressions_eyecheekraisel",
    "ctrl_expressions_eyecheekraiser",
    "ctrl_expressions_eyefacescrunchl",
    "ctrl_expressions_eyefacescrunchr",
    "ctrl_expressions_eyeupperlidupl",
    "ctrl_expressions_eyeupperlidupr",
    "ctrl_expressions_eyerelaxl",
    "ctrl_expressions_eyerelaxr",
    "ctrl_expressions_eyelowerlidupl",
    "ctrl_expressions_eyelowerlidupr",
    "ctrl_expressions_eyelowerliddownl",
    "ctrl_expressions_eyelowerliddownr",
    "ctrl_expressions_eyelookupl",
    "ctrl_expressions_eyelookupr",
    "ctrl_expressions_eyelookdownl",
    "ctrl_expressions_eyelookdownr",
    "ctrl_expressions_eyelookleftl",
    "ctrl_expressions_eyelookleftr",
    "ctrl_expressions_eyelookrightl",
    "ctrl_expressions_eyelookrightr",
    "ctrl_expressions_eyepupilwidel",
    "ctrl_expressions_eyepupilwider",
    "ctrl_expressions_eyepupilnarrowl",
    "ctrl_expressions_eyepupilnarrowr",
    "ctrl_expressions_eyeparallellookdirection",
    "ctrl_expressions_eyelashesupinl",
    "ctrl_expressions_eyelashesupinr",
    "ctrl_expressions_eyelashesupoutl",
    "ctrl_expressions_eyelashesupoutr",
    "ctrl_expressions_eyelashesdowninl",
    "ctrl_expressions_eyelashesdowninr",
    "ctrl_expressions_eyelashesdownoutl",
    "ctrl_expressions_eyelashesdownoutr",
    "ctrl_expressions_nosewrinklel",
    "ctrl_expressions_nosewrinkler",
    "ctrl_expressions_nosewrinkleupperl",
    "ctrl_expressions_nosewrinkleupperr",
    "ctrl_expressions_nosenostrildepressl",
    "ctrl_expressions_nosenostrildepressr",
    "ctrl_expressions_nosenostrildilatel",
    "ctrl_expressions_nosenostrildilater",
    "ctrl_expressions_nosenostrilcompressl",
    "ctrl_expressions_nosenostrilcompressr",
    "ctrl_expressions_nosenasolabialdeepenl",
    "ctrl_expressions_nosenasolabialdeepenr",
    "ctrl_expressions_mouthcheeksuckl",
    "ctrl_expressions_mouthcheeksuckr",
    "ctrl_expressions_mouthcheekblowl",
    "ctrl_expressions_mouthcheekblowr",
    "ctrl_expressions_mouthlipsblowl",
    "ctrl_expressions_mouthlipsblowr",
    "ctrl_expressions_mouthleft",
    "ctrl_expressions_mouthright",
    "ctrl_expressions_mouthup",
    "ctrl_expressions_mouthdown",
    "ctrl_expressions_mouthupperlipraisel",
    "ctrl_expressions_mouthupperlipraiser",
    "ctrl_expressions_mouthlowerlipdepressl",
    "ctrl_expressions_mouthlowerlipdepressr",
    "ctrl_expressions_mouthcornerpulll",
    "ctrl_expressions_mouthcornerpullr",
    "ctrl_expressions_mouthstretchl",
    "ctrl_expressions_mouthstretchr",
    "ctrl_expressions_mouthstretchlipsclosel",
    "ctrl_expressions_mouthstretchlipscloser",
    "ctrl_expressions_mouthdimplel",
    "ctrl_expressions_mouthdimpler",
    "ctrl_expressions_mouthcornerdepressl",
    "ctrl_expressions_mouthcornerdepressr",
    "ctrl_expressions_mouthpressul",
    "ctrl_expressions_mouthpressur",
    "ctrl_expressions_mouthpressdl",
    "ctrl_expressions_mouthpressdr",
    "ctrl_expressions_mouthlipspurseul",
    "ctrl_expressions_mouthlipspurseur",
    "ctrl_expressions_mouthlipspursedl",
    "ctrl_expressions_mouthlipspursedr",
    "ctrl_expressions_mouthlipstowardsul",
    "ctrl_expressions_mouthlipstowardsur",
    "ctrl_expressions_mouthlipstowardsdl",
    "ctrl_expressions_mouthlipstowardsdr",
    "ctrl_expressions_mouthfunnelul",
    "ctrl_expressions_mouthfunnelur",
    "ctrl_expressions_mouthfunneldl",
    "ctrl_expressions_mouthfunneldr",
    "ctrl_expressions_mouthlipstogetherul",
    "ctrl_expressions_mouthlipstogetherur",
    "ctrl_expressions_mouthlipstogetherdl",
    "ctrl_expressions_mouthlipstogetherdr",
    "ctrl_expressions_mouthupperlipbitel",
    "ctrl_expressions_mouthupperlipbiter",
    "ctrl_expressions_mouthlowerlipbitel",
    "ctrl_expressions_mouthlowerlipbiter",
    "ctrl_expressions_mouthlipstightenul",
    "ctrl_expressions_mouthlipstightenur",
    "ctrl_expressions_mouthlipstightendl",
    "ctrl_expressions_mouthlipstightendr",
    "ctrl_expressions_mouthlipspressl",
    "ctrl_expressions_mouthlipspressr",
    "ctrl_expressions_mouthsharpcornerpulll",
    "ctrl_expressions_mouthsharpcornerpullr",
    "ctrl_expressions_mouthstickyuc",
    "ctrl_expressions_mouthstickyuinl",
    "ctrl_expressions_mouthstickyuinr",
    "ctrl_expressions_mouthstickyuoutl",
    "ctrl_expressions_mouthstickyuoutr",
    "ctrl_expressions_mouthstickydc",
    "ctrl_expressions_mouthstickydinl",
    "ctrl_expressions_mouthstickydinr",
    "ctrl_expressions_mouthstickydoutl",
    "ctrl_expressions_mouthstickydoutr",
    "ctrl_expressions_mouthlipsstickylph1",
    "ctrl_expressions_mouthlipsstickylph2",
    "ctrl_expressions_mouthlipsstickylph3",
    "ctrl_expressions_mouthlipsstickyrph1",
    "ctrl_expressions_mouthlipsstickyrph2",
    "ctrl_expressions_mouthlipsstickyrph3",
    "ctrl_expressions_mouthlipspushul",
    "ctrl_expressions_mouthlipspushur",
    "ctrl_expressions_mouthlipspushdl",
    "ctrl_expressions_mouthlipspushdr",
    "ctrl_expressions_mouthlipspullul",
    "ctrl_expressions_mouthlipspullur",
    "ctrl_expressions_mouthlipspulldl",
    "ctrl_expressions_mouthlipspulldr",
    "ctrl_expressions_mouthlipsthinul",
    "ctrl_expressions_mouthlipsthinur",
    "ctrl_expressions_mouthlipsthindl",
    "ctrl_expressions_mouthlipsthindr",
    "ctrl_expressions_mouthlipsthickul",
    "ctrl_expressions_mouthlipsthickur",
    "ctrl_expressions_mouthlipsthickdl",
    "ctrl_expressions_mouthlipsthickdr",
    "ctrl_expressions_mouthlipsthininwardul",
    "ctrl_expressions_mouthlipsthininwardur",
    "ctrl_expressions_mouthlipsthininwarddl",
    "ctrl_expressions_mouthlipsthininwarddr",
    "ctrl_expressions_mouthlipsthickinwardul",
    "ctrl_expressions_mouthlipsthickinwardur",
    "ctrl_expressions_mouthlipsthickinwarddl",
    "ctrl_expressions_mouthlipsthickinwarddr",
    "ctrl_expressions_mouthcornersharpenul",
    "ctrl_expressions_mouthcornersharpenur",
    "ctrl_expressions_mouthcornersharpendl",
    "ctrl_expressions_mouthcornersharpendr",
    "ctrl_expressions_mouthcornerrounderul",
    "ctrl_expressions_mouthcornerrounderur",
    "ctrl_expressions_mouthcornerrounderdl",
    "ctrl_expressions_mouthcornerrounderdr",
    "ctrl_expressions_mouthupperliptowardsteethl",
    "ctrl_expressions_mouthupperliptowardsteethr",
    "ctrl_expressions_mouthlowerliptowardsteethl",
    "ctrl_expressions_mouthlowerliptowardsteethr",
    "ctrl_expressions_mouthupperlipshiftleft",
    "ctrl_expressions_mouthupperlipshiftright",
    "ctrl_expressions_mouthlowerlipshiftleft",
    "ctrl_expressions_mouthlowerlipshiftright",
    "ctrl_expressions_mouthupperliprollinl",
    "ctrl_expressions_mouthupperliprollinr",
    "ctrl_expressions_mouthupperliprolloutl",
    "ctrl_expressions_mouthupperliprolloutr",
    "ctrl_expressions_mouthlowerliprollinl",
    "ctrl_expressions_mouthlowerliprollinr",
    "ctrl_expressions_mouthlowerliprolloutl",
    "ctrl_expressions_mouthlowerliprolloutr",
    "ctrl_expressions_mouthcornerupl",
    "ctrl_expressions_mouthcornerupr",
    "ctrl_expressions_mouthcornerdownl",
    "ctrl_expressions_mouthcornerdownr",
    "ctrl_expressions_mouthcornerwidel",
    "ctrl_expressions_mouthcornerwider",
    "ctrl_expressions_mouthcornernarrowl",
    "ctrl_expressions_mouthcornernarrowr",
    "ctrl_expressions_jawopen",
    "ctrl_expressions_jawleft",
    "ctrl_expressions_jawright",
    "ctrl_expressions_jawfwd",
    "ctrl_expressions_jawback",
    "ctrl_expressions_jawclenchl",
    "ctrl_expressions_jawclenchr",
    "ctrl_expressions_jawchinraisedl",
    "ctrl_expressions_jawchinraisedr",
    "ctrl_expressions_jawchinraiseul",
    "ctrl_expressions_jawchinraiseur",
    "ctrl_expressions_jawchincompressl",
    "ctrl_expressions_jawchincompressr",
    "ctrl_expressions_jawopenextreme",
    "ctrl_expressions_neckstretchl",
    "ctrl_expressions_neckstretchr",
    "ctrl_expressions_neckswallowph1",
    "ctrl_expressions_neckswallowph2",
    "ctrl_expressions_neckswallowph3",
    "ctrl_expressions_neckswallowph4",
    "ctrl_expressions_neckmastoidcontractl",
    "ctrl_expressions_neckmastoidcontractr",
    "ctrl_expressions_neckthroatdown",
    "ctrl_expressions_neckthroatup",
    "ctrl_expressions_neckdigastricdown",
    "ctrl_expressions_neckdigastricup",
    "ctrl_expressions_neckthroatexhale",
    "ctrl_expressions_neckthroatinhale",
    "ctrl_expressions_teethupu",
    "ctrl_expressions_teethupd",
    "ctrl_expressions_teethdownu",
    "ctrl_expressions_teethdownd",
    "ctrl_expressions_teethleftu",
    "ctrl_expressions_teethleftd",
    "ctrl_expressions_teethrightu",
    "ctrl_expressions_teethrightd",
    "ctrl_expressions_teethfwdu",
    "ctrl_expressions_teethfwdd",
    "ctrl_expressions_teethbacku",
    "ctrl_expressions_teethbackd",
    "ctrl_expressions_tongueup",
    "ctrl_expressions_tonguedown",
    "ctrl_expressions_tongueleft",
    "ctrl_expressions_tongueright",
    "ctrl_expressions_tongueout",
    "ctrl_expressions_tonguein",
    "ctrl_expressions_tonguebendup",
    "ctrl_expressions_tonguebenddown",
    "ctrl_expressions_tonguetwistleft",
    "ctrl_expressions_tonguetwistright",
    "ctrl_expressions_tonguetipup",
    "ctrl_expressions_tonguetipdown",
    "ctrl_expressions_tonguetipleft",
    "ctrl_expressions_tonguetipright",
    "ctrl_expressions_tonguewide",
    "ctrl_expressions_tonguenarrow",
    "ctrl_expressions_tonguepress",
    "ctrl_expressions_tongueroll",
    "ctrl_expressions_tonguethick",
    "ctrl_expressions_tonguethin",
    "headyaw",
    "headpitch",
    "headroll",
    "headtranslationx",
    "headtranslationy",
    "headtranslationz",
    "headcontrolswitch",
    "mhfdsversion",
    "disablefaceoverride"
]

create_expression_shapes(selected, float_curve_names, namespace="")