# 测试文档使用说明

## 推荐上传顺序

```bash
curl -F "file=@samples/employee_handbook.md" http://127.0.0.1:8000/upload
curl -F "file=@samples/finance_policy.md" http://127.0.0.1:8000/upload
curl -F "file=@samples/it_security.md" http://127.0.0.1:8000/upload
curl -F "file=@samples/company_benefits.txt" http://127.0.0.1:8000/upload
```

记录每次返回的 `document_id`。

## 测试问答

不指定文档，全库检索：

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"公司年假制度是怎样的？","top_k":3}'
```

指定员工手册文档：

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"公司年假制度是怎样的？","document_ids":["替换为员工手册document_id"],"top_k":3}'
```

指定财务制度文档，验证文档隔离：

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"公司年假制度是怎样的？","document_ids":["替换为财务制度document_id"],"top_k":3}'
```

测试财务问题：

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"差旅报销需要多久提交？","top_k":3}'
```

测试 IT 安全问题：

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"账号异常登录应该怎么处理？","top_k":3}'
```

测试拒答：

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"公司股票期权如何行权？","top_k":3}'
```

## 测试文档更新

使用 `employee_handbook_v2.md` 更新员工手册：

```bash
curl -X PUT -F "file=@samples/employee_handbook_v2.md" \
  http://127.0.0.1:8000/documents/替换为员工手册document_id
```

更新后再次询问：

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"公司年假制度是怎样的？","document_ids":["替换为员工手册document_id"],"top_k":3}'
```

预期能看到年假从五天变为七天，提前申请时间从五个工作日变为三个工作日。
