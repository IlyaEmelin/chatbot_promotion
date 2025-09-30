import { configureStore } from '@reduxjs/toolkit';
import surveyReducer from './surveySlice';
import { storageMiddleware } from './middleware/storageMiddleware';

export const store = configureStore({
  reducer: {
    survey: surveyReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [
          'survey/addMessage', 
          'survey/loadFromStorage',
          'survey/startSurveyAsync/fulfilled',
          'survey/submitAnswerAsync/fulfilled'
        ],
        ignoredPaths: ['survey.messages.timestamp', 'survey.messages.attachments'],
      },
    }).concat(storageMiddleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
