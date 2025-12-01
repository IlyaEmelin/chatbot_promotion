import { Middleware, AnyAction } from '@reduxjs/toolkit';
import { storage } from '../../utils/storage';

interface StoreWithSurvey {
  getState: () => {
    survey: {
      surveyId: string | null;
      messages: any[];
      answers: string[];
      result: Record<string, any>;
      questionsVersionUuid: string | null;
    };
  };
}

export const storageMiddleware: Middleware = (store: StoreWithSurvey) => (next) => (action: AnyAction) => {
  const result = next(action);
  
  // Сохраняем состояние после определенных действий
  if (
    action.type?.startsWith('survey/') &&
    (action.type.includes('fulfilled') || 
     action.type === 'survey/addMessage' ||
     action.type === 'survey/resetSurvey')
  ) {
    try {
      const state = store.getState().survey;
      
      const stateToSave = {
        surveyId: state.surveyId,
        messages: state.messages.map(msg => ({
          ...msg,
          timestamp: msg.timestamp.toISOString(),
          attachments: msg.attachments?.map((file: File) => ({ 
            name: file.name, 
            size: file.size 
          }))
        })),
        answers: state.answers,
        result: state.result,
        questionsVersionUuid: state.questionsVersionUuid,
        lastUpdated: new Date().toISOString()
      };
      
      storage.save(stateToSave);
    } catch (error) {
      console.warn('Failed to save state to storage:', error);
    }
  }
  
  return result;
};