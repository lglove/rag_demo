# 企业知识库问答系统最小版本

这是一个 Python + FastAPI 实现的最小 RAG 系统，支持文档上传、文档向量化、相似度检索、基于检索结果生成回答，并返回引用来源。

## 启动

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

接口文档：

```text
http://127.0.0.1:8000/docs
```

内置测试页面：

```text
http://127.0.0.1:8000/
```

## 容器化部署

使用 Docker Compose 启动：

```bash
docker compose up --build
```

服务地址：

```text
http://127.0.0.1:8000
```

打开该地址即可使用内置 UI 页面上传文档、选择文档、提问、更新和删除文档。

接口文档：

```text
http://127.0.0.1:8000/docs
```

数据持久化：

```text
docker-compose.yml 使用 rag_data volume 挂载 /app/data
documents.json、chunks.json、embedding_cache.json 会保存在该 volume 中
```

单独构建镜像：

```bash
docker build -t rag-demo .
docker run --rm -p 8000:8000 -v rag_demo_data:/app/data rag-demo
```

## 模型配置

默认配置使用 Mock LLM 和 Mock Embedding，便于本地演示：

```bash
docker compose up --build
```

### 使用 DeepSeek 生成答案

DeepSeek API 兼容 OpenAI SDK。设置以下环境变量即可切换 LLM：

```bash
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY
docker compose up --build
```

`.env` 示例：

```text
LLM_PROVIDER=deepseek
EMBEDDING_PROVIDER=mock
DEEPSEEK_API_KEY=你的 DeepSeek API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_LLM_MODEL=deepseek-v4-flash
```

可选模型示例：

```text
deepseek-v4-flash
deepseek-v4-pro
```

### 使用 OpenAI 生成答案

```bash
LLM_PROVIDER=openai \
OPENAI_API_KEY="你的 OpenAI API Key" \
OPENAI_LLM_MODEL="gpt-4o-mini" \
docker compose up --build
```

### Embedding 说明

当前 `EMBEDDING_PROVIDER` 支持：

```text
EMBEDDING_PROVIDER=mock
EMBEDDING_PROVIDER=openai
EMBEDDING_PROVIDER=openai-compatible
```

OpenAI embedding：

```text
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=你的 OpenAI API Key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

OpenAI-compatible embedding 服务：

```text
EMBEDDING_PROVIDER=openai-compatible
EMBEDDING_API_KEY=你的 embedding 服务 Key
EMBEDDING_BASE_URL=https://your-embedding-api.example.com/v1
EMBEDDING_MODEL=你的 embedding 模型名
```

`mock` 适合 Demo 测试，不适合生产语义检索。生产环境建议使用真实 embedding 模型，例如 OpenAI embedding、BGE、Jina、Qwen embedding 或企业内部 embedding 服务。

切换 embedding 模型后，旧向量不能混用，需要删除旧索引或重新上传文档：

```bash
docker compose down -v
docker compose up --build
```

## API

### 上传文档

```http
POST /upload
Content-Type: multipart/form-data
```

字段：

```text
file: txt 或 md 文件
```

响应：

```json
{
  "document_id": "doc_xxx",
  "filename": "employee_handbook.md",
  "chunk_count": 12,
  "embedded_chunk_count": 10,
  "skipped_duplicate_count": 2
}
```

### 问答

```http
POST /ask
```

请求：

```json
{
  "question": "公司年假制度是怎样的？",
  "document_ids": ["doc_xxx"],
  "top_k": 5
}
```

`document_ids` 可选。不传时在所有文档中检索；传入时只在指定文档中检索。

### 更新文档

```http
PUT /documents/{document_id}
Content-Type: multipart/form-data
```

更新采用版本化策略：先写入新版本 chunks，成功后切换 `active_version`，再删除旧版本 chunks。问答只检索文档的当前活跃版本。

### 文档列表

```http
GET /documents
```

### 删除文档

```http
DELETE /documents/{document_id}
```

删除该文档的 metadata 和所有 chunks。embedding cache 不删除，因为相同内容可能被其他文档复用。

## 架构设计

系统分为 API 层、服务层、核心能力层、Provider 抽象层和存储层。

```text
FastAPI API
  -> DocumentService / QAService
  -> Text Splitter / Prompt Builder
  -> EmbeddingProvider / LLMProvider / VectorStore
  -> JSON documents / chunks / embedding cache
```

业务层只依赖抽象接口：

```python
class BaseLLMProvider:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError

