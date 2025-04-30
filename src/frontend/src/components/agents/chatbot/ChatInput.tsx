import React, {
  useState,
  FormEvent,
  KeyboardEvent,
  useRef,
  useEffect,
} from "react";
import { Button, Input, Tooltip } from "@fluentui/react-components";
import {
  SendRegular,
  ArrowCounterclockwiseRegular,
} from "@fluentui/react-icons";
import { ChatInputProps } from "./types";

import styles from "./ChatInput.module.css";

export const ChatInput: React.FC<ChatInputProps> = ({
  onSubmit,
  isGenerating,
  currentUserMessage,
}) => {
  const [inputText, setInputText] = useState<string>("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (currentUserMessage !== undefined) {
      setInputText(currentUserMessage);
    }
  }, [currentUserMessage]);

  const handleSubmit = (e?: FormEvent): void => {
    e?.preventDefault();
    if (inputText.trim() && !isGenerating) {
      onSubmit(inputText.trim());
      setInputText("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>): void => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const clearChat = (): void => {
    window.location.reload();
  };

  return (
    <form onSubmit={handleSubmit} className={styles.chatInputContainer}>
      <div className={styles.inputWrapper}>
        <Tooltip content="Clear Chat" relationship="label">
          <Button
            appearance="subtle"
            icon={<ArrowCounterclockwiseRegular />}
            onClick={clearChat}
            disabled={isGenerating}
          />
        </Tooltip>

        <Input
          ref={inputRef}
          className={styles.textInput}
          placeholder="Type your message here..."
          value={inputText}
          onChange={(_, data) => setInputText(data.value)}
          onKeyDown={handleKeyDown}
          disabled={isGenerating}
        />

        <Tooltip content="Send Message" relationship="label">
          <Button
            appearance="primary"
            icon={<SendRegular />}
            type="submit"
            disabled={isGenerating || !inputText.trim()}
          />
        </Tooltip>
      </div>
    </form>
  );
};

export default ChatInput;
