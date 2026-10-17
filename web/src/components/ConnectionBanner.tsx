import { CONNECTION_LOST_DETAIL, CONNECTION_LOST_TITLE } from "../constants";
import { AlertIcon } from "./icons";

export function ConnectionBanner() {
    return (
        <div className="banner-area">
            <div className="connection-banner notice" role="status">
                <AlertIcon />
                <div>
                    <p className="notice-title">{CONNECTION_LOST_TITLE}</p>
                    <p className="notice-detail">{CONNECTION_LOST_DETAIL}</p>
                </div>
            </div>
        </div>
    );
}
