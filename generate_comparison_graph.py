import matplotlib.pyplot as plt
import numpy as np
import os
import time
from matplotlib.ticker import MaxNLocator, FuncFormatter

def create_comprehensive_comparison(data, directory):
    categories: list[str] = ['Total', 'Infantry', 'Armor', 'Artillery']
    metrics: list[str] = ['Kills', 'Deaths', 'Cmbt Eff', 'Off Pts', 'Def Pts', 'Supp Pts', 'MG Kills']
    full_metrics: list[str] = ['Kills', 'Deaths', 'CombatEffectiveness', 'OffensivePoints', 'DefensivePoints', 'SupportPoints', 'MachineGunKills']
    
    team1_name = data['Axis']['Team Name']
    team2_name = data['Allies']['Team Name']
    
    fig, axs = plt.subplots(2, 2, figsize=(20, 20))
    fig.suptitle(f'{team1_name} vs {team2_name} Comparison', fontsize=24)
    
    colors = ['#ff9999', '#66b3ff']  # Light red and light blue for better visibility
    
    def format_with_commas(x, p):
        return f"{x:,}"
    
    for idx, category in enumerate(categories):
        row = idx // 2
        col = idx % 2
        ax = axs[row, col] # type: ignore
        
        team1_data = data['Axis'][category]
        team2_data = data['Allies'][category]
        
        team1_values = [team1_data[metric] for metric in full_metrics]
        team2_values = [team2_data[metric] for metric in full_metrics]
        
        x = np.arange(len(metrics))
        width = 0.35
        
        rects1 = ax.bar(x - width/2, team1_values, width, label=team1_name, color=colors[0])
        rects2 = ax.bar(x + width/2, team2_values, width, label=team2_name, color=colors[1])
        
        ax.set_ylabel('Values', fontsize=14)
        ax.set_title(f'{category}', fontsize=18)
        ax.set_xticks(x)
        ax.set_xticklabels(metrics, rotation=45, ha='right', fontsize=12)
        ax.legend(fontsize=12)
        
        # Add gridlines
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Adjust y-axis to use appropriate scale and add comma formatting
        ax.yaxis.set_major_locator(MaxNLocator(nbins=6))
        ax.yaxis.set_major_formatter(FuncFormatter(format_with_commas))
        
        def autolabel(rects):
            for rect in rects:
                height = rect.get_height()
                ax.annotate(f'{height:,}',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom',
                            fontsize=10)
        
        autolabel(rects1)
        autolabel(rects2)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # type: ignore
    
    # Add a legend for abbreviated metrics
    fig.text(0.5, 0.01, ' | '.join([f"{short} = {full}" for short, full in zip(metrics, full_metrics)]),
             ha='center', fontsize=12, bbox=dict(facecolor='white', alpha=0.5))
    
    output_file = os.path.join(directory, f'{team1_name}_vs_{team2_name}_comparison_{int(time.time())}.png')
    plt.savefig(output_file, dpi=300)
    plt.close()
    
    return output_file