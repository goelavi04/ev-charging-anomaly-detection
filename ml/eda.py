import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from label_engineering import load_and_clean, engineer_features, generate_labels

# ── Load data ──────────────────────────────────────────────
df = load_and_clean('ml/dataset/ev_charging_data.csv')
print("=" * 50)
print("STEP 1: RAW DATA OVERVIEW")
print("=" * 50)
print(f"Total sessions     : {len(df)}")
print(f"Total stations     : {df['station_id'].nunique()}")
print(f"Date range         : {df['start_time'].min()} → {df['start_time'].max()}")
print(f"Avg energy (kWh)   : {df['energy_kwh'].mean():.2f}")
print(f"Max energy (kWh)   : {df['energy_kwh'].max():.2f}")
print(f"Min energy (kWh)   : {df['energy_kwh'].min():.2f}")
print(f"Missing values     :\n{df.isnull().sum()}")

# ── Engineer features ──────────────────────────────────────
print("\n" + "=" * 50)
print("STEP 2: FEATURE ENGINEERING")
print("=" * 50)
df = engineer_features(df)
print("Features created:")
print(f"  energy_per_min     → min={df['energy_per_min'].min():.3f}, max={df['energy_per_min'].max():.3f}, mean={df['energy_per_min'].mean():.3f}")
print(f"  idle_ratio         → min={df['idle_ratio'].min():.3f}, max={df['idle_ratio'].max():.3f}, mean={df['idle_ratio'].mean():.3f}")
print(f"  energy_zscore      → min={df['energy_zscore'].min():.3f}, max={df['energy_zscore'].max():.3f}")
print(f"  sessions_last_30min→ max={df['sessions_last_30min'].max()}")

# ── Generate labels ────────────────────────────────────────
print("\n" + "=" * 50)
print("STEP 3: ANOMALY LABEL DISTRIBUTION")
print("=" * 50)
df = generate_labels(df)
label_counts = df['anomaly_type'].value_counts()
print(label_counts)
print(f"\nTotal anomalies    : {df['is_anomaly'].sum()} ({df['is_anomaly'].mean()*100:.2f}% of data)")

# ── Plot 1: Anomaly distribution ───────────────────────────
plt.figure(figsize=(10, 5))
colors = ['#2ecc71' if x == 'normal' else '#e74c3c' for x in label_counts.index]
bars = plt.bar(label_counts.index, label_counts.values, color=colors, edgecolor='black', linewidth=0.5)
for bar, val in zip(bars, label_counts.values):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
             str(val), ha='center', va='bottom', fontsize=10)
plt.title('Anomaly Type Distribution', fontsize=14)
plt.xlabel('Anomaly Type')
plt.ylabel('Number of Sessions')
plt.tight_layout()
plt.savefig('ml/eda_anomaly_distribution.png', dpi=150)
plt.close()
print("\nSaved: ml/eda_anomaly_distribution.png")

# ── Plot 2: Energy distribution ────────────────────────────
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
df[df['anomaly_type'] == 'normal']['energy_kwh'].hist(bins=50, color='#2ecc71', alpha=0.7, label='Normal')
df[df['is_anomaly'] == 1]['energy_kwh'].hist(bins=50, color='#e74c3c', alpha=0.7, label='Anomaly')
plt.xlabel('Energy (kWh)')
plt.ylabel('Count')
plt.title('Energy Distribution')
plt.legend()

plt.subplot(1, 2, 2)
df[df['anomaly_type'] == 'normal']['total_duration_mins'].clip(0, 300).hist(
    bins=50, color='#2ecc71', alpha=0.7, label='Normal')
df[df['is_anomaly'] == 1]['total_duration_mins'].clip(0, 300).hist(
    bins=50, color='#e74c3c', alpha=0.7, label='Anomaly')
