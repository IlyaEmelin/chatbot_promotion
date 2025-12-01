import {
     useDispatch as dispatchHook,
     useSelector as selectorHook
} from 'react-redux';
import { store, rootReducer } from '../services/store';

export type RootState = ReturnType<typeof rootReducer>;
export type AppDispatch = typeof store.dispatch;

export const useDispatch = dispatchHook.withTypes<AppDispatch>();
export const useSelector = selectorHook.withTypes<RootState>(); 