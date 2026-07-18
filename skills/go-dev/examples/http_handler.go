// HTTP Handler 示例

package product

import (
	"context"
	"net/http"
	"time"

	"myproject/internal/apis/client"
	"myproject/internal/pkg/codes"

	"myproject/pb/product"

	"github.com/gin-gonic/gin"
	"gitlab-esd.leapmotor.com/psa/product/lp-go-tool.git/log"
)

const RPC_TIMEOUT = 5 * time.Second

// InitRouter 注册产品相关路由
// 路由按领域分组，每个领域有自己的 RouterGroup
func InitRouter(routerGroup *gin.RouterGroup) {
	productRouterGroup := routerGroup.Group("/device/management/product")
	productRouterGroup.POST("/add", AddProduct)
	productRouterGroup.POST("/delete", DeleteProduct)
	productRouterGroup.POST("/update", UpdateProduct)
	productRouterGroup.POST("/list", ListProduct)
	productRouterGroup.POST("/detail", GetProduct)
}

// ===== Request 结构体 =====
// 命名规范: Api{Action}{Entity}Request
// 验证标签: required, min=N, max=N, oneof=...

type ApiAddProductRequest struct {
	Name               string `json:"name" binding:"required,min=1,max=30"`
	CategoryId         int64  `json:"categoryId"`
	NodeType           int32  `json:"nodeType" binding:"required,oneof=1 2 3"`
	NetworkMethod      int32  `json:"networkMethod" binding:"required,oneof=1 2 3 4"`
	Protocol           int32  `json:"protocol" binding:"required,oneof=1 2"`
	DataFormat         int32  `json:"dataFormat" binding:"required,oneof=1 2"`
	CheckType          int32  `json:"checkType" binding:"required,oneof=1 2"`
	VerificationMethod int32  `json:"verificationMethod" binding:"required,oneof=1 2"`
	Description        string `json:"description" binding:"max=100"`
}

type ApiListProductRequest struct {
	Name       string `json:"name"`
	CategoryId int64  `json:"categoryId"`
	Status     int32  `json:"status"`
	PageNumber int32  `json:"pageNumber"`
	PageSize   int32  `json:"pageSize"`
}

// ===== Response 结构体 =====
// 命名规范: Api{Action}{Entity}Response + Api{Action}{Entity}Data
// 所有响应必须包含 Code 和 Message 字段

type ApiAddProductResponse struct {
	Code    int32              `json:"code"`
	Message string             `json:"message"`
	Data    *ApiAddProductData `json:"data"`
}

type ApiAddProductData struct {
	Id int64 `json:"id"`
}

type ApiListProductResponse struct {
	Code    int32               `json:"code"`
	Message string              `json:"message"`
	Data    *ApiListProductData `json:"data"`
}

type ApiListProductData struct {
	PageNumber int32               `json:"pageNumber"`
	PageSize   int32               `json:"pageSize"`
	Total      int32               `json:"total"`
	RecordList []*ApiProductDetail `json:"recordList"` // List 接口必须初始化为空数组
}

type ApiProductDetail struct {
	Id            int64  `json:"id"`
	ProductKey    string `json:"productKey"`
	Name          string `json:"name"`
	NodeType      int32  `json:"nodeType"`
	NetworkMethod int32  `json:"networkMethod"`
	Protocol      int32  `json:"protocol"`
	DataFormat    int32  `json:"dataFormat"`
	Status        int32  `json:"status"`
	Description   string `json:"description"`
	CreateTime    int64  `json:"createTime"`
}

// ===== Handler 函数 =====

// AddProduct 添加产品
// 模式: in/out 日志 + 预初始化响应 + defer 统一返回 HTTP 200 + ShouldBindJSON + context.WithTimeout
// @Summary 添加产品
// @Accept json
// @Tags 产品管理
// @Security Bearer
// @Param request body ApiAddProductRequest true "请求body"
// @Success 200 {object} ApiAddProductResponse "响应"
// @Router /device/management/product/add [post]
func AddProduct(c *gin.Context) {
	log.Infof("=== AddProduct in ===")

	apiResp := &ApiAddProductResponse{
		Code:    int32(codes.OK),
		Message: codes.Message(codes.OK),
	}

	defer func() {
		log.Infof("resp: %+v", apiResp)
		log.Infof("=== AddProduct out ===")
		c.JSON(http.StatusOK, apiResp)
	}()

	var apiReq ApiAddProductRequest
	if err := c.ShouldBindJSON(&apiReq); err != nil {
		apiResp.Code = int32(codes.BadRequest)
		apiResp.Message = codes.Message(codes.BadRequest)
		log.Errorf("AddProduct ShouldBindJSON error. err[%v]", err)
		return
	}
	log.Infof("request: %+v", apiReq)

	ctx, cancel := context.WithTimeout(c.Request.Context(), RPC_TIMEOUT)
	defer cancel()

	grpcReq := ConvertToAddProductRequest(&apiReq)
	grpcResp, err := client.ProductGrpcClient.AddProduct(ctx, grpcReq)
	if err != nil {
		apiResp.Code = int32(codes.Internal)
		apiResp.Message = codes.Message(codes.Internal)
		log.Errorf("AddProduct gRPC error. err[%v]", err)
		return
	}

	if grpcResp.GetCode() != int32(codes.OK) {
		apiResp.Code = grpcResp.GetCode()
		apiResp.Message = grpcResp.GetMessage()
		return
	}

	apiResp.Data = &ApiAddProductData{
		Id: grpcResp.GetId(),
	}
}

