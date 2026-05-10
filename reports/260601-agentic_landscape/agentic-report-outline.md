# 主题：Towards inclusive AGI: An Overview of Agentic AI's Past and Future in the Middle of 2026

## 需求
1. 你是一个基于详实数据进行分析、观察和总结的 AI 生态研究者；
2. 在需要进行数据补充的地方，我会用 xx() 作为占位，其中，xx 是需要补充的数字，用（）中的提示或者结合上下文寻找获得数据的方法。
3. 在 2026 年 5 月底的时间，蚂蚁开源会再次发布生态洞察，站在这个时间节点，基于开发者生态产生数据和社会（硅谷一线、创业公司等）新闻，对大模型生态、 Agentic AI 的现状、过去和未来发布相关研究报告；
4. 在内容撰写上，你不能只做一个冰冷的数字观察者，而是要在详实数据辅助的基础上，用具备人文关怀的文字风格撰写文章，文笔一定要朴实、简单，具有人情味；
5. 随时进入 DeepResearch 模式，在需要的时候深度调查产业，进行必要的引用，在下面的 outline 中，我也会在一些地方提示你可以阅读相关文章作为参考；

## Outline

1. 对去年整体的大模型开发生态的回顾
基于 /20250527_llm_landscape 和 /20250913_llm_landscape 的内容，对 2025 年大模型开发生态，我们的观点，洞察，做一个简要的总结。

主要思考：从 24 年到现在，我们看到了很多的项目出现，迅速火爆，取得大量的关注，又昙花一现，这种情况在应用端尤其常见（举一两个例子）。而来到 2026 年，我们感受到似乎黑客松要结束了，因为以开发者为主要生产力的软件生产模式，似乎要被极大的颠覆了。

整体的数字：
- 2026 年刚过去的这 4 个月里，GitHub 上的仓库数量增长了 xx 个（Clickhouse 查询，也可以寻找下 GitHub Octoverse 报告有没有披露），开发者（账号）新增了 xx 个，GitHub APP 的数量新增了 xx 个，这些数据和过去五年的同比数量的曲线如何，反映了什么？
- 参考 /260401_agentic_landscape 中的报告分析方式，一段简短的说明，看看 26 年（1月到4月），头部 star 数增长最多，和活跃度最高的项目，都是什么。

2. 黑客松结束了，软件会走向何方？

阅读文章：https://mp.weixin.qq.com/s/kwErGjX231e2efVWhERzTw

我们在去年把大模型开发生态形容为一场真实世界的黑客松，今年，而从去年 11 月份（验证具体时间），以 Opus 5.4 为代表的能力让我们感到了一切的再一次加速，甚至大有越过了比赛的终点意味，颠覆还是终结？蒸汽机已经被发明出来，虽然跑的还没那么稳定，但所有人都知道会比马更快，有人说软件工程已死，开源已死。究竟是一种终结还是颠覆？未来的生产模式和消费模式，会是怎样的？


a16z 曾说软件吞噬世界，开源吞噬软件，现在，模型要吞噬软件和开源了？（查一下 a16z 有没有相关观点可以引用）软件被加速颠覆的同时，模型厂商之间军备竞赛式的发布没有停止，但是牌桌上的模型玩家正在明显收敛，我们也见证了御三家的形成，国内六小虎的繁荣，智谱作为模型第一股地抢跑，inclusionAI 的百灵 Elephant 神秘模型登上了openrouter的调用榜单。这里统计下 OpenRouter 的模型榜单，核心观点：今年，性能刷榜也许不那么具有说服力，模型 API 调用量体现了用户的用脚投票。

阅读 OpenRouter 报告：https://openrouter.ai/state-of-ai

[大模型全景图：美国御三家 Gemini、Claude、OpenAI，中国 inclusionAI、Qwen、字节 Seed、zhipu、kimi、minimax]

关于软件开发的范式，spec driven swe-AI革命到了哪一步？未来走向哪？


3. 2026 年的 Agentic AI 生态

今年的整体思路是，不再做静态的完整项目列表的大图展示，而是用排行榜来动态追踪战场上的厮杀和赛马，而对于生态的 landscape，由于它的迅速变化和不稳定性，我们重点用 taxonomy 来突出架构（这一套分类体系是模型基于项目的 topics 的描述动态生成的），每个体系下的top1～3个项目示意（也可以放头部闭源）。至于完整的项目都有哪些值得关注，可以移步 inclusionAI 官网上的 agentic ai 生态排行榜，每一个项目都有单独的面板和开发者的详情。

大的架构图分层（可以参考 ai-landscape-full-stack.html）：
- Application Layer
- Agent Layer
- Model Layer
- Model Infra Layer
- Hardware & Compilers

每一层都给出一些生态上的玩家和数据分析，可以引用市场占有率、社区活跃度等丰富的数据维度，并且给出开源的战略；有一些可以参考引用的材料：

- Hardware层参考引用 GTC 2026 上黄仁勋的演讲，并看看其他厂商（AMD、Intel、TPU 和国产算力平头哥、CANN 等发展情况），给出主要的编译器生态，解读开源战略；
- Infra层参考阅读：1. https://mp.weixin.qq.com/s/8TYMn2DVE6vTo4xL64CkJA；2. https://mp.weixin.qq.com/s/_8vfcc0Ly8Au-NnMTO-BPw；讲推理，算力，token 的故事，算力的价值流动，生产端，消费端（阿里成立ATH事业群，NVIDIA的动作）
- 模型层是这场变革的核心，关于模型的讨论网上也很多了，从机器之心、InfoQ AI 前线、量子位等扒一些高质量内容和最新新闻，总结一下趋势和产业现状，给我一些有意思的观点来参考。拼性能榜单还是拼 API 调用？受众在 C 端还是 B 端？大家都在卷 Coding 能力？
- Agent 和应用层是更群智群力的地方，是大家共同期望的 AGI 的最终实现，这里不像模型和infra那么烧钱，玩家更多一些，是泛开发者群体主要聚集的地方，也是我们从社区数据能分析到的最多的地方，选几个头部的热门的项目深挖一下。
  
4. Agentic， AGI，ASI
结合热门项目，数据辅助，做宏观和微观的分析
有几个思考 ：
- Coding - coding plans 频频售罄，rate limit 频繁触及，coding agent 项目大爆发，这是当下最热的场景。
- 编码即世界吗？如果 coding 能力足够强，是不是在别的生活的场景也会做的足够好？还有哪些场景会率先落地，或者已经落地？payment？生活服务？甚至于具身到了哪一步？
- AI 辅助之下，会成为全民构建的时代吗。软件开发之外，社会的生产结构、消费结构会被 AI 改变成什么样子？

参考阅读：https://mp.weixin.qq.com/s/VFf1B1CaCicegOA3tykuaA（一篇我认为非常制造焦虑的文章）


5. AI Built by everyone, for everyone

这里会回到蚂蚁的 AI Initiative——Inclusion AI，给出 inclusionAI 的架构图和主要叙事，前面可能讲了 AI 给大家带来的焦虑，无论是硅谷精英、Researcher们还是普通人，似乎都无法幸免，最后我们把情绪从 AI fomo 拉回到技术普惠，回到inclusive agi的叙事，回到垂类场景在通用模型场景通吃下的挣扎和思考（医疗、金融）开放、共享。


[一张iai的架构图]

这是 inclusionAI 的一篇叙事博客：https://yuque.antfin.com/ospo/growth/psxgeiqeg41ll5cz。