// gRPC 错误映射示例：请求响应类型经过简化，实际项目使用生成的 pb 类型。
package examples

import (
	"context"
	"errors"

	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

var (
	errAccountNotFound  = errors.New("account not found")
	errStoreUnavailable = errors.New("store unavailable")
)

type getAccountRequest struct {
	AccountID string
}

type getAccountResponse struct {
	AccountID string
	Name      string
}

type accountReader interface {
	GetAccount(context.Context, string) (getAccountResponse, error)
}

type accountService struct {
	reader accountReader
}

func (service *accountService) getAccount(
	ctx context.Context,
	request *getAccountRequest,
) (*getAccountResponse, error) {
	if request == nil || request.AccountID == "" {
		return nil, status.Error(codes.InvalidArgument, "account_id is required")
	}

	account, err := service.reader.GetAccount(ctx, request.AccountID)
	if err != nil {
		switch {
		case errors.Is(err, errAccountNotFound):
			return nil, status.Error(codes.NotFound, "account not found")
		case errors.Is(err, context.Canceled):
			return nil, status.Error(codes.Canceled, "request canceled")
		case errors.Is(err, context.DeadlineExceeded):
			return nil, status.Error(codes.DeadlineExceeded, "request deadline exceeded")
		case errors.Is(err, errStoreUnavailable):
			return nil, status.Error(codes.Unavailable, "service unavailable")
		default:
			return nil, status.Error(codes.Internal, "internal error")
		}
	}
	return &account, nil
}
