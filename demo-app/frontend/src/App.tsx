import React, { useState, useEffect } from 'react';
import {
  Header,
  HeaderName,
  HeaderGlobalBar,
  HeaderGlobalAction,
  Grid,
  Column,
  Button,
  Theme,
  Tile,
  Layer,
  Stack,
} from '@carbon/react';
import { Logout, UserAvatar, Chat, Security, Locked } from '@carbon/icons-react';
import './App.css';
import ChatWidget from './components/ChatWidget';

interface UserInfo {
  email?: string;
  name?: string;
  groups?: string[];
  sub?: string;
}

interface AuthState {
  isAuthenticated: boolean;
  user: UserInfo | null;
  accessToken: string | null;
  idToken: string | null;
  loading: boolean;
  error: string | null;
}

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5001';

function App() {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    accessToken: null,
    idToken: null,
    loading: true,
    error: null
  });

  useEffect(() => {
    // Check if user is already authenticated
    checkAuthStatus();
    
    // Handle OAuth callback
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');
    
    if (code && state) {
      handleCallback(code, state);
    }
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/user`, {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setAuthState({
          isAuthenticated: data.authenticated,
          user: data.user,
          accessToken: data.access_token || null,
          idToken: data.id_token || null,
          loading: false,
          error: null
        });
      } else {
        setAuthState(prev => ({ ...prev, loading: false }));
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
      setAuthState(prev => ({ ...prev, loading: false }));
    }
  };

  const handleLogin = async () => {
    try {
      setAuthState(prev => ({ ...prev, loading: true, error: null }));
      
      const response = await fetch(`${BACKEND_URL}/api/auth/login`, {
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Failed to initiate login');
      }
      
      const data = await response.json();
      
      // Redirect to IBM Verify
      window.location.href = data.auth_url;
    } catch (error) {
      console.error('Login error:', error);
      setAuthState(prev => ({
        ...prev,
        loading: false,
        error: 'Failed to initiate login. Please try again.'
      }));
    }
  };

  const handleCallback = async (code: string, state: string) => {
    try {
      setAuthState(prev => ({ ...prev, loading: true, error: null }));
      
      const response = await fetch(`${BACKEND_URL}/api/auth/callback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ code, state })
      });
      
      if (!response.ok) {
        throw new Error('Authentication failed');
      }
      
      const data = await response.json();
      
      setAuthState({
        isAuthenticated: true,
        user: data.user,
        accessToken: data.access_token,
        idToken: data.id_token,
        loading: false,
        error: null
      });
      
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
    } catch (error) {
      console.error('Callback error:', error);
      setAuthState(prev => ({
        ...prev,
        loading: false,
        error: 'Authentication failed. Please try again.'
      }));
    }
  };

  const handleLogout = async () => {
    try {
      await fetch(`${BACKEND_URL}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      });
      
      setAuthState({
        isAuthenticated: false,
        user: null,
        accessToken: null,
        idToken: null,
        loading: false,
        error: null
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  if (authState.loading) {
    return (
      <Theme theme="white">
        <div className="app-container">
          <Header aria-label="AskHR Platform">
            <HeaderName href="#" prefix="IBM">
              AskHR Assistant
            </HeaderName>
          </Header>
          <div className="main-content">
            <Grid fullWidth>
              <Column lg={16} md={8} sm={4}>
                <div className="loading-container">
                  <div className="loading-spinner"></div>
                  <p className="loading-text">Loading...</p>
                </div>
              </Column>
            </Grid>
          </div>
        </div>
      </Theme>
    );
  }

  return (
    <Theme theme="white">
      <div className="app-container">
        <Header aria-label="AskHR Platform">
          <HeaderName href="#" prefix="IBM">
            AskHR Assistant
          </HeaderName>
          <HeaderGlobalBar>
            {authState.isAuthenticated && (
              <>
                <div className="user-profile-container">
                  <UserAvatar size={20} />
                  <span className="user-name-display">
                    {authState.user?.name || authState.user?.email}
                  </span>
                </div>
                <HeaderGlobalAction
                  aria-label="Logout"
                  tooltipAlignment="end"
                  onClick={handleLogout}
                >
                  <Logout size={20} />
                </HeaderGlobalAction>
              </>
            )}
          </HeaderGlobalBar>
        </Header>

        <div className="main-content">
          {!authState.isAuthenticated ? (
            <Grid fullWidth className="login-grid">
              <Column lg={{ span: 8, offset: 4 }} md={{ span: 6, offset: 1 }} sm={4}>
                <Stack gap={7}>
                  <div className="hero-section">
                    <h1 className="hero-title">AskHR Assistant</h1>
                    <p className="hero-subtitle">
                      AI-powered HR platform with enterprise-grade security
                    </p>
                  </div>

                  {authState.error && (
                    <Tile className="error-tile">
                      <p className="error-text">{authState.error}</p>
                    </Tile>
                  )}

                  <Layer>
                    <Tile className="login-tile">
                      <Stack gap={5}>
                        <div>
                          <h2 className="tile-heading">Secure Authentication</h2>
                          <p className="tile-description">
                            Sign in with your IBM Verify credentials to access the HR Assistant. 
                            Your identity and permissions are verified through enterprise SSO.
                          </p>
                        </div>
                        <Button
                          size="lg"
                          onClick={handleLogin}
                          disabled={authState.loading}
                          renderIcon={Locked}
                        >
                          Log in with SSO
                        </Button>
                      </Stack>
                    </Tile>
                  </Layer>

                  <Grid narrow className="features-grid">
                    <Column lg={8} md={4} sm={4}>
                      <Tile className="feature-tile">
                        <Security size={32} className="feature-icon" />
                        <h3 className="feature-title">IBM Verify</h3>
                        <p className="feature-description">
                          Enterprise-grade authentication with single sign-on
                        </p>
                      </Tile>
                    </Column>
                    <Column lg={8} md={4} sm={4}>
                      <Tile className="feature-tile">
                        <Locked size={32} className="feature-icon" />
                        <h3 className="feature-title">HashiCorp Vault</h3>
                        <p className="feature-description">
                          Secure secrets management and credential rotation
                        </p>
                      </Tile>
                    </Column>
                  </Grid>
                </Stack>
              </Column>
            </Grid>
          ) : (
            <Grid fullWidth className="authenticated-grid">
              <Column lg={16} md={8} sm={4}>
                <Stack gap={6}>
                  <Layer>
                    <Tile className="welcome-tile">
                      <div className="welcome-content">
                        <div>
                          <h2 className="welcome-title">
                            Welcome, {authState.user?.name || authState.user?.email}!
                          </h2>
                          <p className="welcome-subtitle">
                            {authState.user?.email}
                            {authState.user?.groups && authState.user.groups.length > 0 && (
                              <span className="user-role"> • {authState.user.groups.join(', ')}</span>
                            )}
                          </p>
                        </div>
                        <Chat size={32} className="welcome-icon" />
                      </div>
                    </Tile>
                  </Layer>

                  <Layer>
                    <Tile className="chat-tile">
                      <Stack gap={5}>
                        <div>
                          <h3 className="chat-title">AskHR Assistant</h3>
                          <p className="chat-description">
                            Ask me anything about HR policies, employee information, or company procedures.
                            Your identity and permissions are automatically verified for secure access.
                          </p>
                        </div>
                        <div className="chat-widget-wrapper">
                          <ChatWidget
                            userToken={authState.accessToken || ''}
                            flowId={process.env.REACT_APP_LANGFLOW_FLOW_ID || '6158c23c-7d05-49db-ba6e-0b3304f7df2a'}
                            hostUrl={process.env.REACT_APP_LANGFLOW_HOST_URL || 'http://localhost:7860'}
                            apiKey={process.env.REACT_APP_LANGFLOW_API_KEY || ''}
                            componentId={process.env.REACT_APP_LANGFLOW_COMPONENT_ID || 'vault_credentials_tool-okuBC'}
                            windowTitle="AskHR Assistant"
                            className="chat-widget-container"
                          />
                        </div>
                      </Stack>
                    </Tile>
                  </Layer>
                </Stack>
              </Column>
            </Grid>
          )}

          <div className="footer">
            <p>Built by IBM Bob</p>
          </div>
        </div>
      </div>
    </Theme>
  );
}

export default App;

// Made with Bob
