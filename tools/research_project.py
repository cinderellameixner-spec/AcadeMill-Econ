"""Create isolated research folders and discussion runs using only stdlib."""
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / "research"
LOCAL_TIME = timezone(timedelta(hours=8), "Asia/Shanghai")


def write(path, content):
    path.write_text(content, encoding="utf-8")


def projects(root):
    return sorted(p for p in root.glob("R[0-9]*_*") if p.is_dir() and (p / "PROJECT.md").is_file())


def resolve(root, project_id):
    if not re.fullmatch(r"R\d{3,}", project_id):
        raise ValueError("研究 ID 应为 R001 等格式")
    matches = [p for p in projects(root) if p.name.split("_", 1)[0] == project_id]
    if len(matches) != 1:
        raise ValueError("研究 ID 不存在或不唯一，请先运行 list")
    return matches[0]


def create_run(project, request):
    stamp = datetime.now(LOCAL_TIME).strftime("%Y%m%d_%H%M%S_%f")
    run = project / "runs" / stamp
    run.mkdir(parents=True, exist_ok=False)
    write(run / "request.md", "# 本轮需求\n\n" + request + "\n")
    write(run / "summary.md", "# 讨论摘要\n\n尚未开展本轮讨论。\n\n## 证据与核验\n\n待记录。\n\n## 下一步\n\n按本轮需求开展讨论。\n")
    write(run / "task.md", "# 本轮任务\n\n状态：进行中\n\n## 已完成\n\n- 建立记录目录。\n\n## 未完成\n\n- 本轮研究任务。\n\n## 成果\n\n尚无。\n")
    return run


def create_project(root, title):
    title = title.strip()
    if not title:
        raise ValueError("研究名称不能为空")
    slug = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", title).strip(" .")[:48].rstrip(" .")
    if not slug:
        raise ValueError("研究名称没有可用字符")
    root.mkdir(parents=True, exist_ok=True)
    number = 1
    while True:
        project_id = f"R{number:03d}"
        # A reservation directory prevents simultaneous creators reusing the ID.
        reservation = root / ("." + project_id + ".reserved")
        if any(root.glob(project_id + "_*")):
            number += 1
            continue
        try:
            reservation.mkdir()
            break
        except FileExistsError:
            number += 1
    project = root / f"{project_id}_{slug}"
    try:
        project.mkdir(exist_ok=False)
        for name in ("inbox", "work", "output", "runs"):
            (project / name).mkdir()
        write(project / "decisions.md", "# 决策记录\n\n尚无研究决策。追加时注明轮次、依据与用户确认状态。\n")
        write(project / "sources.md", "# 来源清单\n\n尚未登记材料。记录项目相对路径、来源/DOI、Zotero 条目键与核验状态。\n")
        run = create_run(project, f"开始独立研究：{title}")
        write(project / "PROJECT.md", f"# {title}\n\n研究 ID：{project_id}\n\n创建时间：{datetime.now(LOCAL_TIME).isoformat(timespec='seconds')}\n\n## 研究问题\n\n待讨论聚焦。\n\n## 用户约束\n\n待记录。\n\n## 当前阶段\n\n初次讨论，尚未评估。\n\n## 已完成成果\n\n仅建立目录，无研究成果。\n\n## 待核验事项\n\n待记录。\n\n## 下一步\n\n确认研究兴趣、问题与约束。\n\n## 最近轮次\n\n[本轮记录](runs/{run.name}/summary.md)\n")
    finally:
        reservation.rmdir()
    return project, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list")
    new = commands.add_parser("new")
    new.add_argument("title")
    run = commands.add_parser("run")
    run.add_argument("project_id")
    run.add_argument("request")
    args = parser.parse_args()
    try:
        if args.command == "list":
            found = projects(ROOT)
            print("\n".join(p.name for p in found) if found else "尚无研究项目")
        elif args.command == "new":
            project, record = create_project(ROOT, args.title)
            print(f"研究目录：{project}\n本轮记录：{record}")
        else:
            if not args.request.strip():
                raise ValueError("本轮需求不能为空")
            record = create_run(resolve(ROOT, args.project_id), args.request)
            print(f"本轮记录：{record}\n请在讨论后更新 PROJECT.md 和本轮记录。")
    except (ValueError, OSError) as error:
        parser.exit(1, f"创建/读取失败：{error}\n")


if __name__ == "__main__":
    main()
