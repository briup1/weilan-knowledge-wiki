# MaxKB v2 RAG Domain Flow Map

> Generated from analysis of `/home/weilan/workdir/excellent_project/001-rag-research-projects/MaxKB` (v2 branch, HEAD `f580c0827`).
> This document serves as a structured navigation guide for deep code reading.

---

## 1. Document Upload & Storage Flow

**Purpose:** Ingest raw documents (files, web pages, QA pairs, tables) into the knowledge base, store them as `Document` records, and persist raw file bytes via PostgreSQL Large Objects (LO).

### Key Data Objects
- `Knowledge` (`apps/knowledge/models/knowledge.py:118`) -- knowledge base container
- `Document` (`apps/knowledge/models/knowledge.py:187`) -- represents an uploaded document; tracks `status` (bit-field for EMBEDDING / GENERATE_PROBLEM / SYNC / TOKENIZE tasks)
- `File` (`apps/knowledge/models/knowledge.py:365`) -- stores raw bytes as compressed zip in PostgreSQL LO; deduplicated by SHA-256
- `Paragraph` (`apps/knowledge/models/knowledge.py:249`) -- extracted text segments from a document

### Flow Steps & Implementation

| Step | Module / File | Key Classes / Functions | Description |
|------|---------------|------------------------|-------------|
| 1.1 HTTP Upload / Web URL | `apps/knowledge/views/document.py` | `DocumentView.post()` | Receives multipart upload or web URL list. Delegates to `DocumentSerializers.Create`. |
| 1.2 File Persistence | `apps/knowledge/models/knowledge.py:385` | `File.save(bytea)` | Compresses with ZIP, stores in PostgreSQL LO via `lo_creat` / `lo_put`. Deduplicates by `sha256_hash`. |
| 1.3 Document Record Creation | `apps/knowledge/serializers/document.py` | `DocumentSerializers.Create.save()` | Creates `Document` row, links to `Knowledge`, initializes `status` bit-field to pending. |
| 1.4 Web Crawl (optional) | `apps/knowledge/task/handler.py` | `get_sync_web_document_handler()` | Uses `Fork` utility to fetch web pages; parses HTML to markdown via `get_split_model("web.md")`. |
| 1.5 QA Pair Import (optional) | `apps/knowledge/serializers/document.py` | `CsvParseQAHandle`, `XlsParseQAHandle`, `ZipParseQAHandle` | Parses CSV/Excel/ZIP into QA pairs directly as paragraphs. |
| 1.6 Table Import (optional) | `apps/knowledge/serializers/document.py` | `CsvParseTableHandle`, `XlsParseTableHandle`, `XlsxParseTableHandle` | Parses tabular data. |

**Cross-domain interactions:**
- Calls `oss.serializers.file.FileSerializer` for temporary file handling.
- Triggers Celery tasks in **Flow 4 (Embedding)** after paragraph creation.

---

## 2. Document Parsing / OCR / Cleaning Flow

**Purpose:** Extract clean text and images from raw files (PDF, DOCX, HTML, TXT, CSV, XLSX, etc.), producing structured paragraph candidates.

### Key Data Objects
- `BaseSplitHandle` (`apps/common/handle/base_split_handle.py`) -- abstract interface for all parsers
- `SplitModel` (`apps/common/utils/split_model.py`) -- heading-based hierarchical text splitter
- `Paragraph` (pre-save form) -- `content`, `title`, `parent_chain`, `keywords`

### Flow Steps & Implementation

