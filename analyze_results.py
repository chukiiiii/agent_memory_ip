#!/usr/bin/env python3
"""
分析测试结果文件的脚本
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List
import statistics

def load_results(filepath: str) -> Dict:
    """加载结果文件"""
    with open(filepath, 'r') as f:
        return json.load(f)

def print_summary(results: Dict, filename: str = ""):
    """打印结果摘要"""
    if filename:
        print(f"\n=== 分析结果: {filename} ===")

    print(f"模型: {results.get('model', '未知')}")
    print(f"总问题数: {results.get('total_questions', 0)}")

    if 'category_distribution' in results:
        print("\n问题类别分布:")
        for cat, count in sorted(results['category_distribution'].items()):
            print(f"  类别 {cat}: {count} 个问题")

    if 'aggregate_metrics' in results:
        agg = results['aggregate_metrics']

        print("\n=== 整体指标 ===")
        overall = agg.get('overall', {})
        for metric_name, stats in overall.items():
            if 'mean' in stats:
                print(f"{metric_name:20} 均值: {stats['mean']:.4f} ± {stats['std']:.4f}")

        # 按类别打印
        print("\n=== 按类别指标 ===")
        for key in sorted(agg.keys()):
            if key.startswith('category_'):
                cat = key.replace('category_', '')
                print(f"\n类别 {cat}:")
                for metric_name, stats in agg[key].items():
                    if 'mean' in stats:
                        print(f"  {metric_name}: {stats['mean']:.4f}")

def compare_results(result_files: List[str]):
    """比较多个结果文件"""
    print("=== 模型性能比较 ===")
    print(f"{'模型':<30} {'F1':>8} {'Exact Match':>12} {'BLEU-4':>8} {'ROUGE-1':>8}")
    print("=" * 70)

    comparisons = []

    for filepath in result_files:
        try:
            results = load_results(filepath)
            model = results.get('model', Path(filepath).stem)
            agg = results.get('aggregate_metrics', {})
            overall = agg.get('overall', {})

            f1 = overall.get('f1', {}).get('mean', 0)
            exact = overall.get('exact_match', {}).get('mean', 0)
            bleu4 = overall.get('bleu4', {}).get('mean', 0)
            rouge1 = overall.get('rouge1_f', {}).get('mean', 0)

            comparisons.append({
                'model': model,
                'f1': f1,
                'exact_match': exact,
                'bleu4': bleu4,
                'rouge1': rouge1,
                'file': filepath
            })

            print(f"{model:<30} {f1:>8.4f} {exact:>12.4f} {bleu4:>8.4f} {rouge1:>8.4f}")

        except Exception as e:
            print(f"错误加载 {filepath}: {e}")

    return comparisons

def print_detailed_metrics(results: Dict):
    """打印详细指标解释"""
    print("\n=== 指标解释 ===")
    metrics_info = {
        'exact_match': '完全匹配（1表示完全相同，0表示不同）',
        'f1': 'F1分数（精确率和召回率的调和平均）',
        'rouge1_f': 'ROUGE-1 F1分数（一元语法召回率）',
        'rouge2_f': 'ROUGE-2 F1分数（二元语法召回率）',
        'rougeL_f': 'ROUGE-L F1分数（最长公共子序列）',
        'bleu1': 'BLEU-1（一元语法精确率）',
        'bleu2': 'BLEU-2（二元语法精确率）',
        'bleu3': 'BLEU-3（三元语法精确率）',
        'bleu4': 'BLEU-4（四元语法精确率）',
        'bert_f1': 'BERT F1分数（语义相似度）',
        'meteor': 'METEOR分数（基于对齐的召回率）',
        'sbert_similarity': 'Sentence BERT相似度（句子嵌入）'
    }

    overall = results.get('aggregate_metrics', {}).get('overall', {})

    for metric_name, description in metrics_info.items():
        if metric_name in overall:
            stats = overall[metric_name]
            if 'mean' in stats:
                print(f"{metric_name:20} {description}")
                print(f"                   均值: {stats['mean']:.4f} (范围: {stats['min']:.4f}-{stats['max']:.4f})")

def export_to_csv(result_files: List[str], output_file: str = "results_comparison.csv"):
    """导出为CSV格式"""
    import csv

    comparisons = compare_results(result_files)

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Model', 'F1', 'Exact_Match', 'BLEU4', 'ROUGE1', 'Questions'])

        for comp in comparisons:
            # 从文件中获取总问题数
            try:
                results = load_results(comp['file'])
                total_questions = results.get('total_questions', 0)
            except:
                total_questions = 0

            writer.writerow([
                comp['model'],
                f"{comp['f1']:.4f}",
                f"{comp['exact_match']:.4f}",
                f"{comp['bleu4']:.4f}",
                f"{comp['rouge1']:.4f}",
                total_questions
            ])

    print(f"\n结果已导出到: {output_file}")

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="分析A-Mem测试结果")
    parser.add_argument("files", nargs="+", help="结果文件路径")
    parser.add_argument("--compare", action="store_true", help="比较多个结果文件")
    parser.add_argument("--export", metavar="CSV_FILE", help="导出为CSV文件")
    parser.add_argument("--detailed", action="store_true", help="显示详细指标解释")

    args = parser.parse_args()

    # 检查文件是否存在
    valid_files = []
    for filepath in args.files:
        if os.path.exists(filepath):
            valid_files.append(filepath)
        else:
            print(f"警告：文件不存在: {filepath}")

    if not valid_files:
        print("错误：没有有效的输入文件")
        sys.exit(1)

    if args.compare or len(valid_files) > 1:
        comparisons = compare_results(valid_files)

        if args.export:
            export_to_csv(valid_files, args.export)
    else:
        # 单个文件分析
        for filepath in valid_files:
            try:
                results = load_results(filepath)
                print_summary(results, os.path.basename(filepath))

                if args.detailed:
                    print_detailed_metrics(results)

            except Exception as e:
                print(f"错误分析 {filepath}: {e}")

if __name__ == "__main__":
    main()