from pathlib import Path

from app.services.csv_importer import normalize_answer, parse_question_csv


def test_parse_existing_question_csv_supports_all_question_types():
    result = parse_question_csv(Path("../question/questions.csv"))

    assert result.total_rows == 169
    assert result.valid_count == 168
    assert result.type_counts == {"single": 112, "multiple": 31, "judgment": 25}
    assert len(result.errors) == 1
    assert result.errors[0].row_number == 170
    assert result.rows[0].source_no == "1"
    assert result.rows[0].stem
    assert result.rows[0].options


def test_parse_question_csv_reports_invalid_rows_without_crashing(tmp_path):
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text(
        "题号,题型,题干,选项A,选项B,选项C,选项D,选项E,正确答案,正确答案文本,解析\n"
        "1,单选题,题干,A,B,C,D,,A,A文本,解析\n"
        "2,单选题,缺答案,A,B,C,D,,,\n",
        encoding="utf-8-sig",
    )

    result = parse_question_csv(csv_file)

    assert result.total_rows == 2
    assert result.valid_count == 1
    assert len(result.errors) == 1
    assert result.errors[0].row_number == 3
    assert "正确答案" in result.errors[0].message


def test_normalize_answer_sorts_multiple_choice_answers():
    assert normalize_answer("C， A,B") == "A,B,C"
