import { Component, type ErrorInfo, type ReactNode } from "react";

export interface ParseFallbackProps {
  rawText: string;
  componentName: string;
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ParseFallback extends Component<ParseFallbackProps, State> {
  override state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  override componentDidCatch(error: Error, _info: ErrorInfo): void {
    // eslint-disable-next-line no-console
    console.error(`[${this.props.componentName}]`, error);
  }

  override render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="parse-fallback" role="alert">
          <div className="parse-error-banner">
            Parse error — falling back to raw text ({this.props.componentName})
          </div>
          <pre>{this.props.rawText}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}
