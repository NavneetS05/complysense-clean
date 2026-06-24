// Use: FileUpload — dashed-border drag-and-drop file upload zone with validation.

import { useRef, useState, useCallback } from "react";
import { UploadCloud, File, X, AlertCircle } from "lucide-react";

interface FileUploadProps {
  accept?: string;
  maxSizeMB?: number;
  onFile: (file: File) => void;
  label?: string;
  hint?: string;
  disabled?: boolean;
}

export function FileUpload({
  accept,
  maxSizeMB = 10,
  onFile,
  label = "Drop file here",
  hint,
  disabled = false,
}: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [selected, setSelected] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const validate = useCallback(
    (file: File): string | null => {
      if (maxSizeMB && file.size > maxSizeMB * 1024 * 1024) {
        return `File size exceeds ${maxSizeMB}MB limit.`;
      }
      if (accept) {
        const allowed = accept.split(",").map((s) => s.trim());
        const ext = "." + file.name.split(".").pop()?.toLowerCase();
        const mime = file.type;
        const ok = allowed.some(
          (a) => a === ext || mime.startsWith(a.replace("*", ""))
        );
        if (!ok) return `File type not allowed. Accepted: ${accept}`;
      }
      return null;
    },
    [accept, maxSizeMB]
  );

  function handle(file: File) {
    const err = validate(file);
    if (err) {
      setError(err);
      setSelected(null);
      return;
    }
    setError(null);
    setSelected(file);
    onFile(file);
  }

  function onInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (f) handle(f);
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragging(false);
    if (disabled) return;
    const f = e.dataTransfer.files?.[0];
    if (f) handle(f);
  }

  function clear(e: React.MouseEvent) {
    e.stopPropagation();
    setSelected(null);
    setError(null);
    if (inputRef.current) inputRef.current.value = "";
  }

  const sizeLabel = selected
    ? selected.size > 1024 * 1024
      ? `${(selected.size / 1024 / 1024).toFixed(1)} MB`
      : `${(selected.size / 1024).toFixed(0)} KB`
    : null;

  return (
    <div>
      <div
        className={[
          "file-upload-zone",
          dragging ? "drag-over" : "",
          selected ? "has-file" : "",
          error ? "error" : "",
          disabled ? "disabled" : "",
        ]
          .filter(Boolean)
          .join(" ")}
        onClick={() => !disabled && !selected && inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); if (!disabled) setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        role="button"
        tabIndex={disabled ? -1 : 0}
        onKeyDown={(e) => e.key === "Enter" && !disabled && !selected && inputRef.current?.click()}
        aria-label={label}
      >
        {selected ? (
          <div className="file-upload-preview">
            <File size={20} color="var(--success)" />
            <div style={{ flex: 1, textAlign: "left" }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)" }}>
                {selected.name}
              </div>
              <div style={{ fontSize: 11, color: "var(--text-secondary)" }}>{sizeLabel}</div>
            </div>
            <button
              onClick={clear}
              style={{ background: "none", border: "none", cursor: "pointer", color: "var(--text-secondary)", display: "flex" }}
              aria-label="Remove file"
            >
              <X size={16} />
            </button>
          </div>
        ) : (
          <>
            <UploadCloud size={40} className="file-upload-icon" />
            <div className="file-upload-label">{label}</div>
            <div className="file-upload-hint">
              {disabled
                ? "Upload in progress…"
                : `or click to browse${maxSizeMB ? ` · Max ${maxSizeMB}MB` : ""}`}
            </div>
            {hint && <div className="file-upload-hint" style={{ marginTop: 4 }}>{hint}</div>}
          </>
        )}
      </div>
      {error && (
        <div className="inline-error" style={{ marginTop: 6 }}>
          <AlertCircle size={12} /> {error}
        </div>
      )}
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        style={{ display: "none" }}
        onChange={onInputChange}
        disabled={disabled}
      />
    </div>
  );
}
