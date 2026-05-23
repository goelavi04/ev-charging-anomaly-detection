import { AlertTriangle, CheckCircle2, XCircle } from "lucide-react";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { ScrollArea } from "./ui/scroll-area";
import type { EVSession } from "./EVDashboard";

interface AnomalyTableProps {
  sessions: EVSession[];
  onSelectSession: (session: EVSession) => void;
  selectedSessionId?: string;
  title?: string;
  description?: string;
}

export function AnomalyTable({
  sessions,
  onSelectSession,
  selectedSessionId,
  title = "Session Monitoring",
  description = "Real-time anomaly detection"
}: AnomalyTableProps) {
  const getStatusIcon = (status: string) => {
    if (status === "critical") return <XCircle className="w-5 h-5 text-red-500" />;
    if (status === "warning") return <AlertTriangle className="w-5 h-5 text-amber-500" />;
    return <CheckCircle2 className="w-5 h-5 text-emerald-500" />;
  };

  const getAnomalyBadge = (type: string | null) => {
    if (!type) return null;
    const colors = {
      fraud: "bg-red-600 hover:bg-red-700",
      dos: "bg-purple-600 hover:bg-purple-700",
      multiuser: "bg-amber-600 hover:bg-amber-700"
    };
    const labels = {
      fraud: "Fraud",
      dos: "DoS / Burst",
      multiuser: "Idle Abuse"
    };
    return (
      <Badge className={colors[type as keyof typeof colors]}>
        {labels[type as keyof typeof labels]}
      </Badge>
    );
  };

  return (
    <Card className="bg-slate-900 border-slate-800 p-6">
      <div className="mb-4">
        <h2 className="text-2xl text-white font-bold">{title}</h2>
        <p className="text-sm text-slate-300 font-medium mt-1">{description}</p>
      </div>

      {sessions.length === 0 ? (
        <div className="py-12 text-center">
          <p className="text-slate-400 font-semibold text-lg">No anomalies detected in this category</p>
          <p className="text-slate-500 text-sm mt-2">All sessions are running normally</p>
        </div>
      ) : (
        <ScrollArea className="h-[500px]">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-800 sticky top-0 z-10">
                <tr>
                  <th className="text-left p-3 text-white text-sm font-bold uppercase tracking-wider">Status</th>
                  <th className="text-left p-3 text-white text-sm font-bold uppercase tracking-wider">Session ID</th>
                  <th className="text-left p-3 text-white text-sm font-bold uppercase tracking-wider">Charger ID</th>
                  <th className="text-left p-3 text-white text-sm font-bold uppercase tracking-wider">Start Time</th>
                  <th className="text-left p-3 text-white text-sm font-bold uppercase tracking-wider">Duration</th>
                  <th className="text-left p-3 text-white text-sm font-bold uppercase tracking-wider">Energy</th>
                  <th className="text-left p-3 text-white text-sm font-bold uppercase tracking-wider">Confidence</th>
                  <th className="text-left p-3 text-white text-sm font-bold uppercase tracking-wider">Anomaly</th>
                </tr>
              </thead>
              <tbody>
                {sessions.map((session) => (
                  <tr
                    key={session.sessionId}
                    onClick={() => onSelectSession(session)}
                    className={`border-b border-slate-800 hover:bg-slate-800/50 cursor-pointer transition-colors ${
                      selectedSessionId === session.sessionId ? 'bg-slate-800' : ''
                    }`}
                  >
                    <td className="p-3">
                      {getStatusIcon(session.status)}
                    </td>
                    <td className="p-3 text-white font-semibold">{session.sessionId}</td>
                    <td className="p-3 text-blue-400 font-semibold">{session.chargerId}</td>
                    <td className="p-3 text-slate-300 text-sm font-medium">{session.startTime}</td>
                    <td className="p-3 text-slate-300 text-sm font-medium">{session.duration} min</td>
                    <td className="p-3 text-emerald-400 font-semibold">{session.energy.toFixed(2)} kWh</td>
                    <td className="p-3">
                      <span className={`text-sm font-bold ${
                        session.score > 0.8 ? 'text-red-400' :
                        session.score > 0.5 ? 'text-amber-400' :
                        'text-emerald-400'
                      }`}>
                        {session.score > 0 ? `${(session.score * 100).toFixed(0)}%` : '-'}
                      </span>
                    </td>
                    <td className="p-3">
                      {getAnomalyBadge(session.anomalyType)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </ScrollArea>
      )}
    </Card>
  );
}
