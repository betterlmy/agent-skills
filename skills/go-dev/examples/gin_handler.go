// Gin Handler 示例：只在项目已经使用 Gin 时参考。
package examples

import (
	"context"
	"net/http"

	"github.com/gin-gonic/gin"
)

type listTaskData struct {
	Tasks []taskSummary `json:"tasks"`
}

type taskSummary struct {
	TaskID string `json:"task_id"`
	Title  string `json:"title"`
}

type taskLister interface {
	ListTasks(context.Context) ([]taskSummary, error)
}

type ginTaskHandler struct {
	service taskLister
}

func (handler *ginTaskHandler) listTasks(c *gin.Context) {
	tasks, err := handler.service.ListTasks(c.Request.Context())
	if err != nil {
		// 实际项目应在统一错误映射层使用 errors.Is/As 分类并记录安全日志。
		c.JSON(http.StatusOK, response[any]{Code: codeInternal, Message: "服务暂时不可用", Data: nil})
		return
	}
	if tasks == nil {
		tasks = []taskSummary{}
	}
	c.JSON(http.StatusOK, response[listTaskData]{
		Code: codeOK, Message: "成功", Data: listTaskData{Tasks: tasks},
	})
}
