# A-Mem 测试指南

## 测试需求

你需要：
1. 简单跑通测试 ✅ (已有 `test_simple.py`)
2. 量化测试指标 ✅ (提供多种指标：F1、精确匹配、精确率、召回率等)
3. 测试集和指标 ✅ (使用 LoCoMo 数据集，包含5种问题类型)

## 快速开始

### 1. 简单测试（不需要API密钥）

```bash
python test_simple.py
```

这会：
- 加载少量数据样本
- 生成模拟预测
- 计算基本量化指标
- 输出综合评分

**示例输出指标：**
- F1分数: 0.96 (token重叠的调和平均)
- 精确匹配: 0.80 (完全一致的预测比例)
- 精确率: 1.00 (预测中的相关token比例)
- 召回率: 0.93 (参考答案中被覆盖的token比例)
- 综合评分: 0.93 (加权平均值)

### 2. 完整测试（需要OpenAI API密钥）

```bash
# 使用小样本测试（10%的数据）
python test_advanced_robust.py --backend openai --model gpt-4o-mini --ratio 0.1
```

### 3. 查看现有测试结果

如果有 `results_robust_*.json` 文件，可以使用：

```bash
python -c "
import json, glob
for f in glob.glob('results_robust_*.json'):
    with open(f) as file:
        data = json.load(file)
    print(f'{data[\"model\"]}:')
    overall = data['aggregate_metrics']['overall']
    print(f'  F1: {overall[\"f1\"][\"mean\"]:.4f}')
    print(f'  Exact match: {overall[\"exact_match\"][\"mean\"]:.4f}')
    print(f'  BLEU-1: {overall[\"bleu1\"][\"mean\"]:.4f}')
    print(f'  ROUGE-1: {overall[\"rouge1_f\"][\"mean\"]:.4f}')
"
```

## 量化指标详解

### 基础指标 (test_simple.py)

| 指标 | 范围 | 说明 |
|------|------|------|
| F1分数 | 0-1 | 精确率和召回率的调和平均，衡量token级别的匹配 |
| 精确匹配 | 0/1 | 预测与参考答案完全一致 |
| 精确率 | 0-1 | 预测中相关token的比例 |
| 召回率 | 0-1 | 参考答案中被正确预测的token比例 |
| 长度比率 | 0-1 | 预测与参考长度的相似度 |

### 高级指标 (test_advanced_robust.py)

| 指标 | 计算方式 | 适用场景 |
|------|----------|----------|
| **ROUGE-1** | 一元语法召回率 | 评估内容覆盖 |
| **ROUGE-2** | 二元语法召回率 | 评估词组匹配 |
| **ROUGE-L** | 最长公共子序列 | 评估结构相似性 |
| **BLEU-1** | 一元语法精确率 | 机器翻译标准指标 |
| **BLEU-2** | 二元语法精确率 | 评估连贯性 |
| **BLEU-3** | 三元语法精确率 | 评估流畅性 |
| **BLEU-4** | 四元语法精确率 | 综合评估 |
| **BERT F1** | 语义相似度 | 评估语义一致性 |
| **METEOR** | 基于对齐的召回率 | 考虑同义词匹配 |
| **Sentence BERT** | 句子嵌入相似度 | 整体语义相似 |

### 数据集分类

LoCoMo 数据集包含5类问题：
1. **Category 1: Multi-hop** - 多跳推理
2. **Category 2: Temporal** - 时间相关
3. **Category 3: Open-domain** - 开放领域
4. **Category 4: Single-hop** - 单跳推理
5. **Category 5: Adversarial** - 对抗性问题

## 运行完整测试的步骤

### 步骤1: 环境准备

```bash
# 确保依赖安装
pip install -r requirements.txt

# 设置OpenAI API密钥
export OPENAI_API_KEY="your-api-key"
# Windows:
# set OPENAI_API_KEY=your-api-key
```

### 步骤2: 小规模测试（验证配置）

```bash
python test_advanced_robust.py \
  --backend openai \
  --model gpt-4o-mini \
  --dataset data/locomo10.json \
  --ratio 0.01 \
  --output test_results_small.json
```

### 步骤3: 完整测试（需要较长时间）

```bash
python test_advanced_robust.py \
  --backend openai \
  --model gpt-4o-mini \
  --dataset data/locomo10.json \
  --ratio 1.0 \
  --output results_robust_gpt-4o-mini.json
```

### 步骤4: 分析结果

```bash
python analyze_results.py results_robust_gpt-4o-mini.json
```

## 常见问题解决

### 1. sentence-transformers 下载失败

如果遇到 huggingface.co 连接问题：

```bash
# 方法1: 使用离线模式（如果已有缓存）
export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1

# 方法2: 手动下载模型
# 从 https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
# 下载到 ~/.cache/huggingface/hub/
```

### 2. OpenAI API 连接问题

```bash
# 检查API密钥
echo $OPENAI_API_KEY

# 测试连接
python -c "import openai; openai.api_key='your-key'; print('Connected')"
```

### 3. 内存不足

减少测试样本数：

```bash
# 使用10%的数据
--ratio 0.1

# 或指定具体问题数
python test_simple.py --max_questions 10
```

## 自定义测试

### 创建自己的测试脚本

```python
from utils import calculate_metrics, aggregate_metrics
from load_dataset import load_locomo_dataset

# 1. 加载数据
samples = load_locomo_dataset("data/locomo10.json")

# 2. 生成预测
predictions = ["prediction1", "prediction2"]
references = ["reference1", "reference2"]

# 3. 计算指标
all_metrics = []
for pred, ref in zip(predictions, references):
    metrics = calculate_metrics(pred, ref)
    all_metrics.append(metrics)

# 4. 聚合结果
results = aggregate_metrics(all_metrics)
print(f"平均F1: {results['overall']['f1']['mean']:.4f}")
```

## 性能基准

预期结果（基于论文）：

| 模型 | F1分数 | 精确匹配 | BLEU-4 |
|------|--------|----------|--------|
| GPT-4 | ~0.85 | ~0.65 | ~0.70 |
| GPT-4o | ~0.83 | ~0.63 | ~0.68 |
| GPT-4o-mini | ~0.80 | ~0.60 | ~0.65 |
| Qwen-3B | ~0.75 | ~0.55 | ~0.60 |
| Llama-3.2-3B | ~0.72 | ~0.52 | ~0.58 |

## 后续步骤

1. **运行 k 值扫描** - 优化检索参数
   ```bash
   bash run_k_sweep.sh
   ```

2. **比较不同模型** - 使用完整测试脚本
   ```bash
   bash run_all_experiments.sh
   ```

3. **分析结果** - 创建可视化报告
   ```bash
   python plot_results.py results_robust_*.json
   ```

## 联系支持

如需进一步帮助：
  - 查看项目 README.md
  - 参考论文: [A-Mem: Agentic Memory for LLM Agents](https://arxiv.org/pdf/2502.12110)
  - 开源实现: [A-mem-sys](https://github.com/WujiangXu/A-mem-sys)