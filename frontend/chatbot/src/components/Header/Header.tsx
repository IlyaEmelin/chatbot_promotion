import React from 'react';
import { RotateCcw, X } from 'lucide-react';
import { useAppDispatch, useAppSelector } from '../../hooks/redux';
import { resetSurvey, startSurveyAsync } from '../../store/surveySlice';
import { storage } from '../../utils/storage';
import styles from './Header.module.css';

interface HeaderProps {
  onClose: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onClose }) => {
  const dispatch = useAppDispatch();
  const { isLoading } = useAppSelector(state => state.survey);

  const handleReset = async () => {
    if (window.confirm('Вы уверены, что хотите начать заново? Все данные будут потеряны.')) {
      try {
        // 1. Очищаем localStorage
        storage.clear();
        
        // 2. Сбрасываем состояние Redux
        dispatch(resetSurvey());
        
        // 3. Создаем новый опрос с restart_question: true
        await dispatch(startSurveyAsync(true)).unwrap();
        
        console.log('✅ Опрос успешно перезапущен');
      } catch (error) {
        console.error('❌ Ошибка при перезапуске опроса:', error);
      }
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.titleBlock}>
        <h2 className={styles.title}>Оставить заявку</h2>
        <p className={styles.subtitle}>для получения помощи</p>
      </div>
      <div className={styles.actions}>
        <button
          className={styles.actionButton}
          onClick={handleReset}
          disabled={isLoading}
          title="Начать заново"
          type="button"
        >
          <RotateCcw size={18} />
        </button>
        <button
          className={styles.actionButton}
          onClick={onClose}
          title="Закрыть"
          type="button"
        >
          <X size={18} />
        </button>
      </div>
    </div>
  );
};

export default Header;