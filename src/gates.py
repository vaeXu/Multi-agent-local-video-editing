"""人工确认门：人可以随时查验任一环节，并通过 output/gates.json 批准或驳回。

默认模式：门为 pending 时流水线暂停，等人写入 gates.json 后用 --from 继续。
--auto-approve：演示/无人值守模式，全部自动通过，但 note 会标注「仍需人工复核」。
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

GATE_DEFS = [
    {
        "id": "G1", "stage": "01_script", "name": "剧本与分镜确认",
        "how_to_verify": "打开 output/01_script/script.md 与 storyboard.json，核对钩子、题材红线、台词长度与镜头时长",
        "reject_action": "修改 input/<项目名>/storyboard.json 后执行 pipeline.py --from 01_script",
    },
    {
        "id": "G2", "stage": "02_characters", "name": "角色定妆与一致性锁定",
        "how_to_verify": "打开 output/02_characters/character_sheets/ 逐张核对五官与 3 条以上刚性锚点、音色分配",
        "reject_action": "修改 input/<项目名>/characters.json 后执行 pipeline.py --from 02_characters",
    },
    {
        "id": "G3", "stage": "03_frames", "name": "真人转绘帧验收",
        "how_to_verify": "打开 output/03_frames/*.png 与 frame_sources.csv，核对画风统一、无水印、无黑边、每镜来源",
        "reject_action": "替换 input/<项目名>/frames/ 或调整 config/project.json 的 comicify 参数后 --from 03_frames",
    },
    {
        "id": "G4", "stage": "05_audio", "name": "配音与音画同步预检",
        "how_to_verify": "试听 output/05_audio/S*.wav，核对 audio_sync.json 中每镜音轨长度与镜头时长一致",
        "reject_action": "调整 characters.json 的 voice 或 tts_rate 后 --from 05_audio",
    },
    {
        "id": "G5", "stage": "07_reports", "name": "成片终审（人工）",
        "how_to_verify": "播放 output/06_final/EP01.mp4；打开 console/index.html 逐条核对现场无法自动判定的规则（标 warn 项）",
        "reject_action": "按合规报告 fix_hint 修改后 --from 对应环节；确认通过请把 G5 置为 approved",
    },
]

FILE = "output/gates.json"


def load(root: Path) -> dict:
    p = root / FILE
    if p.is_file():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {}


def save(root: Path, data: dict) -> None:
    p = root / FILE
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def resolve(root: Path, gate_id: str, auto_approve: bool) -> dict:
    """返回单个门的记录；auto_approve 时不覆盖人工已经写入的驳回决定。"""
    defn = next((g for g in GATE_DEFS if g["id"] == gate_id), None)
    if defn is None:
        return {}
    data = load(root)
    rec = data.get(gate_id, {})
    status = rec.get("status", "pending")
    note = rec.get("note", "")
    reviewer = rec.get("reviewer", "人工")
    if auto_approve and status == "pending":
        status = "approved"
        note = "演示模式自动通过，仍需人工复核"
        reviewer = "auto-approve（待人工复核）"
        data[gate_id] = {"status": status, "note": note, "reviewer": reviewer,
                         "at": datetime.now().astimezone().isoformat(timespec="seconds")}
        save(root, data)
    out = dict(defn)
    out.update({"status": status, "note": note, "reviewer": reviewer,
                "decided_at": rec.get("at", "")})
    return out


def all_gates(root: Path) -> list[dict]:
    data = load(root)
    out = []
    for g in GATE_DEFS:
        rec = dict(g)
        r = data.get(g["id"], {})
        rec.update({"status": r.get("status", "pending"), "note": r.get("note", ""),
                    "reviewer": r.get("reviewer", "人工"), "decided_at": r.get("at", "")})
        out.append(rec)
    return out


def pending_hint(root: Path, gate: dict) -> str:
    return (
        f"\n⏸ 人工确认门 {gate['id']}「{gate['name']}」当前为 {gate['status']}，流水线已暂停。\n"
        f"  查验方式：{gate['how_to_verify']}\n"
        f"  通过：编辑 {FILE}，把 \"{gate['id']}\" 的 status 改为 \"approved\"\n"
        f"  驳回：改为 \"rejected\" 并在 note 写明意见；{gate['reject_action']}\n"
        f"  继续：python3 src/pipeline.py --from {gate['stage']}\n"
        f"  或用 --auto-approve 无人值守跑完全流程（门会标注仍需人工复核）。\n"
    )
