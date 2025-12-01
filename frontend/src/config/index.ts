import dotenv from 'dotenv';
dotenv.config();

export const config = {
  apiUrl: process.env.VITE_API_URL|| 'http://localhost:8000/api',
  widgetPosition: process.env.REACT_APP_WIDGET_POSITION || 'bottom-right',
  theme: process.env.REACT_APP_WIDGET_THEME || 'light',
  storage: {
    maxAge: 7 * 24 * 60 * 60 * 1000, // 7 дней в миллисекундах
    key: 'survey_chat_bot_state'
  }
}