import React from 'react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        self = this;
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error("[ErrorBoundary] Caught error:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div style={{
                    height: '100vh',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundColor: '#0a0a0a',
                    color: '#fff',
                    fontFamily: 'Inter, system-ui, sans-serif',
                    textAlign: 'center',
                    padding: '20px'
                }}>
                    <h1 style={{ color: '#ff4444', marginBottom: '10px' }}>⚠️ System Critical Error</h1>
                    <p style={{ color: '#aaa', maxWidth: '500px' }}>
                        The UI has encountered a fatal exception. PRALAYA-NET protection systems are stabilizing the environment.
                    </p>
                    <pre style={{
                        backgroundColor: '#1a1a1a',
                        padding: '15px',
                        borderRadius: '8px',
                        border: '1px solid #333',
                        marginTop: '20px',
                        fontSize: '12px',
                        color: '#ff4444'
                    }}>
                        {this.state.error?.toString()}
                    </pre>
                    <button
                        onClick={() => window.location.reload()}
                        style={{
                            marginTop: '30px',
                            backgroundColor: '#00cc66',
                            color: 'white',
                            border: 'none',
                            padding: '12px 24px',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontWeight: 'bold'
                        }}
                    >
                        REBOOT SYSTEM
                    </button>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
