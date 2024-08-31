# Premiere Cut Pro

Premiere Pro 剃刀自动化，加速 **YTPMV / 音 MAD** PV 制作

启发自 [Otomad Helper for Vegas](https://github.com/otomad/OtomadHelper)、[om midi for After Effects](https://github.com/otomad/om_midi)

使用图像识别和模拟输入，对照音频波形裁剪视频剪辑，隔一个选一个，方便左右抽效果的制作

## 演示

细细的切做臊子

https://github.com/user-attachments/assets/eff4215a-357d-4d50-b25d-987cd28fe085

## 开始使用

### 环境

Windows 11，Python 3.12，Adobe Premiere Pro 2024

```powershell
pip install opencv-python numpy pyautogui pygetwindow
```

### 参数

修改 `cut.py` 中的三个颜色值为自己的用户界面设置

```python
color_timeline = (0x3D, 0xBD, 0xFF) # 面板焦点框的亮蓝色
color_audioclip = (0x9E, 0xCB, 0x79) # 音频剪辑中波形的浅绿色
color_scrollhandle = (0x8A, 0x8A, 0x8A) # 滚动条两侧可拖拽柄的边框浅灰色
```

此外还使用了大量硬编码数值，请根据运行结果自行调整

### 运行

仅保证在类似演示视频情况下的正常使用

确保 Adobe Premiere Pro 此时的输入法为英文状态，脚本将自动获得其窗口焦点

```powershell
python cut.py
```

## 说明

代码质量和可扩展性很差，编写目的仅为解决个人视频创作需要，获得的支持亦会有限
