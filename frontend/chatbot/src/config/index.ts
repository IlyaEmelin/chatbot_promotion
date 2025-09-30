export const config = {
  apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  widgetPosition: process.env.REACT_APP_WIDGET_POSITION || 'bottom-right',
  theme: process.env.REACT_APP_WIDGET_THEME || 'light',
  storage: {
    maxAge: 7 * 24 * 60 * 60 * 1000, // 7 дней в миллисекундах
    key: 'survey_chat_bot_state'
  }
};