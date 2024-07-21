import time
import matplotlib.pyplot as plt
import numpy as np
import os

def create_comprehensive_comparison(data, directory):
    categories: list[str] = ['Total', 'Infantry', 'Armor', 'Artillery']
    metrics: list[str] = ['Kills', 'Deaths', 'CombatEffectiveness', 'OffensivePoints', 'DefensivePoints', 'SupportPoints']

    fig, axs = plt.subplots(2, 2, figsize=(20, 20))
    fig.suptitle('Axis vs Allies Comprehensive Comparison', fontsize=16)

    for idx, category in enumerate(categories):
        row = idx // 2
        col = idx % 2
        ax = axs[row, col] # type: ignore
        
        axis_data = data['Axis'][category]
        allies_data = data['Allies'][category]

        axis_values = [axis_data[metric] for metric in metrics]
        allies_values = [allies_data[metric] for metric in metrics]

        x = np.arange(len(metrics))
        width = 0.35

        rects1 = ax.bar(x - width/2, axis_values, width, label='Axis', color='red', alpha=0.7)
        rects2 = ax.bar(x + width/2, allies_values, width, label='Allies', color='blue', alpha=0.7)

        ax.set_ylabel('Values')
        ax.set_title(f'{category} Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics, rotation=45, ha='right')
        ax.legend()

        def autolabel(rects):
            for rect in rects:
                height = rect.get_height()
                ax.annotate(f'{height}',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom', rotation=90)

        autolabel(rects1)
        autolabel(rects2)

    plt.tight_layout()
    output_file: str = os.path.join(directory, f'axis_vs_allies_comprehensive_comparison_{int(time.time())}.png')
    plt.savefig(output_file, dpi=300)
    plt.close()
    
    return output_file  # Return the path of the saved file