plt.xlabel('Duration (mins)')
plt.ylabel('Count')
plt.title('Duration Distribution')
plt.legend()
plt.tight_layout()
plt.savefig('ml/eda_energy_duration.png', dpi=150)
plt.close()
print("Saved: ml/eda_energy_duration.png")

# ── Plot 3: Correlation heatmap ────────────────────────────
feature_cols = [
    'energy_kwh', 'total_duration_mins', 'charging_time_mins',
    'energy_per_min', 'idle_ratio', 'energy_zscore',
    'sessions_last_30min', 'port_type_num', 'ghg_savings', 'is_anomaly'
]
plt.figure(figsize=(10, 8))
corr = df[feature_cols].corr()
sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdYlGn',
            center=0, square=True, linewidths=0.5)
plt.title('Feature Correlation Heatmap', fontsize=14)
plt.tight_layout()
plt.savefig('ml/eda_correlation_heatmap.png', dpi=150)
plt.close()
print("Saved: ml/eda_correlation_heatmap.png")

# ── Plot 4: Idle ratio vs energy (scatter) ─────────────────
plt.figure(figsize=(8, 6))
normal = df[df['anomaly_type'] == 'normal'].sample(min(2000, len(df[df['anomaly_type']=='normal'])))
anomaly = df[df['is_anomaly'] == 1]
plt.scatter(normal['idle_ratio'], normal['energy_kwh'],
            alpha=0.3, s=5, color='#2ecc71', label='Normal')
plt.scatter(anomaly['idle_ratio'], anomaly['energy_kwh'],
            alpha=0.6, s=15, color='#e74c3c', label='Anomaly')
plt.xlabel('Idle Ratio')
plt.ylabel('Energy (kWh)')
plt.title('Idle Ratio vs Energy — Normal vs Anomaly')
plt.legend()
plt.tight_layout()
plt.savefig('ml/eda_scatter.png', dpi=150)
plt.close()
print("Saved: ml/eda_scatter.png")

# ── Summary stats per anomaly type ────────────────────────
print("\n" + "=" * 50)
print("STEP 4: STATS PER ANOMALY TYPE")
print("=" * 50)
summary = df.groupby('anomaly_type')[['energy_kwh', 'total_duration_mins', 'idle_ratio']].mean().round(2)
print(summary)

print("\n✅ EDA complete. Check ml/ folder for 4 PNG charts.")
# ── Plot 5: Top 10 stations by total energy ────────────────
plt.figure(figsize=(12, 5))
top_stations = df.groupby('station_id')['energy_kwh'].sum().sort_values(ascending=False).head(10)
bars = plt.bar(range(len(top_stations)), top_stations.values, color='#3498db', edgecolor='black', linewidth=0.5)
plt.xticks(range(len(top_stations)), [s[:20] for s in top_stations.index], rotation=45, ha='right')
for bar, val in zip(bars, top_stations.values):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
             f'{val:.0f}', ha='center', va='bottom', fontsize=8)
plt.title('Top 10 Stations by Total Energy Delivered (kWh)', fontsize=14)
plt.xlabel('Station')
plt.ylabel('Total Energy (kWh)')
plt.tight_layout()
plt.savefig('ml/eda_top_stations.png', dpi=150)
plt.close()
print("Saved: ml/eda_top_stations.png")

# ── Plot 6: Sessions by hour of day ───────────────────────
plt.figure(figsize=(12, 5))
df['hour'] = df['start_time'].dt.hour
hourly = df.groupby(['hour', 'is_anomaly']).size().unstack(fill_value=0)
hourly.columns = ['Normal', 'Anomaly']
x = range(24)
width = 0.4
plt.bar([i - width/2 for i in x], hourly['Normal'], width=width,
        color='#2ecc71', label='Normal', edgecolor='black', linewidth=0.5)
plt.bar([i + width/2 for i in x], hourly['Anomaly'], width=width,
        color='#e74c3c', label='Anomaly', edgecolor='black', linewidth=0.5)
