import { StoredState } from '../types';
import { getCookie } from '../api/surveyAPI';

export const STORAGE_KEY = 'survey_chat_bot_state';

export const storage = {
  save: (state: StoredState) => {
    try {
      const authToken = sessionStorage.getItem('auth_token');
      const dataToStore = {
        ...state,
        lastUpdated: new Date().toISOString(),
        authToken // Сохраняем токен пользователя
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(dataToStore));
      console.log('💾 Saved to localStorage:', dataToStore);
    } catch (error) {
      console.warn('Failed to save to localStorage:', error);
    }
  },

  load: (): StoredState | null => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (!stored) return null;
      
      const parsed: StoredState & { authToken?: string } = JSON.parse(stored);
      
      // Проверяем, что это данные текущего пользователя
      const currentAuthToken = sessionStorage.getItem('auth_token');
      if (parsed.authToken !== currentAuthToken) {
        console.log('🗑️ User changed, clearing old data');
        localStorage.removeItem(STORAGE_KEY);
        return null;
      }
      
      // Проверяем, не слишком ли старые данные
      const lastUpdated = new Date(parsed.lastUpdated);
      const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
      
      if (lastUpdated < weekAgo) {
        console.log('🗑️ Removing old data from localStorage');
        localStorage.removeItem(STORAGE_KEY);
        return null;
      }
      
      console.log('📖 Loaded from localStorage:', parsed);
      return parsed;
    } catch (error) {
      console.warn('Failed to load from localStorage:', error);
      localStorage.removeItem(STORAGE_KEY);
      return null;
    }
  },

  clear: () => {
    try {
      localStorage.removeItem(STORAGE_KEY);
      console.log('🗑️ Cleared localStorage');
    } catch (error) {
      console.warn('Failed to clear localStorage:', error);
    }
  }
};