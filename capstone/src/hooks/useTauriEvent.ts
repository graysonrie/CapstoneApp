import { listen, UnlistenFn } from "@tauri-apps/api/event";
import { useEffect } from "react";

export default function useTauriEvent<T>(
  eventName: string,
  eventCallback: (payload: T) => void
) {
  useEffect(() => {
    let unlisten: UnlistenFn | undefined;

    const setupListener = async function () {
      unlisten = await listen<T>(eventName, (event) => {
        eventCallback(event.payload);
      });
    };

    setupListener();

    return function () {
      if (unlisten) {
        unlisten();
      }
    };
  }, [eventCallback, eventName]);
}