plt.xlabel('Hour of Day')
plt.ylabel('Number of Sessions')
plt.title('Sessions by Hour of Day — Normal vs Anomaly', fontsize=14)
plt.xticks(range(24))
plt.legend()
plt.tight_layout()
plt.savefig('ml/eda_hourly_pattern.png', dpi=150)
plt.close()
print("Saved: ml/eda_hourly_pattern.png")

# ── Plot 7: Sessions by day of week ───────────────────────
plt.figure(figsize=(10, 5))
df['day_of_week'] = df['start_time'].dt.day_name()
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
daily = df.groupby(['day_of_week', 'is_anomaly']).size().unstack(fill_value=0)
daily = daily.reindex(day_order)
daily.columns = ['Normal', 'Anomaly']
x = range(7)
width = 0.4
plt.bar([i - width/2 for i in x], daily['Normal'], width=width,
        color='#2ecc71', label='Normal', edgecolor='black', linewidth=0.5)
plt.bar([i + width/2 for i in x], daily['Anomaly'], width=width,
        color='#e74c3c', label='Anomaly', edgecolor='black', linewidth=0.5)
plt.xticks(range(7), day_order, rotation=30, ha='right')
plt.xlabel('Day of Week')
plt.ylabel('Number of Sessions')
plt.title('Sessions by Day of Week — Normal vs Anomaly', fontsize=14)
plt.legend()
plt.tight_layout()
plt.savefig('ml/eda_daily_pattern.png', dpi=150)
plt.close()
print("Saved: ml/eda_daily_pattern.png")

# ── Plot 8: Monthly trend ──────────────────────────────────
plt.figure(figsize=(14, 5))
df['month'] = df['start_time'].dt.to_period('M')
monthly = df.groupby(['month', 'anomaly_type']).size().unstack(fill_value=0)
monthly.index = monthly.index.astype(str)
anomaly_cols = [c for c in monthly.columns if c != 'normal']
plt.stackplot(range(len(monthly)),
              [monthly[c] for c in anomaly_cols],
              labels=anomaly_cols,
              colors=['#e74c3c', '#e67e22', '#9b59b6', '#e91e8c', '#1abc9c'])
plt.xticks(range(len(monthly)), monthly.index, rotation=45, ha='right', fontsize=8)
plt.xlabel('Month')
plt.ylabel('Anomaly Count')
plt.title('Anomaly Types Over Time (Monthly)', fontsize=14)
plt.legend(loc='upper left')
plt.tight_layout()
plt.savefig('ml/eda_monthly_trend.png', dpi=150)
plt.close()
print("Saved: ml/eda_monthly_trend.png")

# ── Plot 9: Energy boxplot by anomaly type ─────────────────
plt.figure(figsize=(12, 6))
anomaly_types = df['anomaly_type'].unique().tolist()
data_to_plot = [df[df['anomaly_type'] == a]['energy_kwh'].clip(0, 50).values for a in anomaly_types]
bp = plt.boxplot(data_to_plot, labels=anomaly_types, patch_artist=True, notch=False)
colors_box = ['#2ecc71', '#e74c3c', '#e67e22', '#9b59b6', '#3498db', '#1abc9c']
for patch, color in zip(bp['boxes'], colors_box):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
plt.xlabel('Anomaly Type')
plt.ylabel('Energy (kWh) — clipped at 50')
plt.title('Energy Distribution by Anomaly Type', fontsize=14)
plt.tight_layout()
plt.savefig('ml/eda_boxplot_energy.png', dpi=150)
plt.close()
print("Saved: ml/eda_boxplot_energy.png")

