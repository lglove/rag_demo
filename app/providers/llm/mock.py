from app.providers.llm.base import BaseLLMProvider


class MockLLMProvider(BaseLLMProvider):
    def generate(self, prompt: str) -> str:
        marker = "【知识库片段开始】"
        end_marker = "【知识库片段结束】"
        question_marker = "【用户问题】"
        if marker not in prompt or end_marker not in prompt or question_marker not in prompt:
            return "根据当前知识库内容，无法回答该问题。"

        context = prompt.split(marker, 1)[1].split(end_marker, 1)[0].strip()
        question = prompt.split(question_marker, 1)[1].strip()
        if not context:
            return "根据当前知识库内容，无法回答该问题。"

        sentences = self._extract_sentences(context)
        keywords = self._keywords(question)
        matched = [
            sentence
            for sentence in sentences
            if any(keyword in sentence for keyword in keywords)
        ]
        selected = matched[:3] or sentences[:3]

        if not selected:
            return "根据当前知识库内容，无法回答该问题。"

        return "".join(selected)

    def _extract_sentences(self, context: str) -> list[str]:
        content_lines = []
        for line in context.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("[来源") or stripped.startswith("#"):
                continue
            content_lines.append(stripped)

        text = "".join(content_lines)
        sentences: list[str] = []
        current = []
        for char in text:
            current.append(char)
            if char in "。！？；;":
                sentence = "".join(current).strip()
                if sentence:
                    sentences.append(sentence)
                current = []

        tail = "".join(current).strip()
        if tail:
            sentences.append(tail)
        return sentences

    def _keywords(self, question: str) -> list[str]:
        normalized = "".join(question.lower().split())
        stop_words = {
            "公司",
            "制度",
            "怎样",
            "怎么样",
            "什么",
            "如何",
            "多少",
            "需要",
            "可以",
            "的是",
        }
        words = [word for word in question.lower().split() if word and word not in stop_words]
        grams = [
            normalized[index : index + 2]
            for index in range(max(len(normalized) - 1, 0))
            if normalized[index : index + 2] not in stop_words
        ]
        return words + grams
