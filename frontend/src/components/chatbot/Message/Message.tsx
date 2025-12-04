import React from 'react';
import { Message as MessageType } from '../../../types';
import styles from './Message.module.css';

interface MessageProps {
  message: MessageType;
}

export const Message: React.FC<MessageProps> = ({ message }) => {
  const wrapperClass = message.isBot 
    ? `${styles.messageWrapper} ${styles.messageWrapperBot}`
    : `${styles.messageWrapper} ${styles.messageWrapperUser}`;
    
  const messageClass = message.isBot 
    ? `${styles.message} ${styles.messageBot}`
    : `${styles.message} ${styles.messageUser}`;

  return (
    <div className={wrapperClass}>
      <div className={messageClass}>
        <p style={{ margin: 0 }}>{message.text}</p>
        
        {message.attachments && message.attachments.length > 0 && (
          <div className={styles.attachments}>
            {message.attachments.map((file, index) => (
              <span key={index} className={styles.attachment}>
                📎 {file.name}
              </span>
            ))}
          </div>
        )}
        
        <p className={styles.timestamp}>
          {message.timestamp.toLocaleTimeString('ru-RU', { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </p>
      </div>
    </div>
  );
};

export default Message;