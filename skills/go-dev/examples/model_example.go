// GORM Model 示例：只在仓库已经选择 GORM 时参考。
package examples

import (
	"time"

	"gorm.io/gorm"
)

// accountModel 是持久化模型，不直接作为公开 HTTP/gRPC DTO。
type accountModel struct {
	ID        uint64         `gorm:"column:id;primaryKey;autoIncrement"`
	Name      string         `gorm:"column:name;size:100;not null"`
	CreatedAt time.Time      `gorm:"column:created_at;autoCreateTime"`
	UpdatedAt time.Time      `gorm:"column:updated_at;autoUpdateTime"`
	DeletedAt gorm.DeletedAt `gorm:"column:deleted_at;index"`
}

func (accountModel) TableName() string {
	return "accounts"
}

type account struct {
	ID   uint64
	Name string
}

func (model accountModel) toDomain() account {
	return account{ID: model.ID, Name: model.Name}
}
