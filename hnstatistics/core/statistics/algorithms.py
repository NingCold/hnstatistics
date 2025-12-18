from collections import Counter

from hnstatistics.core.statistics.analyze_options import AnalyzeOptions

def count_frequencies(text: str, options: AnalyzeOptions) -> dict:
    """
    统计频率
    """
    items = text.split()
    if options.enable_star:
        result = {}
        for item in list(items):
            base, count = parse_text_with_star(item)
            result[base] = result.get(base, 0) + count
        return result
    else:
        return dict(Counter(items))

def calculate_probability(freq: dict) -> dict:
    """
    计算概率
    """
    total = sum(freq.values())
    if total == 0:
        return {}
    return {k: v / total for k, v in freq.items()}

def parse_text_with_star(text: str) -> tuple[str, int]:
    """
    根据分析选项预处理文本
    """
    if '*' not in text:
        return text, 1

    base, _, count = text.rpartition('*')
    base = base.strip()
    if not base:
        return text, 1
    count = count.strip()
    if not count:
        return base, 1
    if not count.isdigit():
        return text, 1
    count = int(count)
    if count <= 0:
        return text, 1
    return base, count