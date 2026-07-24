# GORM 可选参考

仅当仓库已经使用 GORM，或用户明确选择 GORM 时读取本文。数据库方言、插件和 GORM 版本以 `go.mod` 为准。

## 初始化与注入

- 在启动层创建 `*gorm.DB` 并通过构造函数注入 Store/Repository；仓库已有包级 `DB` 时可以沿用，但不要在新项目默认增加可变全局变量。
- 配置连接池、慢查询阈值和日志等级；生产环境不要无条件使用 `Debug()`。
- GORM Logger 必须接入项目安全日志入口，并避免输出敏感 SQL 参数。
- 初始化失败向启动层返回错误，由进程入口决定退出策略；库代码不要直接 `Fatal`。

## Model

- `column`、主键、索引、时间和软删除标签必须匹配真实 Schema，不依赖猜测或仅依赖 AutoMigrate。
- JSON 标签属于公开传输契约时，不应直接复用数据库 Model；优先使用独立 DTO。
- 时间字段是否使用 `autoCreateTime`、`autoUpdateTime` 和数据库默认值取决于写入来源与 Schema 事实。
- MySQL、PostgreSQL、SQLite 和 SQL Server 的默认值、类型、索引和锁行为不同，不复制其他方言标签。

## 查询

```go
func (store *Store) FindAccount(ctx context.Context, id uint64) (Account, error) {
    var model accountModel
    result := store.db.WithContext(ctx).Where("id = ?", id).First(&model)
    if errors.Is(result.Error, gorm.ErrRecordNotFound) {
        return Account{}, ErrAccountNotFound
    }
    if result.Error != nil {
        return Account{}, fmt.Errorf("find account: %w", result.Error)
    }
    return model.toDomain(), nil
}
```

- 每次操作传播 Context，并通过稳定错误映射隔离 GORM 错误。
- 软删除使用 GORM 内置机制还是显式字段由仓库 Schema 决定，不机械追加 `is_deleted = 0`。
- 检查 `RowsAffected` 只能作为明确操作语义的一部分，不能替代错误处理或唯一约束。
- List 查询初始化空结果、提供稳定排序与上限；Count 与数据查询的一致性要求由业务决定。

## 事务

```go
func (store *Store) InTransaction(ctx context.Context, fn func(*Store) error) error {
    return store.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
        return fn(&Store{db: tx})
    })
}
```

- 所有事务内操作必须使用 `tx` 派生的 Store，不能回退到根 `db`。
- 不在事务闭包中调用不可控的长网络操作。
- Nested Transaction、Savepoint、锁和重试行为依赖方言与版本，使用前查阅对应版本文档并测试。

## AutoMigrate

- 生产是否允许 AutoMigrate 是仓库部署策略，不是 GORM 默认选择。
- 已采用版本化迁移的仓库，不应在应用启动时再隐式修改 Schema。
- 生成或评审迁移时仍需检查锁、回滚、混合版本兼容和数据回填风险。
