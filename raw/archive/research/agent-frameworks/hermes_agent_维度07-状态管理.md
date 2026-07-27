# 维度 07：状态管理（State Management）

## 1. 一句话定位

Hermes Agent 的状态管理采用**“运行时内存状态 + SQLite 持久化状态”双轨架构**：AIAgent 实例持有会话运行期的可变状态（迭代预算、中断信号、API 计数等），而 `SessionDB` 通过启用 WAL 模式的 SQLite 提供事务化的持久化存储，并辅以声明式 schema 调和、FTS5 全文检索、版本门控迁移与随机抖动写竞争重试机制，实现高并发、可检索、可演化的会话数据生命周期管理。

## 2. 设计动机

在长时间运行的 Agent 系统中，状态管理面临以下核心挑战：

- **并发安全**：多个 CLI 实例或后台进程可能同时读写同一会话数据库，需要避免脏写与数据损坏。
- **可检索性**：随着会话历史膨胀，必须支持高效的全文检索（包括中文/日文/韩文等 CJK 文本）。
- **Schema 演化**：功能迭代要求数据库 schema 持续演进，但又要避免手动迁移脚本的维护负担。
- **运行时可观测性**：运维与调试需要实时获取 Agent 的运行时活动快照，而非仅依赖落盘后的静态数据。
- **容错与维护**：长期运行后数据库文件可能膨胀，需要自动化的剪枝与维护策略。

因此，状态管理维度被设计为“内存运行时状态”与“磁盘持久化状态”的协同体系，分别解决不同时间尺度与一致性要求的问题。

## 3. 核心设计哲学

1. **分离运行时状态与持久化状态**：
   - 运行时状态（如 `_interrupt_requested`、`_api_call_count`、`_last_activity_ts`）保存在 `AIAgent` 实例内存中，支持低延迟的读写与实时诊断。
   - 持久化状态（会话元数据、消息历史、全文索引）保存在 SQLite 中，支持跨进程共享与崩溃恢复。

2. **SQLite WAL + 应用级随机抖动重试**：
   - 启用 WAL（Write-Ahead Logging）模式，允许多个并发 reader 与单个 writer 共存，避免传统 rollback journal 的读写互斥。
   - 不依赖 SQLite 内置的 busy handler（其超时行为是确定性的），而是在应用层实现随机抖动退避（20–150 ms），降低多进程同时重试时的碰撞概率。

3. **声明式 Schema 调和（Beets/sqlite-utils 风格）**：
   - 以 `SCHEMA_SQL` 字符串作为 schema 的唯一真实来源（single source of truth）。
   - 启动时通过内存 SQLite 解析 `SCHEMA_SQL`，与目标数据库的 `PRAGMA table_info(...)` 进行列级对比，自动执行 `ALTER TABLE ADD COLUMN` 补齐缺失列，无需手写迁移脚本。
   - 数据迁移（如 FTS 索引回填）通过 `state_meta` 表中的版本门控标记实现，确保幂等且可重复执行。

4. **FTS5 双索引策略（unicode61 + trigram）**：
   - 默认使用 `unicode61` tokenizer 处理英文及常规文本。
   - 针对 CJK 文本 fallback 到 `trigram` tokenizer，实现子串级匹配，弥补 unicode61 对无空格分词语言的不足。
   - 搜索时先查 FTS5，若无结果再降级为 `LIKE` 子串匹配，兼顾性能与召回率。

5. **原子性消息替换**：
   - `/retry`、`/undo`、`/compress` 等命令需要重写会话 transcript。`replace_messages()` 在单个事务内删除旧消息并插入新消息，保证 transcript 的一致性。

6. **会话压缩延续链**：
   - 压缩后的会话通过 `parent_session_id` 建立递归关联，`list_sessions_rich()` 使用递归 CTE 展示压缩链，使用户可追溯历史版本。

## 4. 关键机制与源码拆解

### 4.1 运行时状态（AIAgent 内存态）