| Step | Module / File | Key Classes / Functions | Description |
|------|---------------|------------------------|-------------|
| 2.1 Parser Routing | `apps/knowledge/serializers/document.py:95` | `split_handles` list | Chooses parser by file extension: `PdfSplitHandle`, `DocSplitHandle`, `HTMLSplitHandle`, `XlsxSplitHandle`, `CsvSplitHandle`, `ZipSplitHandle`, `TextSplitHandle`. |
| 2.2 PDF Parsing | `apps/common/handle/impl/text/pdf_split_handle.py` | `PdfSplitHandle.handle()` | Uses `pypdf.PdfReader`. Handles TOC-based extraction, internal link traversal, and fallback to page-level text. |
| 2.3 DOCX Parsing | `apps/common/handle/impl/text/doc_split_handle.py` | `DocSplitHandle.handle()` | Uses `python-docx`. Extracts paragraphs, tables, and inline images (stored as `File` LO objects, referenced via `![name](oss/file/{id})` markdown). |
| 2.4 HTML Parsing | `apps/common/handle/impl/text/html_split_handle.py` | `HTMLSplitHandle.handle()` | Uses `BeautifulSoup` + `markdownify` to convert HTML to markdown. Removes anchor links. |
| 2.5 Text Splitting (hierarchical) | `apps/common/utils/split_model.py` | `SplitModel.parse()`, `smart_split_paragraph()` | Parses markdown headings (`#` to `######`) into a tree, flattens into paragraphs with `parent_chain` and `keywords` (via `jieba`). |
| 2.6 Image Extraction | `apps/common/handle/impl/text/doc_split_handle.py:39` | `image_to_mode()` | Extracts images from DOCX parts, stores as `File` rows, replaces with markdown image links. |
| 2.7 Cleaning / Filtering | `apps/common/utils/split_model.py:43` | `remove_special_symbol()`, `filter_special_symbol()` | Strips special characters (currently minimal; placeholder for future OCR cleaning). |

**Note:** No dedicated OCR engine (e.g., Tesseract) is integrated in v2. PDF text is extracted via `pypdf` (text-layer only). Images within documents are extracted and referenced, but not OCR'd.

---

## 3. Chunking / Segmentation Flow

**Purpose:** Further subdivide parsed paragraphs into smaller chunks suitable for embedding, and optionally generate associated questions.

### Key Data Objects
- `Paragraph.chunks` (`apps/knowledge/models/knowledge.py:264`) -- `ArrayField` of chunk strings
- `MarkChunkHandle` -- sentence-aware chunk splitter

### Flow Steps & Implementation

| Step | Module / File | Key Classes / Functions | Description |
|------|---------------|------------------------|-------------|
| 3.1 Chunk Generation | `apps/common/chunk/impl/mark_chunk_handle.py` | `MarkChunkHandle.handle()` | Splits text into chunks by sentence boundaries (`。`, ` `, `.`, `!`, `;`, `;`, `!`, `\n`), max 256 chars. Falls back to fixed-size char chunks for oversized remainders. |
| 3.2 Chunk Storage | `apps/common/event/listener_manage.py:216` | `ListenerManagement.tokenize_by_paragraph()` | Stores `chunks` array on `Paragraph` model. Also updates `Embedding.search_vector` (PostgreSQL `tsvector`) for each chunk using `Termbase` user words. |
| 3.3 Question Generation (optional) | `apps/knowledge/task/generate.py` | `generate_problem_by_paragraph()` | Uses LLM (`llm_model.invoke`) with a prompt to generate related questions from paragraph content. Stores in `Problem` + `ProblemParagraphMapping`. |
| 3.4 Paragraph Persistence | `apps/knowledge/serializers/paragraph.py` | `ParagraphSerializers` | Saves `Paragraph` rows with `content`, `title`, `position`, `chunks`, and linked `Problem` list. |

**Data flow:**
```
Parsed text (from Flow 2)
  -> SplitModel.parse() -> tree of headings/blocks
  -> flat_map -> Paragraph candidates
  -> text_to_chunk() -> chunk_list (256-char sentence-aware)
  -> Paragraph.chunks = chunk_list
  -> Celery: tokenize_by_document() -> update search_vector per chunk
```

---

## 4. Embedding & Vector Indexing Flow

**Purpose:** Convert text (paragraphs, chunks, generated questions) into dense embeddings and store them in PostgreSQL with `pgvector`, alongside full-text search vectors.

### Key Data Objects
- `Embedding` (`apps/knowledge/models/knowledge.py:347`) -- stores `vector` + `search_vector` (tsvector) + metadata
- `Model` (`apps/models_provider/models/model_management.py:21`) -- embedding model configuration (provider, credentials, model_name)
- `ModelManage` (`apps/common/config/embedding_config.py:19`) -- caches model instances in memory

### Flow Steps & Implementation

