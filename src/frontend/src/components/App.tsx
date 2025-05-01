import React from "react";
import { FluentProvider, webLightTheme } from "@fluentui/react-components";
import { AgentPreview } from "./agents/AgentPreview";

const App: React.FC = () => {
  // Sample agent details - in a real application, this would come from an API
  const mockAgentDetails = {
    id: "sample-agent-1",
    name: "Sample AI Agent",
    description: "A helpful AI assistant",
    logo: "Avatar_Default.svg",
  };

  return (
    <FluentProvider theme={webLightTheme}>
      <div className="app-container">
        <AgentPreview
          resourceId="sample-resource-id"
          agentDetails={mockAgentDetails}
        />
      </div>
    </FluentProvider>
  );
};

export default App;
