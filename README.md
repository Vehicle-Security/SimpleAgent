
## 开发一个基本功能的Agent

学习资料：  
AGENT AI: SURVEYING THE HORIZONS OF MULTIMODAL INTERACTION  
https://arxiv.org/pdf/2401.03568  

Agent Getting Start  
https://github.com/e2b-dev/awesome-ai-agents  
开发一个简单的agent  
https://medium.com/ai-agent-insider/build-an-ai-agent-from-scratch-2796150db2b2  
https://www.newsletter.swirlai.com/p/building-ai-agents-from-scratch-part  

### 功能描述  

agent能执行简单任务，任务会出错，需要多轮次交互，例如：  
- 调用gcc编译c代码  
- 实现C++代码到rust代码的转写
  
实现多个agent交互，例如：  
- agent-1：负责修改代码错误  
- agent-2：负责调用gcc编译  

### Demo 规划
1. Leetcode Agent，给一个算法题（例如：八皇后），让agent生成C/C++ Solution，然后自动编译代码，用几个测试用例本地验证正确性
- 生成代码
- 编译C （简单起见暂时只支持C）
- 修正编译错误/题目错误

2. C/C++到Rust的代码转写
- 继续将上面的C solution转成Rust，修复错误直到编译成功，并且验证功能 

3. 路由器固件漏洞验证Agent （hy负责）
- 解析漏洞分析结果，生成请求http post request
- 调用qemu运行固件，解决网络、账号等运行环境依赖，
- 测试request看是否crash
  
5. 漏洞识别、修复、验证Agent（科研项目，TODO） 
     


## Requirements


- 本地 Ollama
- python3.9
- python requests库、json库

### Ollama使用
安装：  
`curl -fsSL https://ollama.com/install.sh | sh`

安装模型：  
ollama pull llama3.2
