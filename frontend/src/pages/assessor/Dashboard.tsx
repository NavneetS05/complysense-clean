// Use: Real read-only compliance readiness dashboard for assessors.

import { useEffect, useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { PageShell } from "../../components/shared/PageShell";
import { api } from "../../lib/api";
import { getFrameworkColor } from "../../lib/frameworkColors";

type FrameworkReadiness = { framework: string; readiness: number; assessment_count: number };
type Risk = { title: string; framework: string; severity: string };
type Stats = {
  overall_compliance: number;
  frameworks_assessed: number;
  framework_readiness: FrameworkReadiness[];
  active_gaps_by_severity: Record<string, number>;
  incidents_this_quarter: { resolved: number; open: number };
  compliance_trend: Array<{ month: string; compliance: number }>;
};

const severityColors: Record<string, string> = {
  critical: "#dc2626",
  high: "#ea580c",
  medium: "#ca8a04",
  low: "#65a30d",
  unknown: "#64748b",
};

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [risks, setRisks] = useState<Risk[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [{ data: statsData }, { data: risksData }] = await Promise.all([
          api.get<Stats>("/api/v1/assessor/dashboard-stats"),
          api.get<Risk[]>("/api/v1/assessor/top-risks"),
        ]);
        setStats(statsData);
        setRisks(risksData);
      } catch {
        // errors handled by loading state clearing
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, []);

  const gapChart = useMemo(() => Object.entries(stats?.active_gaps_by_severity ?? {}).map(([severity, count]) => ({ severity, count })), [stats]);
  const incidentChart = stats ? [
    { status: "Open", count: stats.incidents_this_quarter.open },
    { status: "Resolved", count: stats.incidents_this_quarter.resolved },
  ] : [];
  const activeGapTotal = gapChart.reduce((sum, item) => sum + item.count, 0);

  if (loading) {
    return <section className="page-panel">Loading assessor dashboard...</section>;
  }

  return (
    <div style={{ display: "grid", gap: 16 }}>
      <PageShell title="Executive View" context="Read-only compliance posture, incidents, and risk trends." />

      <div className="grid-4">
        <Kpi title="Compliance Score" value={`${Math.round(stats?.overall_compliance ?? 0)}%`} />
        <Kpi title="Frameworks Assessed" value={String(stats?.frameworks_assessed ?? 0)} />
        <Kpi title="Active Gaps" value={String(activeGapTotal)} />
        <Kpi title="Incidents This Quarter" value={String((stats?.incidents_this_quarter.open ?? 0) + (stats?.incidents_this_quarter.resolved ?? 0))} />
      </div>

      <div className="grid-2">
        <ChartCard title="Framework Readiness">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={stats?.framework_readiness ?? []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="framework" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="readiness" radius={[4, 4, 0, 0]}>
                {(stats?.framework_readiness ?? []).map((entry, index) => {
                  const colors = getFrameworkColor(entry.framework);
                  return <Cell key={`cell-${index}`} fill={colors.text} />;
                })}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="6-Month Compliance Trend">
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={stats?.compliance_trend ?? []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Line type="monotone" dataKey="compliance" stroke="#16a34a" strokeWidth={3} dot />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="grid-2">
        <ChartCard title="Active Gaps By Severity">
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={gapChart} dataKey="count" nameKey="severity" outerRadius={90} label>
                {gapChart.map((entry) => <Cell key={entry.severity} fill={severityColors[entry.severity] ?? severityColors.unknown} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Incident Summary">
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={incidentChart}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="status" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#0891b2" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <section className="card">
        <h3 className="card-title">Top Risk Areas</h3>
        <div className="divide-y mt-3">
          {risks.length === 0 ? <p className="text-secondary-color">No active risk areas found.</p> : risks.map((risk, index) => (
            <div key={`${risk.title}-${index}`} className="flex justify-between gap-4" style={{ padding: "12px 0" }}>
              <div>
                <div className="font-semibold">{index + 1}. {risk.title}</div>
                <div className="text-sm text-secondary-color">{risk.framework}</div>
              </div>
              <span className={`badge badge-${risk.severity}`}>{risk.severity}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function Kpi({ title, value }: { title: string; value: string }) {
  return (
    <section className="stat-card">
      <div className="stat-card-label">{title}</div>
      <div className="stat-card-value">{value}</div>
    </section>
  );
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="card">
      <h3 className="card-title">{title}</h3>
      <div className="mt-3">{children}</div>
    </section>
  );
}
