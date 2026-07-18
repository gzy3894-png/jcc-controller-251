# JCC Controller 2.5.1

你给的 **原版约 39MB JCC Controller（2.5.0）** 的「当前赛季数据」更新包。

## 这才是你要的东西

| | 之前推的 jcc-shell 2MB | **这个** |
|--|----------------------|---------|
| 是什么 | 另做的小壳 | **原 2.5.0 那个大 App** |
| 界面/图标 | 没有原版浮层 | **原版 UI 全保留** |
| 体积 | ~2MB | **~38MB** |
| 改了什么 | 全新小工程 | **只换了失效的 libJCC.so** |

## 下载

见 [Releases](https://github.com/gzy3894-png/jcc-controller-251/releases) 里的  
JCC-Controller-2.5.1.apk

## 安装

1. 卸载旧版 Controller（如有）
2. 安装本 APK（debug 签名，允许未知来源）
3. Root 后按原来 2.5.0 的方式启动注入
4. 进大厅看牌库

## 功能进度（实话）

- **已更新：** 读英雄表/牌库列表（新赛季字段）
- **界面还在但数据可能不全：** 对局叠层、剩余张数等原 SO 高级能力，新核心库还在补
- 目标：继续把原 2.5.0 功能按新数据接回去

## 技术说明

- 底包：你提供的 JCC Controller.apk
- 替换：ssets/emu/libJCC.so → 2.5.1 赛季 SO（真机扫描偏移）
- 签名：debug keystore（可自行重签）
