import time

import cv2
import numpy as np
import pyautogui as ag
import pygetwindow as gw

color_timeline = (0x3D, 0xBD, 0xFF)
color_audioclip = (0x9E, 0xCB, 0x79)
color_scrollhandle = (0x8A, 0x8A, 0x8A)


def handle_cv2_image(image):
    if isinstance(image, str):
        img = cv2.imread(image)
    else:
        img = np.array(image)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img


def find_contours(image, color):
    img = handle_cv2_image(image)
    target_color = np.array(color[::-1])
    mask = cv2.inRange(img, target_color, target_color)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def find_timeline(image, color):
    contours = find_contours(image, color)
    x = y = w = h = 0
    for contour in contours:
        if len(contour) == 4:
            x2, y2, w2, h2 = cv2.boundingRect(contour)
            if w2 > w and h2 > h:
                x, y, w, h = x2, y2, w2, h2
    return (x, y, x + w, y + h) if w else None


def find_handle(image, color):
    img = handle_cv2_image(image)
    target_color = np.array(color[::-1])
    mask = np.all(img == target_color, axis=-1)
    return next((x for x in range(img.shape[1]) if mask[0, x]), None)


def find_audioclip(image, color):
    contours = find_contours(image, color)
    if not contours:
        return None
    contour_combined = np.vstack(contours)
    x, y, w, h = cv2.boundingRect(contour_combined)
    return (x, y, x + w, y + h - 2)


def find_waves(image, color):
    image = handle_cv2_image(image)
    target_color = np.array(color[::-1])
    height, width, _ = image.shape
    # 找到所有目标颜色的像素
    mask = np.all(image == target_color, axis=-1)
    # 查找连续的条带
    start_positions = []
    current_start = None
    for x in range(width):
        if (
            mask[0, x]
            and x != 0
            and (
                len(start_positions)
                and x - start_positions[-1][1] >= 10
                or not len(start_positions)
            )
        ):  # 只有一行，因此直接使用 `0` 行
            if current_start is None:
                current_start = x
        else:
            if current_start is not None:
                start_positions.append((current_start, x - 1))
                current_start = None
    # 如果条带在行的末尾处仍然存在
    if current_start is not None:
        start_positions.append((current_start, width - 1))
    print(f'找到 {len(start_positions)} 个波条带')
    return start_positions


def find_hscroll(image, color):
    handle_start = find_handle(image, color)
    return handle_start + 24 if handle_start else None


def focus_window(title):
    window = gw.getWindowsWithTitle(title)
    if window:
        window[0].activate()
        print(f"{title} 已获得焦点")
    else:
        print(f"没有找到 {title} 窗口")


print('\n\033[9mFinal\033[0m Premiere Cut Pro\n')

ag.PAUSE = 0.03


