import { useCallback, useEffect, useState } from "react";
import useTauriStore, { TauriStore, tauriStoreDefaults } from "./useTauriStore";

type SetStoreValue<K extends keyof TauriStore> = (
  value: TauriStore[K] | ((prev: TauriStore[K]) => TauriStore[K]),
) => void;

export default function useTauriStoreValue<K extends keyof TauriStore>(
  key: K,
): [TauriStore[K], SetStoreValue<K>] {
  const { get, set } = useTauriStore();
  const [value, setValueState] = useState<TauriStore[K]>(
    () => tauriStoreDefaults[key],
  );

  useEffect(() => {
    let cancelled = false;

    get(key).then((loaded) => {
      if (!cancelled) {
        setValueState(loaded);
      }
    });

    return () => {
      cancelled = true;
    };
  }, [key, get]);

  const setValue = useCallback<SetStoreValue<K>>(
    (update) => {
      setValueState((prev) => {
        const next =
          typeof update === "function"
            ? (update as (prev: TauriStore[K]) => TauriStore[K])(prev)
            : update;
        void set(key, next);
        return next;
      });
    },
    [key, set],
  );

  return [value, setValue];
}
