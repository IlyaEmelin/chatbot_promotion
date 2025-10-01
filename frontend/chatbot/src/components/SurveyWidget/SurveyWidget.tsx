import React, { useState, useEffect } from 'react';
import { Provider } from 'react-redux';
import { MessageCircle, X } from 'lucide-react';
import { store } from '../../store';
import { useAppDispatch } from '../../hooks/redux';
import { loadFromStorage } from '../../store/surveySlice';
import { storage } from '../../utils/storage';
import Chat from '../Chat/Chat';
import styles from './SurveyWidget.module.css';

const SurveyWidgetInner: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const dispatch = useAppDispatch();

  useEffect(() => {
    // Загружаем сохраненное состояние при инициализации
    const savedState = storage.load();
    if (savedState) {
      // Восстанавливаем даты в сообщениях
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
  }, [dispatch]);

  return (
    <div className={styles.container}>
      {isOpen && <Chat onClose={() => setIsOpen(false)} />}
      
      <button
        className={styles.toggleButton}
        onClick={() => setIsOpen(!isOpen)}
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