class BaseEmbeddingProvider:
    def embed_text(self, text: str) -> list[float]:
        raise NotImplementedError

class BaseVectorStore:
    def search(...):
        raise NotImplementedError
```

当前默认实现：

```text
MockLLMProvider
DeepSeekLLMProvider
OpenAILLMProvider
MockEmbeddingProvider
JsonVectorStore
```

后续可以替换为 OpenAI、Claude、Gemini、FAISS、Qdrant、Milvus 或 Chroma。

## 模块划分

```text
app/api              HTTP 接口
app/services         上传、更新、问答编排
app/core             schema、切分、prompt
app/providers        LLM 和 Embedding 抽象及实现
app/vectorstores     向量库抽象及 JSON 实现
app/repositories     文档、chunk、embedding cache 持久化
tests                基础接口测试
```

## 文档隔离设计

本版本只按 `document_id` 做隔离。

每个文档上传后生成独立 `document_id`。每个 chunk 都保存：

```json
{
  "document_id": "doc_xxx",
  "document_version": 1,
  "chunk_id": 3,
  "filename": "employee_handbook.md",
  "content": "...",
  "content_hash": "sha256_xxx",
  "embedding_model": "mock-embedding-v1",
  "embedding": []
}
```

检索时如果传入 `document_ids`，向量库先按 `document_id` 过滤，再计算相似度。

## RAG 流程

上传流程：

```text
上传 txt/md
  -> 读取文本
  -> 文本切分
  -> 计算 chunk hash
  -> 命中 embedding cache 则复用
  -> 未命中则生成 embedding
  -> chunk 写入向量库
  -> document metadata 写入仓储
```

问答流程：

```text
用户问题
  -> 问题 embedding
  -> 按 document_id 和 active_version 过滤
  -> Top-K 相似度检索
  -> 相似度阈值判断
  -> 构造 Prompt
  -> 调用 LLM
  -> 返回 answer + sources
```

## Prompt 设计思路

Prompt 明确要求模型只能基于检索片段回答：

```text
请严格基于以下【知识库片段】回答用户问题。
如果知识库片段中没有足够信息，请回答：
“根据当前知识库内容，无法回答该问题。”
```

同时要求：

```text
不编造不存在的信息
不使用外部常识补充
引用来源编号
```

## 如何避免 hallucination

当前实现包含四层基础防护：

```text
1. 没有文档或没有检索结果时拒答
2. Top-K 结果低于 MIN_SCORE_THRESHOLD 时拒答
3. Prompt 约束只能基于知识库片段回答
4. 返回 sources，方便用户核查
```

生产环境可继续增加答案一致性校验，让另一个模型判断答案是否完全被 sources 支撑。

## 避免重复 embedding

每个 chunk 计算：

```text
content_hash = sha256(chunk_content)
```

embedding cache 的 key 是：

```text
embedding_model:content_hash
```

这样同样内容在同一个 embedding 模型下不会重复计算。缓存和文档归属解耦，因此删除某个文档不会删除 cache。

## 如果要支持 10 万 QPS

需要从单机 Demo 升级为分布式架构：

```text
1. API Gateway + 多实例 FastAPI 水平扩展
2. 文档上传异步化，使用 Kafka/RabbitMQ/Celery
3. embedding 服务独立部署，支持批量推理和 GPU
4. 使用 Qdrant/Milvus/Pinecone 等分布式向量数据库
5. 高频问题缓存：问题 embedding、检索结果、最终答案
6. 多级检索：BM25 粗召回 + 向量召回 + rerank
7. 模型路由：简单问题走小模型，复杂问题走大模型
8. LLM 限流、熔断、降级和流式返回
9. 按 document_id 或业务域分片，降低单次检索范围
```

10 万 QPS 下 LLM 调用通常是瓶颈，必须依赖缓存、路由、降级和异步架构。

## 如果 embedding 模型升级

不要覆盖旧向量。应保留模型版本：

```text
embedding_model = text-embedding-3-small@v1
embedding_model = text-embedding-3-small@v2
```

迁移流程：

```text
1. 新模型作为 v2 上线
2. 新上传文档写入 v2 embedding
3. 老文档后台异步重算 v2 embedding
4. 查询层支持按 embedding_model 检索
5. 灰度部分流量到 v2
6. 对比召回率、答案质量、延迟和成本
7. 稳定后切默认版本
8. 保留 v1 一段时间用于回滚
```

## 测试

```bash
pytest
```
