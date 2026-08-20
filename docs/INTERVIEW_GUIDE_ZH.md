# SignalOps 面试讲解指南

## 30 秒介绍

> 我使用 Python 开发了一个可解释的 AIOps 日志分析原型。系统读取多个服务的结构化日志，计算错误率和 P95 延迟，并与正常基线比较。它可以识别错误率突增、延迟异常和重复错误模式，再把同一服务的信号合并成一个事件并生成排查 Runbook。项目包含 pytest 测试、GitHub Actions 自动验证以及 GitHub Pages 可视化页面。

## 为什么做这个项目

> 我申请的岗位涉及日志分析、异常检测、智能告警和运维流程自动化。我的科研项目已经包含 Python 数据处理、规则判断、异常检查和参数验证，因此我希望把这些能力迁移到更接近云运维的日志场景中。

## 为什么没有直接使用机器学习

> 第一版选择规则和统计基线，是为了保证每个告警都可以解释和测试，也便于控制误报。系统的检测模块是独立的，后续可以增加统计模型或机器学习检测器，并与现有规则结果对比。

## 如何识别异常

> 系统先按服务计算当前窗口和基线窗口的错误率与 P95 延迟。如果当前错误率同时超过最低阈值和基线倍数，就生成错误率信号；延迟规则采用类似方式。重复错误规则则统计结构化错误码的出现次数。每个信号都保留 observed、baseline、threshold 和 evidence。

## 如何避免告警风暴

> 同一服务在同一分析窗口中的多个信号不会分别创建事件，而是按照服务进行关联，选择最高严重等级作为主事件，并把全部证据和排查步骤合并。

## 测试了什么

- 正确日志能否解析；
- 非法 JSON 是否明确报错；
- 错误率、延迟和重复错误能否同时触发；
- 完整分析是否生成预期的 checkout-api 事件和 Runbook。

## 诚实回答项目边界

如果被问到生产使用，应回答：

> 这是一个可运行的工程原型，目前使用合成日志和静态基线，还没有接入真实云平台。生产化需要增加流式输入、持久化、动态基线、权限控制、监控自身状态以及更完整的误报评估。

## 可写入英文简历的描述

**SignalOps — AIOps Log Monitoring and Intelligent Alerting Platform**  
*Python, GitHub Actions, Pytest, GitHub Pages*

- Built an explainable Python pipeline to parse structured service logs, calculate error-rate and P95-latency baselines, and detect abnormal operational behavior.
- Implemented rule-based signals for error spikes, latency degradation, repeated error patterns, and event-volume drops, retaining measured evidence and thresholds for each alert.
- Correlated service-level signals into prioritized incidents and generated deterministic investigation runbooks covering trace review, recent changes, and upstream dependencies.
- Added automated parser, detector, and integration tests and configured GitHub Actions to regenerate the report and publish a responsive operational dashboard.
