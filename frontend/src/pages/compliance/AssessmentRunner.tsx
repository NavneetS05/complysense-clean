// Use: Assessment question wizard capturing control answers.

import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../../lib/api";

type AssessmentData = {
  assessment_id: string;
  assessment_name: string;
  framework_name: string;
  assessment_status: string;
};

const QUESTIONS = [
  { id: "q1", control_id: "ISO-A.5.1", prompt: "Do you have documented information security policies approved by management?" },
  { id: "q2", control_id: "ISO-A.8.1", prompt: "Are access management processes documented and reviewed?" },
  { id: "q3", control_id: "ISO-A.12.1", prompt: "Is logging and monitoring coverage in place for critical systems?" },
];

export default function AssessmentRunner() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [assessment, setAssessment] = useState<AssessmentData | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [notes, setNotes] = useState<Record<string, string>>({});

  useEffect(() => {
    async function load() {
      if (!id) return;
      const { data } = await api.get(`/api/v1/assessments/${id}`);
      setAssessment(data);
    }
    void load();
  }, [id]);

  const question = QUESTIONS[currentIndex];
  const progress = useMemo(() => ((currentIndex + 1) / QUESTIONS.length) * 100, [currentIndex]);

  const saveAnswer = async (value: string) => {
    if (!id || !question) return;
    setAnswers((prev) => ({ ...prev, [question.id]: value }));
    await api.patch(`/api/v1/assessments/${id}/responses`, {
      question_id: question.id,
      control_id: question.control_id,
      response_value: value,
      score_value: value === "yes" ? 1 : value === "partial" ? 0.5 : 0,
    });
  };

  const submit = async () => {
    if (!id) return;
    await api.post(`/api/v1/assessments/${id}/submit`);
    navigate("/compliance/assessments");
  };

  return (
    <div style={{ padding: 16 }}>
      <div className="card" style={{ padding: 16, marginBottom: 12 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <strong>{assessment?.assessment_name ?? "Assessment"}</strong>
            <div style={{ color: "var(--muted)", fontSize: 12 }}>{assessment?.framework_name ?? "Framework"}</div>
          </div>
          <div style={{ fontSize: 12 }}>{currentIndex + 1} of {QUESTIONS.length}</div>
        </div>
        <div style={{ height: 8, background: "#e2e8f0", borderRadius: 999, marginTop: 8 }}>
          <div style={{ width: `${progress}%`, height: 8, background: "var(--primary)", borderRadius: 999 }} />
        </div>
      </div>
      <div className="card" style={{ padding: 24, maxWidth: 720, margin: "0 auto" }}>
        <div style={{ color: "var(--muted)", fontSize: 12 }}>{question.control_id}</div>
        <h3 style={{ marginTop: 8 }}>{question.prompt}</h3>
        <div style={{ display: "grid", gap: 8, marginTop: 16 }}>
          {[
            { value: "yes", label: "Yes — Fully implemented" },
            { value: "partial", label: "Partial — In progress" },
            { value: "no", label: "No — Not implemented" },
            { value: "na", label: "Not Applicable" },
          ].map((option) => (
            <button key={option.value} onClick={() => void saveAnswer(option.value)} style={{ textAlign: "left", padding: 12, borderRadius: 8, border: answers[question.id] === option.value ? "2px solid var(--primary)" : "1px solid #cbd5e1" }}>
              {option.label}
            </button>
          ))}
        </div>
        <textarea value={notes[question.id] ?? ""} onChange={(event) => setNotes((prev) => ({ ...prev, [question.id]: event.target.value }))} placeholder="Supporting notes or evidence reference" rows={3} style={{ width: "100%", marginTop: 12, padding: 8 }} />
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 16 }}>
          <button disabled={currentIndex === 0} onClick={() => setCurrentIndex((prev) => prev - 1)}>Previous</button>
          {currentIndex < QUESTIONS.length - 1 ? (
            <button onClick={() => setCurrentIndex((prev) => prev + 1)}>Next</button>
          ) : (
            <button onClick={() => void submit()}>Submit Assessment</button>
          )}
        </div>
      </div>
    </div>
  );
}
