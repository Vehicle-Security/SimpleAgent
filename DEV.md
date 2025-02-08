目标：打造开源安全Agent项目  

### Agent框架开发说明  
开发出最简agent框架，避免多余的代码的同时，满足基本扩展需求：  
- LLM API封装，能灵活的切换url和模型名，来使用deepseek、ollama和poe上其他模型  
- LLM Chatbot封装，能同一个context下多轮次对话  
- 基本agent封装，能执行命令  
- 能多个agent之间按照指定pipeline调用  

#### 开发步骤拆解  
> 交替实现Demo和优化LLM框架  

1. 简单LLM调用实现：gcc编译C, C到rust转写
  
2. 简单LLM框架封装，v0.1
   
3. 基于LLM框架，实现复杂Agent：Leetcode Agent

4. 优化LLM框架

#### 当前代码改进  
1. demos里面每个demo加简单的文档，写设计目标、实现思路、使用方法  
> 可以先完成由简单到难的几个agent demo，然后逐步去抽取为agent框架  
> 可参考这个：https://medium.com/ai-agent-insider/build-an-ai-agent-from-scratch-2796150db2b2  
> 注意利用python 3.12的高级特性，例如：dataclass，类型提示等  
> 使用pycharm开发  

2. 将agent框架抽取到agent目录，每个demo简单的调用agent公共接口，传入prompt配置agent执行的命令，来实现功能  

#### 功能参考  
收集目前最新的agent工作：  
- Evaluating Agent-based Program Repair at Google https://arxiv.org/pdf/2501.07531  
- PaSa: An LLM Agent for Comprehensive Academic Paper Search https://arxiv.org/pdf/2501.10120

