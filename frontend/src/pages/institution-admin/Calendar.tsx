// Use: Institution Admin — Compliance Calendar. Month-view timeline for all compliance deadlines and events.

import { useState, useEffect, useCallback } from "react";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { useToast } from "../../components/shared/ToastContext";
import { getApiErrorMessage } from "../../lib/errors";
import { ConfirmModal } from "../../components/shared/ConfirmModal";
import { Plus, ChevronLeft, ChevronRight, Calendar as CalendarIcon, Check, Trash2, Info, Tag } from "lucide-react";

interface CalendarEvent {
  calendar_id: string;
  title: string;
  event_type: string;
  description: string | null;
  due_date: string;
  is_completed: boolean;
  created_at: string;
}

interface EventForm {
  title: string;
  event_type: string;
  description: string;
  due_date: string;
}

const EVENT_TYPES = [
  "control_due", "assessment_scheduled", "evidence_expiry",
  "policy_review", "vendor_contract_expiry", "audit_scheduled",
];

const EVENT_TYPE_LABELS: Record<string, string> = {
  control_due: "Control Due",
  assessment_scheduled: "Assessment Scheduled",
  evidence_expiry: "Evidence Expiry",
  policy_review: "Policy Review",
  vendor_contract_expiry: "Vendor Expiry",
  audit_scheduled: "Audit Scheduled",
};

const EVENT_COLORS: Record<string, string> = {
  control_due: "#2563EB",
  assessment_scheduled: "#7C3AED",
  evidence_expiry: "#D97706",
  policy_review: "#0284C7",
  vendor_contract_expiry: "#EA580C",
  audit_scheduled: "#059669",
};

const EMPTY_FORM: EventForm = { title: "", event_type: "control_due", description: "", due_date: "" };
const DAYS_OF_WEEK = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

function isSameDay(d1: Date, d2: Date) {
  return d1.getFullYear() === d2.getFullYear() && d1.getMonth() === d2.getMonth() && d1.getDate() === d2.getDate();
}

