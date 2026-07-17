// Use: Assessment question wizard capturing control answers.

import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../../lib/api";
import { useApi } from "../../hooks/useApi";
import Loading from "../../components/shared/Loading";
import ErrorState from "../../components/shared/ErrorState";
import EmptyState from "../../components/shared/EmptyState";

type AssessmentData = {
  assessment_id: string;
  assessment_name: string;
  framework_name: string;
  assessment_status: string;
};

// Questions are derived from control assignments for the assessment's framework.
// We generate a stable question_id using the pattern `Q-{control_id}` so it matches
// seeded responses and backend expectations.

export default function AssessmentRunner() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: assessment, loading: loadingAssessment, error: assessmentError, refetch: refetchAssessment } = useApi<AssessmentData | null>(async () => {
    if (!id) return null as any;
    const res = await api.get(`/api/v1/assessments/${id}`);
    return res.data as AssessmentData;
  }, [id]);

  const { data: questionsData, loading: loadingQuestions, error: questionsError, refetch: refetchQuestions } = useApi(async () => {
    if (!assessment) return [] as any[];
    const res = await api.get(`/api/v1/controls`);
    const controls = Array.isArray(res.data) ? res.data : res.data?.controls ?? [];
    const relevant = controls.filter((c: any) => c.framework_name === assessment.framework_name);
    return relevant.map((c: any) => ({ id: `Q-${c.control_id}`, control_id: c.control_id, prompt: c.control_title || c.control_id }));
  }, [assessment]);

  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [notes, setNotes] = useState<Record<string, string>>({});

  const questions = (questionsData as { id: string; control_id: string; prompt: string }[]) ?? [];

  const question = questions[currentIndex];
  const progress = useMemo(() => ((currentIndex + 1) / Math.max(questions.length, 1)) * 100, [currentIndex, questions.length]);

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
          <div style={{ fontSize: 12 }}>{questions.length > 0 ? `${currentIndex + 1} of ${questions.length}` : "0 of 0"}</div>
        </div>
        <div style={{ height: 8, background: "#e2e8f0", borderRadius: 999, marginTop: 8 }}>
          <div style={{ width: `${progress}%`, height: 8, background: "var(--primary)", borderRadius: 999 }} />
        </div>
      </div>
      <div className="card" style={{ padding: 24, maxWidth: 720, margin: "0 auto" }}>
        {loadingAssessment ? (
          <Loading />
        ) : assessmentError ? (
          <ErrorState message={assessmentError.message} onRetry={() => void refetchAssessment()} />
        ) : loadingQuestions ? (
          <Loading />
        ) : questionsError ? (
          <ErrorState message={questionsError.message} onRetry={() => void refetchQuestions()} />
        ) : questions.length === 0 ? (
          <EmptyState title="No questions" description="No controls found for this assessment framework." />
        ) : question ? (
          <>
            <div style={{ color: "var(--muted)", fontSize: 12 }}>{question.control_id}</div>
            <h3 style={{ marginTop: 8 }}>{question.prompt}</h3>
          </>
        ) : null}
        <div style={{ display: "grid", gap: 8, marginTop: 16 }}>
          {[
            { value: "yes", label: "Yes — Fully implemented" },
            { value: "partial", label: "Partial — In progress" },
            { value: "no", label: "No — Not implemented" },
            { value: "na", label: "Not Applicable" },
          ].map((option) => (
            <button key={option.value} onClick={() => void saveAnswer(option.value)} style={{ textAlign: "left", padding: 12, borderRadius: 8, border: answers[question?.id ?? ''] === option.value ? "2px solid var(--primary)" : "1px solid #cbd5e1" }}>
              {option.label}
            </button>
          ))}
        </div>
        <textarea value={question ? notes[question.id] ?? "" : ""} onChange={(event) => question && setNotes((prev) => ({ ...prev, [question.id]: event.target.value }))} placeholder="Supporting notes or evidence reference" rows={3} style={{ width: "100%", marginTop: 12, padding: 8 }} />
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 16 }}>
          <button disabled={currentIndex === 0} onClick={() => setCurrentIndex((prev) => Math.max(prev - 1, 0))}>Previous</button>
          {currentIndex < questions.length - 1 ? (
            <button onClick={() => setCurrentIndex((prev) => Math.min(prev + 1, questions.length - 1))}>Next</button>
          ) : (
            <button onClick={() => void submit()}>Submit Assessment</button>
          )}
        </div>
      </div>
    </div>
  );
}
