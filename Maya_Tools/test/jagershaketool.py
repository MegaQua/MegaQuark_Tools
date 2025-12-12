import maya.cmds as cmds


def create_smooth_and_noise_groups(selected_obj, translate_threshold=0.02, rotate_threshold=0.85, translate_deviation=0.1, rotate_deviation=20,
                                   n_frames=4,
                                   translateX_correction=0, translateY_correction=3, translateZ_correction=0,
                                   rotateX_correction=0, rotateY_correction=0, rotateZ_correction=0, excessive_deviation_threshold=1,
                                   useless_rate_threshold=0.1):
    if not selected_obj:
        raise ValueError("No object selected.")

    test_obj = cmds.duplicate(selected_obj, name=selected_obj+'_test_cam')[0]
    cmds.setAttr(f'{test_obj}.translate', 0, 0, 0)
    cmds.setAttr(f'{test_obj}.rotate', 0, 0, 0)
    smooth_group = cmds.group(em=True, name=selected_obj+'_smooth_GP')
    noise_group = cmds.group(em=True, name=selected_obj+'_noise_GP')

    # 设置层级结构
    cmds.parent(test_obj, noise_group)
    cmds.parent(noise_group, smooth_group)

    corrections = {
        'translateX': translateX_correction,
        'translateY': translateY_correction,
        'translateZ': translateZ_correction,
        'rotateX': rotateX_correction,
        'rotateY': rotateY_correction,
        'rotateZ': rotateZ_correction,
    }

    # 处理 translate 和 rotate 的每个属性
    for attr in ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']:
        is_translate = 'translate' in attr
        threshold = translate_threshold + corrections[attr] if is_translate else rotate_threshold + corrections[attr]
        deviation_threshold = (translate_deviation + corrections[attr]) if is_translate else (rotate_deviation + corrections[attr])
        #deviation_threshold = translate_deviation if is_translate else rotate_deviation

        keyframes = cmds.keyframe(selected_obj, attribute=attr, query=True)

        if not keyframes:
            continue

        # 对每个关键帧进行处理
        for frame in keyframes:

            current_value = cmds.getAttr(f'{selected_obj}.{attr}', time=frame)

            if frame == keyframes[0]:
                first_value=current_value
                cmds.setKeyframe(smooth_group, attribute=attr, time=frame, value=current_value)
                continue

            start_frame = max(frame - n_frames, min(keyframes))
            end_frame = min(frame + n_frames + 1, max(keyframes) + 1)
            frame_range = range(int(start_frame), int(end_frame))
            frame_values = [cmds.getAttr(f'{selected_obj}.{attr}', time=f) for f in frame_range]

            if len(frame_values) >= 3:
                frame_values.remove(max(frame_values))
                frame_values.remove(min(frame_values))

            avg_value = sum(frame_values) / len(frame_values)

            if abs(current_value - avg_value) < threshold:
                continue
            else:
                prev_frame = frame - 1
                cmds.setKeyframe(smooth_group, attribute=attr, time=frame, value=current_value)
                if cmds.keyframe(smooth_group, attribute=attr, query=True, time=(prev_frame, prev_frame)) and prev_frame!=keyframes[0]:
                    cmds.cutKey(smooth_group, time=(prev_frame, prev_frame), attribute=attr)

        # 检查偏离并根据需要调整关键帧
        for frame in keyframes:
            original_value = cmds.getAttr(f'{selected_obj}.{attr}', time=frame)
            smooth_value = cmds.getAttr(f'{smooth_group}.{attr}', time=frame)
            if abs(original_value - smooth_value) > deviation_threshold and abs(original_value - smooth_value) <= excessive_deviation_threshold:
                prev_frame = frame - 1
                cmds.setKeyframe(smooth_group, attribute=attr, time=frame, value=original_value)
                #if cmds.keyframe(smooth_group, attribute=attr, query=True, time=(prev_frame, prev_frame)) and prev_frame!=keyframes[0]:
                #    cmds.cutKey(smooth_group, time=(prev_frame, prev_frame), attribute=attr)

        keyframes_smooth_group = cmds.keyframe(smooth_group, attribute=attr, query=True)
        # 遍历关键帧
        if keyframes_smooth_group:
            for _ in range(2):
                for i in range(1, len(keyframes_smooth_group) - 1):  # 跳过第一个和最后一个关键帧
                    try:
                        current_frame = keyframes_smooth_group[i]
                        prev_frame = keyframes_smooth_group[i - 1]
                        next_frame = keyframes_smooth_group[i + 1]

                        # 获取关键帧的值
                        current_value = cmds.getAttr(f'{smooth_group}.{attr}', time=current_frame)
                        prev_value = cmds.getAttr(f'{smooth_group}.{attr}', time=prev_frame)
                        next_value = cmds.getAttr(f'{smooth_group}.{attr}', time=next_frame)

                        # 计算值变化率
                        rate_prev = (current_value - prev_value) / (current_frame - prev_frame)
                        rate_next = (next_value - current_value) / (next_frame - current_frame)

                        # 判断是否为无用帧
                        if abs(rate_next - rate_prev) < useless_rate_threshold:
                            cmds.cutKey(smooth_group, time=(current_frame, current_frame), attribute=attr)
                            del keyframes_smooth_group[i]
                        if len(keyframes_smooth_group) <= 3:
                            break
                    except:
                        pass

    # 创建噪点帧
    keyframes = cmds.keyframe(selected_obj, attribute=attr, query=True)

    if  keyframes:

        for frame in keyframes:
            cmds.currentTime(frame)
            cmds.matchTransform(noise_group, selected_obj, position=True)
            cmds.matchTransform(noise_group, selected_obj, rotation=True)
            for attr in ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']:
                attr_value = cmds.getAttr(f'{noise_group}.{attr}')
                cmds.setKeyframe(noise_group, attribute=attr, time=frame, value=attr_value)


# 使用示例
selected_obj = cmds.ls(selection=True)[0]
create_smooth_and_noise_groups(selected_obj)
