// Use: DataTable — sortable, paginated, skeleton-loading data table component.

import { useState } from "react";
import { ChevronUp, ChevronDown, ChevronsUpDown, Inbox, ChevronLeft, ChevronRight } from "lucide-react";

export interface Column<T = Record<string, unknown>> {
  key: string;
  label: string;
  sortable?: boolean;
  width?: string;
  render?: (value: unknown, row: T) => React.ReactNode;
}

interface DataTableProps<T extends Record<string, unknown>> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  onRowClick?: (row: T) => void;
  emptyTitle?: string;
  emptyDesc?: string;
  emptyAction?: React.ReactNode;
  pageSize?: number;
  keyField?: string;
}

type SortDir = "asc" | "desc" | null;

export function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  loading = false,
  onRowClick,
  emptyTitle = "No results found",
  emptyDesc = "There are no records matching your criteria.",
  emptyAction,
  pageSize = 20,
  keyField = "id",
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<SortDir>(null);
  const [page, setPage] = useState(1);

  // Sort
  const sorted = [...data].sort((a, b) => {
    if (!sortKey || !sortDir) return 0;
    const av = a[sortKey];
    const bv = b[sortKey];
    if (av === bv) return 0;
    const cmp = String(av) < String(bv) ? -1 : 1;
    return sortDir === "asc" ? cmp : -cmp;
  });

  // Paginate
  const totalPages = Math.max(1, Math.ceil(sorted.length / pageSize));
  const paginated = sorted.slice((page - 1) * pageSize, page * pageSize);

  function handleSort(key: string) {
    if (sortKey !== key) {
      setSortKey(key);
      setSortDir("asc");
    } else if (sortDir === "asc") {
      setSortDir("desc");
    } else {
      setSortKey(null);
      setSortDir(null);
    }
    setPage(1);
  }

  function SortIcon({ col }: { col: Column<T> }) {
    if (!col.sortable) return null;
    if (sortKey !== col.key) return <ChevronsUpDown size={12} style={{ opacity: 0.4 }} />;
    if (sortDir === "asc")   return <ChevronUp size={12} />;
    return <ChevronDown size={12} />;
  }

  const skeletonWidths = [60, 85, 70, 90, 50, 80];

  return (
    <div className="data-table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                className={col.sortable ? "sortable" : ""}
                style={{ width: col.width }}
                onClick={() => col.sortable && handleSort(col.key)}
              >
                <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
                  {col.label}
                  <SortIcon col={col} />
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {loading
            ? Array.from({ length: 5 }).map((_, ri) => (
                <tr key={ri} className="skeleton-row">
                  {columns.map((col, ci) => (
                    <td key={col.key}>
                      <div
                        className="skeleton-cell"
                        style={{ width: `${skeletonWidths[(ci + ri) % skeletonWidths.length]}%` }}
                      />
                    </td>
                  ))}
                </tr>
              ))
            : paginated.length === 0
            ? (
              <tr>
                <td colSpan={columns.length}>
                  <div className="table-empty">
                    <Inbox size={48} className="table-empty-icon" />
                    <div className="table-empty-title">{emptyTitle}</div>
                    <div className="table-empty-desc">{emptyDesc}</div>
                    {emptyAction && <div style={{ marginTop: 16 }}>{emptyAction}</div>}
                  </div>
                </td>
              </tr>
            )
            : paginated.map((row, i) => (
              <tr
                key={String(row[keyField] ?? i)}
                className={onRowClick ? "clickable" : ""}
                onClick={() => onRowClick?.(row)}
              >
                {columns.map((col) => (
                  <td key={col.key}>
                    {col.render
                      ? col.render(row[col.key], row)
                      : String(row[col.key] ?? "—")}
                  </td>
                ))}
              </tr>
            ))}
        </tbody>
      </table>

      {/* Pagination */}
      {!loading && data.length > pageSize && (
        <div className="table-pagination">
          <span className="table-pagination-info">
            Showing {(page - 1) * pageSize + 1}–
            {Math.min(page * pageSize, data.length)} of {data.length} results
          </span>
          <div className="table-pagination-controls">
            <button
              className="pagination-btn"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              aria-label="Previous page"
            >
              <ChevronLeft size={14} />
            </button>
            {Array.from({ length: Math.min(7, totalPages) }).map((_, i) => {
              const pg = i + 1;
              return (
                <button
                  key={pg}
                  className={`pagination-btn ${pg === page ? "active" : ""}`}
                  onClick={() => setPage(pg)}
                >
                  {pg}
                </button>
              );
            })}
            <button
              className="pagination-btn"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              aria-label="Next page"
            >
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
