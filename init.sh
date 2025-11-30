#!/bin/bash
# MD Audit 开发环境初始化脚本
# 用途：每个会话开始时运行，快速启动开发环境

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "=== MD Audit 开发环境初始化 ==="
echo "工作目录: $PROJECT_DIR"
echo ""

# 1. 激活虚拟环境
if [ -d "venv" ]; then
    echo "[1/5] 激活虚拟环境..."
    source venv/bin/activate
    echo "      Python: $(which python)"
else
    echo "[1/5] 警告: venv目录不存在，跳过虚拟环境激活"
fi

# 2. 检查依赖
echo "[2/5] 检查依赖..."
if pip show frontmatter >/dev/null 2>&1 && pip show beautifulsoup4 >/dev/null 2>&1; then
    echo "      核心依赖已安装"
else
    echo "      安装依赖..."
    pip install -r requirements.txt -q
fi

# 3. 检查配置文件
echo "[3/5] 检查配置文件..."
if [ -f "config/default_config.json" ]; then
    echo "      配置文件存在"
else
    echo "      警告: 配置文件缺失"
fi

# 4. 运行快速测试验证环境
echo "[4/5] 验证核心模块..."
python -c "
from md_audit.analyzer import MarkdownSEOAnalyzer
from md_audit.parsers.markdown_parser import MarkdownParser
from md_audit.engines.rules_engine import RulesEngine
print('      核心模块加载成功')
" 2>/dev/null || echo "      警告: 部分模块加载失败"

# 5. 显示项目状态
echo "[5/5] 项目状态..."
echo "      最近提交: $(git log --oneline -1 2>/dev/null || echo '无git仓库')"
echo "      修改文件: $(git status --porcelain 2>/dev/null | wc -l) 个"

echo ""
echo "=== 初始化完成 ==="
echo ""
echo "常用命令:"
echo "  分析文件:    python -m md_audit.main analyze docs/sample.md"
echo "  运行测试:    pytest tests/ -v"
echo "  启动Web:     python -m md_audit.main serve"
echo ""
