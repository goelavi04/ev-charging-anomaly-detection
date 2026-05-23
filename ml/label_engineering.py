import pandas as pd
import numpy as np


def load_and_clean(filepath):
    df = pd.read_csv(filepath)

    df = df.rename(columns={
        'ObjectID':                  'session_id',
        'Station_Name':              'station_id',
        'Start_Date___Time':         'start_time',
        'End_Date___Time':           'end_time',
        'Total_Duration__hh_mm_ss_': 'total_duration',
        'Charging_Time__hh_mm_ss_':  'charging_time',
        'Energy__kWh_':              'energy_kwh',
        'Port_Type':                 'port_type',
        'GHG_Savings__kg_':          'ghg_savings',
    })

    df['start_time'] = pd.to_datetime(df['start_time'], format='mixed', dayfirst=False)
    df['end_time']   = pd.to_datetime(df['end_time'],   format='mixed', dayfirst=False)

    df = df.dropna(subset=['end_time'])

    df['total_duration_mins'] = pd.to_timedelta(df['total_duration']).dt.total_seconds() / 60
    df['charging_time_mins']  = pd.to_timedelta(df['charging_time']).dt.total_seconds()  / 60

    df = df[df['total_duration_mins'] >= 0]
    df = df[df['charging_time_mins']  >= 0]
    df = df[df['energy_kwh']          >= 0]
    df = df[df['charging_time_mins']  <= df['total_duration_mins'] + 1]

    df = df.reset_index(drop=True)
    return df


def engineer_features(df, fast=False):

    df['energy_per_min'] = df['energy_kwh'] / (df['charging_time_mins'] + 0.001)

    df['idle_ratio'] = (
        (df['total_duration_mins'] - df['charging_time_mins']) /
        (df['total_duration_mins'] + 0.001)
    )
    df['idle_ratio'] = df['idle_ratio'].clip(0, 1)

    df['charge_efficiency'] = df['charging_time_mins'] / (df['total_duration_mins'] + 0.001)

    df['idle_mins'] = (df['total_duration_mins'] - df['charging_time_mins']).clip(0)

    station_stats = df.groupby('station_id')['energy_kwh'].agg(
        ['mean', 'std', 'median', 'count']
    ).reset_index()
    station_stats.columns = [
        'station_id', 'station_mean_energy',
        'station_std_energy', 'station_median_energy', 'station_session_count'
    ]
    df = df.merge(station_stats, on='station_id', how='left')

    df['energy_zscore'] = (
        (df['energy_kwh'] - df['station_mean_energy']) /
        (df['station_std_energy'] + 0.001)
    )

    df['energy_vs_median'] = df['energy_kwh'] / (df['station_median_energy'] + 0.001)

    station_dur = df.groupby('station_id')['total_duration_mins'].agg(
        ['mean', 'std']
    ).reset_index()
    station_dur.columns = ['station_id', 'station_mean_dur', 'station_std_dur']
    df = df.merge(station_dur, on='station_id', how='left')

    df['duration_zscore'] = (
        (df['total_duration_mins'] - df['station_mean_dur']) /
        (df['station_std_dur'] + 0.001)
    )

    df = df.sort_values('start_time').reset_index(drop=True)

    if fast:
        # skip slow burst detection loop in backend/real-time mode
        df['sessions_last_30min'] = 0
    else:
        df['start_ts'] = df['start_time'].astype(np.int64) // 10**9
        result = pd.Series(0, index=df.index)

        for station, group in df.groupby('station_id'):
            timestamps = group['start_ts'].values
            counts = []
            for i, ts in enumerate(timestamps):
                window = 30 * 60
                count = np.sum(
                    (timestamps[:i] >= ts - window) &
                    (timestamps[:i] < ts)
                )
                counts.append(int(count))
            result.loc[group.index] = counts

        df['sessions_last_30min'] = result
        df = df.drop(columns=['start_ts'])

    df['port_type_num'] = df['port_type'].apply(
        lambda x: 2 if 'Level 2' in str(x) else 1
    )

    df['hour']        = df['start_time'].dt.hour
    df['day_of_week'] = df['start_time'].dt.dayofweek
    df['month']       = df['start_time'].dt.month
    df['is_weekend']  = (df['day_of_week'] >= 5).astype(int)
    df['is_night']    = ((df['hour'] >= 22) | (df['hour'] <= 5)).astype(int)

    return df


