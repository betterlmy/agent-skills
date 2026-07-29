# 持久化与数据层（第二步·下）

对 GORM/SQL 服务尤其重要。命令限制在用户范围；文件或 diff 改动数据访问时，必须读取事务入口、调用方和相关 schema 作为上下文。重点查事务边界、Rows 关闭、连接池和迁移一致性。

## N+1 查询

循环内单条查询：

```bash
rg -n 'for\s.*\{[\s\S]*?\.(First|Find|Take|Get|Where)\(' --type go -U
```

- GORM：循环内 `db.First(&x, id)` 或 `Range` 后逐条查关联。应 `Preload`/`Joins`/批量 `IN` 查询。
- 人工读 service 层循环体，确认循环内无 DB 调用。

## 事务边界

- `Begin` 后必须保证所有路径 `Rollback`（失败）或 `Commit`（成功）。检测：

  ```bash
  rg -n '\.Begin\(|Transaction\(|Tx\(' --type go
  ```

  对照 `defer` Rollback 与返回前的 Commit 是否覆盖所有 return。

- 事务内 RPC、HTTP 或其他外部 IO 是高风险候选；结合超时、锁范围、重试与数据一致性影响定级。
- 嵌套事务：GORM 嵌套 `Transaction` 语义是否正确（实际是 savepoint 还是复用同一 tx）。
- `Commit` 错误被忽略：`tx.Commit()` 返回的 err 未检查。

## Rows 与结果集关闭

- `Rows` 未 `defer Close()`，或迭代中 `return` 未 defer 导致泄漏。`rowserrcheck`/`sqlclosecheck` linter。
- `Rows.Err()` 未检查：迭代结束后应 `if rows.Err() != nil`。

## SQL 注入

- 字符串拼接 SQL、`Raw` 直接拼参数、动态表名/列名拼接：

  ```bash
  rg -n '\.Raw\(|fmt\.Sprintf.*SELECT|fmt\.Sprintf.*INSERT|fmt\.Sprintf.*WHERE' --type go
  rg -n '"SELECT.*"\s*\+' --type go
  ```

  外部输入进入 SQL 结构或值拼接时属于阻断级候选；确认可达性和驱动行为后定级。常量拼接不自动构成注入，值参数优先使用参数化查询。

## 连接池配置

- `sql.DB` 的 `SetMaxOpenConns`、`SetMaxIdleConns`、`SetConnMaxLifetime` 是否与部署规模、数据库限制和代理配置匹配。未显式设置是容量风险候选，不应脱离部署证据断言必然故障。
- GORM `DB.DB()` 暴露底层 `*sql.DB`，配置是否生效。
- Redis 客户端连接池大小与超时配置。

## 迁移与字段一致性

- DDL（`sql/ddl.sql` 或迁移文件）字段与 GORM 模型 `mysql_model.go` 是否一致：列名、类型、索引、非空。
- 查询条件是否命中索引：高频 WHERE/JOIN 字段是否有索引（需对照 DDL）。
- 软删除字段（`deleted_at`）是否在所有查询正确过滤；GORM 默认行为是否被意外绕过。
- 时间字段时区与精度（`DATETIME` vs `TIMESTAMP`）。

## ORM 陷阱

- `Updates(map)` 与 `Updates(struct)` 的零值差异：struct 更新会忽略零值字段。
- `First` 未找到记录返回 `ErrRecordNotFound`，是否被当作业务错误正确处理。
- 钩子（`BeforeCreate` 等）副作用是否隐蔽、是否在批量操作生效。

## 产出

- N+1 查询点清单。
- 事务问题：范围过大 / Rollback 缺口 / Commit 错误忽略 / 嵌套语义。
- Rows 关闭与 `Rows.Err` 缺口。
- SQL 注入风险点。
- 连接池与迁移一致性问题。
