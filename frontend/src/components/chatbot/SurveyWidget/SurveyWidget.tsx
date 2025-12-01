import React, { useState, useEffect } from 'react';
import { Provider } from 'react-redux';
import { MessageCircle, X } from 'lucide-react';
import { store } from '../../../services/store';
import { useAppDispatch, useAppSelector } from '../../../hooks/redux';
import { loadFromStorage, resetSurvey } from '../../../services/surveySlice';
import { storage } from '../../../utils/storage';
import { getCookie } from '../../../utils/surveyAPI';
import Chat from '../Chat/Chat';
import styles from './SurveyWidget.module.css';
import { logoutUser } from '../../../services/auth/action';
import { getUser } from '../../../services/auth/slice';

const SurveyWidgetInner: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState<string | null>(null);
  const dispatch = useAppDispatch();
  const user = useAppSelector(getUser);

  useEffect(() => {
    // Проверяем текущего пользователя
    const authToken = getCookie('auth_token');
    
    // Если пользователь изменился - сбрасываем состояние
    if (authToken !== currentUser) {
      storage.clear();
      dispatch(resetSurvey());
      setCurrentUser(authToken || null);
      return;
    }
    
    // Загружаем сохраненное состояние только если пользователь тот же
    if (authToken) {
      const savedState = storage.load();
      if (savedState) {
        const messagesWithDates = savedState.messages.map(msg => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }));
        
        dispatch(loadFromStorage({
          ...savedState,
          messages: messagesWithDates,
          isLoading: false,
          error: null
        }));
      }
    }
  }, [dispatch, currentUser]);

  // Следим за изменением токена авторизации
  useEffect(() => {
    const checkAuthInterval = setInterval(() => {
      const authToken = getCookie('auth_token');
      if (authToken !== currentUser) {
        console.log('🔄 Auth token changed');
        setCurrentUser(authToken || null);
      }
    }, 1000); // Проверяем каждую секунду

    return () => clearInterval(checkAuthInterval);
  }, [currentUser]);

  return (
    <div className={styles.container}>
      {isOpen && <Chat onClose={() => {
        setIsOpen(false);
        if(isOpen && user) dispatch(logoutUser())
      }} />}
      
      <button
        className={styles.toggleButton}
        onClick={() => {
          if(isOpen && user) dispatch(logoutUser());
          setIsOpen(!isOpen)
        }}
        title={isOpen ? 'Закрыть чат' : 'Открыть чат'}
        type="button"
        aria-label={isOpen ? 'Закрыть чат' : 'Открыть чат'}
      >
        {isOpen ? <X size={24} /> : <MessageCircle size={24} />}
      </button>
    </div>
  );
};

export const SurveyWidget: React.FC = () => {
  return (
    <Provider store={store}>
      <SurveyWidgetInner />
    </Provider>
  );
};

export default SurveyWidget;