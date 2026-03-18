#!/usr/bin/env python3
"""
Lina Content Analyzer - 数据获取脚本
从飞书多维表格获取内容表现数据
"""

import requests
import json
from datetime import datetime

# ========== 配置 ==========
FEISHU_CONFIG = {
    "app_id": "cli_a9fbcb802e789ed2",
    "app_secret": "6DluFaAcL0klYLDhQk5W7bLO4yRRhotN",
    "api_base": "https://open.larksuite.com/open-apis",
    "app_token": "APIhbAcq9aLJQxskyPIl6fxRgnd",
    "table_id": "tblGmzYquULXY3oX"
}

# 字段映射
FIELD_MAPPING = {
    "name": "name",
    "script": "【AI script】\nAI script ",
    "ins_view": "view",
    "ins_likes": "Likes ",
    "ins_shares": "Shares",
    "ins_save": "save",
    "ins_comments": "Comments",
    "ins_engagement": "互动率",
    "tt_view": "view_1",
    "tt_likes": "Likes _1",
    "tt_shares": "Shares_1",
    "tt_save": "save_1",
    "tt_comments": "comment",
    "tt_engagement": "互动率_1"
}


def get_token():
    """获取飞书 tenant_access_token"""
    resp = requests.post(
        f"{FEISHU_CONFIG['api_base']}/auth/v3/tenant_access_token/internal/",
        json={
            "app_id": FEISHU_CONFIG['app_id'],
            "app_secret": FEISHU_CONFIG['app_secret']
        }
    )
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"获取Token失败: {data}")
    return data.get("tenant_access_token")


def get_records(token):
    """获取所有记录"""
    records = []
    page_token = None

    while True:
        payload = {"page_size": 100}
        if page_token:
            payload["page_token"] = page_token

        resp = requests.post(
            f"{FEISHU_CONFIG['api_base']}/bitable/v1/apps/{FEISHU_CONFIG['app_token']}/tables/{FEISHU_CONFIG['table_id']}/records/search",
            headers={"Authorization": f"Bearer {token}"},
            json=payload
        )
        data = resp.json()

        if data.get("code") != 0:
            raise Exception(f"获取记录失败: {data}")

        items = data.get("data", {}).get("items", [])
        records.extend(items)

        if not data.get("data", {}).get("has_more"):
            break
        page_token = data.get("data", {}).get("page_token")

    return records


def get_text(field):
    """提取文本字段值"""
    if isinstance(field, list):
        return field[0].get("text", "") if field else ""
    return str(field) if field else ""


def transform_records(raw_records):
    """转换原始记录为结构化数据"""
    data = []

    for rec in raw_records:
        f = rec.get("fields", {})

        item = {
            "name": get_text(f.get(FIELD_MAPPING["name"], "")),
            "script": get_text(f.get(FIELD_MAPPING["script"], "")),
            "ins": {
                "view": f.get(FIELD_MAPPING["ins_view"], 0) or 0,
                "likes": f.get(FIELD_MAPPING["ins_likes"], 0) or 0,
                "shares": f.get(FIELD_MAPPING["ins_shares"], 0) or 0,
                "save": f.get(FIELD_MAPPING["ins_save"], 0) or 0,
                "comments": f.get(FIELD_MAPPING["ins_comments"], 0) or 0,
                "engagement": get_text(f.get(FIELD_MAPPING["ins_engagement"], "")),
            },
            "tiktok": {
                "view": f.get(FIELD_MAPPING["tt_view"], 0) or 0,
                "likes": f.get(FIELD_MAPPING["tt_likes"], 0) or 0,
                "shares": f.get(FIELD_MAPPING["tt_shares"], 0) or 0,
                "save": f.get(FIELD_MAPPING["tt_save"], 0) or 0,
                "comments": f.get(FIELD_MAPPING["tt_comments"], 0) or 0,
                "engagement": get_text(f.get(FIELD_MAPPING["tt_engagement"], "")),
            }
        }

        # 计算总互动
        item["ins"]["total_engagement"] = (
            item["ins"]["likes"] + item["ins"]["shares"] +
            item["ins"]["save"] + item["ins"]["comments"]
        )
        item["tiktok"]["total_engagement"] = (
            item["tiktok"]["likes"] + item["tiktok"]["shares"] +
            item["tiktok"]["save"] + item["tiktok"]["comments"]
        )

        data.append(item)

    return data


def generate_summary(data):
    """生成数据初评摘要"""
    total = len(data)
    ins_valid = len([d for d in data if d["ins"]["view"] > 0])
    tt_valid = len([d for d in data if d["tiktok"]["view"] > 0])
    script_filled = len([d for d in data if d["script"] and len(d["script"]) > 50])

    total_ins_views = sum(d["ins"]["view"] for d in data)
    total_tt_views = sum(d["tiktok"]["view"] for d in data)

    summary = {
        "fetch_time": datetime.now().isoformat(),
        "total_records": total,
        "ins_valid": ins_valid,
        "ins_valid_pct": round(ins_valid / total * 100, 1) if total > 0 else 0,
        "tt_valid": tt_valid,
        "tt_valid_pct": round(tt_valid / total * 100, 1) if total > 0 else 0,
        "script_filled": script_filled,
        "script_filled_pct": round(script_filled / total * 100, 1) if total > 0 else 0,
        "total_ins_views": total_ins_views,
        "total_tt_views": total_tt_views,
        "avg_ins_views": round(total_ins_views / ins_valid) if ins_valid > 0 else 0,
        "avg_tt_views": round(total_tt_views / tt_valid) if tt_valid > 0 else 0,
        "data_sufficient": total >= 10 and (ins_valid >= 5 or tt_valid >= 5)
    }

    return summary


def main():
    print("=" * 60)
    print("Lina Content Analyzer - 数据获取")
    print("=" * 60)

    # 1. 获取Token
    print("\n[1/4] 获取飞书 Token...")
    token = get_token()
    print("✅ Token 获取成功")

    # 2. 获取记录
    print("\n[2/4] 获取表格记录...")
    raw_records = get_records(token)
    print(f"✅ 获取到 {len(raw_records)} 条记录")

    # 3. 转换数据
    print("\n[3/4] 转换数据格式...")
    data = transform_records(raw_records)
    print(f"✅ 转换完成")

    # 4. 生成摘要
    print("\n[4/4] 生成数据摘要...")
    summary = generate_summary(data)

    # 保存数据
    output = {
        "summary": summary,
        "data": data
    }

    with open('/tmp/lina_raw_data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("数据初评报告")
    print("=" * 60)
    print(f"\n总记录数: {summary['total_records']} 条")
    print(f"Instagram 有效: {summary['ins_valid']} 条 ({summary['ins_valid_pct']}%)")
    print(f"TikTok 有效: {summary['tt_valid']} 条 ({summary['tt_valid_pct']}%)")
    print(f"口播稿填充率: {summary['script_filled_pct']}%")
    print(f"\nInstagram 总播放: {summary['total_ins_views']:,}")
    print(f"TikTok 总播放: {summary['total_tt_views']:,}")
    print(f"\n数据充分性: {'✅ 可以进行分析' if summary['data_sufficient'] else '⚠️ 数据不足'}")
    print(f"\n数据已保存到: /tmp/lina_raw_data.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
