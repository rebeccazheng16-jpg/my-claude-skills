#!/usr/bin/env python3
"""Creator Matrix Manager - 创作者矩阵管理工具

用法:
    python matrix_manager.py list [persons|accounts|personas]
    python matrix_manager.py get <type> <id>
    python matrix_manager.py scope <persona_id>
    python matrix_manager.py style <person_id>
    python matrix_manager.py search --audience <audience_id>
    python matrix_manager.py tree [person_id]
"""

import json
import sys
from pathlib import Path

# 数据文件路径
DATA_FILE = Path(__file__).parent.parent / "data" / "matrix.json"


def load_data():
    """加载矩阵数据"""
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def cmd_list(entity_type="all"):
    """列出实体"""
    data = load_data()

    if entity_type in ["all", "persons"]:
        print("\n=== Persons (人员) ===")
        for p in data["persons"]:
            print(f"  {p['id']}: {p['name']} ({p['type']})")
            if p.get("style_ref"):
                print(f"    └── style: {p['style_ref']}")

    if entity_type in ["all", "accounts"]:
        print("\n=== Accounts (账号) ===")
        for a in data["accounts"]:
            print(f"  {a['id']}: {a['handle']} @ {a['platform']} ({a['region']})")

    if entity_type in ["all", "personas"]:
        print("\n=== Personas (人设) ===")
        for p in data["personas"]:
            scope = ", ".join(p["knowledge_scope"][:2])
            if len(p["knowledge_scope"]) > 2:
                scope += "..."
            print(f"  {p['id']}: {p['name']}")
            print(f"    └── scope: [{scope}]")


def cmd_get(entity_type, entity_id):
    """获取单个实体详情"""
    data = load_data()

    entities = {
        "person": data["persons"],
        "account": data["accounts"],
        "persona": data["personas"]
    }

    if entity_type not in entities:
        print(f"错误: 未知类型 '{entity_type}'，支持: person, account, persona")
        return

    for e in entities[entity_type]:
        if e["id"] == entity_id:
            print(json.dumps(e, indent=2, ensure_ascii=False))
            return

    print(f"未找到: {entity_type} '{entity_id}'")


def cmd_scope(persona_id):
    """获取人设的知识范围"""
    data = load_data()

    for p in data["personas"]:
        if p["id"] == persona_id:
            print(f"人设: {p['name']} ({persona_id})")
            print(f"知识范围:")
            for scope in p["knowledge_scope"]:
                print(f"  - {scope}")
            return

    print(f"未找到人设: {persona_id}")


def cmd_style(person_id):
    """获取人员的风格引用"""
    data = load_data()

    for p in data["persons"]:
        if p["id"] == person_id:
            style_ref = p.get("style_ref")
            if style_ref:
                print(f"人员: {p['name']}")
                print(f"风格 Skill: {style_ref}")
                print(f"\n调用方式: 触发 '{style_ref}' skill")
            else:
                print(f"人员 '{person_id}' 没有关联的风格 skill")
            return

    print(f"未找到人员: {person_id}")


def cmd_search_audience(audience_id):
    """按目标受众搜索人设"""
    data = load_data()

    # 获取受众信息
    audience = None
    for a in data["target_audiences"]["available"]:
        if a["id"] == audience_id:
            audience = a
            break

    if not audience:
        print(f"未找到受众: {audience_id}")
        print("可用受众:", ", ".join(a["id"] for a in data["target_audiences"]["available"]))
        return

    print(f"目标受众: {audience['name']}")
    print(f"痛点关键词: {', '.join(audience['pain_keywords'])}")
    print(f"\n匹配的人设:")

    for p in data["personas"]:
        if p.get("target_audience") == audience_id:
            print(f"  - {p['id']}: {p['name']}")


def cmd_tree(person_id=None):
    """显示矩阵树形结构"""
    data = load_data()

    persons = data["persons"]
    if person_id:
        persons = [p for p in persons if p["id"] == person_id]
        if not persons:
            print(f"未找到人员: {person_id}")
            return

    for person in persons:
        print(f"\n{person['name']} ({person['type']})")
        if person.get("style_ref"):
            print(f"├── style: {person['style_ref']}")

        # 获取该人员的账号
        accounts = [a for a in data["accounts"] if a["person_id"] == person["id"]]
        for i, account in enumerate(accounts):
            is_last_account = (i == len(accounts) - 1)
            prefix = "└──" if is_last_account else "├──"
            print(f"{prefix} {account['platform']}: {account['handle']}")

            # 获取该账号的人设
            personas = [p for p in data["personas"] if p["account_id"] == account["id"]]
            for j, persona in enumerate(personas):
                is_last_persona = (j == len(personas) - 1)
                sub_prefix = "    └──" if is_last_persona else "    ├──"
                if not is_last_account:
                    sub_prefix = "│   └──" if is_last_persona else "│   ├──"
                scope_str = ", ".join(persona["knowledge_scope"][:2])
                print(f"{sub_prefix} {persona['name']} [{scope_str}]")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "list":
        entity_type = sys.argv[2] if len(sys.argv) > 2 else "all"
        cmd_list(entity_type)

    elif cmd == "get":
        if len(sys.argv) < 4:
            print("用法: python matrix_manager.py get <type> <id>")
            return
        cmd_get(sys.argv[2], sys.argv[3])

    elif cmd == "scope":
        if len(sys.argv) < 3:
            print("用法: python matrix_manager.py scope <persona_id>")
            return
        cmd_scope(sys.argv[2])

    elif cmd == "style":
        if len(sys.argv) < 3:
            print("用法: python matrix_manager.py style <person_id>")
            return
        cmd_style(sys.argv[2])

    elif cmd == "search":
        if len(sys.argv) < 4 or sys.argv[2] != "--audience":
            print("用法: python matrix_manager.py search --audience <audience_id>")
            return
        cmd_search_audience(sys.argv[3])

    elif cmd == "tree":
        person_id = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_tree(person_id)

    else:
        print(f"未知命令: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
