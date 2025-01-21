
## 开发一个基本功能的Agent

学习资料：  
AGENT AI: SURVEYING THE HORIZONS OF MULTIMODAL INTERACTION  
https://arxiv.org/pdf/2401.03568  

Agent Getting Start  
https://github.com/e2b-dev/awesome-ai-agents  
开发一个简单的agent  
https://medium.com/ai-agent-insider/build-an-ai-agent-from-scratch-2796150db2b2  
https://www.newsletter.swirlai.com/p/building-ai-agents-from-scratch-part  

#### 任务描述  
agent能执行简单任务，任务会出错，需要多轮次交互，例如：  
- 调用gcc编译c代码  
- 实现C++代码到rust代码的转写  

实现多个agent交互，例如：  
- agent-1：负责修改代码错误  
- agent-2：负责调用gcc编译  

---

## Requirements


- 本地 Ollama
- python3.9
- python requests库、json库