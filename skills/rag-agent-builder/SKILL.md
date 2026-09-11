---
name: rag-agent-builder
description: 构建结合大语言模型能力与外部知识源的检索增强生成（RAG）应用。覆盖向量数据库选型、Embedding 向量化、检索策略优化与回答生成。Use when 开发文档问答系统、知识库检索、企业私有数据搜索，或将 LLM 与定制数据源结合；不用于常规数据库 CRUD 查询或不涉及外部检索增强的通用搜索任务。
---

# RAG Agent Builder

构建高可用、生产级的检索增强生成（Retrieval-Augmented Generation，RAG）应用，通过外部专业知识库扩展大语言模型的能力边界，生成精准、基于事实且具备上下文依据的回答。

## 快速上手与示例工具

本 Skill 在配套目录中提供了完整的实现范例与实用工具模块：

- **代码范例**：查阅 [`examples/`](examples/) 目录：
  - [`basic_rag.py`](examples/basic_rag.py)：分块、向量化、检索、生成的经典流水线；
  - [`retrieval_strategies.py`](examples/retrieval_strategies.py)：混合检索（BM25+向量）、重排序（Reranking）与元数据过滤；
  - [`agentic_rag.py`](examples/agentic_rag.py)：由 Agent 自主控制的多轮迭代检索与意图细化。
- **公用工具**：查阅 [`scripts/`](scripts/) 目录：
  - [`embedding_management.py`](scripts/embedding_management.py)：向量生成、归一化与本地缓存管理；
  - [`vector_db_manager.py`](scripts/vector_db_manager.py)：主流向量数据库的统一抽象与工厂模式封装；
  - [`rag_evaluation.py`](scripts/rag_evaluation.py)：检索准确率与回答生成质量量化评估指标。

## 系统核心架构概述

一个标准的 RAG 系统由三大核心环节协同构成：
1. **文档检索（Document Retrieval）**：从结构化或非结构化知识库中精准检索与问题高度相关的信息片段；
2. **上下文整合（Context Integration）**：对检索出的多源片段进行清洗、排序、压缩，并组装进 Prompt 上下文窗口；
3. **回答生成（Response Generation）**：引导 LLM 基于提供的上下文事实生成严谨、带溯源引用的答案。

### 为什么需要 RAG？

- **无 RAG 模式**：LLM 仅依赖训练时的预训练权重，存在知识时效滞后、无法触达私有数据、容易产生事实幻觉的问题；
- **RAG 增强模式**：LLM 结合实时、动态的垂直业务知识，产出事实可考、来源可溯的可靠回答。

### 核心适用场景

- **私有文档问答**：针对 PDF、技术手册、合同报告、产品文档进行精准解答；
- **知识库智能搜索**：企业内网 Wiki、Notion、Confluence 文档智能检索；
- **企业级统一搜索**：打通多系统异构数据孤岛；
- **特定上下文辅助助手**：客户服务机器人、HR 规章答疑、技术支持助手；
- **强事实敏感型领域**：法律法规条文比对、医疗健康知识库、金融投研分析。

### 不适合采用 RAG 的场景

- 通用常识闲聊与开放性创意写作；
- 秒级高频变动的纯实时交易流数据（优先采用实时 Tool 调用）；
- 简单的主键查找或单表结构化精确过滤（直接编写 SQL 数据库查询更稳定）。

## 核心架构演进模式

### 1. 经典基础流水线（Basic RAG）
```text
原始文档 → 分块（Chunks） → 向量化（Embeddings） → 存入向量数据库
                                                         ↓
用户提问 → 向量化查询 → 相似度检索 → 拼装 Prompt → LLM → 生成最终回答
                            ↑           ↓
                        向量数据库    检索上下文
```
- **优势**：结构清晰、开发周期短，适用于基础单轮问答。
- **局限**：对复杂多跳问题缺乏深挖能力，一次检索质量决定成败。

### 2. Agent 驱动型检索（Agentic RAG）
- 由 Agent 自主判断是否需要检索、何时检索；
- 能够根据中间推理结果动态重写并多轮迭代检索查询；
- 擅长处理多步骤、多线索的复杂推理与长链路任务。

### 3. 分层检索架构（Hierarchical RAG）
- 建立多层级文档拓扑结构（篇章级摘要 → 小节级细粒度块）；
- 先锁定高层概括主题，再深入定位局部细节块，大幅优化召回效率与上下文相关度。

### 4. 混合检索模式（Hybrid Search RAG）
- 结合传统关键词检索（BM25 / 倒排索引）与语义向量相似度检索（Dense Embeddings）；
- 兼顾专业专有名词、编号的精准命中与抽象语义泛化匹配；
- 显著提升混合复杂查询的召回稳定性。

### 5. 矫正性检索（CRAG，Corrective RAG）
- 检索后先由评价模型对文档相关性进行质量打分；
- 若相关性不足，自动触发备选检索策略、扩大检索范围或回退到网络搜索；
- 确保注入上下文的信息真实可靠。

## 关键实施组件与技术实现

### 1. 文档解析与分块策略（Chunking）

```python
# 1. 简单固定大小分块（带重叠区）
chunks = split_text(doc, chunk_size=1000, overlap=100)

# 2. 语义分块（按语义段落连贯度切分）
chunks = semantic_chunking(doc, max_tokens=512)

# 3. 结构化分层切分（保持标题与小节层级）
chapters = split_by_heading(doc)
chunks = split_each_chapter(chapters, size=1000)
```