`run_agent.py` 中 `AIAgent` 初始化时声明了若干运行时状态字段（约 lines 1020–1280）：

```python
self.iteration_budget = iteration_budget or IterationBudget(max_iterations)
self._interrupt_requested = False
self._last_activity_ts: float = time.time()
self._last_activity_desc: str = "initializing"
self._api_call_count: int = 0
```

这些字段服务于：
- **迭代预算控制**：`IterationBudget` 防止无限循环。
- **中断信号**：`_interrupt_requested` 支持用户或系统优雅地终止当前 Agent 运行。
- **活动诊断**：`_last_activity_ts` / `_last_activity_desc` / `_api_call_count` 为 `get_activity_summary()`（lines 4859–4875）提供实时快照，用于运维观测。

会话 ID 的生成策略（lines 1666–1673）兼顾可读性与唯一性：

```python
if session_id:
    self.session_id = session_id
else:
    timestamp_str = self.session_start.strftime("%Y%m%d_%H%M%S")
    short_uuid = uuid.uuid4().hex[:6]
    self.session_id = f"{timestamp_str}_{short_uuid}"
```

`AIAgent` 与 `SessionDB` 的集成点（lines 1699–1707）：

```python
self._session_db = session_db
self._parent_session_id = parent_session_id
self._last_flushed_db_idx = 0
self._session_db_created = False
```

这里 `_last_flushed_db_idx` 追踪已持久化的消息索引，实现增量刷盘而非全量重写。

### 4.2 持久化状态（SessionDB）

#### Schema 定义

`hermes_state.py` lines 38–100 的 `SCHEMA_SQL` 定义了三张核心表：

- **`sessions`**：会话元数据（`session_id`、启动时间、模型、模式、标题、父会话 ID 等）。
- **`messages`**：消息历史（`session_id`、`role`、`content`、`created_at`、`metadata` 等），支持 JSON sentinel prefix 编码以承载多模态内容。
- **`state_meta`**：键值存储，用于 schema 版本标记与迁移门控。

此外，schema 还包含：
- **FTS5 虚拟表**：`messages_fts` 与 `messages_fts_trigram`，分别使用 `unicode61` 与 `trigram` tokenizer。
- **Telegram topic 侧表**（lines 2195–2499）：可选的 `telegram_dm_bindings`、`telegram_topic_bindings` 等，用于 Telegram 集成场景下的 topic 模式。

#### WAL 模式与写竞争重试

`SessionDB` 初始化（line 159 附近）启用 WAL：

```python
self._conn.execute("PRAGMA journal_mode=WAL")
```

核心写方法 `_execute_write()`（lines 208–258）实现了应用级重试：

```python
def _execute_write(self, fn: Callable[[sqlite3.Connection], T]) -> T:
    last_err: Optional[Exception] = None
    for attempt in range(self._WRITE_MAX_RETRIES):
        try:
            with self._lock:
                self._conn.execute("BEGIN IMMEDIATE")
                try:
                    result = fn(self._conn)
                    self._conn.commit()
                except BaseException:
                    try:
                        self._conn.rollback()
                    except Exception:
                        pass
                    raise
            self._write_count += 1
            if self._write_count % self._CHECKPOINT_EVERY_N_WRITES == 0:
                self._try_wal_checkpoint()
            return result
        except sqlite3.OperationalError as exc:
            err_msg = str(exc).lower()
            if "locked" in err_msg or "busy" in err_msg:
                last_err = exc
                if attempt < self._WRITE_MAX_RETRIES - 1:
                    jitter = random.uniform(
                        self._WRITE_RETRY_MIN_S,
                        self._WRITE_RETRY_MAX_S,
                    )
                    time.sleep(jitter)
                    continue
            raise
```

关键设计点：
- `BEGIN IMMEDIATE`：在事务开始时即获取写锁，若失败立即抛出 `OperationalError`，避免等待。
- `self._lock`：线程级互斥锁，防止同进程内多线程并发写。
- 随机抖动：`random.uniform(0.02, 0.15)`（20–150 ms），避免多进程同时重试导致的“ thundering herd ”问题。
- 定期 WAL checkpoint：每 `_CHECKPOINT_EVERY_N_WRITES` 次写操作后尝试 `wal_checkpoint`，防止 `-wal` 文件无限增长。

