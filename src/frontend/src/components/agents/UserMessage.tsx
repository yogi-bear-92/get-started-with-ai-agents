import { Spinner, ToolbarButton } from "@fluentui/react-components";
import { bundleIcon, EditFilled, EditRegular } from "@fluentui/react-icons";
import { Suspense } from "react";

import { Markdown } from "../core/Markdown";
import { useFormatTimestamp } from "./hooks/useFormatTimestamp";
import { IUserMessageProps } from "./chatbot/types";

import styles from "./UserMessage.module.css";

const EditIcon = bundleIcon(EditFilled, EditRegular);

export function UserMessage({
  message,
  onAttachmentPreview,
  onRemoveAttachment,
  onEditMessage,
}: IUserMessageProps): JSX.Element {
  const formatTimestamp = useFormatTimestamp();

  return (
    <div className={styles.userMessageContainer}>
      <div className={styles.userMessageHeader}>
        <div className={styles.userInfo}>
          <div className={styles.userAvatar}>
            <span>User</span>
          </div>
          {message.more?.time && (
            <span className={styles.timestamp}>
              {formatTimestamp(new Date(message.more.time))}
            </span>
          )}
        </div>
        <div className={styles.messageActions}>
          <ToolbarButton
            appearance="transparent"
            icon={<EditIcon />}
            onClick={() => {
              onEditMessage(message.id);
            }}
          />
        </div>
      </div>

      <div className={styles.messageContent}>
        <Suspense fallback={<Spinner size="small" />}>
          <Markdown content={message.content} />

          {message.message_files && message.message_files.length > 0 && (
            <div className={styles.attachments}>
              {message.message_files.map((file) => (
                <div key={file.id} className={styles.attachment}>
                  <div
                    className={styles.attachmentName}
                    onClick={() => onAttachmentPreview?.(file)}
                  >
                    {file.name}
                  </div>
                  {onRemoveAttachment && (
                    <button
                      className={styles.removeButton}
                      onClick={() => onRemoveAttachment(message.id, file.id)}
                    >
                      ✕
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </Suspense>
      </div>
    </div>
  );
}
