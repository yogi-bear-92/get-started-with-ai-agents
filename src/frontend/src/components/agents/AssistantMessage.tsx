import { Button, Spinner } from "@fluentui/react-components";
import { bundleIcon, DeleteFilled, DeleteRegular } from "@fluentui/react-icons";
import { Suspense } from "react";

import { Markdown } from "../core/Markdown";
import { UsageInfo } from "./UsageInfo";
import { IAssistantMessageProps } from "./chatbot/types";

import styles from "./AssistantMessage.module.css";

const DeleteIcon = bundleIcon(DeleteFilled, DeleteRegular);

export function AssistantMessage({
  message,
  agentLogo,
  loadingState,
  agentName,
  showUsageInfo,
  onDelete,
}: IAssistantMessageProps): React.JSX.Element {
  const hasAnnotations = message.annotations && message.annotations.length > 0;

  return (
    <div className={styles.assistantMessageContainer}>
      <div className={styles.messageHeader}>
        <div className={styles.avatarAndName}>
          {agentLogo && (
            <div className={styles.avatar}>
              <img src={agentLogo} alt="" className={styles.avatarImage} />
            </div>
          )}
          <span className={styles.botName}>{agentName ?? "Bot"}</span>
        </div>
        <div className={styles.actions}>
          {onDelete && message.usageInfo && (
            <Button
              appearance="transparent"
              icon={<DeleteIcon />}
              onClick={() => {
                void onDelete(message.id);
              }}
            />
          )}
        </div>
      </div>

      <div className={styles.messageContent}>
        {loadingState === "loading" ? (
          <Spinner size="small" />
        ) : (
          <Suspense fallback={<Spinner size="small" />}>
            <Markdown content={message.content} />
          </Suspense>
        )}
      </div>

      {(hasAnnotations || (showUsageInfo && message.usageInfo)) && (
        <div className={styles.messageFootnote}>
          {hasAnnotations && (
            <div className={styles.references}>
              {/* Simple reference list implementation */}
              <div className={styles.referenceList}>
                {message.annotations?.map((annotation, index) => (
                  <div key={index} className={styles.reference}>
                    {annotation.text || annotation.file_name}
                  </div>
                ))}
              </div>
            </div>
          )}

          {showUsageInfo && message.usageInfo && (
            <UsageInfo info={message.usageInfo} duration={message.duration} />
          )}
        </div>
      )}

      {message.content.includes("disclaimer") && (
        <div className={styles.disclaimer}>
          <span>AI-generated content may contain errors</span>
        </div>
      )}
    </div>
  );
}
