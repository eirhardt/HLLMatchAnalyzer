import matplotlib.pyplot as plt
import numpy as np
import os
import time

def create_comprehensive_comparison(data, directory):
    categories: list[str] = ['Total', 'Infantry', 'Armor', 'Artillery']
    metrics: list[str] = ['Kills', 'Deaths', 'CombatEffectiveness', 'OffensivePoints', 'DefensivePoints', 'SupportPoints']

    # Extract team names
    team1_name = data['Axis']['Team Name']
    team2_name = data['Allies']['Team Name']

    fig, axs = plt.subplots(2, 2, figsize=(20, 20))
    fig.suptitle(f'{team1_name} vs {team2_name} Comprehensive Comparison', fontsize=16)

    for idx, category in enumerate(categories):
        row: int = idx // 2
        col: int = idx % 2
        ax = axs[row, col]  # type: ignore
        
        team1_data = data['Axis'][category]
        team2_data = data['Allies'][category]

        team1_values = [team1_data[metric] for metric in metrics]
        team2_values = [team2_data[metric] for metric in metrics]

        x = np.arange(len(metrics))
        width = 0.35

        rects1 = ax.bar(x - width/2, team1_values, width, label=team1_name, color='red', alpha=0.7)
        rects2 = ax.bar(x + width/2, team2_values, width, label=team2_name, color='blue', alpha=0.7)

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
    output_file: str = os.path.join(directory, f'{team1_name}_vs_{team2_name}_comparison_{int(time.time())}.png')
    plt.savefig(output_file, dpi=300)
    plt.close()
    
    return output_file  # Return the path of the saved file
