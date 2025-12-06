import pandas as pd
import matplotlib.pyplot as plt

def read_results(file_path):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 3:
                metric, qid, value = parts
                try:
                    value = float(value)  # Try converting to float
                    data.append((metric, int(qid), value))
                except ValueError:
                    # Skip invalid values
                    print(f"Skipping invalid line: {line.strip()}")
    df = pd.DataFrame(data, columns=['metric', 'query', 'value'])
    return df


def group_by_system(df):
    system_map = {
        1: 'System 1', 4: 'System 1', 7: 'System 1', 10: 'System 1',
        2: 'System 2', 5: 'System 2', 8: 'System 2', 11: 'System 2',
        3: 'System 3', 6: 'System 3', 9: 'System 3', 12: 'System 3'
    }
    df['system'] = df['query'].map(system_map)
    return df

def compute_metrics(df):
    metrics_of_interest = ['recall_10', 'recall_20', 'map', 'Rprec']
    df_filtered = df[df['metric'].isin(metrics_of_interest)]
    metrics = df_filtered.groupby(['system', 'metric'])['value'].mean().unstack()
    return metrics

def plot_metrics(metrics):
    metrics.plot(kind='bar', figsize=(10,6))
    plt.title("Comparison of Metrics by System")
    plt.ylabel("Average Value")
    plt.xticks(rotation=0)
    plt.ylim(0,1)
    plt.legend(title="MMetrics")
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig("results/metric_comparison.png")

file_path = 'results/trec_eval_output.txt'

# Execução
df = read_results(file_path)
df = group_by_system(df)
metrics = compute_metrics(df)
print(metrics)
plot_metrics(metrics)
