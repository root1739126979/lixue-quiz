import httpx


def build_explanation_prompt(
    stem: str,
    options: dict[str, str],
    correct_answer: str,
    original_explanation: str,
) -> str:
    option_lines = "\n".join(f"{label}. {content}" for label, content in options.items())
    return (
        "你是企业内部培训刷题系统的讲解助手。请基于题目、选项、正确答案和原解析，"
        "给出简洁、准确、适合员工复习的补充讲解。不要编造题目没有支持的事实。\n\n"
        f"题目：{stem}\n"
        f"选项：\n{option_lines}\n"
        f"正确答案：{correct_answer}\n"
        f"原解析：{original_explanation or '无'}\n\n"
        "请输出三段：答案解释、易错点、关联知识。"
    )


async def request_chat_completion(base_url: str, api_key: str, model: str, prompt: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            base_url.rstrip("/") + "/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
