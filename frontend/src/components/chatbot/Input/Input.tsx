import React, { useState, useEffect } from 'react';
import { Send, Lock } from 'lucide-react';
import { useAppDispatch, useAppSelector } from '../../../hooks/redux';
import { addMessage, submitAnswerAsync } from '../../../services/surveySlice';
import { surveyAPI } from '../../../utils/surveyAPI';
import FileUpload from '../FileUpload/FileUpload';
import styles from './Input.module.css';
import { getUser } from '../../../services/auth/slice';
import { useSelector } from '../../../hooks/store';

export const Input: React.FC = () => {
  const dispatch = useAppDispatch();
  const { isLoading, surveyId, isCompleted, messages, status } = useAppSelector(state => state.survey);
  const [inputText, setInputText] = useState('');
  const [uploadedFilesCount, setUploadedFilesCount] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const user = useSelector(getUser);

  // ПРОВЕРКА АВТОРИЗАЦИИ
  useEffect(() => {
    if (user) {
      const authToken = sessionStorage.getItem('auth_token');
      setIsAuthenticated(!!authToken);
    }
  }, [user]);

  // ПРОВЕРЯЕМ, НУЖНА ЛИ ЗАГРУЗКА ДОКУМЕНТОВ: используем статус от сервера
  const isWaitingDocs = status === 'waiting_docs';

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
      
      let errorMessage = 'Не удалось завершить опрос. Попробуйте еще раз.';
      if (error instanceof Error) {
        if (error.message.includes('Учетные данные') || error.message.includes('401')) {
          errorMessage = 'Требуется авторизация';
        } else if (error.message.includes('403')) {
          errorMessage = 'Доступ запрещен';
        } else if (error.message.includes('404')) {
          errorMessage = 'Опрос не найден';
        } else if (error.message.includes('500')) {
          errorMessage = 'Ошибка сервера. Попробуйте позже.';
        }
      }
      
      alert(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  const lastMessage = messages[messages.length - 1];
  const hasOnlyTextOptions = lastMessage?.options && lastMessage.options.length > 0 && !lastMessage.options.includes(null);

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

  // ЕСЛИ ЕСТЬ ТОЛЬКО ТЕКСТОВЫЕ ОПЦИИ (без null) - НЕ ПОКАЗЫВАЕМ ПОЛЕ ВВОДА
  if (hasOnlyTextOptions && !isLoading) {
    return null;
  }

  const inputClass = `${styles.input} ${isLoading ? styles.inputDisabled : ''}`;
  const sendButtonClass = `${styles.button} ${styles.sendButton} ${
    (isLoading || !inputText.trim()) ? styles.sendButtonDisabled : ''
  }`;

  // НЕ ПОКАЗЫВАЕМ ИНПУТ, ЕСЛИ ЭТО ФИНАЛЬНОЕ СООБЩЕНИЕ О ЗАВЕРШЕНИИ
  const isFinalMessage = lastMessage?.text === 'Спасибо! Ваша анкета отправлена на обработку. Мы свяжемся с вами в ближайшее время.';
  if (isFinalMessage) {
    return null;
  }

  // ПОКАЗЫВАЕМ ПОЛЕ ВВОДА, ЕСЛИ НЕТ ОПЦИЙ ИЛИ ОДИН ИЗ ВАРИАНТОВ ОПЦИЙ = NULL
  const showInput = lastMessage?.options === undefined && !isLoading || lastMessage?.options && lastMessage.options.includes(null) && !isLoading
  
  return (
    showInput && (
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
    )
  )
};

export default Input;