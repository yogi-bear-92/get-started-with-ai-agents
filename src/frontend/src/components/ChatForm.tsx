import React, { useState, FormEvent, ChangeEvent } from 'react';

interface ChatFormProps {
  onSubmit: (message: string) => void;
  isGenerating: boolean;
}

const ChatForm: React.FC<ChatFormProps> = ({ onSubmit, isGenerating }) => {
  const [message, setMessage] = useState<string>('');

  const handleSubmit = (e: FormEvent<HTMLFormElement>): void => {
    e.preventDefault();
    if (message.trim() && !isGenerating) {
      onSubmit(message);
      setMessage('');
    }
  };

  const clearChat = (): void => {
    // We'll implement this to match the existing functionality
    window.location.reload();
  };

  return (
    <div id="chat-area" className="text-light px-4 py-2 rounded-top text-dark d-flex flex-column justify-content-center background-user">
      <form id="chat-form" onSubmit={handleSubmit}>
        <div className="input-group">
          <button 
            type="button" 
            className="btn btn-outline-dark" 
            onClick={clearChat}>
            <i className="bi bi-arrow-repeat"></i>
          </button>
          <i className="bi bi-body-text input-group-text dark-border"></i>
          <input 
            id="message" 
            name="message" 
            className="form-control form-control-sm dark-border" 
            type="text" 
            placeholder="Your Message"
            value={message}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setMessage(e.target.value)}
            disabled={isGenerating}
          />
          <button 
            type="submit" 
            className="btn btn-outline-dark" 
            style={{ borderLeftWidth: 0 }}
            disabled={isGenerating}>
            Send <i className="bi bi-send-fill"></i>
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatForm;