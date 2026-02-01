import React, { useState, useEffect } from 'react';
import { Provider } from 'react-redux';
import { MessageCircle, X } from 'lucide-react';
import { store } from '../../../services/store';
import { useAppDispatch, useAppSelector } from '../../../hooks/redux';
import { loadFromStorage, resetSurvey } from '../../../services/surveySlice';
import { storage } from '../../../utils/storage';
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
    // Проверяем текущий токен авторизации и реагируем на его изменение
    const authToken = sessionStorage.getItem('auth_token') || null;

    // Если пользователь изменился - сбрасываем состояние и очищаем хранилище
    if (authToken !== currentUser) {
      console.log('🔄 Auth token changed - clearing stored survey');
      storage.clear();
      dispatch(resetSurvey());
      setCurrentUser(authToken);
      // Если новый токен есть, пробуем загрузить состояние для него
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
    } else {
      // Если токен не изменился, при первом монтировании можно загрузить состояние
      if (authToken && !currentUser) {
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
          setCurrentUser(authToken);
        }
      }
    }
  }, [dispatch, user]);

  window.addEventListener("message", (e) => {
    if (e.data?.type === "openFromTilda") {
        setIsOpen(true);
    }
  });

  return (
    <div className={styles.container}>
      {isOpen && <Chat onClose={() => {
        setIsOpen(false);
        if(isOpen && user) dispatch(logoutUser());
        window.parent.postMessage({ type: "closeChat" }, "*");
      }} />}
      
      <button
        className={styles.toggleButton}
        onClick={() => {
          if(isOpen && user) dispatch(logoutUser());
          setIsOpen(!isOpen)
          if (!isOpen) {
            // Отправляем сообщение в родительское окно, чтобы отлавливать событие из ifraim
            window.parent.postMessage({ type: "openChat" }, "*");
          } else {
            window.parent.postMessage({ type: "closeChat" }, "*");
          }
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