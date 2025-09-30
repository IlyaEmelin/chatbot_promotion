import React, { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../../hooks/redux';
import { startSurveyAsync, clearError } from '../../store/surveySlice';
import Header from '../Header/Header';
import Progress from '../Progress/Progress';
import Messages from '../Messages/Messages';
import Input from '../Input/Input';
import styles from './Chat.module.css';

interface ChatProps {
  onClose: () => void;
}

export const Chat: React.FC<ChatProps> = ({ onClose }) => {
  const dispatch = useAppDispatch();
  const { error, surveyId } = useAppSelector(state => state.survey);

  useEffect(() => {
    if (!surveyId) {
      dispatch(startSurveyAsync(false));
    }
  }, [dispatch, surveyId]);

  return (
    <div className={styles.widget}>
      <Header onClose={onClose} />
      <Progress />
      
      {error && (
        <div className={styles.errorMessage}>
          {error}
          <button 
            onClick={() => dispatch(clearError())} 
            className={styles.errorCloseButton}
            type="button"
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