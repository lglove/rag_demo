from app.core.schemas import SearchResult


def build_qa_prompt(question: str, results: list[SearchResult]) -> str:
    context_blocks = []
    for idx, result in enumerate(results, start=1):
        chunk = result.chunk
        context_blocks.append(
            f"[来源{idx}] 文档：{chunk.filename}，片段：{chunk.chunk_id}\n"
            f"{chunk.content}"
        )

    context = "\n\n".join(context_blocks)
    return f"""你是企业知识库问答助手。

请严格基于以下【知识库片段】回答用户问题。
如果知识库片段中没有足够信息，请回答：“根据当前知识库内容，无法回答该问题。”

要求：
1. 不要编造知识库中不存在的信息。
2. 不要使用外部常识补充答案。
3. 回答应简洁、准确。
4. 如果引用了内容，请在答案中标注来源编号。

【知识库片段开始】
{context}
【知识库片段结束】

【用户问题】
{question}
"""
