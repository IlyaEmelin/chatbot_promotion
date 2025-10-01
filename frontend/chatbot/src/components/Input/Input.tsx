import React, { useState } from 'react';
import { Send } from 'lucide-react';
import { useAppDispatch, useAppSelector } from '../../hooks/redux';
import { addMessage, submitAnswerAsync } from '../../store/surveySlice';
import FileUpload from '../FileUpload/FileUpload';
import styles from './Input.module.css';

export const Input: React.FC = () => {
  const dispatch = useAppDispatch();
  const { isLoading, surveyId, isCompleted, messages } = useAppSelector(state => state.survey);
  const [inputText, setInputText] = useState('');

  const handleSendMessage = async () => {
    if (!inputText.trim() || !surveyId || isLoading) return;

    dispatch(addMessage({ text: inputText, isBot: false }));
    dispatch(submitAnswerAsync({ surveyId, answer: inputText }));
    setInputText('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleUploadComplete = (documents: any[]) => {
    console.log('Files uploaded:', documents);
    // Можно отправить уведомление боту о загрузке файлов
    if (surveyId && documents.length > 0) {
      const fileNames = documents.map(d => d.file_name || 'файл').join(', ');
      dispatch(addMessage({ 
        text: `Загружено файлов: ${documents.length} (${fileNames})`, 
        isBot: false 
      }));
    }
  };

  const lastMessage = messages[messages.length - 1];
  const hasOptions = lastMessage?.options && lastMessage.options.length > 0;
  
  if (isCompleted || (hasOptions && !isLoading)) {
    return null;
  }

  const inputClass = `${styles.input} ${isLoading ? styles.inputDisabled : ''}`;
  const sendButtonClass = `${styles.button} ${styles.sendButton} ${
    (isLoading || !inputText.trim()) ? styles.sendButtonDisabled : ''
  }`;

  return (
    <div className={styles.container}>
      {/* Компонент загрузки файлов */}
      {surveyId && <FileUpload onUploadComplete={handleUploadComplete} />}
      
      <div className={styles.wrapper}>
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Введите ответ..."
          className={inputClass}
          disabled={isLoading}
        />
        
        <button
          onClick={handleSendMessage}
          disabled={isLoading || !inputText.trim()}
          className={sendButtonClass}
          title="Отправить"
          type="button"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
};

export default Input;