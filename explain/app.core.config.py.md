# `app/core/config.py` 详解

这个模块负责把 YAML、`.env` 和默认值合并为类型安全的 `Settings`。非秘密、需要版本管理的参数放 YAML；密钥和环境差异放 `.env`。这是 Twelve-Factor App 的常见配置分离方法。

`PROJECT_ROOT` 从当前文件向上两级得到仓库根目录，避免程序从不同工作目录启动时找错文件。各个 `*Config` 模型对应 `settings.yaml` 的一个区域，使 IDE 能补全 `settings.rag.chunk_size`。`Settings.project_path()` 把项目相对路径解析成绝对路径，集中处理路径基准。

`load_settings()` 使用 `lru_cache(maxsize=1)`，同一进程只读一次磁盘；Streamlit 每次交互会重跑脚本，这能避免重复解析。函数先加载 `.env`，再读 YAML，然后用环境变量覆盖 `demo_mode`、运行环境和 OpenAI 网关。最后 `model_validate` 会在启动阶段暴露类型错误，而不是运行到某次请求才失败。

测试更改环境变量后要调用 `load_settings.cache_clear()`。生产中可进一步接 Vault/KMS，但不要把密钥写回 Settings YAML 或日志。常见错误是以当前工作目录拼路径、用字符串判断布尔值、让配置缓存导致测试互相污染。
