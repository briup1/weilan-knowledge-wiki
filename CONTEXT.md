# Agent Evaluation Platform

企业内部 Agent 质量评测领域词汇表。需求、方案和后续实现统一使用以下术语。

## Language

**Agent**:
被测试的、能够接收用户任务并生成回答或调用工具完成任务的软件主体。
_Avoid_: 机器人、模型

**Scenario**:
描述一个待验证用户目标、输入过程和风险点的测试资产，是评测意图的源头。
_Avoid_: 测试问题、Query

**Expected Toolflow**:
Scenario 对 Agent 工具执行过程的期望，包括工具、关键参数、轮次以及禁止行为。
_Avoid_: 标准调用脚本、唯一正确轨迹

**Expected Answer**:
Scenario 对用户可见回答的语义期望，包括必须满足、不得出现和需要澄清的内容。
_Avoid_: 标准答案、Reference Output

**Real Session**:
Agent 执行一个 Scenario 后产生的多轮回答和工具调用事实记录。
_Avoid_: Benchmark、测试用例

**Run**:
某个确定版本的 Agent 在确定评测条件下执行一次 Scenario 所产生的评测实例。
_Avoid_: Session、批次

**Benchmark Set**:
为了共同评测目标而组织的一组已治理 Scenario。
_Avoid_: Run、报告

**Baseline**:
经过批准、用于和候选版本比较的 Agent 版本及其完整评测条件。
_Avoid_: run-00、参考回答

**Candidate**:
等待与 Baseline 比较并作出质量判断的 Agent 版本及其完整评测条件。
_Avoid_: 新模型、单次 Run

**Evaluation Case**:
可被评估器消费的统一评测载体，关联输入、实际输出、预期、内部证据和评测上下文。
_Avoid_: DeepEval LLMTestCase、测试问题

**End-to-End Evaluation**:
把完整 Agent 交互作为一个整体，评价系统输入到用户可见结果及必要终态。
_Avoid_: Component Evaluation、单轮评估

**Component Evaluation**:
以 Trace 中一个明确内部 Span 为对象，评价 LLM、Tool、Retriever、Memory 或子 Agent 等组件行为。
_Avoid_: End-to-End Evaluation、白盒单元测试

**One-Off Debug Evaluation**:
开发者针对一个 Evaluation Case 临时执行一个 Evaluator，以定位或验证具体问题，不自动成为正式回归结论。
_Avoid_: Official Regression、批量 Benchmark

**Toolflow Evaluation**:
依据 Expected Toolflow 判断 Agent 的工具执行过程是否符合要求。
_Avoid_: 回答评分、综合评分

**Answer Evaluation**:
依据 Expected Answer 判断 Agent 的用户可见回答是否满足语义要求。
_Avoid_: Toolflow Evaluation、字符串匹配

**Stability**:
同一 Agent 版本和评测条件下，多次 Run 的质量结论及关键指标保持一致的程度。
_Avoid_: 单次得分、Baseline 对比

**Regression**:
Candidate 相比 Baseline 在相同可比 Scenario 和评测规则上出现能力下降。
_Avoid_: 任意失败、低分

**Review Scenario**:
具备执行和评估条件、但尚未被批准进入正式回归范围的 Scenario。
_Avoid_: 草稿问题、Official Scenario

**Official Scenario**:
已经责任人批准、会纳入正式回归结论的 Scenario。
_Avoid_: 任意可运行 Scenario、Golden Answer
