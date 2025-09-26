import React from 'react';
import { useAppSelector } from '../../hooks/redux';
import styles from './Progress.module.css';

export const Progress: React.FC = () => {
  const { answers } = useAppSelector(state => state.survey);
  
  const totalQuestions = answers.length || 1;
  const answeredQuestions = answers.filter(answer => answer !== null).length;
  const progress = Math.min((answeredQuestions / totalQuestions) * 100, 100);

  return (
    <div className={styles.container}>
      <div className={styles.bar}>
        <div 
          className={styles.fill}
          style={{ width: `${progress}%` }}
        />
      </div>
      <p className={styles.text}>
        Прогресс: {answeredQuestions} из {totalQuestions} вопросов
      </p>
    </div>
  );
};

export default Progress;