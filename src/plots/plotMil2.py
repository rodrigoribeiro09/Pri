import matplotlib
matplotlib.use("Agg")  # backend só para ficheiro, sem GUI

import matplotlib.pyplot as plt
import pandas as pd

def read_results(file_path):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 3:
                metric, qid, value = parts
                try:
                    value = float(value)
                    data.append((metric, int(qid), value))
                except ValueError:
                    print(f"Skipping invalid line: {line.strip()}")
    df = pd.DataFrame(data, columns=['metric', 'query', 'value'])
    return df


def group_by_system(df):
    # novo mapeamento:
    # 1 -> {1,6,11,16}, 2 -> {2,7,12,17}, ...
    system_map = {
        1:  'System 1', 6:  'System 1', 11: 'System 1', 16: 'System 1',
        2:  'System 2', 7:  'System 2', 12: 'System 2', 17: 'System 2',
        3:  'System 3', 8:  'System 3', 13: 'System 3', 18: 'System 3',
        4:  'System 4', 9:  'System 4', 14: 'System 4', 19: 'System 4',
        5:  'System 5', 10: 'System 5', 15: 'System 5', 20: 'System 5',
    }
    df['system'] = df['query'].map(system_map)
    # opcional: filtrar fora queries que não pertençam a nenhum sistema
    df = df[df['system'].notna()]
    return df


def compute_metrics(df):
    metrics_of_interest = ['recall_10', 'recall_20', 'map', 'Rprec']
    df_filtered = df[df['metric'].isin(metrics_of_interest)]
    metrics = df_filtered.groupby(['system', 'metric'])['value'].mean().unstack()
    return metrics


def plot_metrics(metrics):
    metrics.plot(kind='bar', figsize=(10, 6))
    plt.title("Comparison of Metrics by System")
    plt.ylabel("Average Value")
    plt.xticks(rotation=0)
    plt.ylim(0, 1)
    plt.legend(title="Metrics")
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig("results/metric_comparison.png")


file_path = 'results/trec_eval_output.txt'

df = read_results(file_path)
df = group_by_system(df)
metrics = compute_metrics(df)
print(metrics)
plot_metrics(metrics)
