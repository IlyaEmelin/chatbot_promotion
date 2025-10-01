import { configureStore } from '@reduxjs/toolkit';
import surveyReducer from './surveySlice';
import { storageMiddleware } from './middleware/storageMiddleware';

export const store = configureStore({
  reducer: {
    survey: surveyReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false // фикс ошибки в консоли
    }).concat(storageMiddleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;