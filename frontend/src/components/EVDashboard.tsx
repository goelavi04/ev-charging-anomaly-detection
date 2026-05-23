import { useState, useCallback } from "react";
import { StatsCards } from "./StatsCards";
import { FileUpload } from "./FileUpload";
import { AnomalyTable } from "./AnomalyTable";
import { AlertPanel } from "./AlertPanel";
import { AnomalyCharts } from "./AnomalyCharts";
import { LogsViewer } from "./LogsViewer";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Activity, FileText, DollarSign, Shield, Users, Database } from "lucide-react";
import { Button } from "./ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";

export interface EVSession {
  sessionId: string;
  chargerId: string;
  startTime: string;
  duration: number;
  energy: number;
  score: number;
  anomalyType: "fraud" | "dos" | "multiuser" | null;
  status: "critical" | "warning" | "normal";
  userId: string;
  ipAddress?: string;
  payment?: number;
}

export function EVDashboard() {
  const [sessions, setSessions] = useState<EVSession[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<EVSession | null>(null);
  const [totalDatasetRows, setTotalDatasetRows] = useState<number>(0);

  const handleFileUpload = useCallback((parsedSessions: EVSession[], totalRows = 0) => {
    setSessions(parsedSessions);
    setTotalDatasetRows(totalRows);
    const firstCritical = parsedSessions.find(s => s.status === "critical");
    if (firstCritical) {
      setSelectedAlert(firstCritical);
    }
  }, []);

  const criticalCount = sessions.filter(s => s.status === "critical").length;
  const warningCount = sessions.filter(s => s.status === "warning").length;
  const activeCount = sessions.filter(s => s.status !== "critical").length;

  const fraudSessions = sessions.filter(s => s.anomalyType === "fraud");
  const dosSessions = sessions.filter(s => s.anomalyType === "dos");
  const multiuserSessions = sessions.filter(s => s.anomalyType === "multiuser");
  const allAnomalies = sessions.filter(s => s.anomalyType !== null);

  return (
    <div className="min-h-screen bg-slate-950 text-white p-6">
      <div className="max-w-[1600px] mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Activity className="w-8 h-8 text-emerald-400" />
            <div>
              <h1 className="text-3xl text-white font-bold tracking-tight">EV Charging Anomaly Detection</h1>
              <p className="text-emerald-400 text-sm font-medium mt-1">Real-time Security Monitoring System</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Dialog>
              <DialogTrigger asChild>
                <Button className="bg-purple-600 hover:bg-purple-700">
                  <Database className="w-4 h-4 mr-2" />
                  View Logs
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-3xl bg-slate-950 border-slate-800">
                <DialogHeader>
                  <DialogTitle className="text-white">Anomaly Logs Archive</DialogTitle>
                </DialogHeader>
                <LogsViewer onLoadLog={handleFileUpload} />
              </DialogContent>
            </Dialog>
            <FileUpload onFileUpload={handleFileUpload} />
          </div>
        </div>

        <StatsCards
          activeSessions={activeCount}
          criticalAlerts={criticalCount}
          warningAlerts={warningCount}
          totalSessions={sessions.length}
          totalDatasetRows={totalDatasetRows}
          fraudCount={fraudSessions.length}
          dosCount={dosSessions.length}
          multiuserCount={multiuserSessions.length}
        />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Tabs defaultValue="all" className="w-full">
              <TabsList className="bg-slate-900 border border-slate-800 grid grid-cols-5 w-full">
                <TabsTrigger value="all" className="data-[state=active]:bg-slate-800 data-[state=active]:text-white font-semibold">
                  All Anomalies ({allAnomalies.length})
                </TabsTrigger>
                <TabsTrigger value="fraud" className="data-[state=active]:bg-red-950 data-[state=active]:text-red-300 data-[state=active]:border-red-700 font-semibold">
                  <DollarSign className="w-4 h-4 mr-1" />
                  Fraud ({fraudSessions.length})
                </TabsTrigger>
                <TabsTrigger value="dos" className="data-[state=active]:bg-purple-950 data-[state=active]:text-purple-300 data-[state=active]:border-purple-700 font-semibold">
                  <Shield className="w-4 h-4 mr-1" />
                  DoS ({dosSessions.length})
                </TabsTrigger>
                <TabsTrigger value="multiuser" className="data-[state=active]:bg-amber-950 data-[state=active]:text-amber-300 data-[state=active]:border-amber-700 font-semibold">
                  <Users className="w-4 h-4 mr-1" />
                  Multi-User ({multiuserSessions.length})
                </TabsTrigger>
                <TabsTrigger value="analytics" className="data-[state=active]:bg-blue-950 data-[state=active]:text-blue-300 data-[state=active]:border-blue-700 font-semibold">
                  Analytics
                </TabsTrigger>
              </TabsList>

              <TabsContent value="all" className="mt-4">
                <AnomalyTable
                  sessions={allAnomalies}
                  onSelectSession={setSelectedAlert}
                  selectedSessionId={selectedAlert?.sessionId}
                  title="All Detected Anomalies"
                  description="Complete list of all anomaly types"
                />
              </TabsContent>

              <TabsContent value="fraud" className="mt-4">
                <AnomalyTable
                  sessions={fraudSessions}
                  onSelectSession={setSelectedAlert}
                  selectedSessionId={selectedAlert?.sessionId}
                  title="Fraud Detection"
                  description="Ghost sessions and energy spike anomalies"
                />
              </TabsContent>

              <TabsContent value="dos" className="mt-4">
                <AnomalyTable
                  sessions={dosSessions}
                  onSelectSession={setSelectedAlert}
                  selectedSessionId={selectedAlert?.sessionId}
                  title="DoS / Burst Attack Detection"
                  description="DoS attacks and burst pattern anomalies"
                />
              </TabsContent>

              <TabsContent value="multiuser" className="mt-4">
                <AnomalyTable
                  sessions={multiuserSessions}
                  onSelectSession={setSelectedAlert}
                  selectedSessionId={selectedAlert?.sessionId}
                  title="Idle Abuse Detection"
                  description="Sessions with excessive idle time relative to charging"
                />
              </TabsContent>

              <TabsContent value="analytics" className="mt-4">
                <AnomalyCharts sessions={sessions} />
              </TabsContent>
            </Tabs>
          </div>

          <div className="lg:col-span-1">
            <AlertPanel
              session={selectedAlert}
              sessions={sessions}
              onUpdateSessions={setSessions}
            />
          </div>
        </div>

        {sessions.length === 0 && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center">
            <FileText className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl mb-2 text-slate-300">No Data Loaded</h3>
            <p className="text-slate-500">Upload a CSV file to start detecting anomalies in EV charging sessions</p>
          </div>
        )}
      </div>
    </div>
  );
}
