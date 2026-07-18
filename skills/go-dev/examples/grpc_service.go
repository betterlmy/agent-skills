// gRPC 服务方法示例

package service

import (
	"context"

	"myproject/internal/data"
	"myproject/internal/pkg/codes"
	"myproject/internal/pkg/util"
	"myproject/pb/account"

	"gitlab-esd.leapmotor.com/psa/product/lp-go-tool.git/log"
)

// AccountService 账号服务
// 必须嵌入 UnimplementedXXXServer，确保向前兼容
type AccountService struct {
	account.UnimplementedAccountServer
}

// 编译期接口检查：确保 AccountService 实现了 account.AccountServer 接口
var _ account.AccountServer = &AccountService{}

// RegisterAccount 注册账号
// 遵循 gRPC 接口规范模板：日志 + defer + 错误码
func (s *AccountService) RegisterAccount(ctx context.Context, req *account.RegisterAccountRequest) (*account.RegisterAccountResponse, error) {
	log.Infof("=== RegisterAccount in ===")
	log.Infof("request: %+v", req)

	resp := &account.RegisterAccountResponse{
		Code:    int32(codes.OK),
		Message: codes.Message(codes.OK),
	}

	defer func() {
		log.Infof("resp: %+v", resp)
		log.Infof("=== RegisterAccount out ===")
	}()

	// 参数校验
	if req.GetUsername() == "" || req.GetPassword() == "" {
		resp.Code = int32(codes.InvalidArgument)
		resp.Message = codes.Message(codes.InvalidArgument)
		return resp, nil
	}

	// 检查账号是否已存在
	err := data.CheckAccountExist(ctx, req.GetUsername(), req.GetEmail())
	if err == nil {
		log.Errorf("RegisterAccount account already exists. username[%s]", req.GetUsername())
		resp.Code = int32(codes.AlreadyExists)
		resp.Message = codes.Message(codes.AlreadyExists)
		return resp, nil
	}

	// 密码加密
	passwordH, salt := util.EncryptPassword(req.GetPassword())

	// 调用数据层
	accountId, err := data.RegisterAccount(ctx, req.GetUsername(), req.GetNickname(), req.GetEmail(), passwordH, salt)
	if err != nil {
		log.Errorf("RegisterAccount data error. err[%v]", err)
		resp.Code = int32(codes.Internal)
		resp.Message = codes.Message(codes.Internal)
		return resp, nil
	}

	resp.AccountId = accountId

	return resp, nil
}

// GetAccountList 获取账号列表 - 注意 Data 和 RecordList 必须初始化
func (s *AccountService) GetAccountList(ctx context.Context, req *account.GetAccountListRequest) (*account.GetAccountListResponse, error) {
	log.Infof("=== GetAccountList in ===")
	log.Infof("request: %+v", req)

	resp := &account.GetAccountListResponse{
		Code:    int32(codes.OK),
		Message: codes.Message(codes.OK),
		Data: &account.AccountListData{
			RecordList: []*account.AccountInfo{}, // 必须初始化，返回 [] 而不是 null
		},
	}

	defer func() {
		log.Infof("resp: %+v", resp)
		log.Infof("=== GetAccountList out ===")
	}()

	records, total, err := data.GetAccountList(ctx, req.GetPageNumber(), req.GetPageSize(), req.GetKeyword())
	if err != nil {
		log.Errorf("GetAccountList data error. err[%v]", err)
		resp.Code = int32(codes.Internal)
		resp.Message = codes.Message(codes.Internal)
		return resp, nil
	}

	resp.Data = &account.AccountListData{
		PageNumber: req.GetPageNumber(),
		PageSize:   req.GetPageSize(),
		Total:      total,
		RecordList: convertToAccountInfos(records),
	}

	return resp, nil
}

// convertToAccountInfos 内部转换函数，私有函数用小驼峰
func convertToAccountInfos(records []*data.AccountRecord) []*account.AccountInfo {
	infos := make([]*account.AccountInfo, 0, len(records))
	for _, r := range records {
		infos = append(infos, &account.AccountInfo{
			AccountId:  r.Id,
			Username:   r.Username,
			Nickname:   r.Nickname,
			Email:      r.Email,
			RoleId:     r.RoleId,
			CreateTime: r.CreateTime.UnixMilli(),
		})
	}
	return infos
}
