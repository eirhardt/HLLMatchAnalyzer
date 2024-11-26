import matplotlib.pyplot as plt
import numpy as np
import os
import time
from matplotlib.ticker import MaxNLocator, FuncFormatter, ScalarFormatter
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.pyplot import subplot
from typing import List, Dict, Any, Union, Tuple, cast
from weapon_data import WeaponData

def sanitize_filename(text: str) -> str:
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        text = text.replace(char, '_')
    return text.strip()

def format_with_commas(x: float, p: Any) -> str:
    """
    Format number with commas and appropriate decimal places
    x: the number to format
    p: the position (unused, required by matplotlib)
    """
    if x >= 1000:
        return f"{x:,.0f}"
    elif x >= 100:
        return f"{x:.0f}"
    elif x >= 1:
        return f"{x:.1f}"
    return f"{x:.2f}"

def analyze_mg_deaths(data: Dict[str, Any]) -> Tuple[Dict[str, int], Dict[str, int]]:
    """Analyze MG player deaths for both teams."""
    # Initialize death categories for both teams
    death_categories = ['Small Arms', 'Sniper', 'Tank', 'Artillery', 'Explosives']
    
    mg_deaths = {
        'Axis': dict.fromkeys(death_categories, 0),
        'Allies': dict.fromkeys(death_categories, 0)
    }
    
    def categorize_weapon(weapon: str) -> str:
        """Categorize weapon into death source category."""
        weapon_upper = weapon.upper()
        
        # Artillery weapons
        if any(artillery in weapon_upper for artillery in ['HOWITZER', '155MM', '150MM', '122MM']):
            return 'Artillery'
            
        # Tank weapons
        elif any(tank in weapon_upper for tank in ['SHERMAN', 'TIGER', 'PANZER', 'T34', 'CHURCHILL', 'STUART', 
                                                 'LUCHS', 'PUMA', 'CANNON', 'MM GUN', 'KWK']):
            return 'Tank'
            
        # Sniper weapons
        elif any(sniper in weapon_upper for sniper in ['SCOPED', 'SNIPER', 'X8', 'X4']):
            return 'Sniper'
            
        # Explosive weapons
        elif any(explosive in weapon_upper for explosive in ['GRENADE', 'MINE', 'PANZERSCHRECK', 'BAZOOKA', 
                                                          'STIELHANDGRANATE', 'DYNAMITE', 'TNT']):
            return 'Explosives'
            
        # Default to small arms
        else:
            return 'Small Arms'

    def is_mg_player(weapons: Dict[str, int]) -> bool:
        """Determine if a player is primarily an MG player."""
        if not weapons:  # Handle empty weapons dict
            return False
            
        total_kills = sum(weapons.values())
        if total_kills == 0:
            return False
            
        mg_kills = sum(count for weapon, count in weapons.items() 
                      if weapon in WeaponData.MACHINE_GUNS)
        return (mg_kills / total_kills * 100) >= 50.0

    # Process each team's data
    for side in ['Axis', 'Allies']:
        if side not in data:  # Skip if team data is missing
            continue
            
        for group in ['Infantry', 'Artillery', 'Armor']:
            if group not in data[side]:  # Skip if group data is missing
                continue
                
            if 'Players' not in data[side][group]:  # Skip if player data is missing
                continue
                
            for player in data[side][group]['Players']:
                if not is_mg_player(player.get('Weapons', {})):
                    continue
                    
                # Process death sources
                for weapon, count in player.get('DeathByWeapons', {}).items():
                    if not isinstance(count, (int, float)):  # Skip invalid count data
                        continue
                        
                    category = categorize_weapon(weapon)
                    mg_deaths[side][category] += int(count)  # Explicitly convert to int

    return mg_deaths['Axis'], mg_deaths['Allies']

