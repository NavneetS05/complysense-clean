// Use: Institution Admin — Compliance Calendar. Month-view timeline for all compliance deadlines and events.

import { useState, useEffect, useCallback } from "react";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { useToast } from "../../components/shared/Toast";
import { ConfirmModal } from "../../components/shared/ConfirmModal";
import { Plus, ChevronLeft, ChevronRight, Calendar as CalendarIcon, Check, Trash2 } from "lucide-react";

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
  vendor_contract_expiry: "Vendor Contract Expiry",
  audit_scheduled: "Audit Scheduled",
};

const EVENT_COLORS: Record<string, string> = {
  control_due: "#6366f1",
  assessment_scheduled: "#8b5cf6",
  evidence_expiry: "#f59e0b",
  policy_review: "#3b82f6",
  vendor_contract_expiry: "#f97316",
  audit_scheduled: "#10b981",
};

const EMPTY_FORM: EventForm = { title: "", event_type: "control_due", description: "", due_date: "" };
const DAYS_OF_WEEK = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

function isSameDay(d1: Date, d2: Date) {
  return d1.getFullYear() === d2.getFullYear() && d1.getMonth() === d2.getMonth() && d1.getDate() === d2.getDate();
}

export default function CalendarPage() {
  const { showToast } = useToast();
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
    } catch { showToast("Failed to load events", "error"); }
    setLoading(false);
  }, [currentDate]);

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
      showToast("Event created", "success");
      setShowModal(false);
      setForm(EMPTY_FORM);
      fetchEvents();
    } catch (err: any) {
      showToast(err?.response?.data?.detail ?? "Failed to create event", "error");
    }
    setModalLoading(false);
  }

  async function handleToggleComplete(event: CalendarEvent) {
    try {
      await api.patch(`/api/v1/calendar/${event.calendar_id}`, { is_completed: !event.is_completed });
      showToast(`Event marked as ${event.is_completed ? "pending" : "completed"}`, "success");
      fetchEvents();
      setSelectedEvent(null);
    } catch { showToast("Failed to update event", "error"); }
  }

  async function handleDelete() {
    if (!confirmDelete) return;
    try {
      await api.delete(`/api/v1/calendar/${confirmDelete.calendar_id}`);
      showToast("Event deleted", "success");
      setConfirmDelete(null);
      setSelectedEvent(null);
      fetchEvents();
    } catch { showToast("Failed to delete event", "error"); }
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
      subtitle="Manage all scheduled compliance events and deadlines"
      actions={
        <button className="btn btn-primary" onClick={() => { setForm(EMPTY_FORM); setFormErrors({}); setShowModal(true); }} style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <Plus size={15} /> Add Event
        </button>
      }
    >
      <div style={{ display: "grid", gridTemplateColumns: "1fr 300px", gap: 20 }}>
        {/* Calendar Grid */}
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          {/* Month Navigation */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "16px 20px", borderBottom: "1px solid var(--border)" }}>
            <button className="btn btn-ghost" onClick={() => setCurrentDate(new Date(year, month - 1, 1))} style={{ padding: "6px 10px" }}>
              <ChevronLeft size={18} />
            </button>
            <h2 style={{ fontSize: 16, fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
              {currentDate.toLocaleDateString("en-IN", { month: "long", year: "numeric" })}
            </h2>
            <button className="btn btn-ghost" onClick={() => setCurrentDate(new Date(year, month + 1, 1))} style={{ padding: "6px 10px" }}>
              <ChevronRight size={18} />
            </button>
          </div>

          {/* Day Headers */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", borderBottom: "1px solid var(--border)" }}>
            {DAYS_OF_WEEK.map((d) => (
              <div key={d} style={{ padding: "10px 0", textAlign: "center", fontSize: 12, fontWeight: 600, color: "var(--text-muted)" }}>{d}</div>
            ))}
          </div>

          {/* Calendar Days */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)" }}>
            {calendarCells.map((day, idx) => {
              if (!day) return <div key={`empty-${idx}`} style={{ minHeight: 80, borderBottom: "1px solid var(--border)", borderRight: "1px solid var(--border)" }} />;
              const dayEvents = eventsForDay(day);
              const isToday = isSameDay(day, today);
              const isSelected = selectedDay && isSameDay(day, selectedDay);
              return (
                <div
                  key={day.toISOString()}
                  onClick={() => setSelectedDay(isSelected ? null : day)}
                  style={{
                    minHeight: 80, padding: 6, borderBottom: "1px solid var(--border)", borderRight: "1px solid var(--border)",
                    cursor: "pointer", background: isSelected ? "var(--primary-bg)" : "transparent",
                    transition: "background 0.15s",
                  }}
                >
                  <div style={{
                    width: 26, height: 26, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center",
                    fontWeight: 600, fontSize: 13, marginBottom: 4,
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
                        fontSize: 10, padding: "2px 5px", borderRadius: 3, marginBottom: 2,
                        background: EVENT_COLORS[ev.event_type] ?? "var(--primary)", color: "#fff",
                        overflow: "hidden", whiteSpace: "nowrap", textOverflow: "ellipsis",
                        textDecoration: ev.is_completed ? "line-through" : "none", opacity: ev.is_completed ? 0.5 : 1,
                        cursor: "pointer",
                      }}
                    >
                      {ev.title}
                    </div>
                  ))}
                  {dayEvents.length > 2 && (
                    <div style={{ fontSize: 10, color: "var(--text-muted)" }}>+{dayEvents.length - 2} more</div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Legend */}
          <div style={{ padding: "12px 20px", borderTop: "1px solid var(--border)", display: "flex", gap: 16, flexWrap: "wrap" }}>
            {EVENT_TYPES.map((type) => (
              <div key={type} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <div style={{ width: 10, height: 10, borderRadius: 2, background: EVENT_COLORS[type], flexShrink: 0 }} />
                <span style={{ fontSize: 11, color: "var(--text-muted)" }}>{EVENT_TYPE_LABELS[type]}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Sidebar — Upcoming Events */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="card" style={{ padding: 0, overflow: "hidden" }}>
            <div style={{ padding: "14px 16px", borderBottom: "1px solid var(--border)" }}>
              <h3 style={{ fontSize: 14, fontWeight: 700, margin: 0 }}>Upcoming Events</h3>
              <select className="form-input" value={sidebarFilter} onChange={(e) => setSidebarFilter(e.target.value)} style={{ fontSize: 12, marginTop: 8 }}>
                <option value="All">All Types</option>
                {EVENT_TYPES.map((t) => <option key={t} value={t}>{EVENT_TYPE_LABELS[t]}</option>)}
              </select>
            </div>
            <div style={{ maxHeight: 400, overflowY: "auto" }}>
              {loading ? (
                Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton" style={{ height: 48, margin: "8px 12px", borderRadius: 6 }} />)
              ) : upcomingEvents.length === 0 ? (
                <div style={{ padding: "24px 16px", textAlign: "center" }}>
                  <CalendarIcon size={28} style={{ color: "var(--text-muted)", display: "block", margin: "0 auto 8px" }} />
                  <p style={{ fontSize: 12, color: "var(--text-muted)", margin: 0 }}>No upcoming events.</p>
                </div>
              ) : upcomingEvents.map((ev) => (
                <div
                  key={ev.calendar_id}
                  onClick={() => setSelectedEvent(ev)}
                  style={{ padding: "10px 14px", borderBottom: "1px solid var(--border)", cursor: "pointer", display: "flex", gap: 10, alignItems: "flex-start" }}
                >
                  <div style={{ width: 4, borderRadius: 2, background: EVENT_COLORS[ev.event_type], alignSelf: "stretch", flexShrink: 0 }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 13, fontWeight: 500, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{ev.title}</div>
                    <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
                      {new Date(ev.due_date).toLocaleDateString("en-IN", { day: "numeric", month: "short" })} · {EVENT_TYPE_LABELS[ev.event_type]}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Event Detail Panel */}
      {selectedEvent && (
        <div className="modal-overlay" onClick={() => setSelectedEvent(null)}>
          <div className="modal" style={{ maxWidth: 420 }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">{selectedEvent.title}</h2>
              <button className="modal-close" onClick={() => setSelectedEvent(null)}>×</button>
            </div>
            <div className="modal-body">
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                <div style={{ display: "flex", gap: 8 }}>
                  <span className="badge" style={{ background: EVENT_COLORS[selectedEvent.event_type], color: "#fff" }}>{EVENT_TYPE_LABELS[selectedEvent.event_type]}</span>
                  <span className={`badge ${selectedEvent.is_completed ? "badge-compliant" : "badge-in_progress"}`}>{selectedEvent.is_completed ? "Completed" : "Pending"}</span>
                </div>
                <div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 2 }}>Due Date</div>
                  <div style={{ fontSize: 14, fontWeight: 500 }}>{new Date(selectedEvent.due_date).toLocaleDateString("en-IN", { day: "numeric", month: "long", year: "numeric" })}</div>
                </div>
                {selectedEvent.description && (
                  <div>
                    <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 2 }}>Description</div>
                    <div style={{ fontSize: 13, color: "var(--text-secondary)" }}>{selectedEvent.description}</div>
                  </div>
                )}
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-ghost" onClick={() => setConfirmDelete(selectedEvent)} style={{ color: "var(--danger)", display: "flex", alignItems: "center", gap: 6 }}>
                <Trash2 size={13} /> Delete
              </button>
              <button className="btn btn-ghost" onClick={() => setSelectedEvent(null)}>Close</button>
              <button className="btn btn-primary" onClick={() => handleToggleComplete(selectedEvent)} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <Check size={14} /> {selectedEvent.is_completed ? "Mark Pending" : "Mark Complete"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Event Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Add Compliance Event</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                <div className="form-group">
                  <label className="form-label">Event Title *</label>
                  <input className={`form-input ${formErrors.title ? "input-error" : ""}`} value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="e.g. Annual DPDP audit" />
                  {formErrors.title && <span className="form-error">{formErrors.title}</span>}
                </div>
                <div className="form-group">
                  <label className="form-label">Event Type *</label>
                  <select className="form-input" value={form.event_type} onChange={(e) => setForm({ ...form, event_type: e.target.value })}>
                    {EVENT_TYPES.map((t) => <option key={t} value={t}>{EVENT_TYPE_LABELS[t]}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Due Date *</label>
                  <input type="date" className={`form-input ${formErrors.due_date ? "input-error" : ""}`} value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} />
                  {formErrors.due_date && <span className="form-error">{formErrors.due_date}</span>}
                </div>
                <div className="form-group">
                  <label className="form-label">Description</label>
                  <textarea className="form-input" rows={3} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Optional notes or instructions..." />
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-ghost" onClick={() => setShowModal(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleCreate} disabled={modalLoading}>
                {modalLoading ? "Creating..." : "Create Event"}
              </button>
            </div>
          </div>
        </div>
      )}

      {confirmDelete && (
        <ConfirmModal
          title="Delete Event"
          description={`Delete "${confirmDelete.title}"? This cannot be undone.`}
          confirmLabel="Delete"
          variant="destructive"
          onConfirm={handleDelete}
          onCancel={() => setConfirmDelete(null)}
        />
      )}
    </PageShell>
  );
}