# ── Plot 10: Duration boxplot by anomaly type ──────────────
plt.figure(figsize=(12, 6))
data_dur = [df[df['anomaly_type'] == a]['total_duration_mins'].clip(0, 300).values for a in anomaly_types]
bp2 = plt.boxplot(data_dur, labels=anomaly_types, patch_artist=True)
for patch, color in zip(bp2['boxes'], colors_box):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
plt.xlabel('Anomaly Type')
plt.ylabel('Duration (mins) — clipped at 300')
plt.title('Duration Distribution by Anomaly Type', fontsize=14)
plt.tight_layout()
plt.savefig('ml/eda_boxplot_duration.png', dpi=150)
plt.close()
print("Saved: ml/eda_boxplot_duration.png")

# ── Plot 11: Idle ratio distribution by anomaly ────────────
plt.figure(figsize=(10, 5))
for atype in anomaly_types:
    subset = df[df['anomaly_type'] == atype]['idle_ratio'].clip(0, 1)
    subset.hist(bins=40, alpha=0.5, label=atype, density=True)
plt.xlabel('Idle Ratio')
plt.ylabel('Density')
plt.title('Idle Ratio Distribution by Anomaly Type', fontsize=14)
plt.legend()
plt.tight_layout()
plt.savefig('ml/eda_idle_ratio_dist.png', dpi=150)
plt.close()
print("Saved: ml/eda_idle_ratio_dist.png")

# ── Plot 12: Port type breakdown ───────────────────────────
plt.figure(figsize=(8, 5))
port_anomaly = df.groupby(['port_type', 'is_anomaly']).size().unstack(fill_value=0)
port_anomaly.columns = ['Normal', 'Anomaly']
port_anomaly.plot(kind='bar', color=['#2ecc71', '#e74c3c'],
                  edgecolor='black', linewidth=0.5, ax=plt.gca())
plt.xlabel('Port Type')
plt.ylabel('Count')
plt.title('Normal vs Anomaly by Port Type', fontsize=14)
plt.xticks(rotation=0)
plt.legend()
plt.tight_layout()
plt.savefig('ml/eda_port_type.png', dpi=150)
plt.close()
print("Saved: ml/eda_port_type.png")

# ── Plot 13: Energy zscore histogram ──────────────────────
plt.figure(figsize=(10, 5))
df['energy_zscore'].clip(-3, 6).hist(bins=60, color='#9b59b6', edgecolor='black',
                                      linewidth=0.3, alpha=0.8)
plt.axvline(x=3, color='red', linestyle='--', linewidth=2, label='Anomaly threshold (z=3)')
plt.xlabel('Energy Z-Score')
plt.ylabel('Count')
plt.title('Energy Z-Score Distribution (anomaly threshold at 3)', fontsize=14)
plt.legend()
plt.tight_layout()
plt.savefig('ml/eda_zscore_dist.png', dpi=150)
plt.close()
print("Saved: ml/eda_zscore_dist.png")

# ── Plot 14: Anomaly % by station (top 15) ────────────────
plt.figure(figsize=(13, 5))
station_anomaly_rate = df.groupby('station_id')['is_anomaly'].mean().sort_values(ascending=False).head(15)
bars = plt.bar(range(len(station_anomaly_rate)),
               station_anomaly_rate.values * 100,
               color='#e74c3c', edgecolor='black', linewidth=0.5)
plt.xticks(range(len(station_anomaly_rate)),
           [s[:18] for s in station_anomaly_rate.index], rotation=45, ha='right', fontsize=8)
for bar, val in zip(bars, station_anomaly_rate.values):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
             f'{val*100:.1f}%', ha='center', va='bottom', fontsize=8)
plt.xlabel('Station')
plt.ylabel('Anomaly Rate (%)')
plt.title('Top 15 Stations by Anomaly Rate', fontsize=14)
plt.tight_layout()
plt.savefig('ml/eda_station_anomaly_rate.png', dpi=150)
plt.close()
print("Saved: ml/eda_station_anomaly_rate.png")

print("\n✅ All 14 EDA charts saved in ml/ folder.")
print("Open each PNG by clicking it in the VS Code sidebar.")