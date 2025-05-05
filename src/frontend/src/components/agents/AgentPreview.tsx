import { ReactNode, useState, useMemo } from "react";
import { Body1, Button, Caption1, Title2 } from "@fluentui/react-components";
import { ChatRegular, MoreHorizontalRegular } from "@fluentui/react-icons";

import { AgentIcon } from "./AgentIcon";
import { SettingsPanel } from "../core/SettingsPanel";
import { AgentPreviewChatBot } from "./AgentPreviewChatBot";
import { MenuButton } from "../core/MenuButton/MenuButton";
import { IChatItem } from "./chatbot/types";

import styles from "./AgentPreview.module.css";

interface IAgent {
  id: string;
  name: string;
  description?: string;
  logo?: string;
}

interface IAgentPreviewProps {
  resourceId: string;
  agentDetails: IAgent;
}

export function AgentPreview({ agentDetails }: IAgentPreviewProps): ReactNode {
  const [isSettingsPanelOpen, setIsSettingsPanelOpen] = useState(false);
  const [messageList, setMessageList] = useState<IChatItem[]>([]);
  const [isResponding, setIsResponding] = useState(false);

  const handleSettingsPanelOpenChange = (isOpen: boolean) => {
    setIsSettingsPanelOpen(isOpen);
  };

  const newThread = () => {
    setMessageList([]);
  };

  const onSend = (message: string) => {
    // Add user message
    const userMessage: IChatItem = {
      id: `user-${Date.now()}`,
      content: message,
      role: "user",
      more: { time: new Date().toISOString() },
    };

    setMessageList((prev) => [...prev, userMessage]);
    setIsResponding(true);

    // Simulate agent response after a delay. Can be removed when integrating with a real API.
    setTimeout(() => {
      const botMessage: IChatItem = {
        id: `bot-${Date.now()}`,
        content: `This is a simulated response to: "${message}"`,
        isAnswer: true,
        more: { time: new Date().toISOString() },
      };

      setMessageList((prev) => [...prev, botMessage]);
      setIsResponding(false);
    }, 1000);
  };
  const menuItems = [
    {
      key: "settings",
      children: "Settings",
      onClick: () => {
        setIsSettingsPanelOpen(true);
      },
    },
    {
      key: "terms",
      children: (
        <a
          className={styles.externalLink}
          href="https://aka.ms/aistudio/terms"
          target="_blank"
          rel="noopener noreferrer"
        >
          Terms of Use
        </a>
      ),
    },
    {
      key: "privacy",
      children: (
        <a
          className={styles.externalLink}
          href="https://go.microsoft.com/fwlink/?linkid=521839"
          target="_blank"
          rel="noopener noreferrer"
        >
          Privacy
        </a>
      ),
    },
    {
      key: "feedback",
      children: "Send Feedback",
      onClick: () => {
        // Handle send feedback click
        alert("Thank you for your feedback!");
      },
    },
  ];

  const chatContext = useMemo(
    () => ({
      messageList,
      isResponding,
      onSend,
    }),
    [messageList, isResponding]
  );

  return (
    <div className={styles.container}>
      <div className={styles.topBar}>
        <div className={styles.leftSection}>
          {messageList.length > 0 && (
            <>
              <AgentIcon
                alt=""
                iconClassName={styles.agentIcon}
                iconName={agentDetails.logo}
              />
              <Body1 className={styles.agentName}>{agentDetails.name}</Body1>
            </>
          )}
        </div>
        <div className={styles.rightSection}>
          {" "}
          <Button
            appearance="subtle"
            icon={<ChatRegular aria-hidden={true} />}
            onClick={newThread}
          >
            New Chat
          </Button>{" "}
          <MenuButton
            menuButtonText=""
            menuItems={menuItems}
            menuButtonProps={{
              appearance: "subtle",
              icon: <MoreHorizontalRegular />,
              "aria-label": "Settings",
            }}
          />
        </div>
      </div>
      <div className={styles.content}>
        {messageList.length === 0 && (
          <div className={styles.emptyChatContainer}>
            <AgentIcon
              alt=""
              iconClassName={styles.emptyStateAgentIcon}
              iconName={agentDetails.logo}
            />
            <Caption1 className={styles.agentName}>
              {agentDetails.name}
            </Caption1>
            <Title2>How can I help you today?</Title2>
          </div>
        )}
        <AgentPreviewChatBot
          agentName={agentDetails.name}
          agentLogo={agentDetails.logo}
          chatContext={chatContext}
        />
      </div>

      {/* Settings Panel */}
      <SettingsPanel
        isOpen={isSettingsPanelOpen}
        onOpenChange={handleSettingsPanelOpenChange}
      />
    </div>
  );
}
