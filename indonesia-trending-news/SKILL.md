---
name: indonesia-trending-news
description: Search and aggregate trending news related to female entrepreneurship in Indonesia. This skill should be used when gathering current events, market trends, or hot topics relevant to Indonesian female business owners, KOCs, and e-commerce sellers.
---

# Indonesia Trending News

Search and aggregate trending news related to female entrepreneurship, KOCs, and e-commerce in Indonesia.

## When to Use

- Gathering daily hot topics for content creation
- Finding current events relevant to Indonesian female entrepreneurs
- Researching market trends in Indonesian e-commerce
- Discovering viral topics in the Indonesian creator economy

## Search Strategy

### Primary Search Queries (Indonesian)

Use these search queries to find relevant news:

1. **Female Entrepreneurship**
   - `wanita wirausaha Indonesia 2024` (female entrepreneurs Indonesia)
   - `UMKM wanita sukses` (successful female SMEs)
   - `bisnis online wanita Indonesia` (women's online business)

2. **E-commerce & Live Selling**
   - `TikTok Shop Indonesia seller`
   - `live streaming jualan Indonesia`
   - `Shopee Live seller tips`

3. **Creator Economy**
   - `KOL KOC Indonesia berita` (KOL/KOC Indonesia news)
   - `content creator wanita Indonesia`
   - `influencer marketing Indonesia`

4. **Business Trends**
   - `tren bisnis Indonesia 2024`
   - `peluang usaha wanita`
   - `brand lokal Indonesia sukses`

### News Sources Priority

| Source | Type | Focus |
|--------|------|-------|
| Kompas.com | Major news | Business, economy |
| Detik.com | Major news | Trending, viral |
| Bisnis.com | Business | Entrepreneurship |
| Kontan.co.id | Business | Finance, SMEs |
| TechInAsia | Tech | Startups, e-commerce |
| DailySocial | Tech | Digital economy |

## How to Search

### Using WebSearch

```
Search for: "wanita wirausaha Indonesia 2024 berita terbaru"
```

Then use WebFetch to get article details from relevant results.

### Using Firecrawl MCP (if available)

For deeper content extraction:

```bash
# Use firecrawl to scrape and extract article content
```

## Search Workflow

1. **Morning Search** (for daily script):
   - Search 2-3 primary queries
   - Focus on news from last 24-48 hours
   - Filter for relevance to target audience

2. **Evaluate Results**:
   - Relevance to female entrepreneurs/KOCs (1-10)
   - Emotional resonance potential (1-10)
   - Controversy/discussion potential (1-10)
   - Alignment with Lina Lie's expertise (1-10)

3. **Select Top Story**:
   - Choose 1 news item with highest combined score
   - Extract key facts and angles
   - Identify connection to audience pain points

## Output Format

Structure search results as:

```
## Today's Trending Topic

### Selected News
- **Headline**: [News title]
- **Source**: [Publication name]
- **Date**: [Publication date]
- **URL**: [Link]

### Summary
[2-3 sentence summary of the news]

### Relevance Analysis
- **Target Audience Connection**: [How this relates to Indonesian female KOCs]
- **Pain Point Alignment**: [Which pain point category this touches]
- **Content Angle**: [How Lina Lie can discuss this topic]

### Key Talking Points
1. [Point 1]
2. [Point 2]
3. [Point 3]

### Suggested Hook
[A hook question or statement based on this news]
```

## Example Search Session

```
1. WebSearch: "wanita wirausaha Indonesia Januari 2024"
   → Found: "Jumlah UMKM wanita naik 30% di 2023"

2. WebSearch: "TikTok Shop Indonesia seller update"
   → Found: "TikTok Shop tutup, seller beralih ke platform lain"

3. Evaluate:
   - Story 2 more relevant (TikTok Shop changes)
   - Higher emotional impact (sellers affected)
   - Aligns with monetization pain point

4. Select Story 2 for daily script
```

## Integration with Other Skills

This skill provides input for:
- `tiktok-script-generator`: Trending news becomes the content topic
- `daily-content-orchestrator`: First step in the daily workflow
- `koc-pain-points-researcher`: News helps identify which pain points to query
