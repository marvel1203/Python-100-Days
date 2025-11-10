# Awesome ADB 学习笔记

> 原文仓库：[mzlogin/awesome-adb](https://github.com/mzlogin/awesome-adb)（MIT 许可）
>
> 本文档仅作为项目内部学习资料，版权归原作者 [Zhuang Ma](https://github.com/mzlogin) 所有。
>
> 如需获取完整、最新内容，请访问原始仓库。

我们已经在 `docs/adb/awesome-adb.md` 保存了一份当前版本的原文，配套许可在 `docs/adb/awesome-adb.LICENSE`。

如需获取最新内容，可在线访问：

- [GitHub 上的原始 README](https://github.com/mzlogin/awesome-adb/blob/master/README.md)

若只需快速了解常用命令，可参考本项目稍后补充的摘要文档（TODO）。

---

## 快速命令摘录

> 以下命令来自原文，仅保留最常用的 adb 操作，便于现场教学或排障使用。

- 查看设备：`adb devices`
- 连接无线设备（Android 11+）：

  ```sh
  adb pair <ipaddr>:<port>
  adb connect <ipaddr>:<port>
  ```

- 安装 / 卸载应用：

  ```sh
  adb install <apk-path>
  adb uninstall <package>
  ```

- 查看日志：

  ```sh
  adb logcat
  adb logcat "*:W"
  ```

- 文件互传：

  ```sh
  adb pull /sdcard/file ./local
  adb push ./local/file /sdcard/
  ```

- 截屏/录屏：

  ```sh
  adb exec-out screencap -p > screen.png
  adb shell screenrecord /sdcard/demo.mp4
  ```

- 重启到特定模式：

  ```sh
  adb reboot
  adb reboot recovery
  adb reboot bootloader
  ```

更多细节、注意事项和进阶玩法请参考原作者的 README。
