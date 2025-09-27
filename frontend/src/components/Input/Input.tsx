import React, { useState, useRef } from 'react';
import { Send, Paperclip } from 'lucide-react';
import { useAppDispatch, useAppSelector } from '../../hooks/redux';
import { addMessage, submitAnswerAsync } from '../../store/surveySlice';
import { surveyAPI } from '../../api/surveyAPI';
import styles from './Input.module.css';

export const Input: React.FC = () => {
  const dispatch = useAppDispatch();
  const { isLoading, surveyId, isCompleted, messages } = useAppSelector(state => state.survey);
  const [inputText, setInputText] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSendMessage = async () => {
    if (!inputText.trim() || !surveyId || isLoading) return;

    // Добавляем сообщение пользователя
    dispatch(addMessage({ text: inputText, isBot: false }));
    
    // Отправляем ответ на сервер
    dispatch(submitAnswerAsync({ surveyId, answer: inputText }));
    
    setInputText('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0 || !surveyId) return;

    setIsUploading(true);
    
    try {
      const fileArray = Array.from(files);
      
      // Загружаем файлы на сервер
      const uploadPromises = fileArray.map(file => surveyAPI.uploadFile(file));
      const uploadResults = await Promise.all(uploadPromises);
      
      // Создаем текст с информацией о загруженных файлах
      const fileText = `Загружено файлов: ${fileArray.length}\n${uploadResults.map((result, i) => `${fileArray[i].name}: ${result.url}`).join('\n')}`;
      
      // Добавляем сообщение
      dispatch(addMessage({ 
        text: `Загружено файлов: ${fileArray.length}`, 
        isBot: false, 
        attachments: fileArray 
      }));
      
      // Отправляем информацию о файлах как ответ
      dispatch(submitAnswerAsync({ surveyId, answer: fileText }));
      
    } catch (error) {
      console.error('Error uploading files:', error);
      dispatch(addMessage({ 
        text: `Ошибка загрузки файлов: ${error instanceof Error ? error.message : 'Неизвестная ошибка'}`, 
        isBot: false 
      }));
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  // Проверяем, есть ли у последнего сообщения опции для выбора
  const lastMessage = messages[messages.length - 1];
  const hasOptions = lastMessage?.options && lastMessage.options.length > 0;
  
  // Скрываем поле ввода если опрос завершен или есть опции для выбора
  if (isCompleted || (hasOptions && !isLoading)) {
    return null;
  }

  const inputClass = `${styles.input} ${(isLoading || isUploading) ? styles.inputDisabled : ''}`;
  const sendButtonClass = `${styles.button} ${styles.sendButton} ${
    (isLoading || isUploading || !inputText.trim()) ? styles.sendButtonDisabled : ''
  }`;
  const fileButtonClass = `${styles.button} ${styles.fileButton} ${
    (isLoading || isUploading) ? styles.buttonDisabled : ''
  }`;

  return (
    <div className={styles.container}>
      <div className={styles.wrapper}>
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={isUploading ? "Загрузка файлов..." : "Введите ответ..."}
          className={inputClass}
          disabled={isLoading || isUploading}
        />
        
        <button
          onClick={() => fileInputRef.current?.click()}
          className={fileButtonClass}
          disabled={isLoading || isUploading}
          title="Прикрепить файл"
          type="button"
        >
          <Paperclip size={18} />
        </button>
        
        <button
          onClick={handleSendMessage}
          disabled={isLoading || isUploading || !inputText.trim()}
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