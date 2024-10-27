import matplotlib.pyplot as plt
import numpy as np
import os
import time
from matplotlib.ticker import MaxNLocator, FuncFormatter, ScalarFormatter
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.pyplot import subplot
from typing import List, Dict, Any, Union, Tuple, cast

def sanitize_filename(text: str) -> str:
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        text = text.replace(char, '_')
    return text.strip()

def format_with_commas(x: float, p: Any) -> str:
    if x >= 1000:
        return f"{x:,.0f}"
    elif x >= 100:
        return f"{x:.0f}"
    elif x >= 1:
        return f"{x:.1f}"
    return f"{x:.2f}"

def create_subplot(ax: Any, data: Dict[str, Any], category: str, team1_name: str, team2_name: str,
                  metrics: List[str], full_metrics: List[str], colors: List[str]) -> None:
    """Create a single subplot with improved formatting and readability."""
    team1_data = data['Axis'][category]
    team2_data = data['Allies'][category]
    
    team1_values = [team1_data[metric] for metric in full_metrics]
    team2_values = [team2_data[metric] for metric in full_metrics]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    # Split metrics into two groups based on typical value ranges
    high_value_metrics = ['OffensivePoints', 'DefensivePoints', 'SupportPoints']
    low_value_metrics = ['Kills', 'Deaths', 'CombatEffectiveness', 'MachineGunKills']
    
    # Create two separate y-axes
    ax1 = ax
    ax2 = ax1.twinx()
    
    # Plot bars on appropriate axes
    for i, (metric, t1_val, t2_val) in enumerate(zip(full_metrics, team1_values, team2_values)):
        if metric in high_value_metrics:
            ax_to_use = ax2
            alpha = 0.7  # Slightly transparent for high-value bars
        else:
            ax_to_use = ax1
            alpha = 1.0  # Solid for low-value bars
            
        ax_to_use.bar(x[i] - width/2, t1_val, width, color=colors[0], alpha=alpha,
                     label=f"{team1_name} ({metric})" if i == 0 else "")
        ax_to_use.bar(x[i] + width/2, t2_val, width, color=colors[1], alpha=alpha,
                     label=f"{team2_name} ({metric})" if i == 0 else "")

    # Configure primary y-axis (low values)
    ax1.set_ylabel('Kills/Deaths/Combat Effectiveness', color='white', fontsize=10)
    ax1.tick_params(axis='y', labelcolor='white')
    ax1.yaxis.set_major_formatter(FuncFormatter(format_with_commas))
    
    # Configure secondary y-axis (high values)
    ax2.set_ylabel('Points', color='white', fontsize=10)
    ax2.tick_params(axis='y', labelcolor='white')
    ax2.yaxis.set_major_formatter(FuncFormatter(format_with_commas))
    
    # Set up x-axis
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics, rotation=45, ha='right', fontsize=10, color='white')
    
    # Add gridlines
    ax1.grid(True, linestyle='--', alpha=0.2, color='gray')
    
    # Set title and adjust appearance
    ax1.set_title(f'{category}', fontsize=14, color='white', pad=20)
    
    # Add value labels on bars
    for ax_to_use in [ax1, ax2]:
        for container in ax_to_use.containers:
            ax_to_use.bar_label(container, padding=3, fmt=format_with_commas,
                              fontsize=8, color='white')

def create_comprehensive_comparison(data: Dict[str, Any], directory: str) -> str:
    plt.style.use('dark_background')
    
    # Setup
    categories: List[str] = ['Total', 'Infantry', 'Armor', 'Artillery']
    metrics: List[str] = ['Kills', 'Deaths', 'Cmbt Eff', 'Off Pts', 'Def Pts', 'Supp Pts', 'MG Kills']
    full_metrics: List[str] = ['Kills', 'Deaths', 'CombatEffectiveness', 
                              'OffensivePoints', 'DefensivePoints', 'SupportPoints', 'MachineGunKills']
    
    team1_name_display = data['Axis']['Team Name']
    team2_name_display = data['Allies']['Team Name']
    team1_name_safe = sanitize_filename(team1_name_display)
    team2_name_safe = sanitize_filename(team2_name_display)
    
    # Create figure with subplots
    fig, axs = plt.subplots(2, 2, figsize=(20, 20))
    fig.suptitle(f'{team1_name_display} vs {team2_name_display} Comparison', 
                fontsize=24, color='white', y=0.95)
    
    # Define colors with better contrast
    colors = ['#ff6b6b', '#4dabf7']  # Vibrant red and blue
    
    # Create each subplot
    for idx, category in enumerate(categories):
        row = idx // 2
        col = idx % 2
        create_subplot(axs[row, col], data, category, team1_name_display,  # type: ignore
                      team2_name_display, metrics, full_metrics, colors)
    
    # Add legend for metric abbreviations
    legend_text = ' | '.join([f"{short} = {full}" for short, full in zip(metrics, full_metrics)])
    fig.text(0.5, 0.02, legend_text, ha='center', fontsize=10, color='white',
             bbox=dict(facecolor='#333333', edgecolor='none', alpha=0.8))
    
    # Adjust layout and save
    plt.tight_layout(rect=(0, 0.04, 1, 0.94))
    
    timestamp = int(time.time())
    output_file = os.path.join(directory, 
                              f'match_comparison_{team1_name_safe}_vs_{team2_name_safe}_{timestamp}.png')
    plt.savefig(output_file, dpi=300, facecolor='#1c1c1c', edgecolor='none', bbox_inches='tight')
    plt.close()
    
    return output_file