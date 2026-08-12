# `tests/test_config.py` 详解

这个测试先清除 `load_settings` 缓存，再读取真实 YAML，验证应用名和 `overlap < size`。它属于配置冒烟测试：能提前发现 YAML 缩进、字段改名或不合理切分参数。清缓存是为了测试不依赖其他用例曾经加载的对象。
