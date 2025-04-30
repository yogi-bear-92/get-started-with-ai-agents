import React, { useState } from "react";
import { AssistantMessage } from "./AssistantMessage";
import { UserMessage } from "./UserMessage";
import { ChatInput } from "./chatbot/ChatInput";
import { AgentPreviewChatBotProps } from "./chatbot/types";

import styles from "./AgentPreviewChatBot.module.css";

export function AgentPreviewChatBot({
  agentName,
  agentLogo,
  chatContext,
}: AgentPreviewChatBotProps): React.JSX.Element {
  const [currentUserMessage, setCurrentUserMessage] = useState<
    string | undefined
  >();
  const messageListFromChatContext = chatContext.messageList || [];

  const onEditMessage = (messageId: string) => {
    const selectedMessage = messageListFromChatContext.find(
      (message) => !message.isAnswer && message.id === messageId
    )?.content;
    setCurrentUserMessage(selectedMessage);
  };

  return (
    <div
      className={`${styles.chatContainer} ${
        messageListFromChatContext.length === 0 ? styles.emptyChatContainer : ""
      }`}
    >
      <div className={styles.messagesContainer}>
        {messageListFromChatContext.length > 0 ? (
          <div className={styles.copilotChatContainer}>
            {messageListFromChatContext.map((message, index, messageList) =>
              message.isAnswer ? (
                <AssistantMessage
                  key={message.id}
                  agentLogo={agentLogo}
                  agentName={agentName}
                  loadingState={
                    index === messageList.length - 1 && chatContext.isResponding
                      ? "loading"
                      : "none"
                  }
                  message={message}
                />
              ) : (
                <UserMessage
                  key={message.id}
                  message={message}
                  onEditMessage={onEditMessage}
                />
              )
            )}
          </div>
        ) : (
          <div className={styles.emptyState}>
            <h2>Start a new conversation</h2>
            <p>Type a message below to begin chatting with the AI agent</p>
          </div>
        )}
      </div>
      <div className={styles.inputContainer}>
        <ChatInput
          currentUserMessage={currentUserMessage}
          isGenerating={chatContext.isResponding}
          onSubmit={chatContext.onSend}
        />
      </div>
    </div>
  );
}
