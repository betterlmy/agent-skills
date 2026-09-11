# RAG Agent Builder — 代码与目录结构说明

本 Skill 配套了完整的 Python 辅助工具模块与示例代码，旨在保持主干文档精简的同时兼顾实践工程的可落地性。

## 目录结构

```text
rag-agent-builder/
├── SKILL.md                      # 主干核心文档（核心架构、演进模式、选型指南）
├── README.md                     # 本说明文档
├── examples/                     # 端到端实现代码范例
│   ├── basic_rag.py              # 基础 RAG 完整流水线
│   ├── retrieval_strategies.py   # 混合检索、交叉重排与元数据过滤
│   └── agentic_rag.py            # Agent 自主控制的迭代式检索
└── scripts/                      # 核心辅助公用模块
    ├── embedding_management.py   # Embedding 向量生成、归一化与缓存
    ├── vector_db_manager.py      # 统一向量数据库工厂与管理器抽象
    └── rag_evaluation.py         # 检索准确率与生成质量评测工具
```

## 运行示例代码

### 1. 基础 RAG 流水线
```bash
python examples/basic_rag.py
```
最简洁经典的 RAG 实现：文档分块、Embedding 向量化、Top-K 相似度检索、组装上下文并生成答案。

### 2. 高级检索策略
```bash
python examples/retrieval_strategies.py
```
融合 BM25 关键词检索与 Dense 向量检索的混合召回模式，并使用 Reranker 模型执行重排。

### 3. Agent 驱动型检索（Agentic RAG）
```bash
python examples/agentic_rag.py
```
由 Agent 自主决策何时检索、多轮拆解复杂问题并迭代优化答案的高阶范式。

## 工具模块调用范例

### 向量管理与质量评估（Embedding Management）
```python
from scripts.embedding_management import EmbeddingManager, EmbeddingQualityAssessment

manager = EmbeddingManager(model_name="all-MiniLM-L6-v2")
embeddings = manager.generate_embeddings(texts)
normalized = manager.normalize_embeddings(embeddings)

quality = EmbeddingQualityAssessment.embedding_distribution_quality(embeddings)
print(f"Embedding 向量分布质量: {quality['quality']}")
```

### 向量数据库抽象管理（Vector DB Manager）
```python
from scripts.vector_db_manager import VectorDBFactory, VectorDBManager

# 初始化内存向量库
db = VectorDBFactory.create_db("in_memory")
manager = VectorDBManager(db)

# 写入文档与向量
doc_ids = manager.add_documents(texts, embeddings)

# 执行相似度检索
results = manager.search(query_embedding, k=5)

# 查询数据库状态元数据
info = manager.get_database_info()
```

### 全链路质量评估（RAG Evaluation）
```python
from scripts.rag_evaluation import RAGEvaluator, RetrievalMetrics

evaluator = RAGEvaluator()

# 评估检索侧命中质量
retrieval_eval = evaluator.evaluate_retrieval(retrieved_docs, relevant_docs, query)

# 评估回答生成侧质量（忠实度、相关性）
answer_eval = evaluator.evaluate_answer(answer, context, query)

# 整体端到端流水线评测
pipeline_eval = evaluator.evaluate_rag_pipeline(
    query, retrieved, relevant, answer, context
)

# 输出综合评测报告摘要
summary = evaluator.get_evaluation_summary()
```

## 与主文档 SKILL.md 的协同关系

- `SKILL.md` 承载架构理念、核心模式演进、生产决策与最佳实践指导；
- `examples/` 提供立即可运行的代码范式；
- `scripts/` 提供低耦合、模块化的工程脚手架。
这种分层渐进披露机制有效控制了上下文 Token 开销，同时确保了方案的严谨与完备。
