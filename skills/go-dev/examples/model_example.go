// GORM Model 示例

package data

import "time"

// AccountRecord 账号记录
// 表名: t_account
// 命名规范: 结构体用 {Entity}Record，表名用 t_{entity}
// 所有表必须包含 6 个基础字段：id, create_user, create_time, update_user, update_time, is_deleted
// json 标签使用 snake_case（与线上字段名一致）
// 时间字段使用双重保险：autoCreateTime/autoUpdateTime + default:CURRENT_TIMESTAMP(3)
type AccountRecord struct {
	Id               uint64    `gorm:"column:id;primaryKey;autoIncrement;not null" json:"id"`                                      // 主键，自增
	Username         string    `gorm:"column:username;size:50;unique;not null" json:"username"`                                    // 用户名，唯一
	Nickname         string    `gorm:"column:nickname;size:50;not null" json:"nickname"`                                           // 昵称，默认随机生成
	Email            string    `gorm:"column:email;size:100;not null" json:"email"`                                                // 加密邮箱
	Phone            string    `gorm:"column:phone;size:100" json:"phone"`                                                         // 加密手机号
	Password         string    `gorm:"column:password;size:100;not null" json:"password"`                                          // 加密密码
	Avatar           string    `gorm:"column:avatar;size:100" json:"avatar"`                                                       // 头像Key
	RoleId           uint64    `gorm:"column:role_id" json:"role_id"`                                                              // 对应 t_role
	LastLoginTime    time.Time `gorm:"column:last_login_time" json:"last_login_time"`                                              // 最近登录时间
	CurrentLoginTime time.Time `gorm:"column:current_login_time" json:"current_login_time"`                                        // 当前登录时间
	CreateUser       string    `gorm:"column:create_user;size:50;not null" json:"create_user"`                                     // 创建人
	CreateTime       time.Time `gorm:"column:create_time;autoCreateTime;not null;default:CURRENT_TIMESTAMP(3)" json:"create_time"` // 创建时间
	UpdateUser       string    `gorm:"column:update_user;size:50;not null" json:"update_user"`                                     // 修改人
	UpdateTime       time.Time `gorm:"column:update_time;autoUpdateTime;not null;default:CURRENT_TIMESTAMP(3)" json:"update_time"` // 修改时间
	IsDeleted        bool      `gorm:"column:is_deleted;not null;default:false" json:"is_deleted"`                                 // 是否删除
}

// TableName 返回表名，必须以 t_ 开头
func (r *AccountRecord) TableName() string {
	return "t_account"
}

// TenantRecord 租户记录
// 线上已存在的表保持原名，不强制改为 t_ 前缀
// 如果线上字段名与 go-dev 规范不同（如 created_at vs create_time），通过 gorm column 标签映射
type TenantRecord struct {
	Id         uint64    `gorm:"column:id;primaryKey;autoIncrement;not null" json:"id"`                                      // 主键，自增
	TenantName string    `gorm:"column:tenant_name;size:50;not null" json:"tenant_name"`                                     // 租户名称
	State      uint8     `gorm:"column:state;not null;default:1" json:"state"`                                               // 租户状态
	CreateUser string    `gorm:"column:create_user;size:50;not null" json:"create_user"`                                     // 创建人
	CreateTime time.Time `gorm:"column:create_time;autoCreateTime;not null;default:CURRENT_TIMESTAMP(3)" json:"create_time"` // 创建时间
	UpdateUser string    `gorm:"column:update_user;size:50;not null" json:"update_user"`                                     // 修改人
	UpdateTime time.Time `gorm:"column:update_time;autoUpdateTime;not null;default:CURRENT_TIMESTAMP(3)" json:"update_time"` // 修改时间
	IsDeleted  bool      `gorm:"column:is_deleted;not null;default:false" json:"is_deleted"`                                 // 是否删除
}

func (r *TenantRecord) TableName() string {
	return "t_tenant"
}

// 线上表字段名映射示例：
// 线上表使用 created_at，go-dev 规范要求 create_time
// Go 结构体字段名遵循 go-dev 规范，GORM column 标签映射到线上字段名
// 时间字段双重保险：autoCreateTime/autoUpdateTime + default:CURRENT_TIMESTAMP(3)
type UsageRecord struct {
	Id               uint64    `gorm:"column:id;primaryKey;autoIncrement;not null" json:"id"`
	UserId           uint64    `gorm:"column:user_id;not null;index" json:"user_id"`
	Model            string    `gorm:"column:model;size:100;not null" json:"model"`
	PromptTokens     uint64    `gorm:"column:prompt_tokens;not null" json:"prompt_tokens"`
	CompletionTokens uint64    `gorm:"column:completion_tokens;not null" json:"completion_tokens"`
	TotalTokens      uint64    `gorm:"column:total_tokens;not null" json:"total_tokens"`
	UserAgent        string    `gorm:"column:user_agent;size:512" json:"user_agent"`
	Endpoint         string    `gorm:"column:endpoint;size:255;default:aiworks" json:"endpoint"`
	CreateUser       string    `gorm:"column:create_user;size:50;not null" json:"create_user"`
	CreateTime       time.Time `gorm:"column:created_at;autoCreateTime;not null;default:CURRENT_TIMESTAMP(3)" json:"created_at"` // 注意：column 映射到线上字段名 created_at
	UpdateUser       string    `gorm:"column:update_user;size:50;not null" json:"update_user"`
	UpdateTime       time.Time `gorm:"column:updated_at;autoUpdateTime;not null;default:CURRENT_TIMESTAMP(3)" json:"updated_at"` // 注意：column 映射到线上字段名 updated_at
	IsDeleted        bool      `gorm:"column:deleted;not null;default:false" json:"deleted"`                                     // 注意：column 映射到线上字段名 deleted
}

func (r *UsageRecord) TableName() string {
	return "psci_user_ai_token_usage_record" // 线上表名保持不变
}
