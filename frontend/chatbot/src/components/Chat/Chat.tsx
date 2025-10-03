import React, { useEffect, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../../hooks/redux';
import { startSurveyAsync, clearError, loadExistingSurveysAsync } from '../../store/surveySlice';
import { getCookie } from '../../api/surveyAPI';
import Header from '../Header/Header';
import Messages from '../Messages/Messages';
import Input from '../Input/Input';
import styles from './Chat.module.css';

interface ChatProps {
  onClose: () => void;
}

export const Chat: React.FC<ChatProps> = ({ onClose }) => {
  const dispatch = useAppDispatch();
  const { error, surveyId } = useAppSelector(state => state.survey);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // ПРОВЕРКА АВТОРИЗАЦИИ
  useEffect(() => {
    const authToken = getCookie('auth_token');
    setIsAuthenticated(!!authToken);
  }, []);

  useEffect(() => {
    if (!isAuthenticated) return;

    if (!surveyId) {
      dispatch(loadExistingSurveysAsync())
        .unwrap()
        .then((surveys) => {
          if (surveys.length === 0) {
            dispatch(startSurveyAsync(false));
          }
        })
        .catch(() => {
          dispatch(startSurveyAsync(false));
        });
    }
  }, [dispatch, surveyId, isAuthenticated]);

  const getErrorMessage = (error: string): string => {
    try {
      // Пытаемся распарсить JSON ошибку
      const errorObj = JSON.parse(error);
      if (errorObj.detail) {
        return errorObj.detail;
      }
      if (errorObj.message) {
        return errorObj.message;
      }
      return error;
    } catch {
      // Если не JSON, проверяем текст ошибки
      if (error.includes('Учетные данные не были предоставлены')) {
        return 'Необходимо авторизоваться';
      }
      if (error.includes('401')) {
        return 'Необходимо авторизоваться';
      }
      if (error.includes('403')) {
        return 'Доступ запрещен';
      }
      if (error.includes('404')) {
        return 'Ресурс не найден';
      }
      if (error.includes('500')) {
        return 'Ошибка сервера';
      }
      return error;
    }
  };

  return (
    <div className={styles.widget}>
      <Header onClose={onClose} />
      
      {error && (
        <div className={styles.errorMessage}>
          {getErrorMessage(error)}
          <button 
            onClick={() => dispatch(clearError())} 
            className={styles.errorCloseButton}
            type="button"
            aria-label="Закрыть ошибку"
          >
            ✕
          </button>
        </div>
      )}
      
      <Messages />
      <Input />
    </div>
  );
};

export default Chat;