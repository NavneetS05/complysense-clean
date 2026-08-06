import { useCallback, useEffect, useRef, useState, type DependencyList } from "react";

export function useApi<T>(fn: () => Promise<T>, deps: DependencyList = []) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Keep fn in a ref so the callback always calls the latest version
  // without needing fn in the dependency array (which would cause infinite loops
  // when callers pass inline arrow functions).
  const fnRef = useRef(fn);
  fnRef.current = fn;

  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fnRef.current();
      setData(res);
      return res;
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
      throw err;
    } finally {
      setLoading(false);
    }
  }, deps); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    void fetch();
  }, [fetch]);

  return { data, loading, error, refetch: fetch };
}