while True:
    focus_window('Adobe Premiere Pro')
    time.sleep(0.1)
    # print('等你 1 秒')
    time_start = time.time()

    print('开始细细的切做臊子\n-----------------')
    ag.press('c', _pause=False)

    # 先定位每个波峰头，模拟点击上方时间轴，以柄左侧像素为基准查找柄位置，判断柄是否落在波峰头后，若是模拟按下键盘左箭头
    # 查找柄位置，模拟按下C，模拟点击剪辑，奇数次时模拟按下V，模拟Shift+点击柄右侧28px
    # 最后一点点滚动直到找不到柄，回去一点，重新再来，直到 rect_audioclip 为 None

    should_select = True
    is_first_time = True
    cut_count = 0

    while True:
        ag.PAUSE = 0.01
        img = ag.screenshot()

        rect_timeline = find_timeline(img, color_timeline)
        if not rect_timeline:
            print("未找到时间轴蓝框")
            break
        print(f"时间轴面板: {rect_timeline}")
        img_timeline = img.crop(rect_timeline)

        img_handle = img_timeline.crop(
            (
                1,
                img_timeline.height - 64,
                img_timeline.width - 2,
                img_timeline.height - 63,
            )
        )
        handle_x_init = find_handle(img_handle, color_timeline)
        print(f"柄 X: {handle_x_init}")
        rect_audioclip = find_audioclip(img_timeline, color_audioclip)
        if not rect_audioclip:
            print("未找到音频剪辑的波形")
            break
        print(f"音频剪辑: {rect_audioclip}")
        try:
            img_audioclip = img_timeline.crop(
                (
                    handle_x_init,
                    rect_audioclip[3] - 1,
                    rect_audioclip[2],
                    rect_audioclip[3],
                )
            )
        except:
            print('音频剪辑裁剪出错')
            break

        waves = find_waves(img_audioclip, color_audioclip)

        if not is_first_time and waves:
            del waves[0]

        if not waves:
            print('波形为空，尝试向右继续推时间轴')
            ag.click(
                rect_timeline[2] - 48,
                rect_timeline[1] + 64,
            )

        ag.PAUSE = 0.035
        for start, end in waves:
            if rect_timeline[0] + handle_x_init + start > rect_timeline[2] - 84:
                print('距离面板右边框太近，先滚动')
                break
            ag.click(
                rect_timeline[0] + handle_x_init + start,
                rect_timeline[1] + 64,
            )
            img_handle = (
                ag.screenshot()
                .crop(rect_timeline)
                .crop(
                    (
                        1,
                        img_timeline.height - 64,
                        img_timeline.width - 2,
                        img_timeline.height - 63,
                    )
                )
            )
            handle_x = find_handle(img_handle, color_timeline)
            if handle_x + 1 >= handle_x_init + start:
                print('柄跟波形重合了，左移一帧')
                ag.press('left')
                img_handle = (
                    ag.screenshot()
                    .crop(rect_timeline)
                    .crop(
                        (
                            1,
                            img_timeline.height - 64,
                            img_timeline.width - 2,
                            img_timeline.height - 63,
                        )
                    )
                )
                handle_x = find_handle(img_handle, color_timeline)
            # 切
            cut_count += 1
            ag.click(
                rect_timeline[0] + 1 + handle_x,
                rect_timeline[1] + rect_audioclip[1] - 32,
            )
            if should_select:
                # 间隔选择
                ag.press('v', _pause=False)
                ag.keyDown('shift', _pause=False)
                ag.click(
                    rect_timeline[0] + handle_x + 28,
                    rect_timeline[1] + rect_audioclip[1] - 32,
                )
                ag.keyUp('shift', _pause=False)
                ag.press('shift', _pause=False)
                ag.press('c', _pause=False)
            should_select = not should_select
        # 水平往后滚动到下一页
        # ag.click(rect_timeline[2] - 42, rect_timeline[3] - 28)
        ag.PAUSE = 0.01
        ag.moveTo(
            rect_timeline[0]
            + find_hscroll(
                img_timeline.crop(
                    (
                        0,
                        img_timeline.height - 28,
                        img_timeline.width,
                        img_timeline.height - 27,
                    )
                ),
                color_scrollhandle,
            ),
            rect_timeline[3] - 28,
        )
        while True:
            ag.mouseDown()
            ag.move(3, 0)
            ag.mouseUp()
            img_handle = (
                ag.screenshot()
                .crop(rect_timeline)
                .crop(
                    (
                        1,
                        img_timeline.height - 64,
                        img_timeline.width - 2,
                        img_timeline.height - 63,
                    )
                )
            )
            handle_x = find_handle(img_handle, color_timeline)
            if handle_x == None:
                ag.mouseDown()
                ag.move(-3, 0)
                ag.mouseUp()
                print(f'滚动过头，新的一页，目前切了 {cut_count} 个')
                break
        is_first_time = False

    ag.press('v', _pause=False)

    print(f'\n结束任务，{time.time() - time_start:.1f} 秒切了 {cut_count} 个')
    input('回车以继续切下一个\n')
