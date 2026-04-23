#!/usr/bin/env python3
"""
简单的测试脚本 - 验证指标计算并提供量化结果
不需要LLM API或模型下载
"""

import sys
import os
import json
import statistics
from collections import defaultdict
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from load_dataset import load_locomo_dataset
    DATASET_AVAILABLE = True
except ImportError:
    DATASET_AVAILABLE = False
    print("警告：无法导入load_dataset，将使用模拟数据")

def simple_tokenize(text):
    """简单的分词函数，避免外部依赖"""
    text = str(text)
    return text.lower().replace('.', ' ').replace(',', ' ').replace('!', ' ').replace('?', ' ').split()

def calculate_basic_metrics(prediction: str, reference: str) -> dict:
    """计算基本指标（不依赖外部库）"""
    if not prediction or not reference:
        return {
            "exact_match": 0,
            "f1": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "avg_length_ratio": 0.0,
            "token_overlap": 0.0
        }

    prediction = str(prediction).strip()
    reference = str(reference).strip()

    # 精确匹配
    exact_match = int(prediction.lower() == reference.lower())

    # 基于token的F1分数
    pred_tokens = set(simple_tokenize(prediction))
    ref_tokens = set(simple_tokenize(reference))
    common_tokens = pred_tokens & ref_tokens

    precision = 0.0
    recall = 0.0
    f1 = 0.0

    if pred_tokens and ref_tokens:
        precision = len(common_tokens) / len(pred_tokens)
        recall = len(common_tokens) / len(ref_tokens)
        if (precision + recall) > 0:
            f1 = 2 * precision * recall / (precision + recall)

    # 长度比率
    pred_len = len(prediction.split())
    ref_len = len(reference.split())
    if ref_len > 0:
        length_ratio = min(pred_len, ref_len) / max(pred_len, ref_len)
    else:
        length_ratio = 0.0

    # Token重叠比率
    token_overlap = len(common_tokens) / len(ref_tokens) if ref_tokens else 0.0

    return {
        "exact_match": exact_match,
        "f1": f1,
        "precision": precision,
        "recall": recall,
        "avg_length_ratio": length_ratio,
        "token_overlap": token_overlap,
        "pred_tokens": len(pred_tokens),
        "ref_tokens": len(ref_tokens),
        "common_tokens": len(common_tokens)
    }

def aggregate_basic_metrics(all_metrics, all_categories=None):
    """聚合基本指标"""
    if not all_metrics:
        return {}

    aggregates = defaultdict(list)

    for metrics in all_metrics:
        for metric_name, value in metrics.items():
            if isinstance(value, (int, float)):
                aggregates[metric_name].append(value)

    results = {"overall": {}}

    for metric_name, values in aggregates.items():
        if not values:
            continue

        results["overall"][metric_name] = {
            'mean': statistics.mean(values),
            'std': statistics.stdev(values) if len(values) > 1 else 0.0,
            'median': statistics.median(values),
            'min': min(values),
            'max': max(values),
            'count': len(values)
        }

    return results

def generate_mock_predictions(samples, max_questions=10):
    """生成模拟预测（用于演示）"""
    all_metrics = []
    all_categories = []

    print(f"将评估最多 {max_questions} 个问题...")

    question_count = 0
    for sample_idx, sample in enumerate(samples):
        if question_count >= max_questions:
            break

        # 对每个问题生成模拟预测
        for qa in sample.qa:
            if question_count >= max_questions:
                break

            # 简单的模拟预测：引用答案的修改版本
            reference = qa.final_answer if qa.final_answer else ""
            reference = str(reference)  # 确保是字符串

            if reference and reference != "None" and reference.lower() != "none":
                # 模拟一些变化：80%时间返回正确答案，20%时间返回错误答案
                import random
                if random.random() < 0.8:
                    # 正确但可能有细微变化
                    prediction = reference
                    # 偶尔添加/删除单词
                    if random.random() < 0.3:
                        words = prediction.split()
                        if len(words) > 2 and random.random() < 0.5:
                            words.pop(random.randint(0, len(words)-1))
                            prediction = " ".join(words)
                else:
                    # 错误答案
                    prediction = "Not mentioned in the conversation"
            else:
                prediction = "No answer available"
                reference = ""  # 确保为空字符串

            # 计算指标
            metrics = calculate_basic_metrics(prediction, reference)
            all_metrics.append(metrics)
            all_categories.append(qa.category)

            question_count += 1

            # 打印一些示例
            if question_count <= 3:
                print(f"\n示例 {question_count}:")
                print(f"  问题: {qa.question[:80]}...")
                print(f"  预测: {str(prediction)[:80]}...")
                print(f"  参考答案: {str(reference)[:80]}...")
                print(f"  F1分数: {metrics['f1']:.4f}")
                print(f"  精确匹配: {metrics['exact_match']}")

    return all_metrics, all_categories

