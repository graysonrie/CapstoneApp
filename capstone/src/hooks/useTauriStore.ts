import { load } from "@tauri-apps/plugin-store";

export interface TauriStore {
  version: string;
}

export const tauriStoreDefaults: TauriStore = {
  version: "1",
};

async function loadStore() {
  return await load("store.json", {
    autoSave: false,
    defaults: {
      ...tauriStoreDefaults,
    },
  });
}

async function set<K extends keyof TauriStore>(key: K, value: TauriStore[K]) {
  const store = await loadStore();
  store.set(key, value);
  await store.save();
}

async function get<K extends keyof TauriStore>(key: K): Promise<TauriStore[K]> {
  const store = await loadStore();
  const val = await store.get<TauriStore[K]>(key);
  // 'val' can only be undefined if the key doesn't exist in the store,
  // but our store always initializes with all keys (may be explicitly undefined for some).
  // We cast here to silence the error because intentionally undefined is valid.
  return val as TauriStore[K];
}

export default function useTauriStore() {
  return {
    set,
    get,
  };
}
