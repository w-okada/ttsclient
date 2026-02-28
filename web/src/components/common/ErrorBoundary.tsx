import { Component, type ReactNode } from "react";
import i18n from "@/i18n";

type Props = {
  children: ReactNode;
};

type State = {
  hasError: boolean;
  error: Error | null;
};

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      const t = i18n.t.bind(i18n);
      return (
        <div style={{ padding: 24, color: "red", fontFamily: "monospace" }}>
          <h2>{t("error_boundary_title")}</h2>
          <p>
            <strong>{t("error_boundary_name")}:</strong> {this.state.error?.name}
          </p>
          <p>
            <strong>{t("error_boundary_message")}:</strong> {this.state.error?.message}
          </p>
        </div>
      );
    }
    return this.props.children;
  }
}
