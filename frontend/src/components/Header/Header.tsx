import React from 'react';
import { RotateCcw, X } from 'lucide-react';
import { useAppDispatch, useAppSelector } from '../../hooks/redux';
import { resetSurvey, startSurveyAsync } from '../../store/surveySlice';
import styles from './Header.module.css';

interface HeaderProps {
  onClose: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onClose }) => {
  const dispatch = useAppDispatch();
  const { isLoading } = useAppSelector(state => state.survey);

  const handleReset = () => {
    dispatch(resetSurvey());
    dispatch(startSurveyAsync(true));
  };

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Анкета-бот</h2>
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