| Step | Module / File | Key Classes / Functions | Description |
|------|---------------|------------------------|-------------|
| 4.1 Embedding Model Resolution | `apps/knowledge/task/embedding.py:25` | `get_embedding_model()` | Fetches `Model` from DB, decrypts credentials via RSA, instantiates provider-specific embedding client via `ModelManage.get_model()`. |
| 4.2 Celery Task Dispatch | `apps/knowledge/task/embedding.py` | `embedding_by_document()`, `embedding_by_paragraph()`, `embedding_by_paragraph_list()` | Celery tasks (using `celery_once.QueueOnce` for deduplication). Document-level task iterates paragraphs in pages of 5. |
| 4.3 Text Normalization | `apps/knowledge/vector/base_vector.py:49` | `normalize_for_embedding()` | Removes emoji, collapses whitespace. |
| 4.4 Chunk Expansion | `apps/knowledge/vector/base_vector.py:25` | `chunk_data()` | If source is `PARAGRAPH`, expands each `Paragraph` into its `chunks` array; if `PROBLEM`, keeps as-is. |
| 4.5 Batch Embedding | `apps/knowledge/vector/pg_vector.py:79` | `PGVector._batch_save()` | Calls `embedding.embed_documents(texts)` (LangChain interface), stores as `float[]` in `Embedding.embedding`. |
| 4.6 Full-Text Indexing | `apps/knowledge/vector/pg_vector.py:74` | `SearchVector(Value(to_ts_vector(...)))` | Creates PostgreSQL `tsvector` using `simple` config + custom `Termbase` words for keyword search. |
| 4.7 Vector DB Storage | `apps/knowledge/vector/pg_vector.py` | `QuerySet(Embedding).bulk_create()` | Bulk inserts `Embedding` rows. Uses PostgreSQL `vector` type (pgvector extension). |
| 4.8 Status Update | `apps/common/event/listener_manage.py:325` | `ListenerManagement.update_status()` | Bit-manipulation on `Paragraph.status` and `Document.status` to track EMBEDDING / TOKENIZE task completion. |
| 4.9 HNSW Index Creation | `apps/knowledge/serializers/common.py` | `create_knowledge_index()` | Creates per-knowledge-base partial HNSW index on `embedding` column (`WHERE knowledge_id = '...'`). |
| 4.10 Deletion / Disable | `apps/knowledge/task/embedding.py` | `delete_embedding_by_*`, `disable_embedding_by_paragraph()` | Cascading deletes by knowledge, document, paragraph, or source. |

**Vector Store Architecture:**
- Only `PGVector` is implemented (`apps/knowledge/vector/pg_vector.py`).
- Supports 3 search modes: `embedding` (pure vector), `keywords` (pure tsvector), `blend` (vector + keyword hybrid score).
- SQL templates: `apps/knowledge/sql/embedding_search.sql`, `keywords_search.sql`, `blend_search.sql`.

---

## 5. Query / Retrieval / Rerank Flow

**Purpose:** Given a user query, retrieve the most relevant paragraphs from attached knowledge bases using vector similarity, keyword search, or hybrid blend.

### Key Data Objects
- `ParagraphPipelineModel` (`apps/application/chat_pipeline/I_base_chat_pipeline.py:18`) -- enriched paragraph result with `similarity`, `comprehensive_score`, `hit_handling_method`
- `Application.knowledge_setting` -- JSON config with `top_n`, `similarity`, `search_mode`, `max_paragraph_char_number`

### Flow Steps & Implementation

