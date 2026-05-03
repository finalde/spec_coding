import { Component, type ReactNode } from "react";

interface Props {
  fallback: (cause: string) => ReactNode;
  children: ReactNode;
}

interface State {
  cause: string | null;
}

// REAL React Error Boundary class component (FR-19, AC-20).
// `try { return <QaView/> } catch` does NOT catch render-phase errors. This
// class with `getDerivedStateFromError` + `componentDidCatch` does.
export class QaErrorBoundary extends Component<Props, State> {
  state: State = { cause: null };

  static getDerivedStateFromError(error: Error): State {
    return { cause: error.message || "unknown parse error" };
  }

  componentDidCatch(): void {
    /* swallow — production build does not log boundary catches */
  }

  render(): ReactNode {
    if (this.state.cause !== null) {
      return this.props.fallback(this.state.cause);
    }
    return this.props.children;
  }
}
