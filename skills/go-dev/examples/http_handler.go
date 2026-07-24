// HTTP Handler 示例：使用标准库展示统一响应和安全错误映射。
// 实际项目应复用已有 Router、日志、认证和响应封装。
package examples

import (
	"context"
	"encoding/json"
	"errors"
	"io"
	"net/http"
)

const maxCreateTaskBodyBytes = 64 << 10

type Code uint32

const (
	codeOK              Code = 0
	codeInvalidArgument Code = 10001
	codeConflict        Code = 10002
	codeInternal        Code = 10500
)

var (
	errInvalidJSON  = errors.New("invalid JSON")
	errTaskConflict = errors.New("task conflict")
)

type response[T any] struct {
	Code    Code   `json:"code"`
	Message string `json:"message"`
	Data    T      `json:"data"`
}

type createTaskRequest struct {
	Title string `json:"title"`
}

type createTaskData struct {
	TaskID string `json:"task_id"`
}

type taskCreator interface {
	CreateTask(context.Context, string) (string, error)
}

type safeLogger interface {
	ErrorContext(context.Context, string, ...any)
}

type taskHandler struct {
	creator taskCreator
	logger  safeLogger
}

func (handler *taskHandler) createTask(writer http.ResponseWriter, request *http.Request) {
	request.Body = http.MaxBytesReader(writer, request.Body, maxCreateTaskBodyBytes)
	decoder := json.NewDecoder(request.Body)
	decoder.DisallowUnknownFields()

	var input createTaskRequest
	if err := decodeOneJSON(decoder, &input); err != nil || input.Title == "" {
		handler.writeResponse(request.Context(), writer, response[any]{
			Code: codeInvalidArgument, Message: "请求参数无效", Data: nil,
		})
		return
	}

	taskID, err := handler.creator.CreateTask(request.Context(), input.Title)
	if err != nil {
		if errors.Is(err, errTaskConflict) {
			handler.writeResponse(
				request.Context(), writer,
				response[any]{Code: codeConflict, Message: "任务冲突", Data: nil},
			)
			return
		}
		handler.logger.ErrorContext(request.Context(), "create_task_failed", "error_class", "internal")
		handler.writeResponse(
			request.Context(), writer,
			response[any]{Code: codeInternal, Message: "服务暂时不可用", Data: nil},
		)
		return
	}

	handler.writeResponse(request.Context(), writer, response[createTaskData]{
		Code: codeOK, Message: "成功", Data: createTaskData{TaskID: taskID},
	})
}

func decodeOneJSON(decoder *json.Decoder, destination any) error {
	if err := decoder.Decode(destination); err != nil {
		return errInvalidJSON
	}
	var trailing any
	if err := decoder.Decode(&trailing); !errors.Is(err, io.EOF) {
		return errInvalidJSON
	}
	return nil
}

func (handler *taskHandler) writeResponse(ctx context.Context, writer http.ResponseWriter, body any) {
	if err := writeJSON(writer, body); err != nil {
		handler.logger.ErrorContext(ctx, "write_response_failed", "error_class", "encode_or_write")
	}
}

func writeJSON(writer http.ResponseWriter, body any) error {
	writer.Header().Set("Content-Type", "application/json; charset=utf-8")
	writer.WriteHeader(http.StatusOK)
	return json.NewEncoder(writer).Encode(body)
}
