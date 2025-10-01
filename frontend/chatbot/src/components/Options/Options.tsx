import React from 'react';
import { useAppDispatch, useAppSelector } from '../../hooks/redux';
import { addMessage, submitAnswerAsync } from '../../store/surveySlice';
import styles from './Options.module.css';

interface OptionsProps {
  options: string[];
}

export const Options: React.FC<OptionsProps> = ({ options }) => {
  const dispatch = useAppDispatch();
  const { isLoading, surveyId } = useAppSelector(state => state.survey);

  const handleOptionClick = (option: string) => {
    if (!surveyId || isLoading) return;
    
    dispatch(addMessage({ text: option, isBot: false }));
    dispatch(submitAnswerAsync({ surveyId, answer: option }));
  };

  return (
    <div className={styles.container}>
      {options.map((option, index) => (
        <button
          key={index}
          className={`${styles.button} ${isLoading ? styles.buttonDisabled : ''}`}
          onClick={() => handleOptionClick(option)}
          disabled={isLoading}
          type="button"
        >
          {option}
        </button>
      ))}
    </div>
  );
};

export default Options;