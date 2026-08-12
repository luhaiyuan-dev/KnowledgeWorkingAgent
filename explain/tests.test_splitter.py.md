# `tests/test_splitter.py` 详解

测试构造超过 120 字的中文段落，要求切成多个不超上限的块，并保留 chunk_index。它同时守护切分参数和 metadata。没有断言每个断句完全一致，是为了避免对 LangChain 内部细节过度耦合。
