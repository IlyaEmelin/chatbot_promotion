import React, { useState, useRef } from 'react';
import { Send, Paperclip } from 'lucide-react';
import { useAppDispatch, useAppSelector } from '../../hooks/redux';
import { addMessage, submitAnswerAsync } from '../../store/surveySlice';
import styles from './Input.module.css';

export const Input: React.FC = () => {
  const dispatch = useAppDispatch();
  const { isLoading, surveyId, isCompleted } = useAppSelector(state => state.survey);
  const [inputText, setInputText] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSendMessage = () => {
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

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0 && surveyId) {
      const fileArray = Array.from(files);
      const fileText = `Загружено файлов: ${fileArray.length}`;
      dispatch(addMessage({ text: fileText, isBot: false, attachments: fileArray }));
      dispatch(submitAnswerAsync({ surveyId, answer: fileText }));
    }
  };

  if (isCompleted) return null;

  const inputClass = `${styles.input} ${isLoading ? styles.inputDisabled : ''}`;
  const sendButtonClass = `${styles.button} ${styles.sendButton} ${
    (isLoading || !inputText.trim()) ? styles.sendButtonDisabled : ''
  }`;

  return (
    <div className={styles.container}>
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
          onClick={() => fileInputRef.current?.click()}
          className={`${styles.button} ${styles.fileButton}`}
          disabled={isLoading}
          title="Прикрепить файл"
          type="button"
        >
          <Paperclip size={18} />
        </button>
        
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
      
      <input
        ref={fileInputRef}
        type="file"
        onChange={handleFileUpload}
        multiple
        className={styles.hiddenInput}
        accept="image/*,.pdf,.doc,.docx"
      />
    </div>
  );
};

export default Input;