def create_mg_death_subplot(ax: Any, axis_deaths: Dict[str, int], allies_deaths: Dict[str, int],
                          team1_name: str, team2_name: str, colors: List[str]) -> None:
    """Create subplot showing MG player death sources."""
    categories = list(axis_deaths.keys())
    x = np.arange(len(categories))
    width = 0.35
    
    # Convert death counts to percentages
    axis_total = sum(axis_deaths.values()) or 1  # Avoid division by zero
    allies_total = sum(allies_deaths.values()) or 1
    
    axis_percentages = [axis_deaths[cat] / axis_total * 100 for cat in categories]
    allies_percentages = [allies_deaths[cat] / allies_total * 100 for cat in categories]
    
    # Create bars
    ax.bar(x - width/2, axis_percentages, width, label=team1_name, color=colors[0])
    ax.bar(x + width/2, allies_percentages, width, label=team2_name, color=colors[1])
    
    # Customize the subplot
    ax.set_ylabel('Percentage of Deaths', color='white', fontsize=10)
    ax.set_title('MG Player Death Sources', color='white', fontsize=14, pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha='right', fontsize=10, color='white')
    
    # Add percentage labels on bars
    for i, v in enumerate(axis_percentages):
        ax.text(i - width/2, v, f'{v:.1f}%', color='white', ha='center', va='bottom', fontsize=8)
    for i, v in enumerate(allies_percentages):
        ax.text(i + width/2, v, f'{v:.1f}%', color='white', ha='center', va='bottom', fontsize=8)
    
    ax.legend(loc='upper right', framealpha=0.8, facecolor='#333333', edgecolor='none')
    ax.grid(True, linestyle='--', alpha=0.2, color='gray')
    ax.tick_params(axis='y', colors='white')

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
    
    # Create empty lists to store bar containers for legend
    team1_bars = []
    team2_bars = []
    
    # Plot bars on appropriate axes
    for i, (metric, t1_val, t2_val) in enumerate(zip(full_metrics, team1_values, team2_values)):
        if metric in high_value_metrics:
            ax_to_use = ax2
            alpha = 0.7  # Slightly transparent for high-value bars
        else:
            ax_to_use = ax1
            alpha = 1.0  # Solid for low-value bars
            
        t1_bar = ax_to_use.bar(x[i] - width/2, t1_val, width, color=colors[0], alpha=alpha)
        t2_bar = ax_to_use.bar(x[i] + width/2, t2_val, width, color=colors[1], alpha=alpha)
        
        if i == 0:  # Only store one set of bars for the legend
            team1_bars.append(t1_bar)
            team2_bars.append(t2_bar)

    # Configure primary y-axis (low values)
    ax1.set_ylabel('Kills/Deaths/Combat Effectiveness', color='white', fontsize=10)
    ax1.tick_params(axis='y', labelcolor='white')
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: format_with_commas(x, p)))
    
    # Configure secondary y-axis (high values)
    ax2.set_ylabel('Points', color='white', fontsize=10)
    ax2.tick_params(axis='y', labelcolor='white')
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: format_with_commas(x, p)))
    
    # Set up x-axis
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics, rotation=45, ha='right', fontsize=10, color='white')
    
    # Add gridlines
    ax1.grid(True, linestyle='--', alpha=0.2, color='gray')
    
    # Set title and adjust appearance
    ax1.set_title(f'{category}', fontsize=14, color='white', pad=20)
    
    # Add value labels on bars with proper formatting
    def label_formatter(value: float) -> str:
        return format_with_commas(value, None)
    
    for ax_to_use in [ax1, ax2]:
        for container in ax_to_use.containers:
            ax_to_use.bar_label(container, padding=3, fmt=label_formatter,
                              fontsize=8, color='white')
    
    # Add legend using the first set of bars
    ax1.legend([team1_bars[0], team2_bars[0]], [team1_name, team2_name],
               loc='upper right', framealpha=0.8, facecolor='#333333', edgecolor='none')
    
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
    
    # Create figure with subplots (3x2 grid now)
    fig = plt.figure(figsize=(20, 24))
    gs = fig.add_gridspec(3, 2, height_ratios=[2, 2, 1])
    
    # Define colors with better contrast
    colors = ['#ff6b6b', '#4dabf7']  # Vibrant red and blue
    
    # Create original subplots
    for idx, category in enumerate(categories):
        ax = fig.add_subplot(gs[idx // 2, idx % 2])
        create_subplot(ax, data, category, team1_name_display,
                      team2_name_display, metrics, full_metrics, colors)
    
    # Add MG death analysis subplot
    axis_deaths, allies_deaths = analyze_mg_deaths(data)
    ax_mg = fig.add_subplot(gs[2, :])
    create_mg_death_subplot(ax_mg, axis_deaths, allies_deaths, 
                          team1_name_display, team2_name_display, colors)
    
    # Add main title
    fig.suptitle(f'{team1_name_display} vs {team2_name_display} Comparison', 
                fontsize=24, color='white', y=0.95)
    
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