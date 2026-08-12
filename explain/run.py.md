# `run.py` 详解

这是给初学者的一键入口。`PROJECT_ROOT` 固定工作目录，`main()` 用当前 Python 解释器执行 `python -m streamlit run ui/app.py`。使用 `sys.executable` 能确保调用的是刚安装依赖的虚拟环境，而不是系统另一个 Python。

`subprocess.call` 会把退出码传回，便于脚本或 CI 判断启动失败。这里没有 `shell=True`，避免不必要的命令注入和转义问题。也可直接执行 Streamlit 命令；保留 run.py 是为了 README 命令更统一。
