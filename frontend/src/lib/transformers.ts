import type { Anomaly } from '../types';
import type { EVSession } from '../components/EVDashboard';

const anomalyTypeMap: Record<string, 'fraud' | 'dos' | 'multiuser'> = {
  dos_attack:    'dos',
  burst_pattern: 'dos',
  ghost_session: 'fraud',
  energy_spike:  'fraud',
  idle_abuse:    'multiuser',
};

const statusMap: Record<string, 'critical' | 'warning' | 'normal'> = {
  dos_attack:    'critical',
  burst_pattern: 'critical',
  energy_spike:  'critical',
  ghost_session: 'warning',
  idle_abuse:    'warning',
};

export function transformBackendAnomalyToSession(anomaly: Anomaly): EVSession {
  return {
    sessionId:   anomaly.session_id,
    chargerId:   anomaly.station_id,
    startTime:   new Date(anomaly.start_time).toLocaleTimeString(),
    duration:    Math.round(anomaly.total_duration_mins),
    energy:      anomaly.energy_kwh,
    score:       anomaly.confidence,
    anomalyType: anomalyTypeMap[anomaly.anomaly_type] ?? null,
    status:      statusMap[anomaly.anomaly_type] ?? 'normal',
    userId:      anomaly.port_type || 'Unknown',
  };
}
