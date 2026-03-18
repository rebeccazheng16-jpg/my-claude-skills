#!/usr/bin/env python3
"""
Lina Content Analyzer - 分析脚本
执行多维度内容表现分析
"""

import json
import re
from collections import defaultdict
from datetime import datetime


def load_data():
    """加载原始数据"""
    with open('/tmp/lina_raw_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)


# ========== 分析函数 ==========

def categorize_topic(script):
    """分类主题"""
    if not script:
        return "未分类"

    if any(w in script for w in ["钱", "赚", "经济独立", "财运", "银行卡", "收入", "财务"]):
        return "经济独立/赚钱"
    elif any(w in script for w in ["心态", "能量", "心理暗示", "思维", "情绪"]):
        return "心态/能量"
    elif any(w in script for w in ["男人", "婚姻", "爱情", "感情", "孤独", "老公"]):
        return "关系/婚姻"
    elif any(w in script for w in ["成长", "变强", "进步", "努力", "目标", "提升"]):
        return "成长/自我提升"
    elif any(w in script for w in ["美", "漂亮", "形象", "打扮", "衣服", "风水"]):
        return "美丽/形象"
    else:
        return "其他"


def categorize_hook(script):
    """分类开头风格"""
    if not script:
        return "未知"

    first_50 = script[:50]
    first_100 = script[:100]

    # 问题式
    if "？" in first_50 or "?" in first_50:
        return "问题式"

    # 颠覆式
    if "不是" in first_100 and "而是" in first_100:
        return "颠覆式"

    # 女性定位
    if any(w in first_50 for w in ["女人", "女生", "女孩"]):
        return "女性定位"

    # 借势式
    if "朋友" in first_100 or "华人" in first_100:
        return "借势式"

    # 个人故事
    if script[:10].startswith("我"):
        return "个人故事"

    return "陈述式"


def extract_features(script):
    """提取内容特征"""
    if not script:
        return {}

    return {
        "length": len(script),
        "has_question": "？" in script or "?" in script,
        "has_list": bool(re.search(r'第[一二三四五六七八九十]|1\.|2\.|3\.', script)),
        "has_money_topic": any(w in script for w in ["钱", "赚", "经济", "财", "收入", "独立"]),
        "has_relationship": any(w in script for w in ["男人", "婚姻", "爱情", "感情"]),
        "has_growth": any(w in script for w in ["成长", "变强", "提升", "进步"]),
        "has_beauty": any(w in script for w in ["美", "漂亮", "形象", "打扮"]),
        "has_example": any(w in script for w in ["比如", "例如", "举个例子", "就像"]),
        "has_indonesian": bool(re.search(r'[a-zA-Z]{10,}', script)),  # 简单检测印尼语
    }


def analyze_data(raw_data):
    """执行完整分析"""
    data = raw_data["data"]
    summary = raw_data["summary"]

    # 构建分析数据
    analyzed = []
    for item in data:
        ins_view = item["ins"]["view"]
        tt_view = item["tiktok"]["view"]
        total_view = ins_view + tt_view

        if total_view == 0 and not item["script"]:
            continue

        analyzed.append({
            "name": item["name"],
            "script": item["script"],
            "script_preview": item["script"][:100] if item["script"] else "",
            "ins_view": ins_view,
            "tt_view": tt_view,
            "total_view": total_view,
            "ins_engagement": item["ins"]["engagement"],
            "tt_engagement": item["tiktok"]["engagement"],
            "ins_total_engagement": item["ins"]["total_engagement"],
            "tt_total_engagement": item["tiktok"]["total_engagement"],
            "topic": categorize_topic(item["script"]),
            "hook": categorize_hook(item["script"]),
            "features": extract_features(item["script"]),
        })

    # 按总播放量排序
    analyzed.sort(key=lambda x: x["total_view"], reverse=True)

    # ========== 主题分析 ==========
    topic_stats = defaultdict(lambda: {
        "count": 0,
        "total_view": 0,
        "views": [],
        "items": []
    })

    for item in analyzed:
        topic = item["topic"]
        topic_stats[topic]["count"] += 1
        topic_stats[topic]["total_view"] += item["total_view"]
        topic_stats[topic]["views"].append(item["total_view"])
        topic_stats[topic]["items"].append(item["name"])

    # 计算平均值和最大最小
    for topic, stats in topic_stats.items():
        if stats["count"] > 0:
            stats["avg_view"] = round(stats["total_view"] / stats["count"])
            stats["max_view"] = max(stats["views"]) if stats["views"] else 0
            stats["min_view"] = min(stats["views"]) if stats["views"] else 0
        else:
            stats["avg_view"] = 0
            stats["max_view"] = 0
            stats["min_view"] = 0

    # ========== Hook分析 ==========
    hook_stats = defaultdict(lambda: {
        "count": 0,
        "total_view": 0,
        "views": []
    })

    for item in analyzed:
        hook = item["hook"]
        hook_stats[hook]["count"] += 1
        hook_stats[hook]["total_view"] += item["total_view"]
        hook_stats[hook]["views"].append(item["total_view"])

    for hook, stats in hook_stats.items():
        if stats["count"] > 0:
            stats["avg_view"] = round(stats["total_view"] / stats["count"])
        else:
            stats["avg_view"] = 0

    # ========== 平台对比 ==========
    both_platform = [d for d in analyzed if d["ins_view"] > 0 and d["tt_view"] > 0]
    tt_better = [d for d in both_platform if d["tt_view"] > d["ins_view"]]
    ins_better = [d for d in both_platform if d["ins_view"] > d["tt_view"]]

    platform_comparison = {
        "both_count": len(both_platform),
        "tt_better_count": len(tt_better),
        "ins_better_count": len(ins_better),
        "tt_better_pct": round(len(tt_better) / len(both_platform) * 100) if both_platform else 0,
        "ins_better_pct": round(len(ins_better) / len(both_platform) * 100) if both_platform else 0,
        "tt_better_examples": [
            {
                "name": d["name"],
                "tt_view": d["tt_view"],
                "ins_view": d["ins_view"],
                "ratio": round(d["tt_view"] / d["ins_view"], 1) if d["ins_view"] > 0 else 0
            }
            for d in sorted(tt_better, key=lambda x: x["tt_view"]/x["ins_view"] if x["ins_view"] > 0 else 0, reverse=True)[:5]
        ]
    }

    # ========== 特征对比 ==========
    top_5 = analyzed[:5]
    bottom_5 = analyzed[-5:] if len(analyzed) >= 5 else analyzed

    def aggregate_features(items):
        if not items:
            return {}
        total = len(items)
        total_len = sum(i["features"].get("length", 0) for i in items)
        return {
            "avg_length": round(total_len / total) if total > 0 else 0,
            "has_question_pct": round(sum(1 for i in items if i["features"].get("has_question")) / total * 100),
            "has_list_pct": round(sum(1 for i in items if i["features"].get("has_list")) / total * 100),
            "has_money_pct": round(sum(1 for i in items if i["features"].get("has_money_topic")) / total * 100),
            "has_relationship_pct": round(sum(1 for i in items if i["features"].get("has_relationship")) / total * 100),
            "has_beauty_pct": round(sum(1 for i in items if i["features"].get("has_beauty")) / total * 100),
        }

    feature_comparison = {
        "top_5": aggregate_features(top_5),
        "bottom_5": aggregate_features(bottom_5)
    }

    # ========== 播放量分布 ==========
    view_distribution = {
        "100k_plus": len([d for d in analyzed if d["total_view"] >= 100000]),
        "50k_100k": len([d for d in analyzed if 50000 <= d["total_view"] < 100000]),
        "10k_50k": len([d for d in analyzed if 10000 <= d["total_view"] < 50000]),
        "below_10k": len([d for d in analyzed if d["total_view"] < 10000]),
    }

    total_with_views = sum(view_distribution.values())
    if total_with_views > 0:
        view_distribution["100k_plus_pct"] = round(view_distribution["100k_plus"] / total_with_views * 100)
        view_distribution["50k_100k_pct"] = round(view_distribution["50k_100k"] / total_with_views * 100)
        view_distribution["10k_50k_pct"] = round(view_distribution["10k_50k"] / total_with_views * 100)
        view_distribution["below_10k_pct"] = round(view_distribution["below_10k"] / total_with_views * 100)

    # ========== 汇总结果 ==========
    analysis_result = {
        "analysis_time": datetime.now().isoformat(),
        "summary": summary,
        "total_analyzed": len(analyzed),
        "top_5": [
            {
                "name": d["name"],
                "total_view": d["total_view"],
                "ins_view": d["ins_view"],
                "tt_view": d["tt_view"],
                "topic": d["topic"],
                "hook": d["hook"],
                "script_preview": d["script_preview"]
            }
            for d in top_5
        ],
        "bottom_5": [
            {
                "name": d["name"],
                "total_view": d["total_view"],
                "ins_view": d["ins_view"],
                "tt_view": d["tt_view"],
                "topic": d["topic"],
                "hook": d["hook"],
                "script_preview": d["script_preview"]
            }
            for d in bottom_5
        ],
        "topic_analysis": dict(topic_stats),
        "hook_analysis": dict(hook_stats),
        "platform_comparison": platform_comparison,
        "feature_comparison": feature_comparison,
        "view_distribution": view_distribution,
        "all_data": analyzed
    }

    return analysis_result


def generate_insights(analysis):
    """生成核心洞察"""
    insights = []

    # 1. 主题洞察
    topic_sorted = sorted(
        analysis["topic_analysis"].items(),
        key=lambda x: x[1]["avg_view"],
        reverse=True
    )
    if topic_sorted:
        best_topic = topic_sorted[0]
        worst_topic = topic_sorted[-1]
        insights.append({
            "type": "topic",
            "finding": f'"{best_topic[0]}"主题平均播放量最高({best_topic[1]["avg_view"]:,})，是"{worst_topic[0]}"的{round(best_topic[1]["avg_view"]/worst_topic[1]["avg_view"]) if worst_topic[1]["avg_view"] > 0 else "N"}倍',
            "confidence": "高",
            "action": f'优先创作"{best_topic[0]}"主题内容'
        })

    # 2. Hook洞察
    hook_sorted = sorted(
        analysis["hook_analysis"].items(),
        key=lambda x: x[1]["avg_view"],
        reverse=True
    )
    if hook_sorted:
        best_hook = hook_sorted[0]
        worst_hook = hook_sorted[-1]
        insights.append({
            "type": "hook",
            "finding": f'"{best_hook[0]}"开头效果最好(平均{best_hook[1]["avg_view"]:,}播放)，是"{worst_hook[0]}"的{round(best_hook[1]["avg_view"]/worst_hook[1]["avg_view"]) if worst_hook[1]["avg_view"] > 0 else "N"}倍',
            "confidence": "高",
            "action": f'使用"{best_hook[0]}"开头风格'
        })

    # 3. 平台洞察
    platform = analysis["platform_comparison"]
    if platform["both_count"] > 0:
        if platform["tt_better_pct"] > 60:
            insights.append({
                "type": "platform",
                "finding": f'TikTok表现优于Instagram({platform["tt_better_pct"]}%的内容TikTok更好)',
                "confidence": "高",
                "action": "优先发布TikTok，同步Instagram"
            })

    # 4. 特征洞察
    feat = analysis["feature_comparison"]
    if feat["top_5"]["has_money_pct"] > feat["bottom_5"]["has_money_pct"] + 30:
        insights.append({
            "type": "feature",
            "finding": f'高表现内容{feat["top_5"]["has_money_pct"]}%涉及金钱话题，低表现内容仅{feat["bottom_5"]["has_money_pct"]}%',
            "confidence": "高",
            "action": "内容中植入金钱/经济独立元素"
        })

    # 5. 长度洞察
    if feat["top_5"]["avg_length"] < feat["bottom_5"]["avg_length"]:
        insights.append({
            "type": "length",
            "finding": f'高表现内容更短(平均{feat["top_5"]["avg_length"]}字 vs {feat["bottom_5"]["avg_length"]}字)',
            "confidence": "中",
            "action": "控制内容长度在1000-1200字"
        })

    return insights


def main():
    print("=" * 60)
    print("Lina Content Analyzer - 数据分析")
    print("=" * 60)

    # 加载数据
    print("\n[1/3] 加载数据...")
    raw_data = load_data()
    print(f"✅ 加载完成，共 {len(raw_data['data'])} 条记录")

    # 执行分析
    print("\n[2/3] 执行多维度分析...")
    analysis = analyze_data(raw_data)
    print("✅ 分析完成")

    # 生成洞察
    print("\n[3/3] 生成核心洞察...")
    insights = generate_insights(analysis)
    analysis["insights"] = insights
    print(f"✅ 生成 {len(insights)} 条洞察")

    # 保存结果
    with open('/tmp/lina_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    # 输出摘要
    print("\n" + "=" * 60)
    print("分析结果摘要")
    print("=" * 60)

    print(f"\n📊 数据概览")
    print(f"   分析内容: {analysis['total_analyzed']} 条")
    print(f"   Instagram: {analysis['summary']['total_ins_views']:,} 播放")
    print(f"   TikTok: {analysis['summary']['total_tt_views']:,} 播放")

    print(f"\n📈 主题表现 (按平均播放排序)")
    for topic, stats in sorted(analysis["topic_analysis"].items(), key=lambda x: x[1]["avg_view"], reverse=True):
        print(f"   {topic}: {stats['avg_view']:,} (共{stats['count']}条)")

    print(f"\n🎯 开头效果 (按平均播放排序)")
    for hook, stats in sorted(analysis["hook_analysis"].items(), key=lambda x: x[1]["avg_view"], reverse=True):
        print(f"   {hook}: {stats['avg_view']:,} (共{stats['count']}条)")

    print(f"\n💡 核心洞察")
    for i, insight in enumerate(insights, 1):
        print(f"   {i}. {insight['finding']}")

    print(f"\n分析结果已保存到: /tmp/lina_analysis.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