| Step | Module / File | Key Classes / Functions | Description |
|------|---------------|------------------------|-------------|
| 5.1 Query Reception | `apps/chat/serializers/chat.py` | `ChatSerializers.chat()` | Receives user message, resolves `Application` and linked `Knowledge` IDs. |
| 5.2 Problem Optimization (optional) | `apps/application/chat_pipeline/step/reset_problem_step/impl/base_reset_problem_step.py` | `BaseResetProblemStep.execute()` | Uses LLM to rewrite/expand the user question based on last 3 turns of history. Output wrapped in `<data>` tags. |
| 5.3 Embedding Model Consistency Check | `apps/application/chat_pipeline/step/search_dataset_step/impl/base_search_dataset_step.py:36` | `get_embedding_id()` | Verifies all linked knowledge bases use the same embedding model; raises if inconsistent. |
| 5.4 Query Embedding | `apps/application/chat_pipeline/step/search_dataset_step/impl/base_search_dataset_step.py:69` | `embedding_model.embed_query(exec_problem_text)` | Generates query vector via cached `ModelManage` instance. |
| 5.5 Vector Search | `apps/knowledge/vector/pg_vector.py:149` | `PGVector.query()` | Dispatches to `EmbeddingSearch`, `KeywordsSearch`, or `BlendSearch` based on `search_mode`. |
| 5.6 SQL Retrieval (embedding) | `apps/knowledge/sql/embedding_search.sql` | CTE `vector_top` | Uses `embedding::vector <=> query_vector` (cosine distance) with `LIMIT LEAST(top_n * 10, 500)`, then `DISTINCT ON paragraph_id` dedup, filters by `comprehensive_score > similarity`. |
| 5.7 SQL Retrieval (keywords) | `apps/knowledge/sql/keywords_search.sql` | CTE `keywords_query` | Uses `ts_rank_cd(search_vector, websearch_to_tsquery(...))` with `Termbase` user words. |
| 5.8 SQL Retrieval (blend) | `apps/knowledge/sql/blend_search.sql` | CTE `vector_top` + JOIN | Combines vector distance + keyword rank into `comprehensive_score = (1 - distance) + ts_rank_cd(...)`. |
| 5.9 Paragraph Hydration | `apps/application/chat_pipeline/step/search_dataset_step/impl/base_search_dataset_step.py:108` | `list_paragraph()` | Fetches full `Paragraph` data via `native_search` with SQL join. Deletes stale embeddings if paragraph no longer exists. |
| 5.10 Direct-Return Shortcut | `apps/application/chat_pipeline/step/search_dataset_step/impl/base_search_dataset_step.py:124` | `hit_handling_method == 'directly_return'` | If a paragraph has `directly_return` method and similarity exceeds `directly_return_similarity`, returns only that single paragraph (bypasses LLM). |
| 5.11 Result Enrichment | `apps/application/chat_pipeline/I_base_chat_pipeline.py:69` | `ParagraphPipelineModel.builder()` | Adds `knowledge_name`, `document_name`, `comprehensive_score`, `similarity`, `meta` to each result. |

**Note:** No dedicated reranker model (e.g., Cohere Rerank, BGE Reranker) is used. Reranking is implicit in the `comprehensive_score` sort. MaxKB relies on top-N cutoff (`top_n`, default 3) and similarity threshold (`similarity`, default 0.6).

---

## 6. Prompt Construction / LLM Generation / Citation Flow

**Purpose:** Build the final message list (system prompt + history + retrieved context) and stream/block-generate the LLM response.

### Key Data Objects
- `Application.model_setting` -- JSON with `prompt`, `no_references_prompt`, `reasoning_content_start/end`, `reasoning_content_enable`
- `ChatRecord` (`apps/application/models/application_chat.py:84`) -- stores full conversation turn with `details`, tokens, vote status
- `BaseMessage` (LangChain) -- `SystemMessage`, `HumanMessage`, `AIMessage`

### Flow Steps & Implementation

| Step | Module / File | Key Classes / Functions | Description |
|------|---------------|------------------------|-------------|
| 6.1 Pipeline Orchestration | `apps/application/chat_pipeline/pipeline_manage.py` | `PipelineManage.run()` | Runs 4 steps in sequence: `ResetProblemStep` -> `SearchDatasetStep` -> `GenerateHumanMessageStep` -> `ChatStep`. |
| 6.2 Prompt Construction | `apps/application/chat_pipeline/step/generate_human_message_step/impl/base_generate_human_message_step.py` | `BaseGenerateHumanMessageStep.execute()` | Builds `SystemMessage` (if configured) + history (last N turns) + `HumanMessage` with prompt template replacing `{data}` and `{question}`. |
| 6.3 Context Truncation | `apps/application/chat_pipeline/step/generate_human_message_step/impl/base_generate_human_message_step.py:61` | `to_human_message()` | Concatenates `<data>{title}:{content}</data>` chunks until `max_paragraph_char_number` (default 5000) is reached. |
| 6.4 No-References Fallback | `apps/application/chat_pipeline/step/generate_human_message_step/impl/base_generate_human_message_step.py:55` | `no_references_setting` | If no paragraphs retrieved, either returns designated answer or AI-questioning fallback prompt. |
| 6.5 LLM Invocation (Streaming) | `apps/application/chat_pipeline/step/chat_step/impl/base_chat_step.py` | `BaseChatStep.execute_stream()` | Calls `chat_model.stream(message_list)` via LangChain. Supports reasoning content extraction (e.g., DeepSeek `\n<think>...</think>\n`). |
| 6.6 LLM Invocation (Block) | `apps/application/chat_pipeline/step/chat_step/impl/base_chat_step.py` | `BaseChatStep.execute_block()` | Non-streaming `chat_model.invoke()` for API/block mode. |
| 6.7 Tool / MCP Handling | `apps/application/chat_pipeline/step/chat_step/impl/base_chat_step.py:343` | `_handle_mcp_request()` | Integrates MCP servers, custom tools (converted to MCP), skill tools, and sub-applications as MCP tools. Uses `langchain_mcp_adapters.client.MultiServerMCPClient`. |
| 6.8 Streaming Response | `apps/application/chat_pipeline/step/chat_step/impl/base_chat_step.py:72` | `event_content()` | Yields SSE chunks via `StreamingHttpResponse`. Tracks `message_tokens`, `answer_tokens`, `run_time`. |
| 6.9 Post-Response Persistence | `apps/chat/serializers/chat.py:100` | `PostHandler.handler()` | Creates `ChatRecord` with `problem_text`, `answer_text`, `details` (pipeline step traces), `message_tokens`, `answer_tokens`, `run_time`. |
| 6.10 Citation / Source Tracking | `apps/application/chat_pipeline/I_base_chat_pipeline.py:18` | `ParagraphPipelineModel.to_dict()` | Each retrieved paragraph carries `id`, `document_id`, `knowledge_id`, `document_name`, `similarity`, `meta` into the `details` field of `ChatRecord`. Frontend can render these as citations. |