#### 声明式 Schema 调和

`_reconcile_columns()`（lines 339–382）通过内存 SQLite 解析 `SCHEMA_SQL`，提取目标列定义，再与现有表对比：

```python
def _reconcile_columns(self, conn: sqlite3.Connection, table_name: str):
    # 1. 在内存 DB 中执行 SCHEMA_SQL 获取目标列
    # 2. 在目标 DB 中执行 PRAGMA table_info(table_name) 获取现有列
    # 3. 对缺失列执行 ALTER TABLE ADD COLUMN
```

`_init_schema()`（lines 383–489）在启动时调用 `_reconcile_columns()`，并依据 `state_meta` 中的版本标记执行条件化数据迁移（如 FTS 索引回填）。

#### 消息追加与原子替换

`append_message()`（lines 1266–1351）插入单条消息并更新会话计数器。

`replace_messages()`（lines 1353–1430）在单个事务内完成：
1. `DELETE FROM messages WHERE session_id = ?`
2. 批量 `INSERT INTO messages ...`
3. 更新会话计数器与摘要

这保证了 `/retry`、`/undo`、`/compress` 等重写操作的原子性，不会出现半写状态。

#### 全文检索（FTS5）

`search_messages()`（lines 1713–1957）实现三级 fallback：

1. **FTS5 unicode61**：`MATCH` 查询，适用于常规文本。
2. **FTS5 trigram**：对 CJK 文本使用 trigram tokenizer，支持子串匹配。
3. **LIKE 子串匹配**：若 FTS5 无结果，降级为 `LIKE '%keyword%'`，确保召回率。

#### 会话压缩延续链

`list_sessions_rich()`（lines 995–1183）使用递归 CTE 查询 `parent_session_id`，将会话按压缩链层级展示，使用户可直观看到某一会话是由哪条会话压缩而来。

#### 自动维护

`maybe_auto_prune_and_vacuum()`（lines 2602–2673）依据 `state_meta` 中记录的维护时间戳，以幂等方式执行：
- 旧会话/消息剪枝（基于保留策略）。
- `VACUUM` 或 `wal_checkpoint` 以回收空间。

### 4.3 配置管理

`hermes_cli/config.py` 实现了三级配置加载：

1. **内置默认值**：`DEFAULT_CONFIG`（line 395+），包含 `agent.max_turns=90`、`gateway_timeout=1800` 等。
2. **用户配置文件**：`~/.hermes/config.yaml`，通过 `load_config()`（line 3978）加载。
3. **子命令/直接参数**：命令行参数或代码中直接传入的覆盖值。

`load_config()` 使用 mtime + size 作为缓存键，避免重复解析 YAML：

```python
def load_config() -> Dict[str, Any]:
    with _CONFIG_LOCK:
        ensure_hermes_home()
        config_path = get_config_path()
        path_key = str(config_path)
        try:
            st = config_path.stat()
            cache_key: Optional[Tuple[int, int]] = (st.st_mtime_ns, st.st_size)
        except FileNotFoundError:
            cache_key = None
        cached = _LOAD_CONFIG_CACHE.get(path_key)
        if cached is not None and cache_key is not None and cached[:2] == cache_key:
            return copy.deepcopy(cached[2])
        config = copy.deepcopy(DEFAULT_CONFIG)
        # ... yaml load and deep merge
```

### 4.4 文件系统 Checkpoint（协同机制）

`tools/checkpoint_manager.py` 中的 `CheckpointManager` 使用基于 git 的 shadow store，在破坏性操作（如文件重写、批量替换）前创建透明快照。这与 SQLite 的事务机制形成互补：
- SQLite 事务保护数据库层面的原子性。
- CheckpointManager 保护工作目录层面的文件系统状态，支持在 Agent 工具调用导致文件损坏时快速回滚。

