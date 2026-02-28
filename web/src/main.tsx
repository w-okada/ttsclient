import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "@/styles/global.css";
import "@/i18n";
import { App } from "./App";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
    <ToastContainer position="bottom-right" autoClose={3000} hideProgressBar newestOnTop />
  </StrictMode>,
);
