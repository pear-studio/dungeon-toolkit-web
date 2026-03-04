# Scripts

## 前端代码质量检查

### 使用方法

在项目根目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check-frontend-quality.ps1
```

### 检查项目

1. **Emoji 检测** - 确保代码中不使用 emoji 字符
2. **对比度检查** - 检测低对比度文本（text-slate-500/600/700）
3. **焦点样式** - 确保所有按钮都有焦点样式
4. **ARIA 属性** - 确保所有图标都有 aria-hidden 或 aria-label

### 退出码

- `0`: 检查通过（可能有警告）
- `1`: 检查失败（发现错误）

### 示例输出

```
================================
  Frontend Code Quality Check
================================

Check 1/4: Detecting emoji characters...
PASS: No emoji found

Check 2/4: Detecting low contrast text...
PASS: No low contrast issues

Check 3/4: Detecting buttons without focus styles...
PASS: All buttons have focus styles

Check 4/4: Detecting icons without aria attributes...
PASS: All icons have aria attributes

================================
  Check Complete!
  Duration: 136ms
  Errors: 0
  Warnings: 0
================================

PASSED: All checks successful!
```

### Git Pre-commit Hook

可以将此脚本添加到 Git pre-commit hook 中自动执行：

```bash
#!/bin/bash
powershell -ExecutionPolicy Bypass -File scripts/check-frontend-quality.ps1
if [ $? -ne 0 ]; then
    echo "Frontend quality check failed"
    exit 1
fi
```

### 详细文档

查看 [docs/FRONTEND_QUALITY_CHECK.md](../docs/FRONTEND_QUALITY_CHECK.md) 了解更多细节。
