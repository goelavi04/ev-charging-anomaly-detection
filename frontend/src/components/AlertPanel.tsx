import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { AlertCircle, Flag, CheckCircle, FileText, TrendingUp } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { toast } from "sonner";
import type { EVSession } from "./EVDashboard";

interface AlertPanelProps {
  session: EVSession | null;
  sessions: EVSession[];
  onUpdateSessions: (sessions: EVSession[]) => void;
}

export function AlertPanel({ session, sessions, onUpdateSessions }: AlertPanelProps) {
  if (!session) {
    return (
      <Card className="bg-slate-900 border-slate-800 p-6 h-full">
        <div className="flex flex-col items-center justify-center h-full text-center text-slate-500">
          <AlertCircle className="w-12 h-12 mb-3" />
          <p>Select a session to view details</p>
        </div>
      </Card>
    );
  }

  const handleFlagUser = () => {
    const updatedSessions = sessions.map(s =>
      s.sessionId === session.sessionId
        ? { ...s, status: "critical" as const }
        : s
    );
    onUpdateSessions(updatedSessions);
    toast.success("User flagged and session suspended");
  };

  const handleAcknowledge = () => {
    const updatedSessions = sessions.map(s =>
      s.sessionId === session.sessionId
        ? { ...s, status: "normal" as const, anomalyType: null }
        : s
    );
    onUpdateSessions(updatedSessions);
    toast.success("Alert acknowledged");
  };

  const getAlertTitle = () => {
    if (session.anomalyType === "fraud") return "CRITICAL ALERT: FRAUD DETECTED";
    if (session.anomalyType === "dos") return "CRITICAL ALERT: DoS / BURST ATTACK";
    if (session.anomalyType === "multiuser") return "WARNING: IDLE ABUSE DETECTED";
    return "Session Information";
  };

  const getAlertDescription = () => {
    if (session.anomalyType === "fraud") {
      return `Confidence: ${(session.score * 100).toFixed(0)}%. Energy: ${session.energy.toFixed(2)} kWh. Possible ghost session or energy spike anomaly.`;
    }
    if (session.anomalyType === "dos") {
      return `Confidence: ${(session.score * 100).toFixed(0)}%. Duration: ${session.duration} min. Possible DoS attack or burst pattern anomaly.`;
    }
    if (session.anomalyType === "multiuser") {
      return `Confidence: ${(session.score * 100).toFixed(0)}%. Excessive idle time relative to charging time detected.`;
    }
    return "No anomalies detected for this session.";
  };

  const chartData = Array.from({ length: 20 }, (_, i) => ({
    time: i,
    usage: session.anomalyType === "fraud"
      ? Math.random() * 20 + 60
      : session.anomalyType === "dos"
      ? Math.random() * 10
      : Math.random() * 40 + 20
  }));

  return (
    <Card className="bg-slate-900 border-slate-800 p-6 space-y-6">
      <div className={`p-4 rounded-lg ${
        session.status === "critical" ? "bg-red-900/30 border-2 border-red-600" :
        session.status === "warning" ? "bg-amber-900/30 border-2 border-amber-600" :
        "bg-slate-800 border-2 border-slate-700"
      }`}>
        <div className="flex items-center gap-2 mb-2">
          <AlertCircle className={`w-6 h-6 ${
            session.status === "critical" ? "text-red-400 animate-pulse" :
            session.status === "warning" ? "text-amber-400" :
            "text-slate-400"
          }`} />
          <h3 className={`text-base font-bold ${
            session.status === "critical" ? "text-red-300" :
            session.status === "warning" ? "text-amber-300" :
            "text-slate-400"
          }`}>
            {getAlertTitle()}
          </h3>
        </div>
        <p className="text-sm text-white font-medium leading-relaxed">{getAlertDescription()}</p>
      </div>

      <div className="space-y-3">
        <h4 className="text-white text-base font-bold uppercase tracking-wide">Session Details</h4>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <p className="text-slate-400 font-semibold mb-1">Session ID</p>
            <p className="text-white font-bold">{session.sessionId}</p>
          </div>
          <div>
            <p className="text-slate-400 font-semibold mb-1">Port Type</p>
            <p className="text-white font-bold">{session.userId}</p>
          </div>
          <div>
            <p className="text-slate-400 font-semibold mb-1">Charger / Station</p>
            <p className="text-blue-400 font-bold">{session.chargerId}</p>
          </div>
          <div>
            <p className="text-slate-400 font-semibold mb-1">Start Time</p>
            <p className="text-white font-medium">{session.startTime}</p>
          </div>
          <div>
            <p className="text-slate-400 font-semibold mb-1">Duration</p>
            <p className="text-white font-bold">{session.duration} min</p>
          </div>
          <div>
            <p className="text-slate-400 font-semibold mb-1">Energy Used</p>
            <p className="text-emerald-400 font-bold">{session.energy.toFixed(2)} kWh</p>
          </div>
        </div>
      </div>

      {session.score > 0 && (
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <h4 className="text-white text-base font-bold uppercase tracking-wide">Confidence Score</h4>
            <Badge className={`text-lg font-bold px-3 py-1 ${
              session.score > 0.8 ? "bg-red-600" :
              session.score > 0.5 ? "bg-amber-600" :
              "bg-emerald-600"
            }`}>
              {(session.score * 100).toFixed(0)}%
            </Badge>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-3 overflow-hidden">
            <div
              className={`h-3 rounded-full transition-all duration-500 ${
                session.score > 0.8 ? "bg-gradient-to-r from-red-600 to-red-400" :
                session.score > 0.5 ? "bg-gradient-to-r from-amber-600 to-amber-400" :
                "bg-gradient-to-r from-emerald-600 to-emerald-400"
              }`}
              style={{ width: `${session.score * 100}%` }}
            />
          </div>
        </div>
      )}

      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-emerald-400" />
          <h4 className="text-white text-base font-bold uppercase tracking-wide">Energy Usage Pattern</h4>
        </div>
        <div className="bg-slate-950 rounded-lg p-3">
          <ResponsiveContainer width="100%" height={150}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 10 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 10 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #475569',
                  borderRadius: '6px'
                }}
              />
              <Line
                type="monotone"
                dataKey="usage"
                stroke={
                  session.status === "critical" ? "#ef4444" :
                  session.status === "warning" ? "#f59e0b" :
                  "#10b981"
                }
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="space-y-2">
        {session.status === "critical" && (
          <Button
            onClick={handleFlagUser}
            className="w-full bg-red-600 hover:bg-red-700"
          >
            <Flag className="w-4 h-4 mr-2" />
            Flag User & Suspend Session
          </Button>
        )}

        {session.status !== "normal" && (
          <Button
            onClick={handleAcknowledge}
            className="w-full bg-blue-600 hover:bg-blue-700"
          >
            <CheckCircle className="w-4 h-4 mr-2" />
            Acknowledge Alert
          </Button>
        )}

        <Button
          variant="outline"
          className="w-full bg-slate-800 hover:bg-slate-700 border-slate-700"
        >
          <FileText className="w-4 h-4 mr-2" />
          View Charger Logs
        </Button>
      </div>
    </Card>
  );
}
