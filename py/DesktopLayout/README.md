# DesktopLayout

轻量级 Windows 桌面图标布局保存与恢复工具，使用 Python 标准库和 Windows Shell COM 接口实现。

提供“保存布局”和“恢复布局”两个操作，支持图标增删、网格变化和多显示器布局适配。无需管理员权限，不修改桌面文件内容、注册表或系统排列设置。

## 运行环境

- Windows 11 64 位，标准 Windows Explorer 桌面。
- Python 3.11+ 64 位，包含 `tkinter`。
- 无第三方运行时依赖。

## 使用

在项目目录运行：

```powershell
python main.py
```

也可在 VS Code 中选择 Python 解释器，打开 `main.py` 并运行。程序不需要命令行参数。

1. 整理桌面图标，点击 **保存布局**。
2. 图标位置发生变化后，点击 **恢复布局**。
3. 界面显示保存时间、图标数量和操作结果。

恢复前需关闭桌面右键 → 查看 → **自动排列图标**。**将图标与网格对齐**可以保持开启。

## 恢复规则

| 情况 | 处理方式 |
|---|---|
| 已保存且仍存在的图标 | 优先恢复保存的位置 |
| 已删除的图标 | 保留原位置的空位 |
| 新增图标 | 按名称自然排序，从当前主屏左上角按列填入空位，先上到下、再左到右 |
| 显示环境一致 | 优先恢复精确坐标 |
| 分辨率、工作区或网格变化 | 保持网格行列关系，为越界或冲突的图标重新分配位置 |

再次保存会以当前图标重新建立基准，清除已删除图标的保留位。恢复不会修改保存文件。

### 多显示器

布局类型由已保存图标的实际分布决定，与连接的显示器数量无关。

- **单屏布局**：所有图标集中在一台显示器上，恢复时整体映射到当前 Windows 主屏。主屏、显示器数量或设备变化不影响这一规则；主屏容量不足时可使用其他显示器。
- **跨屏布局**：图标分布在多台显示器上，按显示器设备接口标识匹配。增加显示器不影响已有匹配。若某个旧显示器无法匹配且仍有图标需要恢复到该屏，则停止恢复；该屏旧图标全部缺失时，忽略对应保留位。

新增图标始终优先使用当前主屏。跨屏布局中的旧图标仅在各自匹配的显示器内重新分配。

所有候选屏幕的普通空位不足时，才释放缺失图标的保留位。仍无法容纳全部图标则停止操作。

## 布局文件

布局以 UTF-8 JSON 保存，路径不受当前工作目录影响：

| 运行方式 | 保存与读取位置 |
|---|---|
| Python 源码 | `main.py` 同目录的 `layout.json` |
| 打包后的 EXE | EXE 同目录的 `layout.json` |

首次保存自动创建文件，再次保存原子替换旧文件。程序所在目录需要具有写入权限。

`layout.json` 包含桌面文件路径、图标名称和显示器设备标识，属于本地数据，已通过 `.gitignore` 排除。分享源码、压缩包或诊断输出时应排除个人布局信息。

## 实现概要

图标通过 Shell 解析路径识别：快捷方式使用 `.lnk` 文件自身的路径，系统图标使用 Shell 命名空间标识。显示名称用于展示和排序，不作为唯一身份。

位置读取与修改使用 `IFolderView::GetItemPosition` 和 `IFolderView::SelectAndPositionItems`。标准图标控件仅用于只读坐标校验，不通过 ListView 消息设置位置。程序启用 Per-Monitor V2 DPI 感知，区分 Shell 视图、屏幕、显示器局部和网格坐标。

恢复前完成整批位置计算，移动后回读检查目标位置、重叠和越界。部分失败时尝试恢复操作前的位置，并报告回退结果。

## 打包

在 Windows 上使用 64 位 Python 构建：

```powershell
python -m venv .venv-build
.\.venv-build\Scripts\python.exe -m pip install --upgrade pyinstaller
.\.venv-build\Scripts\python.exe -m PyInstaller --clean --noconfirm --onefile --windowed --name DesktopLayout main.py
```

输出为 `dist\DesktopLayout.exe`，运行时无需安装 Python。PyInstaller 仅用于构建。

布局文件作为外部数据保存在 EXE 旁边，不使用 `--add-data` 将其嵌入程序：

```text
DesktopLayout/
├── DesktopLayout.exe
└── layout.json
```

沿用已有布局或移动程序时，将 `layout.json` 一并复制到 EXE 所在目录。没有布局文件时，可启动程序后重新保存。

## 项目结构

```text
DesktopLayout/
├── main.py                 # Tkinter 界面、保存与恢复流程
├── shell_api.py            # Shell COM、显示器信息和坐标校验
├── layout.py               # 布局算法、JSON 校验与原子保存
├── tests/
│   ├── test_layout.py      # 算法、存储及事务测试
│   └── check_desktop.py    # 真实桌面检查
└── README.md
```

## 测试

运行自动化测试：

```powershell
python -m unittest discover -s tests -v
```

单元测试覆盖图标匹配、空位分配、多屏映射、网格适配、幂等性、JSON 校验及失败回退，使用模拟数据，不操作真实桌面。

运行 `tests/check_desktop.py` 可检查真实 Shell 接口。默认只读；将 `RUN_MOVEMENT_CHECK` 设为 `True` 后，会临时移动图标、验证恢复，并在结束时尝试还原原布局。测试期间应保持桌面和显示配置不变。

已验证真实桌面的图标枚举、批量移动、重复恢复及混合缩放双屏定位。显示器拔插、分辨率与缩放切换、重启后的持久性，以及打包后的 EXE，尚未完成完整实机验证。

## 限制

- 文件重命名按旧图标缺失、新图标增加处理，不追踪重命名历史。
- 显示器设备接口标识可能随端口或驱动变化；跨屏布局无法可靠匹配时需要重新保存。
- 第三方桌面替换和镜像显示模式不在支持范围内。
- 布局仅在点击恢复时应用，不提供开机自启、自动恢复或后台监听。

## 参考

- [IFolderView](https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nn-shobjidl_core-ifolderview)
- [SelectAndPositionItems](https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nf-shobjidl_core-ifolderview-selectandpositionitems)
- [Manipulating the positions of desktop icons](https://devblogs.microsoft.com/oldnewthing/20130318-00/?p=4933)
- [The correct way of manipulating desktop icon positions](https://devblogs.microsoft.com/oldnewthing/20211122-00/?p=105948)
- [PyInstaller runtime information](https://pyinstaller.org/en/stable/runtime-information.html)
