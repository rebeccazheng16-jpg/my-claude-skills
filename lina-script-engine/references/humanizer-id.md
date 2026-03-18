# 印尼语去 AI 味规则

> 来源：content-reviewer/data/methodology-index.json 中的 humanizer-id 规则

## 5 条核心处理原则

1. **删除填充短语**：去除开场白和强调性拐杖词
2. **打破公式化结构**：避免二元对比、戏剧性分段、修辞性设置
3. **变化句子节奏**：长短交替，两项优于三项
4. **信任读者**：直接陈述，不过度解释
5. **删除名言金句感**：如果听起来像格言警句，重写（但保留符合 Lina 人设的自然金句）

## 24 种 AI 写作模式检测（印尼语适配）

参考 `humanizer-zh` skill 的完整模式列表，以下为印尼语特有规则：

### 过度外来词替换

| AI 偏好（外来词） | 自然替代 |
|----------------|---------|
| implementasi | pelaksanaan |
| signifikan | berarti |
| komprehensif | menyeluruh |
| infrastruktur | sarana |
| kontribusi | sumbangan |
| lanskap | — （直接删除，改用具体描述）|

### 减少被动结构

印尼语 di- 前缀被动句过多 = AI 痕迹：
- ❌ "Produk ini dibuat dengan teknologi terbaru"
- ✅ "Kami bikin produk ini pakai teknologi terbaru"

### Lina 的印尼语口语特征

生成印尼语时，注入这些自然表达：
- "Jadi gini..." (所以是这样...)
- "Yang paling penting itu..." (最重要的是...)
- "Dari pengalaman aku..." (从我的经验来看...)
- "Kamu harus percaya..." (你一定要相信...)
- 称呼用 "aku/kamu" 而非 "saya/Anda"（更亲切）
- 适度使用 "sih"、"dong"、"kok" 等口语助词

## 5 维评分

| 维度 | 10 分标准 | 1 分标准 |
|------|---------|---------|
| 直接度 | 直截了当 | 充满铺垫 |
| 节奏 | 长短交错 | 机械重复 |
| 信任度 | 简洁明了 | 过度解释 |
| 真实性 | 自然流畅 | 机械生硬 |
| 简洁度 | 无冗余 | 大量废话 |

**标准**：≥45 优秀 / 35-44 良好 / <35 需重写
