import { Button, Spinner } from "@fluentui/react-components";
import { bundleIcon, DeleteFilled, DeleteRegular } from "@fluentui/react-icons";
import { CopilotMessageV2 as CopilotMessage } from "@fluentui-copilot/react-copilot-chat";
import {
  ReferenceListV2 as ReferenceList,
  ReferenceOverflowButton,
} from "@fluentui-copilot/react-reference";
import { Suspense } from "react";

import { Markdown } from "../core/Markdown";
import { UsageInfo } from "./UsageInfo";
import { IAssistantMessageProps } from "./chatbot/types";

import styles from "./AgentPreviewChatBot.module.css";
import { AgentIcon } from "./AgentIcon";

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
  const references = hasAnnotations
    ? message.annotations?.map((annotation, index) => {
        // Extract additional metadata if available
        const hasExtendedInfo = annotation.file_citation && 
                               annotation.file_citation.file && 
                               annotation.file_citation.file.metadata;
        
        // Format the citation with enhanced metadata when available
        let citationText = annotation.text || annotation.file_name;
        if (hasExtendedInfo) {
          const metadata = annotation.file_citation.file.metadata;
          const title = metadata.title || annotation.file_name;
          const section = metadata.section || '';
          const brand = metadata.brand ? `Brand: ${metadata.brand}` : '';
          const id = metadata.document_id ? `ID: ${metadata.document_id}` : '';
          
          citationText = `${title}${section ? `, Section: ${section}` : ''}${brand ? `, ${brand}` : ''}${id ? `, ${id}` : ''}`;
        }
        
        return (
          <div key={index} className="reference-item">
            {citationText}
          </div>
        );
      })
    : [];

  return (
    <CopilotMessage
      id={"msg-" + message.id}
      key={message.id}
      actions={
        <span>
          {onDelete && message.usageInfo && (
            <Button
              appearance="subtle"
              icon={<DeleteIcon />}
              onClick={() => {
                void onDelete(message.id);
              }}
            />
          )}
        </span>
      }
      avatar={<AgentIcon alt="" iconName={agentLogo} />}
      className={styles.copilotChatMessage}
      disclaimer={<span>AI-generated content may be incorrect</span>}
      footnote={
        <>
          {hasAnnotations && (
            <ReferenceList
              maxVisibleReferences={3}
              minVisibleReferences={2}
              showLessButton={
                <ReferenceOverflowButton>Show Less</ReferenceOverflowButton>
              }
              showMoreButton={
                <ReferenceOverflowButton
                  text={(overflowCount) => `+${overflowCount.toString()}`}
                />
              }
            >
              {references}
            </ReferenceList>
          )}
          {showUsageInfo && message.usageInfo && (
            <UsageInfo info={message.usageInfo} duration={message.duration} />
          )}
        </>
      }
      loadingState={loadingState}
      name={agentName ?? "Bot"}
    >
      <Suspense fallback={<Spinner size="small" />}>
        <Markdown content={message.content} />
      </Suspense>
    </CopilotMessage>
  );
}