**Workflow Mode (Advanced):**
- `Application.type == 'WORK_FLOW'` triggers `WorkflowManage` (`apps/application/flow/workflow_manage.py`) instead of the simple 4-step pipeline.
- Workflow nodes include: `ai-chat-node`, `question-node`, `search-dataset-node`, `condition-node`, `form-node`, `reply-node`, `tool-node`, etc.
- Defined in `application.flow.step_node` module.

---

## 7. Evaluation / Feedback / Observability Flow

**Purpose:** Collect user feedback (vote, reason), log conversation details, and expose usage statistics.

### Key Data Objects
- `ChatRecord.vote_status` (`apps/application/models/application_chat.py:90`) -- `UN_VOTE`, `STAR`, `TRAMPLE`
- `ChatRecord.vote_reason` -- `accurate`, `complete`, `inaccurate`, `incomplete`, `other`
- `ApplicationChatUserStats` (`apps/application/models/application_chat.py:131`) -- access counters per user per app
- `ChatRecord.details` -- full JSON trace of every pipeline step (retrieval, prompt, generation)

### Flow Steps & Implementation

| Step | Module / File | Key Classes / Functions | Description |
|------|---------------|------------------------|-------------|
| 7.1 Vote Recording | `apps/application/models/application_chat.py` | `ChatRecord` fields | Users can upvote/downvote answers with reasons. Stored directly on `ChatRecord`. |
| 7.2 Conversation History | `apps/chat/serializers/chat.py` | `ChatInfo` | Caches chat history in memory; `ChatRecord` persists to DB. |
| 7.3 Usage Stats | `apps/application/models/application_chat.py:131` | `ApplicationChatUserStats` | Tracks `access_num` and `intraday_access_num` per `chat_user_id` per `application`. |
| 7.4 Pipeline Tracing | `apps/application/chat_pipeline/pipeline_manage.py:39` | `get_details()` | Aggregates step-level details (`search_step`, `generate_human_message`, `chat_step`, `problem_padding`) into a single JSON map stored in `ChatRecord.details`. |
| 7.5 Token & Cost Tracking | `apps/application/chat_pipeline/step/chat_step/impl/base_chat_step.py:62` | `write_context()` | Records `message_tokens` and `answer_tokens` per turn. No monetary cost calculation is present (field `cost` is always 0). |
| 7.6 Long-Term Memory (optional) | `apps/application/long_term_memory/` | `extract_long_term_memory.apply_async()` | Async Celery task that extracts long-term memory from conversation history after each chat turn. |
| 7.7 Log Export | `apps/application/views/application_chat.py` | `ApplicationChat.Export` | Exports conversation logs (chat + records) for admin review. |
| 7.8 Audit Logging | `apps/common/log/log.py` | `@log` decorator | Records admin operations (create, delete, update) on documents, knowledge bases, applications. |

