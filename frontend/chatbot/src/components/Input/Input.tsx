import React, { useState, useEffect } from 'react';
import { Send, Lock } from 'lucide-react';
import { useAppDispatch, useAppSelector } from '../../hooks/redux';
import { addMessage, submitAnswerAsync } from '../../store/surveySlice';
import { surveyAPI, getCookie } from '../../api/surveyAPI';
import FileUpload from '../FileUpload/FileUpload';
import styles from './Input.module.css';

export const Input: React.FC = () => {
  const dispatch = useAppDispatch();
  const { isLoading, surveyId, isCompleted, messages } = useAppSelector(state => state.survey);
  const [inputText, setInputText] = useState('');
  const [uploadedFilesCount, setUploadedFilesCount] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // ПРОВЕРКА АВТОРИЗАЦИИ
  useEffect(() => {
    const authToken = getCookie('auth_token');
    setIsAuthenticated(!!authToken);
  }, []);

  // ПРОВЕРЯЕМ current_question_text НА НАЛИЧИЕ waiting_docs
  const lastBotMessage = [...messages].reverse().find(m => m.isBot);
  const isWaitingDocs = lastBotMessage?.text?.includes('загрузим документы') || 
                        lastBotMessage?.text?.toLowerCase().includes('документ');

  // ЗАГРУЖАЕМ СУЩЕСТВУЮЩИЕ ДОКУМЕНТЫ ПРИ МОНТИРОВАНИИ
  useEffect(() => {
    if (surveyId && isWaitingDocs && isAuthenticated) {
      surveyAPI.getDocuments(surveyId)
        .then(docs => {
          setUploadedFilesCount(docs.length);
        })
        .catch(err => {
          console.error('Error loading documents:', err);
        });
    }
  }, [surveyId, isWaitingDocs, isAuthenticated]);

  const handleSendMessage = async () => {
    if (!inputText.trim() || !surveyId || isLoading || !isAuthenticated) return;

    dispatch(addMessage({ text: inputText, isBot: false }));
    dispatch(submitAnswerAsync({ surveyId, answer: inputText }));
    setInputText('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && isAuthenticated) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleUploadComplete = (documents: unknown[]) => {
    setUploadedFilesCount(documents.length);
  };

  const handleFinishSurvey = async () => {
    if (!surveyId || isProcessing || !isAuthenticated) return;

    if (!window.confirm('Вы уверены, что хотите завершить заполнение анкеты?')) {
      return;
    }

    setIsProcessing(true);

    try {
      await surveyAPI.finishSurvey(surveyId);

      dispatch(addMessage({ 
        text: 'Спасибо! Ваша анкета отправлена на обработку. Мы свяжемся с вами в ближайшее время.', 
        isBot: true 
      }));

      console.log('✅ Survey finished successfully');
    } catch (error) {
      console.error('❌ Error finishing survey:', error);
      alert('Не удалось завершить опрос. Попробуйте еще раз.');
    } finally {
      setIsProcessing(false);
    }
  };

  const lastMessage = messages[messages.length - 1];
  const hasOptions = lastMessage?.options && lastMessage.options.length > 0;
  
  if (isCompleted) {
    return null;
  }

  // ЕСЛИ НЕ АВТОРИЗОВАН - ПОКАЗЫВАЕМ СООБЩЕНИЕ
  if (!isAuthenticated) {
    return (
      <div className={styles.container}>
        <div className={styles.authWarning}>
          <Lock size={20} />
          <p>Для отправки сообщений необходимо авторизоваться</p>
        </div>
      </div>
    );
  }

  // ЕСЛИ waiting_docs - ПОКАЗЫВАЕМ ЗАГРУЗКУ И КНОПКУ ЗАВЕРШЕНИЯ
  if (isWaitingDocs) {
    return (
      <div className={styles.container}>
        {surveyId && <FileUpload onUploadComplete={handleUploadComplete} />}
        
        <button
          type="button"
          className={styles.finishButton}
          onClick={handleFinishSurvey}
          disabled={isProcessing || uploadedFilesCount === 0}
        >
          {isProcessing ? 'Отправка...' : 'Завершить заполнение анкеты'}
        </button>
        
        {uploadedFilesCount === 0 && (
          <p className={styles.uploadHint}>
            Загрузите хотя бы один документ для завершения
          </p>
        )}
      </div>
    );
  }

  // ЕСЛИ ЕСТЬ ОПЦИИ - НЕ ПОКАЗЫВАЕМ ПОЛЕ ВВОДА
  if (hasOptions && !isLoading) {
    return null;
  }

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