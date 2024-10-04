import * as React from "react";
import { createRoot } from "react-dom/client";
import { Tests } from "./tests";
import { Demo } from "./demo/demo";
import { ErrorBoundary } from "react-error-boundary";
// import { defaultClass, testContainerStyle, sprinkles } from "./style.css";

import { ErrorInfo, useMemo, useState } from "react";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { AppRootProvider, useAppRoot } from "./001_AppRootProvider";
import { LogViewer } from "./LogViewer/LogViewer";
import { JsonViewer } from "./JsonViewer/JsonViewer";
import { AppStateProvider } from "./002_AppStateProvider";
import { errorBoundaryContainer, errorBoundaryInfo, errorBoundaryMessage, errorBoundaryName, errorBoundaryTitle } from "./styles";
const container = document.getElementById("app")!;
const root = createRoot(container);

const App = () => {
    const { appMode } = useAppRoot();

    if (appMode === "ApiTest") {
        return <Tests></Tests>;
    } else if (appMode === "LogViewer") {
        return <LogViewer></LogViewer>;
    } else if (appMode === "JsonViewer") {
        const url = new URL(window.location.href);
        const params = url.searchParams;
        const jsonUrl = params.get("url") || "";
        return <JsonViewer url={jsonUrl}></JsonViewer>;
    } else {
        return (
            <AppStateProvider>
                <Demo />
            </AppStateProvider>
        );
    }
};

const AppStateWrapper = () => {
    const { guiSetting, triggerToast } = useAppRoot();

    if (guiSetting.guiSettingLoaded) {
        return (
            <>
                <App />
                <ToastContainer />
            </>
        );
    } else {
        return <>loading...</>;
    }
};

const Root = () => {
    const [error, setError] = useState<{ error: Error; errorInfo: ErrorInfo | null }>();

    const errorComponent = useMemo(() => {
        const errorName = error?.error.name || "no error name";
        const errorMessage = error?.error.message || "no error message";
        const errorInfos = (error?.errorInfo?.componentStack || "no error stack").split("\n");
        return (
            <div className={errorBoundaryContainer}>
                <div className={errorBoundaryTitle}>{"error_boundary_title"}</div>
                <div className={errorBoundaryName}>
                    {"error_boundary_name"}:{errorName}
                </div>
                <div className={errorBoundaryMessage}>
                    {"error_boundary_message"}:{errorMessage}
                </div>
                <div className={errorBoundaryInfo}>
                    {errorInfos.map((info, index) => (
                        <div key={index}>{info}</div>
                    ))}
                </div>
            </div>
        );
    }, [error]);

    const updateError = (error: Error, errorInfo: React.ErrorInfo | null) => {
        setError({ error, errorInfo });
    };

    return (
        <ErrorBoundary fallback={errorComponent} onError={updateError}>
            <AppRootProvider>
                <AppStateWrapper></AppStateWrapper>
            </AppRootProvider>
        </ErrorBoundary>
    );
};

root.render(<Root />);
