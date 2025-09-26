import React, { useEffect, useRef } from 'react';
import { useAppSelector } from '../../hooks/redux';
import Message from '../Message/Message';
import Options from '../Options/Options';
import Loading from '../Loading/Loading';
import styles from './Messages.module.css';

export const Messages: React.FC = () => {
  const { messages, isLoading } = useAppSelector(state => state.survey);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const lastMessage = messages[messages.length - 1];

  return (
    <div className={styles.container}>
      {messages.map((message) => (
        <Message key={message.id} message={message} />
      ))}

      {lastMessage?.options && !isLoading && (
        <Options options={lastMessage.options} />
      )}

      {isLoading && <Loading />}
      
      <div ref={messagesEndRef} />
    </div>
  );
};

export default Messages;