export default function CalendarPage() {
  const toast = useToast();
  const today = new Date();
  const [currentDate, setCurrentDate] = useState(new Date(today.getFullYear(), today.getMonth(), 1));
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [form, setForm] = useState<EventForm>(EMPTY_FORM);
  const [formErrors, setFormErrors] = useState<Partial<EventForm>>({});
  const [selectedDay, setSelectedDay] = useState<Date | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<CalendarEvent | null>(null);
  const [sidebarFilter, setSidebarFilter] = useState("All");

  const fetchEvents = useCallback(async () => {
    setLoading(true);
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth() + 1;
    try {
      const res = await api.get("/api/v1/calendar", { params: { year, month } });
      setEvents(res.data ?? []);
    } catch { toast.error("Failed to load events"); }
    setLoading(false);
  }, [currentDate, toast]);

  useEffect(() => { fetchEvents(); }, [fetchEvents]);

  function validateForm(): boolean {
    const errors: Partial<EventForm> = {};
    if (!form.title.trim()) errors.title = "Title is required";
    if (!form.due_date) errors.due_date = "Due date is required";
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleCreate() {
    if (!validateForm()) return;
    setModalLoading(true);
    try {
      await api.post("/api/v1/calendar", form);
      toast.success("Event created successfully");
      setShowModal(false);
      setForm(EMPTY_FORM);
      fetchEvents();
    } catch (err: unknown) {
      toast.error(getApiErrorMessage(err, "Failed to create event"));
    }
    setModalLoading(false);
  }

  async function handleToggleComplete(event: CalendarEvent) {
    try {
      await api.patch(`/api/v1/calendar/${event.calendar_id}`, { is_completed: !event.is_completed });
      toast.success(`Event marked as ${event.is_completed ? "pending" : "completed"}`);
      fetchEvents();
      setSelectedEvent(null);
    } catch { toast.error("Failed to update event"); }
  }

  async function handleDelete() {
    if (!confirmDelete) return;
    try {
      await api.delete(`/api/v1/calendar/${confirmDelete.calendar_id}`);
      toast.success("Event deleted");
      setConfirmDelete(null);
      setSelectedEvent(null);
      fetchEvents();
    } catch { toast.error("Failed to delete event"); }
  }

  // Calendar grid
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();
  const firstDayOfMonth = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const calendarCells: (Date | null)[] = [
    ...Array.from({ length: firstDayOfMonth }).map(() => null),
    ...Array.from({ length: daysInMonth }).map((_, i) => new Date(year, month, i + 1)),
  ];

  const eventsForDay = (day: Date): CalendarEvent[] =>
    events.filter((e) => isSameDay(new Date(e.due_date), day));

  const upcomingEvents = events
    .filter((e) => !e.is_completed && new Date(e.due_date) >= today && (sidebarFilter === "All" || e.event_type === sidebarFilter))
    .sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime())
    .slice(0, 20);

  return (
    <PageShell
      title="Compliance Calendar"
      subtitle="Track institutional deadlines, audits, control reviews, and evidence expiries."
      actions={
        <button className="btn btn-primary" onClick={() => { setForm(EMPTY_FORM); setFormErrors({}); setShowModal(true); }}>
          <Plus size={15} /> Add Event
        </button>
      }
    >
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 20 }}>
        {/* Calendar Grid Container */}
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          {/* Month Navigation Header */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "16px 20px", borderBottom: "1px solid var(--border)" }}>
            <button className="btn btn-ghost btn-sm" onClick={() => setCurrentDate(new Date(year, month - 1, 1))}>
              <ChevronLeft size={18} />
            </button>
            <h2 style={{ fontSize: 16, fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
              {currentDate.toLocaleDateString("en-IN", { month: "long", year: "numeric" })}
            </h2>
            <button className="btn btn-ghost btn-sm" onClick={() => setCurrentDate(new Date(year, month + 1, 1))}>
              <ChevronRight size={18} />
            </button>
          </div>

          {/* Day Headers */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", borderBottom: "1px solid var(--border)", background: "var(--surface-secondary)" }}>
            {DAYS_OF_WEEK.map((d) => (
              <div key={d} style={{ padding: "8px 0", textAlign: "center", fontSize: 11, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase" }}>{d}</div>
            ))}
          </div>

          {/* Calendar Day Cells */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)" }}>
            {calendarCells.map((day, idx) => {
              if (!day) return <div key={`empty-${idx}`} style={{ minHeight: 85, borderBottom: "1px solid var(--border)", borderRight: "1px solid var(--border)", background: "var(--background)" }} />;
              const dayEvents = eventsForDay(day);
              const isToday = isSameDay(day, today);
              const isSelected = selectedDay && isSameDay(day, selectedDay);
              return (
                <div
                  key={day.toISOString()}
                  onClick={() => setSelectedDay(isSelected ? null : day)}
                  style={{
                    minHeight: 85, padding: 6, borderBottom: "1px solid var(--border)", borderRight: "1px solid var(--border)",
                    cursor: "pointer", background: isSelected ? "var(--primary-light)" : "var(--surface)",
                    transition: "background var(--transition-fast)",
                  }}
                >
                  <div style={{
                    width: 24, height: 24, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center",
                    fontWeight: 700, fontSize: 12, marginBottom: 4,
                    background: isToday ? "var(--primary)" : "transparent",
                    color: isToday ? "#fff" : "var(--text-primary)",
                  }}>
                    {day.getDate()}
                  </div>
                  {dayEvents.slice(0, 2).map((ev) => (
                    <div
                      key={ev.calendar_id}
                      onClick={(e) => { e.stopPropagation(); setSelectedEvent(ev); }}
                      style={{
                        fontSize: 10, padding: "3px 6px", borderRadius: "var(--radius-sm)", marginBottom: 3,
                        background: EVENT_COLORS[ev.event_type] ?? "var(--primary)", color: "#fff",
                        overflow: "hidden", whiteSpace: "nowrap", textOverflow: "ellipsis",
                        fontWeight: 600,
                        textDecoration: ev.is_completed ? "line-through" : "none", opacity: ev.is_completed ? 0.6 : 1,
                        cursor: "pointer",
                      }}
                    >
                      {ev.title}
                    </div>
                  ))}
                  {dayEvents.length > 2 && (
                    <div style={{ fontSize: 10, color: "var(--text-secondary)", fontWeight: 600, marginTop: 2 }}>+{dayEvents.length - 2} more</div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Legend */}
          <div style={{ padding: "12px 16px", borderTop: "1px solid var(--border)", display: "flex", gap: 12, flexWrap: "wrap", background: "var(--surface)" }}>
            {EVENT_TYPES.map((type) => (
              <div key={type} style={{ display: "flex", alignItems: "center", gap: 5 }}>
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: EVENT_COLORS[type], flexShrink: 0 }} />
                <span style={{ fontSize: 11, color: "var(--text-secondary)", fontWeight: 500 }}>{EVENT_TYPE_LABELS[type]}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Sidebar — Upcoming Deadlines & Filter */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="card" style={{ padding: 0, overflow: "hidden" }}>
            <div style={{ padding: "14px 16px", borderBottom: "1px solid var(--border)", background: "var(--surface)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                <CalendarIcon size={16} style={{ color: "var(--primary)" }} />
                <h3 style={{ fontSize: 14, fontWeight: 700, margin: 0, color: "var(--text-primary)" }}>Upcoming Deadlines</h3>
              </div>
              <select className="filter-select" value={sidebarFilter} onChange={(e) => setSidebarFilter(e.target.value)} style={{ width: "100%" }}>
                <option value="All">All Event Types</option>
                {EVENT_TYPES.map((t) => <option key={t} value={t}>{EVENT_TYPE_LABELS[t]}</option>)}
              </select>
            </div>
            <div style={{ maxHeight: 440, overflowY: "auto" }}>
              {loading ? (
                Array.from({ length: 4 }).map((_, i) => <div key={i} className="skeleton" style={{ height: 48, margin: "8px 12px", borderRadius: 6 }} />)
              ) : upcomingEvents.length === 0 ? (
                <div style={{ padding: "32px 16px", textAlign: "center" }}>
                  <CalendarIcon size={28} style={{ color: "var(--muted)", display: "block", margin: "0 auto 8px" }} />
                  <p style={{ fontSize: 13, color: "var(--text-secondary)", margin: 0 }}>No upcoming deadlines matching filter.</p>
                </div>
              ) : upcomingEvents.map((ev) => (
                <div
                  key={ev.calendar_id}
                  onClick={() => setSelectedEvent(ev)}
                  style={{ padding: "12px 16px", borderBottom: "1px solid var(--border)", cursor: "pointer", display: "flex", gap: 12, alignItems: "center" }}
                >
                  <div style={{ width: 4, height: 32, borderRadius: 2, background: EVENT_COLORS[ev.event_type], flexShrink: 0 }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{ev.title}</div>
                    <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 2, display: "flex", alignItems: "center", gap: 6 }}>
                      <span>{new Date(ev.due_date).toLocaleDateString("en-IN", { day: "numeric", month: "short" })}</span>
                      <span>·</span>
                      <span>{EVENT_TYPE_LABELS[ev.event_type]}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Event Detail Modal */}
      {selectedEvent && (
        <div className="modal-overlay" onClick={() => setSelectedEvent(null)}>
          <div className="modal" style={{ maxWidth: 440, width: "100%" }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">{selectedEvent.title}</h2>
              <button className="modal-close" onClick={() => setSelectedEvent(null)}>×</button>
            </div>
            <div className="modal-body">
              <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  <span className="badge" style={{ background: EVENT_COLORS[selectedEvent.event_type], color: "#fff" }}>
                    <Tag size={11} /> {EVENT_TYPE_LABELS[selectedEvent.event_type]}
                  </span>
                  <span className={`badge ${selectedEvent.is_completed ? "badge-compliant" : "badge-in_progress"}`}>
                    {selectedEvent.is_completed ? "Completed" : "Pending"}
                  </span>
                </div>
                <div>
                  <div style={{ fontSize: 11, fontWeight: 600, color: "var(--text-secondary)", textTransform: "uppercase" }}>Scheduled Date</div>
                  <div style={{ fontSize: 14, fontWeight: 600, color: "var(--text-primary)", marginTop: 2 }}>
                    {new Date(selectedEvent.due_date).toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long", year: "numeric" })}
                  </div>
                </div>
                {selectedEvent.description && (
                  <div>
                    <div style={{ fontSize: 11, fontWeight: 600, color: "var(--text-secondary)", textTransform: "uppercase" }}>Notes & Instructions</div>
                    <div style={{ fontSize: 13, color: "var(--text-primary)", marginTop: 4, background: "var(--surface-secondary)", padding: 10, borderRadius: "var(--radius-md)" }}>
                      {selectedEvent.description}
                    </div>
                  </div>
                )}
              </div>
            </div>
            <div className="modal-footer" style={{ justifyContent: "space-between" }}>
              <button className="btn btn-ghost" onClick={() => setConfirmDelete(selectedEvent)} style={{ color: "var(--critical)" }}>
                <Trash2 size={14} /> Delete
              </button>
              <div style={{ display: "flex", gap: 8 }}>
                <button className="btn btn-secondary" onClick={() => setSelectedEvent(null)}>Close</button>
                <button className="btn btn-primary" onClick={() => handleToggleComplete(selectedEvent)}>
                  <Check size={14} /> {selectedEvent.is_completed ? "Mark Pending" : "Mark Complete"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Event Modal with Step-by-Step Guidance */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" style={{ maxWidth: 520, width: "100%" }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Schedule Compliance Event</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
            </div>
            <div className="modal-body">
              {/* Step-by-step guidance header */}
              <div className="guidance-banner" style={{ marginBottom: 16, padding: "12px 14px" }}>
                <div className="guidance-header">
                  <Info size={16} /> How to Schedule an Event
                </div>
                <div style={{ fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.5 }}>
                  Add a compliance deadline to notify responsible teams. Events appear on institution dashboards and calendar timelines.
                </div>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                <div className="form-group">
                  <label className="form-label form-label-required">Event Title</label>
                  <input
                    className={`form-input ${formErrors.title ? "input-error" : ""}`}
                    value={form.title}
                    onChange={(e) => setForm({ ...form, title: e.target.value })}
                    placeholder="e.g. Annual DPDP Data Protection Audit"
                  />
                  {formErrors.title && <span className="form-error">{formErrors.title}</span>}
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
                  <div className="form-group">
                    <label className="form-label form-label-required">Event Category</label>
                    <select className="filter-select" style={{ width: "100%" }} value={form.event_type} onChange={(e) => setForm({ ...form, event_type: e.target.value })}>
                      {EVENT_TYPES.map((t) => <option key={t} value={t}>{EVENT_TYPE_LABELS[t]}</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label form-label-required">Due Date</label>
                    <input
                      type="date"
                      className={`form-input ${formErrors.due_date ? "input-error" : ""}`}
                      value={form.due_date}
                      onChange={(e) => setForm({ ...form, due_date: e.target.value })}
                    />
                    {formErrors.due_date && <span className="form-error">{formErrors.due_date}</span>}
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Description & Guidelines</label>
                  <textarea
                    className="form-input"
                    rows={3}
                    style={{ height: "auto", padding: "8px 12px" }}
                    value={form.description}
                    onChange={(e) => setForm({ ...form, description: e.target.value })}
                    placeholder="Provide context, required evidence types, or auditor instructions..."
                  />
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleCreate} disabled={modalLoading}>
                {modalLoading ? "Creating Event..." : "Create Event"}
              </button>
            </div>
          </div>
        </div>
      )}

      <ConfirmModal
        open={!!confirmDelete}
        title="Delete Event"
        description={confirmDelete ? `Delete "${confirmDelete.title}"? This action cannot be undone.` : ""}
        confirmLabel="Delete Event"
        confirmVariant="destructive"
        onConfirm={handleDelete}
        onCancel={() => setConfirmDelete(null)}
      />
    </PageShell>
  );
}
