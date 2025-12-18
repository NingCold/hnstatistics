from collections import Counter

def count_frequencies(text: str) -> dict:
    """
    统计频率
    """
    items = text.split()
    return dict(Counter(items))

def calculate_probability(freq: dict) -> dict:
    """
    计算概率
    """
    total = sum(freq.values())
    if total == 0:
        return {}
    return {k: v / total for k, v in freq.items()}