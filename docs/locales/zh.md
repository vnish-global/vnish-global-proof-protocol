---
layout: default
title: VNISH GLOBAL Proof Protocol 简体中文快速入门
lang: zh-CN
---

# VNISH GLOBAL Proof Protocol：简体中文快速入门

使用 `vnish-verify` 将本地文件与带版本的清单进行比对。该命令只在本地计算哈希值，不会下载固件。

```console
vnish-verify /path/to/local-file.tar.gz --json
```

- `MATCH`：有且仅有一条记录的 SHA-256、字节数和指定筛选条件相符。
- `NO_MATCH`：没有相符记录；请停止操作，并重新检查文件和信息。
- `AMBIGUOUS`：有多条记录相符；请补充准确的版本、型号、控制板和安装方式。
- `SOURCE_UNAVAILABLE`：无法读取或验证文件或清单。

`MATCH` 不代表安全性或适用性已经得到确认。变更前请核对准确型号、控制板、安装方式和恢复路径。

- VNISH GLOBAL 数据与验证方法：<https://vnish.global/zh/data/>
- VNISH Ninja 恢复路径：<https://vnish.ninja/zh/recovery/>
- ROI ASIC 分阶段部署方案：<https://roiasic.com/zh/enterprise/>

协议版本：0.1.0，2026 年 8 月 13 日。

[返回现场手册](../index.md)
