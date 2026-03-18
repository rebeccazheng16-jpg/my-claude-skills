# Daily Content Workflow Reference

## Detailed Workflow Steps

### Pre-Flight Checks

Before running the daily workflow:

1. **NotebookLM Authentication**
   ```bash
   cd ~/.claude/skills/notebooklm && python3 scripts/run.py auth_manager.py status
   ```
   If not authenticated, run setup first.

2. **Lark Webhook Test**
   ```bash
   python3 ~/.claude/skills/lark-webhook-sender/scripts/send_message.py \
     --webhook "https://open.larksuite.com/open-apis/bot/v2/hook/00653044-07ab-4b45-a1aa-b8cda5c93484" \
     --text "Test message - Daily Script System"
   ```

3. **Persona Data**
   ```bash
   cat ~/.claude/skills/founder-persona-manager/data/personas.json | jq '.personas[0].name'
   ```

### Step 1: News Search Strategy

**Primary Search Queries (rotate daily):**

| Day | Focus Area | Search Query |
|-----|------------|--------------|
| Mon | E-commerce trends | `tren e-commerce Indonesia 2024` |
| Tue | Success stories | `wanita wirausaha sukses Indonesia` |
| Wed | Platform updates | `TikTok Shop Shopee update Indonesia` |
| Thu | Business tips | `tips bisnis online wanita` |
| Fri | Challenges/pain | `tantangan UMKM wanita Indonesia` |
| Sat | Inspiration | `motivasi entrepreneur wanita` |
| Sun | Weekly recap | `berita bisnis minggu ini Indonesia` |

**Evaluation Criteria:**

Score each news item 1-10:
- Relevance to female KOCs
- Emotional resonance potential
- Discussion/controversy value
- Alignment with Lina's expertise

Select the highest combined score.

### Step 2: Pain Point Mapping

**News Topic → Pain Point Category:**

| News Topic | Pain Point Category | Query Keywords |
|------------|--------------------|--------------​-|
| Algorithm changes | Identity anxiety | algorithm, reach, engagement |
| Platform policy | Legal/compliance | regulation, policy, rules |
| Success stories | Monetization | income, profit, conversion |
| Market trends | Career direction | pivot, opportunity, growth |
| Creator burnout | Mental health | stress, burnout, overwhelm |
| Work-life content | Family balance | sandwich generation, time |

### Step 3: Script Assembly

**Template Structure:**

```
# Daily Script - [DATE]

## Research Summary
- **News Source**: [Publication]
- **Headline**: [Title]
- **Pain Point Match**: [Category]

## Script Draft

### HOOK ([X] seconds)
[Selected hook type]: [Hook text]

### BODY ([X] seconds)

**Konteks** ([X]s):
[News context adapted for audience]

**Insight** ([X]s):
[Lina's perspective based on experience]

**Tips** ([X]s):
[One actionable takeaway]

### CTA ([X] seconds)
[Engagement prompt]

## Quality Checklist
- [ ] Hook stops the scroll
- [ ] Body provides real value
- [ ] CTA feels natural
- [ ] Language is conversational Indonesian
- [ ] Tone matches persona
- [ ] No AI-sounding phrases
- [ ] Under 1 minute when read aloud

## Full Script
[Complete text for recording]
```

### Step 4: Quality Review Points

Before sending to Lark:

**Content Check:**
- Does it address a real pain point?
- Is the advice actionable?
- Does it sound like Lina speaking?

**Language Check:**
- Is Indonesian conversational (not formal)?
- Are sentences short and punchy?
- No awkward translations?

**Persona Check:**
- Does it reflect her ENFP personality?
- Does it leverage her beauty industry experience?
- Is the tone inspiring but practical?

### Step 5: Lark Message Format

**Card Structure:**
```json
{
  "title": "🎬 Lina Lie Daily Script - YYYY-MM-DD",
  "sections": [
    "Topic + Pain Point",
    "Script Sections",
    "Full Read-through",
    "Timestamp"
  ]
}
```

## Timing Guidelines

| Step | Estimated Time |
|------|----------------|
| News search | 2-3 minutes |
| Pain point query | 1-2 minutes |
| Script generation | 3-5 minutes |
| Quality review | 2-3 minutes |
| Lark push | <1 minute |
| **Total** | **10-15 minutes** |

## Error Recovery

### News Search Fails
- Fallback to evergreen topics
- Use previous day's backup news
- Focus on timeless pain points

### NotebookLM Unavailable
- **首选**: 使用本地痛点JSON文件
  ```bash
  cat ~/.claude/skills/koc-pain-points-researcher/data/pain-points.json | jq '.categories'
  ```
- Reference the pain point categories in skill docs
- Generate script with general pain point

### Lark Push Fails
- Save script locally first
- Retry with exponential backoff
- Manual copy-paste as last resort
