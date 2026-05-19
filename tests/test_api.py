from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import app


def clean_data() -> None:
    for path in Path("data").glob("*.json"):
        path.unlink()


def test_upload_and_ask_with_document_filter() -> None:
    clean_data()
    client = TestClient(app)

    hr = client.post(
        "/upload",
        files={"file": ("hr.md", "年假 制度 入职 满一年 可享受 五天 年假", "text/markdown")},
    )
    finance = client.post(
        "/upload",
        files={"file": ("finance.md", "报销 制度 发票 审批 财务", "text/markdown")},
    )

    assert hr.status_code == 200
    assert finance.status_code == 200
    hr_id = hr.json()["document_id"]
    finance_id = finance.json()["document_id"]

    response = client.post(
        "/ask",
        json={"question": "年假 制度", "document_ids": [hr_id], "top_k": 3},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["sources"]
    assert body["sources"][0]["document_id"] == hr_id
    assert body["sources"][0]["document_id"] != finance_id


def test_update_document_replaces_active_chunks() -> None:
    clean_data()
    client = TestClient(app)

    uploaded = client.post(
        "/upload",
        files={"file": ("policy.md", "年假 制度 入职 满一年 五天", "text/markdown")},
    )
    document_id = uploaded.json()["document_id"]

    updated = client.put(
        f"/documents/{document_id}",
        files={"file": ("policy.md", "费用 发票 审批 财务", "text/markdown")},
    )

    assert updated.status_code == 200
    assert updated.json()["active_version"] == 2

    response = client.post(
        "/ask",
        json={"question": "年假 入职", "document_ids": [document_id], "top_k": 3},
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "根据当前知识库内容，无法回答该问题。"


def test_mock_answer_includes_relevant_policy_content() -> None:
    clean_data()
    client = TestClient(app)

    uploaded = client.post(
        "/upload",
        files={
            "file": (
                "employee_handbook.md",
                "# 员工手册\n\n## 年假制度\n\n员工入职满一年后，可以享受带薪年假。累计工作年限不满十年的员工，每年享有五天年假。年假应至少提前五个工作日申请。\n\n## 病假制度\n\n员工请病假需要通知主管。",
                "text/markdown",
            )
        },
    )
    document_id = uploaded.json()["document_id"]

    response = client.post(
        "/ask",
        json={"question": "公司年假制度是怎么样的", "document_ids": [document_id], "top_k": 3},
    )

    assert response.status_code == 200
    answer = response.json()["answer"]
    assert "五天年假" in answer
    assert "提前五个工作日" in answer


def test_company_benefits_can_be_retrieved_by_keyword() -> None:
    clean_data()
    client = TestClient(app)

    uploaded = client.post(
        "/upload",
        files={
            "file": (
                "company_benefits.txt",
                "公司福利说明\n\n餐补：公司为正式员工提供工作日餐补。\n\n体检：公司每年为正式员工安排一次年度体检。\n\n培训：员工可以申请参加与岗位相关的外部培训。",
                "text/plain",
            )
        },
    )
    document_id = uploaded.json()["document_id"]

    response = client.post(
        "/ask",
        json={"question": "公司福利有哪些", "document_ids": [document_id], "top_k": 3},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["sources"]
    assert body["sources"][0]["document"] == "company_benefits.txt"
    assert "餐补" in body["answer"] or "体检" in body["answer"] or "培训" in body["answer"]
