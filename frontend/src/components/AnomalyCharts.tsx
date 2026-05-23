import { Card } from "./ui/card";
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import type { EVSession } from "./EVDashboard";

interface AnomalyChartsProps {
  sessions: EVSession[];
}

export function AnomalyCharts({ sessions }: AnomalyChartsProps) {
  const fraudCount = sessions.filter(s => s.anomalyType === "fraud").length;
  const dosCount = sessions.filter(s => s.anomalyType === "dos").length;
  const multiuserCount = sessions.filter(s => s.anomalyType === "multiuser").length;
  const normalCount = sessions.filter(s => !s.anomalyType).length;

  const pieData = [
    { name: "Normal", value: normalCount, color: "#10b981" },
    { name: "Fraud", value: fraudCount, color: "#ef4444" },
    { name: "DoS / Burst", value: dosCount, color: "#8b5cf6" },
    { name: "Idle Abuse", value: multiuserCount, color: "#f59e0b" },
  ].filter(item => item.value > 0);

  const barData = [
    {
      name: "Critical",
      sessions: sessions.filter(s => s.status === "critical").length,
      energy: sessions.filter(s => s.status === "critical").reduce((acc, s) => acc + s.energy, 0)
    },
    {
      name: "Warning",
      sessions: sessions.filter(s => s.status === "warning").length,
      energy: sessions.filter(s => s.status === "warning").reduce((acc, s) => acc + s.energy, 0)
    },
    {
      name: "Normal",
      sessions: sessions.filter(s => s.status === "normal").length,
      energy: sessions.filter(s => s.status === "normal").reduce((acc, s) => acc + s.energy, 0)
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <Card className="bg-slate-900 border-slate-800 p-6">
        <h3 className="text-xl mb-4 text-white font-bold tracking-wide">Anomaly Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }: { name?: string; percent?: number }) => `${name ?? ''} ${((percent ?? 0) * 100).toFixed(0)}%`}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #475569',
                borderRadius: '6px'
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </Card>

      <Card className="bg-slate-900 border-slate-800 p-6">
        <h3 className="text-xl mb-4 text-white font-bold tracking-wide">Energy Consumption by Status</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={barData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" stroke="#64748b" />
            <YAxis stroke="#64748b" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #475569',
                borderRadius: '6px'
              }}
            />
            <Legend />
            <Bar dataKey="energy" fill="#3b82f6" name="Total Energy (kWh)" />
            <Bar dataKey="sessions" fill="#8b5cf6" name="Session Count" />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      <Card className="bg-slate-900 border-slate-800 p-6 md:col-span-2">
        <h3 className="text-xl mb-4 text-white font-bold tracking-wide">Session Statistics</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-slate-800 rounded-lg p-4 border-2 border-blue-700 hover:border-blue-500 transition-colors">
            <p className="text-blue-300 text-sm mb-1 font-bold uppercase tracking-wide">Avg Duration</p>
            <p className="text-3xl text-white font-bold">
              {sessions.length > 0
                ? (sessions.reduce((acc, s) => acc + s.duration, 0) / sessions.length).toFixed(1)
                : 0
              } <span className="text-lg text-slate-400">min</span>
            </p>
          </div>
          <div className="bg-slate-800 rounded-lg p-4 border-2 border-emerald-700 hover:border-emerald-500 transition-colors">
            <p className="text-emerald-300 text-sm mb-1 font-bold uppercase tracking-wide">Avg Energy</p>
            <p className="text-3xl text-white font-bold">
              {sessions.length > 0
                ? (sessions.reduce((acc, s) => acc + s.energy, 0) / sessions.length).toFixed(1)
                : 0
              } <span className="text-lg text-slate-400">kWh</span>
            </p>
          </div>
          <div className="bg-slate-800 rounded-lg p-4 border-2 border-amber-700 hover:border-amber-500 transition-colors">
            <p className="text-amber-300 text-sm mb-1 font-bold uppercase tracking-wide">Detection Rate</p>
            <p className="text-3xl text-white font-bold">
              {sessions.length > 0
                ? ((sessions.filter(s => s.anomalyType).length / sessions.length) * 100).toFixed(0)
                : 0
              }<span className="text-lg text-slate-400">%</span>
            </p>
          </div>
          <div className="bg-slate-800 rounded-lg p-4 border-2 border-red-700 hover:border-red-500 transition-colors">
            <p className="text-red-300 text-sm mb-1 font-bold uppercase tracking-wide">Avg Confidence</p>
            <p className="text-3xl text-white font-bold">
              {sessions.length > 0
                ? ((sessions.reduce((acc, s) => acc + s.score, 0) / sessions.length) * 100).toFixed(0)
                : 0
              }<span className="text-lg text-slate-400">%</span>
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
