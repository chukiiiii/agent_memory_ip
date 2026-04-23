#!/usr/bin/env bash
# A-Mem 测试运行脚本

set -e

WORKDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$WORKDIR"

echo "=========================================="
echo "A-Mem 测试脚本"
echo "=========================================="

case "$1" in
    "simple")
        echo "运行简单测试 (无需API密钥)..."
        python test_simple.py
        ;;

    "quick")
        echo "运行快速测试 (需要OpenAI API密钥)..."
        if [ -z "$OPENAI_API_KEY" ]; then
            echo "错误：请设置 OPENAI_API_KEY 环境变量"
            echo "export OPENAI_API_KEY=your-key"
            exit 1
        fi
        python test_advanced_robust.py \
            --backend openai \
            --model gpt-4o-mini \
            --ratio 0.01 \
            --output quick_test.json
        ;;

    "full")
        echo "运行完整测试 (需要OpenAI API密钥)..."
        if [ -z "$OPENAI_API_KEY" ]; then
            echo "错误：请设置 OPENAI_API_KEY 环境变量"
            echo "export OPENAI_API_KEY=your-key"
            exit 1
        fi
        python test_advanced_robust.py \
            --backend openai \
            --model gpt-4o-mini \
            --ratio 1.0 \
            --output full_test.json
        ;;

    "analyze")
        if [ -z "$2" ]; then
            echo "用法: $0 analyze <结果文件>"
            exit 1
        fi
        python analyze_results.py "$2"
        ;;

    "compare")
        shift
        if [ $# -eq 0 ]; then
            echo "用法: $0 compare <文件1> <文件2> ..."
            exit 1
        fi
        python analyze_results.py --compare "$@"
        ;;

    *)
        echo "可用命令:"
        echo "  simple      - 运行简单测试 (模拟预测)"
        echo "  quick       - 运行快速测试 (1%数据, 需要API密钥)"
        echo "  full        - 运行完整测试 (100%数据, 需要API密钥)"
        echo "  analyze <文件> - 分析结果文件"
        echo "  compare <文件1> <文件2> ... - 比较多个结果"
        echo ""
        echo "示例:"
        echo "  $0 simple"
        echo "  $0 quick"
        echo "  $0 analyze quick_test.json"
        echo "  $0 compare result1.json result2.json"
        echo ""
        echo "环境变量:"
        echo "  OPENAI_API_KEY - OpenAI API密钥"
        echo "  HF_HUB_OFFLINE=1 - 离线模式 (避免下载)"
        exit 1
        ;;
esac