**Note:** No automated evaluation pipeline (e.g., LLM-as-a-judge, RAGAS metrics) is integrated. Evaluation is purely manual via user votes.

---

## Module Dependency Graph (Simplified)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         apps/knowledge                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ views/   │  │serializers│  │  task/   │  │  vector/         │ │
│  │document  │->│document  │->│embedding │->│  pg_vector       │ │
│  │  .py     │  │  .py     │  │  .py     │  │  (pgvector)      │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
│       │              │              │              │               │
│       v              v              v              v               │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                    models/knowledge.py                      │   │
│  │  Knowledge -> Document -> Paragraph -> Problem -> Embedding  │   │
│  └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              v
┌─────────────────────────────────────────────────────────────────────┐
│                       apps/application                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ chat_pipeline/   │  │     flow/        │  │     models/      │  │
│  │  PipelineManage  │  │  WorkflowManage  │  │  Application     │  │
│  │  4-step RAG      │  │  node-based      │  │  ChatRecord      │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                              │                                       │
│                              v                                       │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │                      apps/chat                              │     │
│  │              ChatSerializers.chat()                         │     │
│  │  (entry point for all user queries)                         │     │
│  └────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              v
┌─────────────────────────────────────────────────────────────────────┐
│                     apps/models_provider                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ models/          │  │ impl/            │  │ tools.py         │  │
│  │  Model           │  │  provider-specific│  │ get_model()      │  │
│  │  (LLM/Embedding) │  │  model wrappers  │  │ ModelManage      │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Key Files for Deep Reading (by Flow)

| Flow | Must-Read Files |
|------|-----------------|
| 1. Upload & Storage | `apps/knowledge/views/document.py`, `apps/knowledge/serializers/document.py`, `apps/knowledge/models/knowledge.py` (Document, File) |
| 2. Parsing | `apps/common/handle/impl/text/pdf_split_handle.py`, `apps/common/handle/impl/text/doc_split_handle.py`, `apps/common/utils/split_model.py` |
| 3. Chunking | `apps/common/chunk/impl/mark_chunk_handle.py`, `apps/knowledge/serializers/paragraph.py`, `apps/common/event/listener_manage.py` (tokenize) |
| 4. Embedding | `apps/knowledge/task/embedding.py`, `apps/knowledge/vector/pg_vector.py`, `apps/common/config/embedding_config.py`, `apps/common/event/listener_manage.py` (embedding) |
| 5. Retrieval | `apps/application/chat_pipeline/step/search_dataset_step/impl/base_search_dataset_step.py`, `apps/knowledge/vector/pg_vector.py`, `apps/knowledge/sql/embedding_search.sql`, `apps/knowledge/sql/blend_search.sql` |
| 6. Generation | `apps/application/chat_pipeline/pipeline_manage.py`, `apps/application/chat_pipeline/step/chat_step/impl/base_chat_step.py`, `apps/application/chat_pipeline/step/generate_human_message_step/impl/base_generate_human_message_step.py`, `apps/chat/serializers/chat.py` |
| 7. Observability | `apps/application/models/application_chat.py` (ChatRecord), `apps/application/views/application_chat.py`, `apps/application/long_term_memory/` |

---

## Notable Architectural Decisions

1. **PostgreSQL as Universal Store:** Uses PostgreSQL LO for raw files, Django ORM for relational data, `pgvector` for vector storage, and `pg_trgm`/`tsvector` for full-text search. No separate vector DB (Milvus, Qdrant, Weaviate).
2. **Celery + celery_once:** All heavy tasks (embedding, question generation, web sync) are async Celery tasks with `QueueOnce` to prevent duplicate execution.
3. **Bit-Field Status Tracking:** `Document.status` and `Paragraph.status` are compact bit strings encoding state for 4 task types (EMBEDDING, GENERATE_PROBLEM, SYNC, TOKENIZE).
4. **LangChain Integration:** Model providers implement LangChain interfaces (`Embeddings`, `BaseChatModel`), enabling provider-agnostic model swapping.
5. **Dual Application Mode:** "Simple" mode uses a fixed 4-step pipeline; "Workflow" mode uses a visual node-based DAG executor.
6. **No Dedicated Reranker:** Hybrid scoring is done at the SQL level (`1 - distance + ts_rank_cd`), not via a cross-encoder reranker.
7. **No OCR:** Image-based PDFs are not processed; only text-layer PDFs are supported.
