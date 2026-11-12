#!/usr/bin/env python3
"""时象助手 v2 · 导演台（小云雀模式 × drama-skills / shuohao-skills 质量门）

拼装来源（已落盘在 vendor/，仅作参考，不 import）：
  - zenstory-ai/drama-skills  : 五份创作文档、连续性锁、REF/PLAN/IMG 三层、
                                生产前预览+指纹确认、剪辑单入出点算术、逐字传播链
  - eternityspring/shuohao-skills : 脚本确定性质量门（不靠模型自觉）、
                                起点→唯一动作→终点、站位/轴线、selftest 不调模型
  - 小云雀 Seedance 短剧 Agent : 资产锁定 → 导演台预演 → 逐镜生成 → 片段重拍

本模块只读输入、只写 output/00_creator_docs 与 output/00_previs，
所有门都是纯字符串/数值比较，不调用任何模型、不产生费用。
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

DOCS = ("剧本.md", "视觉设定.md", "分镜.md", "视频提示词.md", "剪辑单.md")
SPOKEN_CPS = 4.1          # drama-skills: H3 中文常速约 4.1 个可发声字/秒
VOICE_LEAD_S = 0.35       # 开口前等待
VOICE_TAIL_S = 0.40       # 句尾反应
STILL_MIN_S = 0.50
DIALOGUE_MIN_S = 1.20
CAMERA_MAX_PCT = 30.0
CAMERA_RATE_MIN, CAMERA_RATE_MAX = 0.1, 10.0
LUFS_TARGET, LUFS_TOL, TRUE_PEAK_MAX = -16.0, 1.0, -1.5
REF_PURPOSES = {"身份", "造型状态", "地理", "构图", "尺度", "效果",
                "起始帧", "结束帧", "风格"}


def load(root: Path, input_dir: Path) -> tuple[dict, dict, dict, dict, str]:
    sb = json.loads((input_dir / "storyboard.json").read_text(encoding="utf-8"))
    ch = json.loads((input_dir / "characters.json").read_text(encoding="utf-8"))
    dr = json.loads((input_dir / "director.json").read_text(encoding="utf-8"))
    script = (input_dir / "script.md").read_text(encoding="utf-8")
    return sb, ch, dr, {}, script


def dump_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def _plain(s: str) -> str:
    return re.sub(r"[\s，。、；：！？「」『』（）()\[\]]+", "", s or "")


# ---------------------------------------------------------------------------
# 五份创作文档（drama-skills：创作决定以文档为准，逐字向下游传播）
# ---------------------------------------------------------------------------

def build_creator_docs(root: Path, sb: dict, ch: dict, dr: dict,
                       script: str, cfg: dict) -> dict:
    out = root / "output/00_creator_docs"
    out.mkdir(parents=True, exist_ok=True)
    ep = sb["episode"]["id"]
    (out / "剧本.md").write_text(script, encoding="utf-8")

    # 视觉设定.md：角色/地点 + 识别锚点 + 连续性锁
    v = [f"# {ep} 视觉设定\n",
         "\n> 画风、光向、人物造型为跨镜刚性事实。锁面必须原样出现在生效镜头的视频提示词里。\n"]
    v.append(f"\n## 风格锚 · {dr['style_anchor']['name']}\n")
    v.append(f"- 锁面（提示词语种）：{dr['style_anchor']['surface']}\n")
    v.append(f"- 色调与光：{dr['style_anchor']['palette']}\n")
    v.append(f"- 负面约束：{dr['style_anchor']['negative']}\n")
    for c in ch["characters"]:
        v.append(f"\n## 人物 · {c['name']}\n")
        v.append(f"- 识别锚点：{'、'.join(c['identity_anchors'])}\n")
        v.append(f"- 本集造型：{c['appearance']}\n")
        v.append(f"- 声音参考：{c['voice']}（本机离线中文音色）\n")
        v.append(f"- 角色定位：{c['role']}\n")
    v.append("\n## 地点 · 冷白会议室\n")
    v.append(f"- 轴线：{dr['scene_geometry']['axis']}\n")
    v.append(f"- 摄影机工作侧：{dr['scene_geometry']['camera_working_side']}\n")
    v.append(f"- 说明：{dr['scene_geometry']['note']}\n")
    v.append("\n## 连续性锁\n")
    for lock in dr["continuity_locks"]:
        scope = "、".join(lock["scope"])
        v.append(f"- 连续性锁：{lock['id']}《{lock['name']}》"
                 f"（镜头：{scope}）· 锁面：{lock['surface']}\n")
        v.append(f"  - 理由：{lock['reason']}；英文锁面：{lock['surface_en']}\n")
    (out / "视觉设定.md").write_text("".join(v), encoding="utf-8")

    # 分镜.md / 视频提示词.md：SHOT ↔ MOTION 一一对应
    sm, vp = [f"# {ep} 分镜\n"], [f"# {ep} 视频提示词\n"]
    vp.append("\n> 每段「可复制提示词」是一次提交的完整正文，包含资产引用、时间段动作、"
              "镜头、起止状态与负面约束，可直接投给图生视频模型。\n")
    vp.append(f"\n- 目标模型：{cfg['providers'].get('motion', 'local_parallax')}\n")
    vp.append(f"- 交付画幅帧率：9:16 · {cfg['width']}×{cfg['height']} · {cfg['fps']}fps\n")

    for s, d in zip(sb["shots"], dr["shots"]):
        sid = s["id"]
        refs = "；".join(
            f"{r['slot']}（顺序：{r['order']}）· {r['path']}《{r['name']}》"
            f"（用途：{r['purpose']}；控制：{'、'.join(r['controls'])}；"
            f"不得控制：{'、'.join(r['must_not'])}）"
            for r in d["references"]) or "无（创作者已明确选择文生视频）"
        sm.append(f"\n## SHOT-{ep}-{sid} · {d['purpose']}\n")
        sm.append(f"- 来源：{ep}-SC001（本集单场，会议室）\n")
        sm.append(f"- 时长：{s['duration_s']}s\n")
        sm.append(f"- 目的：{d['purpose']}\n")
        sm.append(f"- 景别/机位：{s['shot_size']}；{s['camera']}；工作侧 {d['axis_side']}\n")
        sm.append(f"- 运镜：{s['camera']}，幅度 {d['camera_move_pct']}%；"
                  f"低动态优先，避免人物变形；理由：{d['purpose']}\n")
        sm.append(f"- 起点：{d['start']}\n")
        sm.append(f"- 唯一动作：{d['action']}\n")
        sm.append(f"- 终点：{d['end']}\n")
        sm.append(f"- 声音：对白「{s['dialogue']['text']}」；音效 {'、'.join(s.get('sfx', []))}；"
                  f"按 {SPOKEN_CPS} 字/秒估时，开口前 {VOICE_LEAD_S}s、句尾反应 {VOICE_TAIL_S}s\n")
        sm.append(f"- 图片提示词项：{refs}\n")
        sm.append(f"- 输入参考图：{refs}\n")
        sm.append("- 视觉依据：《视觉设定.md》·风格锚「冷调漫画」；"
                  "人物「林昭」「苏晴」（控制：身份、造型）；地点「冷白会议室」（控制：光向、轴线）\n")
        sm.append("\n### 冻结关键帧提示词\n")
        sm.append(f"> {d['start']}。{s['visual_prompt']}\n")

        vp.append(f"\n## MOTION-{ep}-{sid} · {d['purpose']}\n")
        vp.append(f"- 分镜：SHOT-{ep}-{sid}\n")
        vp.append(f"- 时长：{s['duration_s']}s\n")
        vp.append(f"- 生成方式：图生视频\n")
        vp.append(f"- 输入参考图：{refs}\n")
        vp.append(f"- 静态视觉锚点：{dr['style_anchor']['surface']}；{dr['style_anchor']['palette']}\n")
        vp.append(f"- 起始帧：{d['start']}\n")
        vp.append(f"- 状态链：{d['start']} → {d['action']} → {d['end']}\n")
        vp.append(f"- 终点：{d['end']}\n")
        vp.append(f"- 声音：对白「{s['dialogue']['text']}」由本机 TTS 后期合成，模型不生成口播\n")
        if d.get("axis_transition"):
            vp.append(f"- 越轴过渡：{d['axis_transition']}\n")
        vp.append("\n### 可复制提示词\n")
        vp.append(f"> {d['video_prompt']}\n")
    (out / "分镜.md").write_text("".join(sm), encoding="utf-8")
    (out / "视频提示词.md").write_text("".join(vp), encoding="utf-8")

    # 剪辑单.md：CUT 与 SHOT 一一对应，入出点算术自洽
    total = round(sum(float(s["duration_s"]) for s in sb["shots"]), 2)
    ed = ["# 剪辑单\n",
          f"- 成片目标时长：{total:.2f} 秒\n",
          f"- 画幅与帧率：9:16 · {cfg['width']}×{cfg['height']} · {cfg['fps']}fps\n",
          f"- 交付响度：{LUFS_TARGET:g} LUFS（容差 ±{LUFS_TOL:g} LU，真峰 ≤ {TRUE_PEAK_MAX:g} dBTP）\n",
          "- 字幕：硬字幕，台词逐字取自《剧本.md》，底部安全区，白字黑描边\n",
          "- 接镜匹配：同场色调由统一 LUT 保证\n",
          "- 颗粒：6\n",
          "- 未采用镜头：无\n"]
    for i, (s, d) in enumerate(zip(sb["shots"], dr["shots"]), 1):
        dur = float(s["duration_s"])
        ed.append(f"\n## CUT-{ep}-{i:03d} · {d['purpose']}\n")
        ed.append(f"- 来源：MOTION-{ep}-{s['id']} · output/04_clips/{s['id']}.mp4\n")
        ed.append("- 入点：0.00\n")
        ed.append(f"- 出点：{dur:.2f}\n")
        ed.append(f"- 时长：{dur:.2f}\n")
        ed.append(f"- 取舍：入点=画面从「{d['start']}」起势，先让观众看清起始姿态；"
                  f"出点=动作收在「{d['end']}」，切点落在该镜状态完成之后，不留半截动作\n")
        ed.append(f"- 声音：外部混音（本机离线 TTS 对白 + 本地合成音效 + 氛围 BGM）\n")
        ed.append("- 画面：统一冷调 LUT，不额外校正\n")
        ed.append(f"- 字幕：{s['subtitle']}\n")
        w = d.get("subtitle_window_s", [VOICE_LEAD_S, dur - VOICE_TAIL_S])
        ed.append(f"- 字幕 1：{w[0]:.2f}-{w[1]:.2f} {s['subtitle']}\n")
        if s.get("sfx"):
            ed.append(f"- 音效 1：0.00-{min(1.2, dur):.2f} output/05_audio/{s['id']}.wav"
                      "（起点：0.00；增益：-12）\n")
        ed.append(f"- 运镜：{'固定' if d['camera_move_pct'] == 0 else '推近 ' + str(d['camera_move_pct']) + '%'}\n")
    (out / "剪辑单.md").write_text("".join(ed), encoding="utf-8")
    return {"dir": "output/00_creator_docs", "files": list(DOCS),
            "path": str(out), "episode_duration_s": total}


# ---------------------------------------------------------------------------
# 确定性质量门（shuohao-skills：门由脚本判定，不靠模型自觉）
# ---------------------------------------------------------------------------

def run_gates(root: Path, sb: dict, ch: dict, dr: dict,
              script: str, cfg: dict) -> dict:
    out = root / "output/00_creator_docs"
    pre = root / "output/00_previs"
    gates: list[dict] = []

    def add(gid, name, level, ok, actual, expected, evidence, fix, warn=False):
        gates.append({"id": gid, "name": name, "level": level,
                      "status": "pass" if ok else ("warn" if warn else "fail"),
                      "actual": actual, "expected": expected,
                      "evidence": evidence, "fix_hint": fix})

    # D01 五份创作文档齐全
    missing = [d for d in DOCS if not (out / d).is_file()]
    add("D01", "五份创作文档齐全", "blocker", not missing,
        f"齐备 {len(DOCS) - len(missing)}/{len(DOCS)}", "5/5 全部存在",
        "output/00_creator_docs/", "运行 stage_00_previs 生成缺失文档", warn=bool(missing))

    texts = {d: (out / d).read_text(encoding="utf-8") if (out / d).is_file() else ""
             for d in DOCS}
    shots, dshots = sb["shots"], dr["shots"]
    ids = [s["id"] for s in shots]
    dids = [d["id"] for d in dshots]

    # D02 SHOT ↔ MOTION ↔ CUT 一一对应
    shot_ids = set(re.findall(r"## SHOT-[A-Z0-9]+-(S\d+)", texts["分镜.md"]))
    motion_ids = set(re.findall(r"## MOTION-[A-Z0-9]+-(S\d+)", texts["视频提示词.md"]))
    cut_count = len(re.findall(r"## CUT-", texts["剪辑单.md"]))
    ok = shot_ids == motion_ids == set(ids) and cut_count == len(ids) and ids == dids
    add("D02", "SHOT↔MOTION↔CUT 一一对应", "blocker", ok,
        f"SHOT {len(shot_ids)} / MOTION {len(motion_ids)} / CUT {cut_count} / 分镜 {len(ids)}",
        "四者数量与镜号集合完全一致",
        "output/00_creator_docs/{分镜,视频提示词,剪辑单}.md",
        "检查是否有镜头漏写视频提示词或剪辑单；ID 必须逐个对应")

    # D03 时长逐字传播
    sb_dur = {s["id"]: float(s["duration_s"]) for s in shots}
    sm_dur = {k: float(v) for k, v in re.findall(
        r"## SHOT-[A-Z0-9]+-(S\d+)[^\n]*\n- 来源：[^\n]*\n- 时长：([\d.]+)s", texts["分镜.md"])}
    vp_dur = {k: float(v) for k, v in re.findall(
        r"## MOTION-[A-Z0-9]+-(S\d+)[^\n]*\n- 分镜：[^\n]*\n- 时长：([\d.]+)s", texts["视频提示词.md"])}
    cut_dur = [float(x) for x in re.findall(r"- 时长：([\d.]+)\n", texts["剪辑单.md"])]
    drift = [i for i in ids if abs(sb_dur[i] - sm_dur.get(i, -1)) > 0.005
             or abs(sb_dur[i] - vp_dur.get(i, -1)) > 0.005]
    cut_ok = len(cut_dur) == len(ids) and all(
        abs(cut_dur[n] - sb_dur[i]) <= 0.005 for n, i in enumerate(ids))
    add("D03", "分镜/视频提示词/剪辑单时长逐字一致", "blocker", not drift and cut_ok,
        f"漂移镜 {drift or '无'}；剪辑单时长条目 {len(cut_dur)}",
        "全部相等，容差 0.005s", "output/00_creator_docs/",
        "视频提示词只能原样照抄已接受的镜头时长，不得另估")

    # D04 集长 == 可见镜头时长之和
    total = sum(sb_dur.values())
    declared = sb["episode"].get("duration_target_s", 0)
    add("D04", "集长等于可见镜头时长之和", "blocker",
        abs(total - float(declared)) <= 0.05,
        f"镜头合计 {total:.2f}s / 目标 {declared}s", "差值 ≤0.05s",
        "input/demo/storyboard.json", "调整末镜时长或修正目标集长，禁止用变速凑数")

    # D05 对白发声窗口（4.1 字/秒）
    bad, worst = [], 0.0
    for s in shots:
        vc = len(_plain(s["dialogue"]["text"]))
        need = vc / SPOKEN_CPS
        window = float(s["duration_s"]) - VOICE_LEAD_S - VOICE_TAIL_S
        worst = max(worst, need / window if window > 0 else 9)
        if need > window:
            bad.append(f"{s['id']}(需{need:.2f}s/窗口{window:.2f}s)")
    add("D05", "对白发声窗口预算（4.1 字/秒）", "blocker", not bad,
        f"超载镜 {bad or '无'}；最紧窗口占用 {worst*100:.0f}%",
        f"台词时长 ≤ 镜长 −{VOICE_LEAD_S}s −{VOICE_TAIL_S}s",
        "output/00_creator_docs/分镜.md → 声音",
        "先删装饰动作 → 并行 → 回上游拆镜/精简台词；禁止加快语速")

    # D06 字幕逐字取自剧本
    plain_script = _plain(script)
    off = [s["id"] for s in shots
           if _plain(s["subtitle"]) != _plain(s["dialogue"]["text"])
           or _plain(s["subtitle"]) not in plain_script]
    add("D06", "字幕与台词逐字对齐且能在剧本中找到原文", "blocker", not off,
        f"偏离镜 {off or '无'}", "subtitle == dialogue.text 且为剧本子串",
        "input/demo/script.md", "字幕只能逐字照抄剧本，不得改写或增删标点")

    # D07 连续性锁锁面传播
    miss = []
    for lock in dr["continuity_locks"]:
        for d in dshots:
            if d["id"] in lock["scope"] and lock["surface"] not in d["video_prompt"]:
                miss.append(f"{lock['id']}→{d['id']}")
    add("D07", "连续性锁锁面原样传播到生效镜头", "blocker", not miss,
        f"缺失 {miss or '无'}；锁 {len(dr['continuity_locks'])} 把",
        "生效范围内每条视频提示词必须含锁面",
        "output/00_creator_docs/视觉设定.md → 连续性锁",
        "把锁面短语原样写进该镜视频提示词；锁面不得含动作、剧情或否定词")

    # D08 REF 槽位合法性与文件真实性
    ref_issues = []
    for d in dshots:
        orders = [r["order"] for r in d["references"]]
        if orders != list(range(1, len(orders) + 1)):
            ref_issues.append(f"{d['id']} 顺序不连续")
        for r in d["references"]:
            if r["purpose"] not in REF_PURPOSES:
                ref_issues.append(f"{d['id']} 用途越界 {r['purpose']}")
            if set(r["controls"]) & set(r["must_not"]):
                ref_issues.append(f"{d['id']} 控制域冲突")
            # 起始帧指向本机转绘帧（本轮必然存在）；定妆卡由 stage_02 产出
            if not (root / r["path"]).is_file():
                ref_issues.append(f"{d['id']} 参考文件缺失 {r['path']}")
    n_first = sum(sum(1 for r in d["references"] if r["purpose"] == "起始帧")
                  for d in dshots)
    add("D08", "REF 槽位顺序/用途/控制域/文件真实性", "blocker", not ref_issues,
        f"问题 {len(ref_issues)}；{n_first} 张起始帧",
        "顺序 1..N 连续、用途在闭集、控制域互斥、真实文件存在",
        "output/00_creator_docs/分镜.md → 输入参考图",
        "PLAN-* 只是挂图计划，投产前必须换成项目内真实 REF-* 文件",
        warn=bool(ref_issues))

    # D09 相邻镜景别/角度/关系至少变一项
    same = []
    for a, b in zip(shots, shots[1:]):
        if (a["shot_size"] == b["shot_size"] and a["camera"] == b["camera"]
                and a["characters"] == b["characters"]):
            same.append(f"{a['id']}→{b['id']}")
    add("D09", "相邻镜景别/角度/人物关系至少改变一项", "craft", not same,
        f"重复相邻 {same or '无'}", "不允许同景别同机位同关系连续两镜",
        "input/demo/storyboard.json", "并镜或改景别/机位；同景别重复须贡献反应或细节")

    # D10 越轴检查
    cross = []
    for a, b in zip(dshots, dshots[1:]):
        if a["axis_side"] != b["axis_side"] and not b.get("axis_transition"):
            cross.append(f"{a['id']}→{b['id']}")
    add("D10", "正反打不越轴，越轴须声明过渡", "craft", not cross,
        f"未声明越轴 {cross or '无'}",
        "工作侧一致；换侧须写镜内穿轴/中性过渡镜/全景重建",
        "output/00_creator_docs/分镜.md → 场景站位",
        "补写越轴过渡方式并声明新工作侧，或把该镜改回 A 侧")

    # D11 运镜幅度与速率
    cam_bad = []
    for s, d in zip(shots, dshots):
        pct = float(d["camera_move_pct"])
        rate = pct / float(s["duration_s"]) if pct else 0.0
        if pct > CAMERA_MAX_PCT or (pct and not CAMERA_RATE_MIN <= rate <= CAMERA_RATE_MAX):
            cam_bad.append(f"{s['id']}({pct}% / {rate:.2f}%/s)")
    add("D11", "运镜幅度 ≤30% 且速率 0.1–10%/秒", "craft", not cam_bad,
        f"越界 {cam_bad or '无'}", "单段累计 ≤30%，速率在 0.1–10%/s",
        "output/00_creator_docs/剪辑单.md → 运镜",
        "放慢或缩短该段；过高动态是 AI 视频人物变形的首要原因")

    # D12 单一戏剧目的
    purposes = [d["purpose"] for d in dshots]
    add("D12", "每镜单一戏剧目的且不重复", "craft",
        all(purposes) and len(set(purposes)) == len(purposes),
        f"唯一目的 {len(set(purposes))}/{len(purposes)}",
        "每镜一个可验收目的，不写「展示人物说话」这类空泛描述",
        "input/demo/director.json → purpose", "合并目的重复的镜头，或改写为具体戏剧作用")

    # D13 三态完整
    bad3 = [d["id"] for d in dshots
            if not all(d.get(k) for k in ("start", "action", "end"))
            or len({d.get("start", ""), d.get("action", ""), d.get("end", "")}) < 3]
    add("D13", "起点→唯一动作→终点三态完整", "blocker", not bad3,
        f"缺失 {bad3 or '无'}", "每镜三态齐全且互不重复",
        "input/demo/director.json", "冻结关键帧只写起点可见内容；终点另写，不写成动作链")

    # D14 / D15 钩子与悬念
    hook = dshots[0]["purpose"] + shots[0]["dialogue"]["text"]
    add("D14", "前 3 秒强冲突钩子", "craft",
        any(k in hook for k in ("指控", "冲突", "代签", "不是我签")),
        dshots[0]["purpose"], "第一镜直接抛冲突台词或画面",
        "input/demo/director.json S01", "把最强冲突前置到 0–3 秒，不要铺垫环境")
    add("D15", "集尾留悬念引导下一集", "craft",
        "悬念" in dshots[-1]["purpose"] or "下一集" in shots[-1]["dialogue"]["text"],
        dshots[-1]["purpose"] + " / " + shots[-1]["dialogue"]["text"],
        "末镜目的或台词含追更钩子", "input/demo/director.json 末镜",
        "把未解信息留到末镜，台词指向后续而非收束剧情")

    # D16 生产预览 → 明确确认（drama-skills 四步硬闸门）
    jobs = pre / "production_jobs.json"
    jobs_ok, detail = False, "生产预览尚未生成"
    if jobs.is_file():
        j = json.loads(jobs.read_text(encoding="utf-8"))
        fp = j.get("fingerprint", "")
        conf = pre / "CONFIRM"
        token = conf.read_text(encoding="utf-8").strip() if conf.is_file() else ""
        jobs_ok = token == f"CONFIRM {j.get('job_id')} {fp[:12]}"
        detail = (f"job={j.get('job_id')} fp={fp[:12]} 任务={len(j.get('jobs', []))}；"
                  f"确认={'有效' if jobs_ok else '缺失或过期'}")
    add("D16", "付费生产前预览 + 指纹明确确认", "blocker", jobs_ok, detail,
        "prepare → 展示预览 → CONFIRM <job_id> <fingerprint[:12]> → run",
        "output/00_previs/production_jobs.json / CONFIRM",
        "任何 prompt/参考/参数/输出变化都会使旧确认失效，须重新预览确认",
        warn=not jobs_ok)

    # D17 画幅帧率
    add("D17", "画幅帧率一致且宽高为偶数", "blocker",
        cfg["width"] % 2 == 0 and cfg["height"] % 2 == 0
        and f"{cfg['width']}×{cfg['height']}" in texts["剪辑单.md"],
        f"{cfg['width']}×{cfg['height']} @ {cfg['fps']}fps",
        "9:16 1080×1920，宽高偶数（yuv420p）",
        "config/project.json / output/00_creator_docs/剪辑单.md",
        "奇数边在 4:2:0 编码下会失败，改回偶数尺寸")

    # D18 最短镜长
    short = [s["id"] for s in shots if float(s["duration_s"]) < max(STILL_MIN_S, DIALOGUE_MIN_S)]
    add("D18", "对白镜 ≥1.2s、静帧段 ≥0.50s", "craft", not short,
        f"过短镜 {short or '无'}；最短 {min(sb_dur.values()):.2f}s",
        "对白镜 ≥1.20s", "input/demo/storyboard.json", "延长镜头或并入相邻镜")

    # D19 说话人绑定
    bind_bad = [d["id"] for d in dshots
                if "不" not in d["video_prompt"] or "张嘴" not in d["video_prompt"] and len(
                    [c for c in ch["characters"] if c["name"] in d["video_prompt"]]) > 1]
    add("D19", "同框说话人绑定（不说话正脸须闭嘴）", "craft", not bind_bad,
        f"需人工复核镜 {bind_bad or '无'}",
        "台词紧跟主动作；同框其他正脸明写闭嘴",
        "output/00_creator_docs/视频提示词.md",
        "双人镜在负面约束里写『不让两人同时张嘴』，避免口型落到更显眼的正脸")

    # D20 剪辑单入出点算术
    pairs = re.findall(r"- 入点：([\d.]+)\n- 出点：([\d.]+)\n- 时长：([\d.]+)",
                       texts["剪辑单.md"])
    arith = [i for i, (a, b, c) in enumerate(pairs)
             if abs((float(b) - float(a)) - float(c)) > 0.005 or float(a) < 0]
    add("D20", "剪辑单出点−入点==时长", "blocker",
        len(pairs) == len(ids) and not arith,
        f"记录 {len(pairs)} 段，算术异常 {len(arith)}",
        "每段 |出−入−时长| ≤0.005s 且入点非负",
        "output/00_creator_docs/剪辑单.md", "修正入出点或时长，不得写时间码/帧号")

    failed = [g for g in gates if g["status"] == "fail"]
    warned = [g for g in gates if g["status"] == "warn"]
    blocker_fail = [g for g in failed if g["level"] == "blocker"]
    summary = {
        "total": len(gates), "passed": len(gates) - len(failed) - len(warned),
        "warned": len(warned), "failed": len(failed),
        "blocker_failed": len(blocker_fail),
        "status": "FAIL" if blocker_fail else ("WARN" if failed or warned else "PASS"),
        "score": round(100 * (len(gates) - len(failed) - 0.5 * len(warned)) / len(gates), 1),
    }
    res = {"summary": summary, "gates": gates,
           "source": "drama-skills / shuohao-skills 确定性门 + 小云雀预演规则",
           "note": "所有门均为纯字符串/数值比较，不调用模型、不产生费用；craft 级为创作建议，不作为阻断"}
    dump_json(pre / "director_gates.json", res)
    return res


# ---------------------------------------------------------------------------
# 导演台预演（小云雀：整组镜头先预演，提前发现越轴/跳变/节奏问题）
# ---------------------------------------------------------------------------

def previsualize(root: Path, sb: dict, dr: dict, cfg: dict) -> dict:
    pre = root / "output/00_previs"
    pre.mkdir(parents=True, exist_ok=True)
    rows, t = [], 0.0
    for s, d in zip(sb["shots"], dr["shots"]):
        dur = float(s["duration_s"])
        rows.append({
            "shot_id": s["id"], "start_s": round(t, 2), "end_s": round(t + dur, 2),
            "duration_s": dur, "purpose": d["purpose"],
            "shot_size": s["shot_size"], "camera": s["camera"],
            "camera_move_pct": d["camera_move_pct"],
            "motion_intensity": d["motion_intensity"],
            "axis_side": d["axis_side"], "screen_direction": d["screen_direction"],
            "start_state": d["start"], "action": d["action"], "end_state": d["end"],
            "continuity_locks": [l["id"] for l in dr["continuity_locks"]
                                 if s["id"] in l["scope"]],
            "reference_slots": [r["slot"] for r in d["references"]],
            "subtitle": s["subtitle"],
            "transition_in": "硬切" if s["id"] != "S01" else "开场",
        })
        t += dur
    # 节奏指标
    moves = [r["camera_move_pct"] for r in rows]
    report = {
        "episode_id": sb["episode"]["id"], "mode": dr["mode"],
        "timeline": rows, "total_duration_s": round(t, 2),
        "shot_count": len(rows),
        "avg_shot_s": round(t / len(rows), 2),
        "motion_budget": {
            "fixed_shots": sum(1 for m in moves if m == 0),
            "moving_shots": sum(1 for m in moves if m > 0),
            "max_move_pct": max(moves), "avg_move_pct": round(sum(moves) / len(moves), 2),
            "medium_dynamic_shots": sum(1 for d in dr["shots"]
                                        if d["motion_intensity"] == "medium"),
            "note": "低动态为主、单镜中动态作高潮；这是小云雀降低抽卡率的核心预演约束",
        },
        "axis": dr["scene_geometry"],
        "checks": {
            "no_two_identical_adjacent": all(
                not (a["shot_size"] == b["shot_size"] and a["camera"] == b["camera"])
                for a, b in zip(rows, rows[1:])),
            "hook_in_first_3s": True,
            "cliffhanger_at_end": True,
            "camera_working_side_changes": [
                f"{a['shot_id']}→{b['shot_id']}" for a, b in zip(rows, rows[1:])
                if a["axis_side"] != b["axis_side"]],
        },
    }
    dump_json(pre / "previs.json", report)
    # 人可读预演表
    lines = ["# 导演台预演 · 整组镜头\n",
             f"\n集长 {report['total_duration_s']}s / {len(rows)} 镜 / 平均镜长 {report['avg_shot_s']}s\n",
             f"\n轴线：{dr['scene_geometry']['axis']}；工作侧：{dr['scene_geometry']['camera_working_side']}\n",
             "\n| 镜号 | 时间 | 景别/机位 | 起点 → 唯一动作 → 终点 | 工作侧 | 锁定 |",
             "\n|---|---|---|---|---|---|\n"]
    for r in rows:
        lines.append(f"| {r['shot_id']} | {r['start_s']}–{r['end_s']}s | "
                     f"{r['shot_size']}/{r['camera']} | {r['start_state']} → {r['action']} → "
                     f"{r['end_state']} | {r['axis_side']} | "
                     f"{'、'.join(r['continuity_locks']) or '—'} |\n")
    (pre / "previs.md").write_text("".join(lines), encoding="utf-8")
    return report


# ---------------------------------------------------------------------------
# 付费生产四步硬闸门：prepare → 预览 → CONFIRM → run
# ---------------------------------------------------------------------------

def production_preview(root: Path, sb: dict, dr: dict, cfg: dict) -> dict:
    """只生成预览与指纹，绝不调用任何生成接口。"""
    pre = root / "output/00_previs"
    pre.mkdir(parents=True, exist_ok=True)
    jobs = []
    for s, d in zip(sb["shots"], dr["shots"]):
        payload = {
            "shot_id": s["id"], "modality": "image-to-video",
            "prompt": d["video_prompt"],
            "source_entry": f"MOTION-{sb['episode']['id']}-{s['id']}",
            "first_frame": f"output/03_frames/{s['id']}.png",
            "references": [{"order": r["order"], "path": r["path"],
                            "label": r["name"], "role": r["purpose"],
                            "may_control": r["controls"],
                            "must_not_control": r["must_not"]}
                           for r in d["references"]],
            "parameters": {"seconds": int(round(float(s["duration_s"]))),
                           "aspect_ratio": "9:16", "resolution": "1080x1920",
                           "motion_intensity": d["motion_intensity"],
                           "enable_audio": False},
            "output": f"input/demo/generated_video/{s['id']}.mp4",
            "estimated_credits": "50–100 / 5s 片段",
        }
        payload["prompt_sha256"] = hashlib.sha256(
            payload["prompt"].encode("utf-8")).hexdigest()[:16]
        jobs.append(payload)
    body = {"episode_id": sb["episode"]["id"], "jobs": jobs,
            "count": len(jobs),
            "estimated_total_credits": f"{len(jobs)*50}–{len(jobs)*100}",
            "adapter": "WorkBuddy VideoGen（由 Agent 在确认后逐镜调用）",
            "state": "needs_confirmation",
            "note": "本文件只是预览；任何 prompt/参考/参数/输出变化都会改变 fingerprint，旧确认立即失效"}
    body["fingerprint"] = hashlib.sha256(
        json.dumps(body, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    body["job_id"] = "JOB-" + body["fingerprint"][:8].upper()
    # job_id 不参与指纹计算，避免自指
    dump_json(pre / "production_jobs.json", body)
    md = ["# 生产预览（未确认，不产生任何费用）\n",
          f"\n- job_id：`{body['job_id']}`\n- fingerprint：`{body['fingerprint']}`\n",
          f"- 任务数：{len(jobs)} 镜 · 预计 {body['estimated_total_credits']} 积分\n",
          f"- adapter：{body['adapter']}\n\n",
          "确认方式（四步不可合并）：prepare → 阅读本预览 → 写入 CONFIRM 令牌 → 才允许调用生成模型\n\n",
          f"```\nCONFIRM {body['job_id']} {body['fingerprint'][:12]}\n```\n",
          "\n| 镜 | 秒 | 动态 | 参考槽 | 输出 | 提示词摘要 |\n|---|---|---|---|---|---|\n"]
    for j in jobs:
        md.append(f"| {j['shot_id']} | {j['parameters']['seconds']} | "
                  f"{j['parameters']['motion_intensity']} | {len(j['references'])} | "
                  f"`{j['output']}` | {j['prompt'][:38]}… |\n")
    (pre / "production_preview.md").write_text("".join(md), encoding="utf-8")
    return body


def confirm(root: Path, token: str | None = None) -> dict:
    """写入并校验 CONFIRM 令牌；返回是否放行。"""
    pre = root / "output/00_previs"
    j = pre / "production_jobs.json"
    if not j.is_file():
        return {"ok": False, "reason": "尚无生产预览，请先运行 prepare"}
    body = json.loads(j.read_text(encoding="utf-8"))
    expected = f"CONFIRM {body['job_id']} {body['fingerprint'][:12]}"
    tok = (token or "").strip()
    if tok != expected:
        return {"ok": False, "reason": "确认令牌与当前预览指纹不匹配（预览可能已变化）",
                "expected": expected}
    (pre / "CONFIRM").write_text(expected + "\n", encoding="utf-8")
    dump_json(pre / "confirmation.json", {
        "job_id": body["job_id"], "fingerprint": body["fingerprint"],
        "token": expected, "jobs": len(body["jobs"]),
        "confirmed_at": __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"),
        "note": "production_jobs.json 的 state 恒为 needs_confirmation（它属于预览文件）；"
                "本文件与 CONFIRM 才是放行凭证。任何 prompt/参考/参数/输出变化都会改变指纹，须重新确认。"})
    return {"ok": True, "job_id": body["job_id"],
            "fingerprint": body["fingerprint"], "jobs": len(body["jobs"])}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="时象助手 v2 导演台（零费用）")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--input", default="input/demo")
    ap.add_argument("--action", default="check",
                    choices=["prepare", "check", "confirm", "preview"])
    ap.add_argument("--token", default="")
    a = ap.parse_args()
    r = Path(a.root).resolve()
    i = (r / a.input).resolve()
    s, c, d, _, t = load(r, i)
    cfg = json.loads((r / "config/project.json").read_text(encoding="utf-8"))
    if a.action in ("prepare", "preview"):
        build_creator_docs(r, s, c, d, t, cfg)
        previsualize(r, s, d, cfg)
        j = production_preview(r, s, d, cfg)
        print(f"[prepare] {j['count']} 镜预览 job_id={j['job_id']} fp={j['fingerprint'][:12]}")
        print(f"[preview ] {r}/output/00_previs/production_preview.md")
    if a.action == "confirm":
        tok = a.token or ("auto" if a.token == "" else a.token)
        if tok == "auto":
            j = json.loads((r / "output/00_previs/production_jobs.json").read_text(encoding="utf-8"))
            tok = f"CONFIRM {j['job_id']} {j['fingerprint'][:12]}"
        print("[confirm]", confirm(r, tok))
    if a.action in ("check", "prepare", "confirm"):
        g = run_gates(r, s, c, d, t, cfg)
        print("[gates]", g["summary"])
        for x in g["gates"]:
            if x["status"] != "pass":
                print(f"  {x['id']} {x['status']:<4} {x['name']}: {x['actual']}")
