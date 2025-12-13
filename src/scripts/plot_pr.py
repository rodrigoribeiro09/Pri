import sys
import matplotlib.pyplot as plt
import numpy as np

GROUP_RANGES = [(1, 5), (6, 10), (11, 15), (16, 20)]

def main(trec_eval_stdout: list[str]):
    results = {x: {} for x in set([x.split()[1] for x in trec_eval_stdout])}

    for metric in trec_eval_stdout:
        (name, query_id, value) = metric.split()
        results[query_id][name] = value

    if "all" in results:
        del results["all"]

    # IDs presentes no trec_eval (como strings)
    available_qids = set(results.keys())

    for qmin, qmax in GROUP_RANGES:
        # constroi a lista de qids deste intervalo que existem de facto
        group_qids = [str(q) for q in range(qmin, qmax + 1) if str(q) in available_qids]
        if not group_qids:
            continue  # nada para este grupo

        plt.figure()

        for query_id in group_qids:
            metrics = results[query_id]

            recall = np.arange(0, 1.1, 0.1)
            pr_keys = [f"iprec_at_recall_{k:.2f}" for k in recall]
            iprecision = np.array([float(metrics[k]) for k in pr_keys])

            ap_score = float(metrics["map"])
            p_20 = float(metrics["P_20"])
            auc_score = float(metrics["11pt_avg"])

            line_kwargs = {
                "drawstyle": "steps-post",
                "label": f"Q{query_id}: AP={ap_score:.3f}, AUC={auc_score:.3f}, P@20={p_20:.3f}",
                "linewidth": 2,
                "markersize": 10,
            }

            plt.plot(recall, iprecision, **line_kwargs)

        plt.title(f"Precision-Recall Curve (Q{qmin}–Q{qmax})")

        axis_kwargs = {
            "fontsize": 9,
            "verticalalignment": "baseline",
            "style": "italic",
        }

        plt.xlabel("Recall", fontdict=axis_kwargs)
        plt.ylabel("Precision", fontdict=axis_kwargs)
        plt.xlim(-0.005, 1.005)
        plt.ylim(-0.005, 1.005)
        plt.legend(loc="upper right", prop={"size": 10})
        plt.grid(True, linestyle="--", linewidth=0.5)
        plt.tight_layout()

        output_file = f"results/pr_curve_q{qmin}-q{qmax}.png"
        plt.savefig(output_file)
        print(f"✅ PR curve saved to {output_file}")

if __name__ == "__main__":
    trec_eval_stdout = sys.stdin.readlines()
    main(trec_eval_stdout)