**设计关键考量：**
- 分块过小会丢失宏观语境，分块过大会引入噪声并挤占 Token 预算；
- 设置适度重叠区（Overlap，通常 10%–20%）可防止关键信息在切割边界处断裂；
- 保留元数据（如章节标题、页码、文档更新时间）对后续精准过滤至关重要。

### 2. 向量嵌入（Embeddings）

- **主流商业模型**：OpenAI `text-embedding-3-small` / `text-embedding-3-large`、Cohere Embed v3；
- **主流开源模型**：BGE 系列（如 `bge-large-zh`）、`all-MiniLM-L6-v2`、`all-mpnet-base-v2`；
- **垂直领域模型**：在医疗、金融、法律等专业术语密集领域，采用微调或垂直领域 Embedding 模型。

**工程准则：**
- 文档建库索引与查询提问必须使用完全相同的 Embedding 模型；
- 存入前对向量执行归一化（L2 Normalization），便于使用更高效的点积代替余弦距离；
- 文档内容变更时建立版本更新与增量刷新机制。

### 3. 向量数据库选型考量

- **Pinecone**：全托管云原生 Serverless 架构，开箱即用，高弹性扩展；
- **Weaviate**：开源且支持自托管，内置混合检索与模块化向量化管线；
- **Milvus / Zilliz**：面向超大规模亿级向量的高性能分布式系统；
- **Qdrant**：Rust 构建的高性能向量数据库，支持极强且丰富的 Payload 过滤；
- **Chroma**：极轻量、内嵌式，适合原型验证与单机中小规模应用；
- **pgvector**：PostgreSQL 插件，适合已有成熟关系型数据库且数据量处于中等规模的业务。

### 4. 检索优化与重排序（Reranking）

```python
# 1. 向量相似度初筛检索（Top-K）
semantic_results = vector_db.query(question_embedding, k=10)

# 2. 关键词检索
keyword_results = bm25.search(question, k=10)

# 3. 结果合并与初步去重
candidates = combine_results(semantic_results, keyword_results)

# 4. 交叉编码重排序（Cross-Encoder Rerank，大幅提升前置精度）
reranked_results = reranker.rank(query=question, documents=candidates, top_n=3)
```

### 5. 上下文组装与 Prompt 模板设计

```text
你是一位严谨的专业知识助手。请严格依据下方提供的参考材料回答用户提问。
若参考材料中未包含能回答该问题的信息，请如实告知“参考资料中没有相关信息”，切勿自行臆造事实。

[参考材料]
{retrieved_documents}

[用户问题]
{user_question}

[回答要求]
1. 观点明确、结构清晰；
2. 涉及具体事实或数据时，在对应陈述后注明引用来源编号（例如 [1]）。
```

## 关键生产级框架集成示例

### LangChain 示例
```python
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Pinecone
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# 加载文档并提取
loader = PyPDFLoader("handbook.pdf")
docs = loader.load()

# 构建向量检索链
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Pinecone.from_documents(docs, embeddings, index_name="knowledge-base")
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# 组装问答流水线
combine_docs_chain = create_stuff_documents_chain(ChatOpenAI(model="gpt-4o"), prompt)
rag_chain = create_retrieval_chain(retriever, combine_docs_chain)
response = rag_chain.invoke({"input": "核心报销流程是什么？"})
```

### LlamaIndex 示例
```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# 自动读取并构建索引
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)

# 创建查询引擎并问答
query_engine = index.as_query_engine(similarity_top_k=3)
response = query_engine.query("项目核心架构是如何设计的？")
```

## 生产落地的黄金法则

1. **源头数据清洗**：剔除冗余页眉页脚、扫描件水印噪点；对表格数据采用 Markdown 或专用 JSON 格式表述；
2. **混合检索先行**：生产环境强烈建议将 BM25 稀疏检索与密集向量检索结合，避免专有名词漏召回；
3. **引入重排序（Reranking）**：初筛召回 15–20 条候选，通过 Cross-Encoder 重排选出最优 3–5 条，质效提升最明显；
4. **强制溯源标记**：在输出回答中明确标注引用的文档标题与段落锚点；
5. **建立全链路评测体系**：
   - 检索侧评估：命中率（Hit Rate）、召回率（Recall）、MRR（平均倒数排名）；
   - 生成侧评估：真实性（Faithfulness，是否脱离上下文幻觉）、相关性（Answer Relevance）。

## 常见瓶颈与对策速查

| 痛点问题 | 根因定位 | 推荐排查与优化对策 |
|---|---|---|
| **检索出大量无关内容** | 分块过大或查询意图漂移 | 减小分块尺寸；使用语义分块；引入查询意图改写（Query Rewriting） |
| **关键信息漏召回** | 专有名词不匹配或相似度阈值过死 | 启用 BM25+向量混合检索；引入假设性文档嵌入（HyDE）；扩大初筛 Top-K |
| **上下文溢出或费用过高** | 注入过多冗余上下文 | 引入 Reranker 过滤低分块；在注入 Prompt 前使用上下文压缩算法 |
| **LLM 生成事实幻觉** | 检索上下文不够明确或 Prompt 约束弱 | 强化系统级 Prompt“未提及则声明不知道”；使用带引用标注模板 |
| **检索延迟过长** | 未建向量索引或网络链路开销 | 启用 HNSW/IVF 向量索引；对高频问题嵌入及检索结果增加 Redis 缓存 |
