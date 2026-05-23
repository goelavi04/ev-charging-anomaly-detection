import { Activity, Zap, IndianRupee, Shield, Users, Bell, AlertTriangle, Database } from "lucide-react";
import { Card } from "./ui/card";

interface StatsCardsProps {
  activeSessions: number;
  criticalAlerts: number;
  warningAlerts: number;
  totalSessions: number;
  totalDatasetRows?: number;
  fraudCount?: number;
  dosCount?: number;
  multiuserCount?: number;
}

export function StatsCards({
  activeSessions,
  criticalAlerts,
  warningAlerts,
  totalSessions,
  totalDatasetRows = 0,
  fraudCount = 0,
  dosCount = 0,
  multiuserCount = 0
}: StatsCardsProps) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-emerald-600 border-emerald-500 p-6 hover:shadow-lg hover:shadow-emerald-600/20 transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-emerald-100 text-sm mb-1 font-semibold tracking-wide uppercase">Active Sessions</p>
              <p className="text-4xl text-white font-bold">{activeSessions}</p>
            </div>
            <Activity className="w-12 h-12 text-emerald-200" />
          </div>
        </Card>

        <Card className="bg-blue-600 border-blue-500 p-6 hover:shadow-lg hover:shadow-blue-600/20 transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm mb-1 font-semibold tracking-wide uppercase">Total Sessions</p>
              <p className="text-4xl text-white font-bold">{totalSessions}</p>
            </div>
            <Zap className="w-12 h-12 text-blue-200" />
          </div>
        </Card>

        <Card className="bg-red-600 border-red-500 p-6 hover:shadow-lg hover:shadow-red-600/20 transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-red-100 text-sm mb-1 font-semibold tracking-wide uppercase">Critical Alerts</p>
              <p className="text-4xl text-white font-bold">{criticalAlerts}</p>
            </div>
            <Bell className="w-12 h-12 text-red-200 animate-pulse" />
          </div>
        </Card>

        <Card className="bg-amber-600 border-amber-500 p-6 hover:shadow-lg hover:shadow-amber-600/20 transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-amber-100 text-sm mb-1 font-semibold tracking-wide uppercase">Warnings</p>
              <p className="text-4xl text-white font-bold">{warningAlerts}</p>
            </div>
            <AlertTriangle className="w-12 h-12 text-amber-200" />
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-slate-900 border-teal-700 border-2 p-5 hover:shadow-lg hover:shadow-teal-700/30 transition-all hover:border-teal-500">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Database className="w-6 h-6 text-teal-400" />
                <p className="text-white text-base font-bold tracking-wide">Dataset Entries</p>
              </div>
              <p className="text-3xl text-teal-400 font-bold">{totalDatasetRows.toLocaleString()}</p>
              <p className="text-xs text-teal-300 mt-1 font-medium">Total Rows Analysed</p>
            </div>
          </div>
        </Card>

        <Card className="bg-slate-900 border-red-700 border-2 p-5 hover:shadow-lg hover:shadow-red-700/30 transition-all hover:border-red-500">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <IndianRupee className="w-6 h-6 text-red-400" />
                <p className="text-white text-base font-bold tracking-wide">Fraud Detected</p>
              </div>
              <p className="text-3xl text-red-400 font-bold">{fraudCount}</p>
              <p className="text-xs text-red-300 mt-1 font-medium">Ghost Sessions & Energy Spikes</p>
            </div>
          </div>
        </Card>

        <Card className="bg-slate-900 border-purple-700 border-2 p-5 hover:shadow-lg hover:shadow-purple-700/30 transition-all hover:border-purple-500">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Shield className="w-6 h-6 text-purple-400" />
                <p className="text-white text-base font-bold tracking-wide">DoS / Burst Attacks</p>
              </div>
              <p className="text-3xl text-purple-400 font-bold">{dosCount}</p>
              <p className="text-xs text-purple-300 mt-1 font-medium">System Abuse Attempts</p>
            </div>
          </div>
        </Card>

        <Card className="bg-slate-900 border-amber-700 border-2 p-5 hover:shadow-lg hover:shadow-amber-700/30 transition-all hover:border-amber-500">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Users className="w-6 h-6 text-amber-400" />
                <p className="text-white text-base font-bold tracking-wide">Idle Abuse</p>
              </div>
              <p className="text-3xl text-amber-400 font-bold">{multiuserCount}</p>
              <p className="text-xs text-amber-300 mt-1 font-medium">Excessive Idle Sessions</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
