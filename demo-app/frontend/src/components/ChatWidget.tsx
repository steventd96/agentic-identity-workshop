import React, { useEffect } from 'react';

// Component to load the chat widget script
const ChatScriptLoader = () => {
  useEffect(() => {
    // Check if script is already loaded to prevent duplicates
    if (!document.querySelector('script[src*="langflow-embedded-chat"]')) {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/gh/logspace-ai/langflow-embedded-chat@v1.0.7/dist/build/static/js/bundle.min.js';
      script.async = true;
      document.body.appendChild(script);
      
      // Cleanup function
      return () => {
        // Only remove if we added it
        const existingScript = document.querySelector('script[src*="langflow-embedded-chat"]');
        if (existingScript && existingScript === script) {
          document.body.removeChild(script);
        }
      };
    }
  }, []);

  return null;
};

// TypeScript declaration for langflow-chat web component
declare global {
  namespace JSX {
    interface IntrinsicElements {
      'langflow-chat': any;
    }
  }
}

// Props interface for ChatWidget component
interface ChatWidgetProps {
  userToken: string;           // JWT from authState.accessToken
  flowId: string;              // Langflow flow ID
  hostUrl: string;             // Langflow backend URL
  apiKey: string;              // Langflow API key
  componentId?: string;        // Langflow component ID for tweaks
  windowTitle?: string;        // Optional chat window title
  className?: string;          // Optional CSS class
}

// ChatWidget component
export default function ChatWidget({
  userToken,
  flowId,
  hostUrl,
  apiKey,
  componentId = process.env.REACT_APP_LANGFLOW_COMPONENT_ID,
  windowTitle = 'AskHR-Agent',
  className = 'chat-widget-container'
}: ChatWidgetProps) {
  // Format tweaks as JSON string with component ID and user JWT token
  // The tweaks object structure: { "component-id": { "parameter": "value" } }
  const tweaks = JSON.stringify({
    [componentId as string]: {
      user_jwt_token: userToken
    }
  });

  return (
    <div className={className}>
      <ChatScriptLoader />
      <langflow-chat
        window_title={windowTitle}
        flow_id={flowId}
        host_url={hostUrl}
        api_key={apiKey}
        tweaks={tweaks}
      ></langflow-chat>
    </div>
  );
}

// Made with Bob