/**
 * GPTService - OpenAI GPT集成服务
 * 
 * TODO for teammate:
 * 1. 申请OpenAI API密钥
 * 2. 实现GPT API调用
 * 3. 优化prompt设计，生成更有诗意的回应
 * 4. 添加多语言支持（中文/英文）
 */

class GPTService {
  constructor() {
    // TODO: 添加你的OpenAI API密钥
    this.apiKey = 'YOUR_OPENAI_API_KEY_HERE';
    this.apiEndpoint = 'https://api.openai.com/v1/chat/completions';
  }

  /**
   * 生成哲学性的情感回应
   * @param {Object} emotionData - 情感分析数据
   * @returns {Promise<string>} GPT生成的回应文字
   */
  async generatePhilosophicalResponse(emotionData) {
    try {
      const { emotion, intensity, text } = emotionData;
      
      // TODO: 实现真实的GPT API调用
      console.log('Generating philosophical response for:', emotion);

      // 模拟响应 - 替换为真实的API调用
      const mockResponse = this.getMockPhilosophicalResponse(emotion);
      
      // 示例API调用框架：
      // const response = await fetch(this.apiEndpoint, {
      //   method: 'POST',
      //   headers: {
      //     'Authorization': `Bearer ${this.apiKey}`,
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify({
      //     model: 'gpt-4',
      //     messages: [
      //       {
      //         role: 'system',
      //         content: this.getSystemPrompt()
      //       },
      //       {
      //         role: 'user',
      //         content: this.getUserPrompt(emotion, intensity, text)
      //       }
      //     ],
      //     max_tokens: 100,
      //     temperature: 0.8,
      //   }),
      // });
      
      // const data = await response.json();
      // return data.choices[0].message.content;

      return mockResponse;
    } catch (error) {
      console.error('GPT response generation failed:', error);
      return this.getFallbackResponse(emotionData.emotion);
    }
  }

  /**
   * 生成系统提示词
   * @returns {string} 系统提示词
   */
  getSystemPrompt() {
    return `你是一个温暖、富有诗意的情感导师。
    请用简短（50-80字）、温暖、富有哲理的话语回应用户的情感状态。
    你的回应应该：
    1. 表达理解和共情
    2. 提供温和的智慧和启发
    3. 使用诗意的语言，但不过于复杂
    4. 给人以安慰和力量
    5. 避免说教，更多是陪伴和理解`;
  }

  /**
   * 生成用户提示词
   * @param {string} emotion - 情感类型
   * @param {number} intensity - 情感强度
   * @param {string} text - 用户说的话
   * @returns {string} 用户提示词
   */
  getUserPrompt(emotion, intensity, text) {
    const intensityText = intensity > 0.7 ? '强烈地' : intensity > 0.4 ? '明显地' : '轻微地';
    
    return `用户今天${intensityText}感到${emotion}。
    ${text ? `他们说："${text}"` : ''}
    请给出一个温暖、诗意的回应，让他们感到被理解和支持。`;
  }

  /**
   * 获取模拟的哲学回应（开发阶段使用）
   * @param {string} emotion - 情感类型
   * @returns {string} 模拟回应
   */
  getMockPhilosophicalResponse(emotion) {
    const responses = {
      happy: [
        "快乐如夏日暖阳，照亮心中每个角落。愿这份美好如涟漪般扩散，温暖更多的心灵。",
        "幸福是心灵的花朵，在此刻绽放得如此绚烂。珍藏这份纯真的喜悦，它是生命最美的礼物。",
        "你的笑容如春风拂面，带来无限生机。让这份快乐成为前行路上的明灯。"
      ],
      sad: [
        "眼泪是心灵的雨水，洗涤着内心的尘埃。雨后必有彩虹，你的坚强正在孕育新的希望。",
        "悲伤如夜色深沉，但请记住，最暗的时刻往往距离黎明最近。温柔地拥抱这份情感，它也是成长的一部分。",
        "每一滴眼泪都是珍贵的，因为它见证了你内心的真诚。给自己一些时间，让心灵慢慢愈合。"
      ],
      calm: [
        "宁静如湖水般清澈，映照着内心的安详。在这份平静中，你找到了与自己对话的空间。",
        "安静的心如同古井，深沉而智慧。在这份宁静中，生命的真谛正悄然显现。",
        "平静是心灵的港湾，让疲惫的灵魂得以休憩。享受这份珍贵的内心安宁。"
      ],
      angry: [
        "愤怒如火焰燃烧，但请记住，你有驾驭这团火的力量。让它成为改变的动力，而非毁灭的工具。",
        "怒气是内心力量的体现，说明你对不公有着敏锐的感知。深呼吸，让智慧引导这份力量。",
        "愤怒如暴风雨，来得猛烈，去得也快。风雨过后，天空会更加清澈。"
      ],
      excited: [
        "兴奋如星光闪烁，点亮了夜空的精彩。让这份热情成为追梦路上的燃料。",
        "激动的心如同奔腾的河流，充满着生命的活力。愿这份能量带你到达更高的山峰。",
        "兴奋是生命的交响乐，在此刻奏响最动人的乐章。让这份美好感染每一个明天。"
      ]
    };

    const emotionResponses = responses[emotion] || responses.calm;
    return emotionResponses[Math.floor(Math.random() * emotionResponses.length)];
  }

  /**
   * 获取备用回应（API失败时使用）
   * @param {string} emotion - 情感类型
   * @returns {string} 备用回应
   */
  getFallbackResponse(emotion) {
    const fallbacks = {
      happy: "愿你的快乐如阳光般温暖，照亮每一个平凡的日子。",
      sad: "给自己一个温暖的拥抱，每一份情感都值得被温柔对待。",
      calm: "在这份宁静中，你找到了内心最真实的自己。",
      angry: "深呼吸，让内心的风暴慢慢平息，智慧会指引方向。",
      excited: "让这份美好的能量，成为你前行路上的明灯。"
    };

    return fallbacks[emotion] || "每一份真实的情感，都是生命中珍贵的色彩。";
  }

  /**
   * 生成每日情感总结
   * @param {Array} dailyEmotions - 一天的情感记录
   * @returns {Promise<string>} 每日总结
   */
  async generateDailySummary(dailyEmotions) {
    // TODO: 实现每日情感总结功能
    console.log('Generating daily summary for emotions:', dailyEmotions);
    
    // 模拟总结
    return "今天的你如同四季更迭，体验了情感的丰富层次。每一种感受都是成长路上的足迹，值得被记录和珍藏。";
  }
}

export default new GPTService();
