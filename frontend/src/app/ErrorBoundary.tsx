import { Component, type ErrorInfo, type ReactNode } from "react";

export class ErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch(error: Error, info: ErrorInfo) { console.error("MileLedger UI error", error, info); }
  render() {
    if (this.state.failed) return <main className="fatal"><p className="eyebrow">Workspace interrupted</p><h1>The trip view could not be drawn.</h1><p>Your plan has not been changed. Refresh the page and try again.</p></main>;
    return this.props.children;
  }
}

