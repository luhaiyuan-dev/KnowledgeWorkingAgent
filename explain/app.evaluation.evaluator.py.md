# `app/evaluation/evaluator.py` 详解

`ResponseEvaluator` 提供无需另一个 LLM 的确定性基础评估。`EvaluationResult` 包含 citation_coverage、has_answer、grounded_format_ok 和 notes。

`evaluate()` 对普通回答只检查非空；对 knowledge/combo 路径，如果没有引用，则只有明确说“证据不足”才算格式合规。存在引用时，统计回答中实际出现的 `[Sx]` 占返回引用总数的比例。这个指标发现“检索有来源但回答忘记标注”的问题。

它不能判断事实是否真的被引用片段支持，也不能替代人工评测。完整评估应有黄金问答集，测 retrieval recall@k、答案正确率、引用忠实度、越权率、注入成功率、延迟和成本。LLM-as-judge 可辅助，但要防止评委偏差，并用人工样本校准。
