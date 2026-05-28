from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import csv


QUESTION_TYPE_MAP = {
    "单选题": "single",
    "多选题": "multiple",
    "判断题": "judgment",
}


@dataclass(frozen=True)
class ParsedOption:
    label: str
    content: str


@dataclass(frozen=True)
class ParsedQuestion:
    source_no: str
    question_type: str
    stem: str
    options: list[ParsedOption]
    correct_answer: str
    correct_answer_text: str
    explanation: str


@dataclass(frozen=True)
class ImportErrorItem:
    row_number: int
    message: str


@dataclass(frozen=True)
class ImportPreview:
    total_rows: int
    valid_count: int
    type_counts: dict[str, int]
    rows: list[ParsedQuestion]
    errors: list[ImportErrorItem]


def normalize_answer(answer: str) -> str:
    normalized = answer.replace("，", ",").replace("、", ",").replace("；", ",")
    labels = [part.strip().upper() for part in normalized.split(",") if part.strip()]
    return ",".join(sorted(labels))


def parse_question_csv(path: Path) -> ImportPreview:
    rows: list[ParsedQuestion] = []
    errors: list[ImportErrorItem] = []
    type_counter: Counter[str] = Counter()

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for row_index, row in enumerate(reader, start=2):
            question_type = QUESTION_TYPE_MAP.get((row.get("题型") or "").strip())
            stem = (row.get("题干") or "").strip()
            answer = normalize_answer(row.get("正确答案") or "")
            source_no = (row.get("题号") or "").strip()

            if not source_no:
                errors.append(ImportErrorItem(row_index, "题号不能为空"))
                continue
            if not question_type:
                errors.append(ImportErrorItem(row_index, "题型必须是单选题、多选题或判断题"))
                continue
            if not stem:
                errors.append(ImportErrorItem(row_index, "题干不能为空"))
                continue
            if not answer:
                errors.append(ImportErrorItem(row_index, "正确答案不能为空"))
                continue
            if question_type == "single" and "," in answer:
                errors.append(ImportErrorItem(row_index, "单选题正确答案只能有一个选项"))
                continue

            options = []
            option_labels = set()
            for label in ["A", "B", "C", "D", "E"]:
                content = (row.get(f"选项{label}") or "").strip()
                if content:
                    options.append(ParsedOption(label=label, content=content))
                    option_labels.add(label)
            if not options:
                errors.append(ImportErrorItem(row_index, "至少需要一个选项"))
                continue
            missing_labels = [label for label in answer.split(",") if label not in option_labels]
            if missing_labels:
                errors.append(
                    ImportErrorItem(row_index, f"正确答案选项不存在：{','.join(missing_labels)}")
                )
                continue

            rows.append(
                ParsedQuestion(
                    source_no=source_no,
                    question_type=question_type,
                    stem=stem,
                    options=options,
                    correct_answer=answer,
                    correct_answer_text=(row.get("正确答案文本") or "").strip(),
                    explanation=(row.get("解析") or "").strip(),
                )
            )
            type_counter[question_type] += 1

    return ImportPreview(
        total_rows=len(rows) + len(errors),
        valid_count=len(rows),
        type_counts=dict(type_counter),
        rows=rows,
        errors=errors,
    )
