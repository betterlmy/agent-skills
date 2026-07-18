# GORM 与数据库规范

## Model 时间字段规范

所有 Model 的时间字段使用双重保险 GORM 标签，与线上 MySQL 表结构对应：

```go
CreateTime time.Time `gorm:"column:create_time;autoCreateTime;not null;default:CURRENT_TIMESTAMP(3)" json:"create_time"`
UpdateTime time.Time `gorm:"column:update_time;autoUpdateTime;not null;default:CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3)" json:"update_time"`
```

注意：

- `autoCreateTime` / `autoUpdateTime`：GORM 应用层自动设置。
- `default:CURRENT_TIMESTAMP(3)`：数据库层默认值，毫秒精度，即使直接用 SQL 也能正确设置时间。
- `json` 标签使用 snake_case，与线上字段名一致，如 `json:"create_time"`。
- 如果线上表字段名与 go-dev 规范不同，如 `created_at` vs `create_time`，通过 `gorm:"column:created_at"` 映射，Go 结构体字段名遵循 go-dev 规范。

## GORM 初始化

```go
var Db *gorm.DB

func InitMysql(dsn string) {
    dbLogger := logger.New(
        gormLogWriter{},
        logger.Config{
            SlowThreshold:             time.Second,
            Colorful:                  true,
            IgnoreRecordNotFoundError: false,
            LogLevel:                  logger.Silent,
        },
    )

    db, err := gorm.Open(
        mysql.Open(dsn),
        &gorm.Config{
            NamingStrategy: schema.NamingStrategy{
                SingularTable: true,
            },
            Logger: dbLogger,
        },
    )
    if err != nil {
        log.Fatalf("mysql connect error:%v", err)
    }

    Db = db
}

type gormLogWriter struct{}

func (gormLogWriter) Printf(format string, args ...any) {
    log.Infof(format, args...)
}
```

## DAO 函数模式

使用扁平包级函数，不默认引入 struct/repository 模式：

```go
// GetXxxRecord 根据ID获取XXX记录
func GetXxxRecord(ctx context.Context, id uint64) (*XxxRecord, error) {
    var record XxxRecord
    err := Db.Debug().WithContext(ctx).
        Where("is_deleted = 0").
        Where("id = ?", id).
        First(&record).Error
    if err != nil {
        return nil, fmt.Errorf("数据库查询xxx错误:%v", err)
    }
    if record.Id == 0 {
        return nil, fmt.Errorf("xxx record is nil")
    }
    return &record, nil
}
```

关键要点：

- `Db.Debug().WithContext(ctx)` 是标准查询链。
- 手动 `Where("is_deleted = 0")` 做软删除过滤。
- `record.Id == 0` 作为未找到的辅助判断。
- `fmt.Errorf("数据库查询xxx错误:%v", err)` 使用中文错误描述。
- 分页使用 `Count(&total)` + `Limit(int(pageSize)).Offset(int(offset)).Find(&records)`。
- 事务使用 `Db.Transaction(func(tx *gorm.DB) error { ... })`。

## 错误处理

```go
if errors.Is(err, gorm.ErrRecordNotFound) {
    return nil, nil
}

var ErrConfigNotFound = errors.New("config not found")

if errors.Is(err, ErrConfigNotFound) {
    resp.Code = int32(codes.NotFound)
    resp.Message = codes.Message(codes.NotFound)
    return
}
```

使用 `errors.Is` 检查特定错误，不用字符串比较。

## SQL 核心规则

详细规则见 `../sql-standards.md`。

表命名：

- 必须以 `t_` 开头，小写下划线分隔，如 `t_device`、`t_monitor_alarm`。
- 线上已存在的表保持原名，不强制改为 `t_` 前缀。

基础字段固定包含：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | `BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY` | 自增主键，与 PRIMARY KEY 同行 |
| `create_time` | `DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3)` | 创建时间 |
| `create_user` | `VARCHAR(50) NOT NULL` | 创建人 |
| `update_time` | `DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3)` | 更新时间 |
| `update_user` | `VARCHAR(50) NOT NULL` | 修改人 |
| `is_deleted` | `TINYINT(1) UNSIGNED NOT NULL DEFAULT 0` | 逻辑删除 |

Model 字段示例：

```go
type XxxRecord struct {
    Id         uint64    `gorm:"column:id;primaryKey;autoIncrement;not null" json:"id"`
    CreateUser string    `gorm:"column:create_user;size:50;not null" json:"create_user"`
    CreateTime time.Time `gorm:"column:create_time;not null;default:CURRENT_TIMESTAMP(3)" json:"create_time"`
    UpdateUser string    `gorm:"column:update_user;size:50;not null" json:"update_user"`
    UpdateTime time.Time `gorm:"column:update_time;not null;default:CURRENT_TIMESTAMP(3)" json:"update_time"`
    IsDeleted  bool      `gorm:"column:is_deleted;not null;default:false" json:"is_deleted"`
}

func (r *XxxRecord) TableName() string {
    return "t_xxx"
}
```

其他要求：

- 时间字段统一 `DATETIME(3)` 毫秒精度，禁止新表使用 `DATETIME` 或 `TIMESTAMP`；已有字段不干预，仅提醒。
- 表级声明：`ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin`。
- 索引命名：普通索引 `idx_` 前缀，唯一索引 `uk_` 前缀，使用 `KEY` 关键字，禁止 `INDEX`。
- 所有字段和表必须添加中文 `COMMENT`。
- 数据库名使用 `${DBNAME}` 变量占位，禁止硬编码。