// ListProduct 产品列表
// 模式: in/out 日志 + 预初始化响应 + defer 统一返回 HTTP 200 + List 接口初始化空数组
func ListProduct(c *gin.Context) {
	log.Infof("=== ListProduct in ===")

	apiResp := &ApiListProductResponse{
		Code:    int32(codes.OK),
		Message: codes.Message(codes.OK),
		Data: &ApiListProductData{
			RecordList: []*ApiProductDetail{},
		},
	}

	defer func() {
		log.Infof("resp: %+v", apiResp)
		log.Infof("=== ListProduct out ===")
		c.JSON(http.StatusOK, apiResp)
	}()

	var apiReq ApiListProductRequest
	if err := c.ShouldBindJSON(&apiReq); err != nil {
		apiResp.Code = int32(codes.BadRequest)
		apiResp.Message = codes.Message(codes.BadRequest)
		log.Errorf("ListProduct ShouldBindJSON error. err[%v]", err)
		return
	}
	log.Infof("request: %+v", apiReq)

	ctx, cancel := context.WithTimeout(c.Request.Context(), RPC_TIMEOUT)
	defer cancel()

	grpcReq := ConvertToListProductRequest(&apiReq)
	grpcResp, err := client.ProductGrpcClient.ListProduct(ctx, grpcReq)
	if err != nil {
		apiResp.Code = int32(codes.Internal)
		apiResp.Message = codes.Message(codes.Internal)
		log.Errorf("ListProduct gRPC error. err[%v]", err)
		return
	}

	if grpcResp.GetCode() != int32(codes.OK) {
		apiResp.Code = grpcResp.GetCode()
		apiResp.Message = grpcResp.GetMessage()
		return
	}

	apiResp.Data = ConvertToApiListProductData(grpcResp.GetData())
}

// ===== 转换函数 =====

// ConvertToAddProductRequest API 请求转 gRPC 请求
// 命名规范: ConvertTo{Target}
func ConvertToAddProductRequest(req *ApiAddProductRequest) *product.AddProductRequest {
	if req == nil {
		return nil
	}
	return &product.AddProductRequest{
		Name:               req.Name,
		CategoryId:         req.CategoryId,
		NodeType:           req.NodeType,
		NetworkMethod:      req.NetworkMethod,
		Protocol:           req.Protocol,
		DataFormat:         req.DataFormat,
		CheckType:          req.CheckType,
		VerificationMethod: req.VerificationMethod,
		Description:        req.Description,
	}
}

// ConvertToListProductRequest API 列表请求转 gRPC 请求
func ConvertToListProductRequest(req *ApiListProductRequest) *product.ListProductRequest {
	if req == nil {
		return nil
	}
	return &product.ListProductRequest{
		Name:       req.Name,
		CategoryId: req.CategoryId,
		Status:     req.Status,
		PageNumber: req.PageNumber,
		PageSize:   req.PageSize,
	}
}

// ConvertToApiListProductData gRPC 响应转 API 响应
func ConvertToApiListProductData(data *product.ListProductData) *ApiListProductData {
	if data == nil {
		return &ApiListProductData{
			RecordList: []*ApiProductDetail{}, // 必须初始化为空数组
		}
	}
	return &ApiListProductData{
		PageNumber: data.GetPageNumber(),
		PageSize:   data.GetPageSize(),
		Total:      data.GetTotal(),
		RecordList: ConvertToApiProductDetails(data.GetRecordList()),
	}
}

// ConvertToApiProductDetails 批量转换
func ConvertToApiProductDetails(list []*product.ProductInfo) []*ApiProductDetail {
	result := make([]*ApiProductDetail, 0, len(list))
	for _, item := range list {
		result = append(result, &ApiProductDetail{
			Id:            item.GetId(),
			ProductKey:    item.GetProductKey(),
			Name:          item.GetName(),
			NodeType:      item.GetNodeType(),
			NetworkMethod: item.GetNetworkMethod(),
			Protocol:      item.GetProtocol(),
			DataFormat:    item.GetDataFormat(),
			Status:        item.GetStatus(),
			Description:   item.GetDescription(),
			CreateTime:    item.GetCreateTime(),
		})
	}
	return result
}
