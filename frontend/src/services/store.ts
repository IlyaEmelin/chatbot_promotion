import { combineSlices, configureStore } from "@reduxjs/toolkit";
import { authSlice } from "./auth/slice";
import { surveySlice } from './surveySlice';
import { storageMiddleware } from './middleware/storageMiddleware';

export const rootReducer = combineSlices(
    authSlice,
    surveySlice,
);

export const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false // фикс ошибки в консоли
    }).concat(storageMiddleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;