def run_test_on_dataset(dataset_path, max_samples=2, max_questions=10):
    """在数据集上运行测试"""
    if not DATASET_AVAILABLE:
        print("错误：无法加载数据集")
        return None

    if not os.path.exists(dataset_path):
        print(f"错误：数据集文件不存在: {dataset_path}")
        return None

    print(f"加载数据集: {dataset_path}")
    samples = load_locomo_dataset(dataset_path)

    # 限制样本数量
    samples = samples[:max_samples]
    print(f"使用 {len(samples)} 个样本（每个样本最多 {max_questions//len(samples) if samples else 0} 个问题）")

    # 生成模拟预测
    all_metrics, all_categories = generate_mock_predictions(samples, max_questions)

    # 聚合指标
    aggregate_results = aggregate_basic_metrics(all_metrics, all_categories)

    # 计算综合分数
    if all_metrics:
        avg_f1 = statistics.mean([m['f1'] for m in all_metrics])
        avg_exact_match = statistics.mean([m['exact_match'] for m in all_metrics])
        avg_precision = statistics.mean([m['precision'] for m in all_metrics])
        avg_recall = statistics.mean([m['recall'] for m in all_metrics])

        # 综合分数：F1权重最高
        composite_score = (0.5 * avg_f1 + 0.2 * avg_exact_match +
                          0.15 * avg_precision + 0.15 * avg_recall)
    else:
        avg_f1 = avg_exact_match = avg_precision = avg_recall = composite_score = 0.0

    results = {
        "total_questions": len(all_metrics),
        "average_f1": avg_f1,
        "average_exact_match": avg_exact_match,
        "average_precision": avg_precision,
        "average_recall": avg_recall,
        "composite_score": composite_score,
        "aggregate_metrics": aggregate_results
    }

    return results

def main():
    """主函数"""
    print("=" * 70)
    print("A-Mem 项目简单测试套件")
    print("=" * 70)
    print("\n这个测试演示了量化指标的生成，使用模拟预测。")
    print("要运行完整测试，请使用 test_advanced.py 或 test_advanced_robust.py。\n")

    # 测试数据集路径
    dataset_path = os.path.join(os.path.dirname(__file__), "data", "locomo10.json")

    if os.path.exists(dataset_path):
        # 运行测试
        results = run_test_on_dataset(dataset_path, max_samples=1, max_questions=5)

        if results:
            print("\n" + "=" * 70)
            print("量化测试指标")
            print("=" * 70)

            print(f"\n总问题数: {results['total_questions']}")
            print(f"平均F1分数: {results['average_f1']:.4f}")
            print(f"平均精确匹配: {results['average_exact_match']:.4f}")
            print(f"平均精确率: {results['average_precision']:.4f}")
            print(f"平均召回率: {results['average_recall']:.4f}")
            print(f"综合评分: {results['composite_score']:.4f}")

            print("\n详细指标统计:")
            if 'aggregate_metrics' in results:
                for metric_name, stats in results['aggregate_metrics'].get('overall', {}).items():
                    if 'mean' in stats:
                        print(f"  {metric_name}: {stats['mean']:.4f} ± {stats['std']:.4f}")

            print("\n" + "=" * 70)
            print("指标解释:")
            print("=" * 70)
            print("1. F1分数: 精确率和召回率的调和平均（0-1，越高越好）")
            print("2. 精确匹配: 预测与参考答案完全一致的比例")
            print("3. 精确率: 预测中相关token的比例")
            print("4. 召回率: 参考答案中被正确预测的token比例")
            print("5. 综合评分: 加权平均指标（F1权重50%）")
            print("\n要获得更全面的指标（ROUGE、BLEU、BERT等），请运行完整测试:")
            print("  python test_advanced_robust.py --ratio 0.1 --backend openai --model gpt-4o-mini")
    else:
        print(f"数据集未找到: {dataset_path}")
        print("请确保已下载数据集到 data/locomo10.json")

    print("\n" + "=" * 70)
    print("现有完整测试脚本:")
    print("=" * 70)
    print("\n1. test_advanced.py - 原始测试（需要OpenAI JSON schema支持）")
    print("   用法: python test_advanced.py --model gpt-4o-mini --ratio 0.1")
    print("\n2. test_advanced_robust.py - 增强版测试（支持多种后端）")
    print("   用法: python test_advanced_robust.py --backend openai --model gpt-4o-mini --ratio 0.1")
    print("\n3. 运行k值扫描（优化检索参数）:")
    print("   bash run_k_sweep.sh")
    print("\n4. 运行所有实验（需要GPU和API密钥）:")
    print("   bash run_all_experiments.sh")

if __name__ == "__main__":
    main()