def generate_labels(df):
    df['anomaly_type'] = 'normal'
    df['is_anomaly']   = 0

    np.random.seed(42)

    dos_mask    = (df['total_duration_mins'] < 5) & (df['energy_kwh'] < 0.5)
    dos_indices = df[dos_mask].index
    flip        = np.random.choice(dos_indices, size=int(len(dos_indices) * 0.08), replace=False)
    df.loc[dos_mask, 'anomaly_type'] = 'dos_attack'
    df.loc[dos_mask, 'is_anomaly']   = 1
    df.loc[flip,     'anomaly_type'] = 'normal'
    df.loc[flip,     'is_anomaly']   = 0

    borderline_dos = df[
        (df['total_duration_mins'] >= 5) &
        (df['total_duration_mins'] <  10) &
        (df['energy_kwh'] < 1.0) &
        (df['anomaly_type'] == 'normal')
    ].index
    add_dos = np.random.choice(
        borderline_dos,
        size=min(int(len(borderline_dos) * 0.15), 50),
        replace=False
    )
    df.loc[add_dos, 'anomaly_type'] = 'dos_attack'
    df.loc[add_dos, 'is_anomaly']   = 1

    idle_mask    = (
        (df['idle_ratio'] > 0.92) &
        (df['total_duration_mins'] > 120) &
        (df['energy_kwh'] > 2.0)
    )
    idle_indices = df[idle_mask].index
    if len(idle_indices) > 0:
        flip = np.random.choice(idle_indices, size=int(len(idle_indices) * 0.10), replace=False)
        df.loc[idle_mask, 'anomaly_type'] = 'idle_abuse'
        df.loc[idle_mask, 'is_anomaly']   = 1
        df.loc[flip,      'anomaly_type'] = 'normal'
        df.loc[flip,      'is_anomaly']   = 0

    spike_mask    = (df['energy_zscore'] > 3.0) & (df['energy_vs_median'] > 4.0)
    spike_indices = df[spike_mask].index
    if len(spike_indices) > 0:
        flip = np.random.choice(spike_indices, size=int(len(spike_indices) * 0.10), replace=False)
        df.loc[spike_mask, 'anomaly_type'] = 'energy_spike'
        df.loc[spike_mask, 'is_anomaly']   = 1
        df.loc[flip,       'anomaly_type'] = 'normal'
        df.loc[flip,       'is_anomaly']   = 0

    burst_mask    = (df['sessions_last_30min'] >= 8)
    burst_indices = df[burst_mask].index
    if len(burst_indices) > 0:
        flip = np.random.choice(burst_indices, size=int(len(burst_indices) * 0.12), replace=False)
        df.loc[burst_mask, 'anomaly_type'] = 'burst_pattern'
        df.loc[burst_mask, 'is_anomaly']   = 1
        df.loc[flip,       'anomaly_type'] = 'normal'
        df.loc[flip,       'is_anomaly']   = 0

    ghost_mask    = (df['energy_kwh'] == 0)
    ghost_indices = df[ghost_mask].index
    if len(ghost_indices) > 0:
        flip = np.random.choice(ghost_indices, size=int(len(ghost_indices) * 0.08), replace=False)
        df.loc[ghost_mask, 'anomaly_type'] = 'ghost_session'
        df.loc[ghost_mask, 'is_anomaly']   = 1
        df.loc[flip,       'anomaly_type'] = 'normal'
        df.loc[flip,       'is_anomaly']   = 0

    return df


def get_feature_columns():
    return [
        'energy_kwh',
        'total_duration_mins',
        'charging_time_mins',
        'energy_per_min',
        'idle_ratio',
        'idle_mins',
        'charge_efficiency',
        'energy_zscore',
        'energy_vs_median',
        'duration_zscore',
        'station_mean_energy',
        'station_std_energy',
        'station_median_energy',
        'station_session_count',
        'station_mean_dur',
        'sessions_last_30min',
        'hour',
        'day_of_week',
        'month',
        'is_weekend',
        'is_night',
        'port_type_num',
        'ghg_savings',
    ]