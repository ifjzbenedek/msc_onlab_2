import { useEffect, useState } from "react";

import { checkBackendHealth } from "../api";
import { HEALTH_CHECK_INTERVAL_MS } from "../constants";

export function useBackendStatus() {
    const [isBackendReachable, setIsBackendReachable] = useState(true);

    useEffect(() => {
        checkBackendHealth().then(setIsBackendReachable);
    }, []);

    useEffect(() => {
        if (isBackendReachable) {
            return;
        }
        const timer = setInterval(async () => {
            setIsBackendReachable(await checkBackendHealth());
        }, HEALTH_CHECK_INTERVAL_MS);
        return () => clearInterval(timer);
    }, [isBackendReachable]);

    return [isBackendReachable, setIsBackendReachable] as const;
}