## 5. 与其他维度的交互

| 交互维度 | 交互方式与说明 |
|---------|--------------|
| **会话管理（Session Management）** | `AIAgent` 通过 `_session_db` 读写 `SessionDB`；`session_id` 与 `parent_session_id` 构成会话树；`list_sessions_rich()` 的递归 CTE 直接服务于会话列表展示。 |
| **命令系统（Command System）** | `/retry`、`/undo`、`/compress` 等命令调用 `replace_messages()` 实现 transcript 原子重写；`/search` 调用 `search_messages()` 提供全文检索。 |
| **配置系统（Configuration）** | `load_config()` 提供的数据库路径、保留策略、FTS 开关等参数直接影响 `SessionDB` 的初始化与 `maybe_auto_prune_and_vacuum()` 的行为。 |
| **工具系统（Tool System）** | `CheckpointManager` 在工具执行前对文件系统做快照，与 SQLite 事务共同构成“数据库 + 文件”双重复原点。 |
| **消息协议（Message Protocol）** | `messages` 表的 `content` 字段支持 JSON sentinel prefix 编码，承载多模态消息（图片、文件引用等），是消息协议在持久化层的落地。 |
| **迭代控制（Iteration Control）** | `AIAgent.iteration_budget` 与 `_api_call_count` 等运行时状态直接决定 Agent 何时终止，这些状态虽在内存中，但其历史记录通过 `append_message()` 持久化到 `messages` 表。 |

## 6. 设计权衡

1. **SQLite vs. 客户端/服务器型数据库**
   - **选择 SQLite**：零部署、单文件、跨平台、Python 标准库原生支持，适合个人/本地优先的 Agent 场景。
   - **代价**：高并发写仍需应用级协调；WAL 模式下单机性能足够，但无法横向扩展到多机。
   - **缓解**：WAL + 随机抖动重试 + 线程锁，在“单用户多进程”场景下已足够稳健。

2. **运行时内存状态 vs. 全持久化**
   - **选择内存态**：`_interrupt_requested`、`_last_activity_ts` 等字段需要亚毫秒级响应，不适合每次操作都写盘。
   - **代价**：进程崩溃时运行时状态丢失；但会话历史已通过 `append_message()` 增量持久化，重启后可恢复上下文，仅丢失最近一次未刷新的活动描述。
   - **缓解**：`get_activity_summary()` 提供实时观测，运维脚本可通过轮询获取快照。

3. **声明式 Schema 调和 vs. 显式迁移脚本**
   - **选择声明式**：减少维护负担，新列自动补齐，适合快速迭代。
   - **代价**：无法表达复杂迁移逻辑（如列类型变更、数据拆分）。
   - **缓解**：复杂迁移仍可在 `_init_schema()` 中通过版本门控手动实现；`state_meta` 表保留了扩展空间。

4. **FTS5 双索引 vs. 单索引**
   - **选择双索引**：兼顾英文与 CJK 的检索质量。
   - **代价**：磁盘占用增加；插入时需要维护两份 FTS 索引。
   - **缓解**：FTS5 虚拟表本身不存储原始数据，仅存储索引，空间开销可控；且 CJK 场景可通过配置开关控制是否启用 trigram。

5. **随机抖动重试 vs. SQLite busy handler**
   - **选择应用级随机抖动**：避免确定性重试导致的碰撞放大。
   - **代价**：增加了 Python 层的代码复杂度。
   - **缓解**：该逻辑被封装在 `_execute_write()` 内部，对外完全透明。

6. **JSON sentinel prefix 编码 vs. 多模态专用表**
   - **选择 sentinel prefix**：在现有 `TEXT` 列中内嵌多模态内容，避免 schema 爆炸。
   - **代价**：`content` 列的语义变得混合，查询时需要解析前缀。
   - **缓解**：序列化/反序列化逻辑集中在消息协议层，数据库层仅负责透明存储。
