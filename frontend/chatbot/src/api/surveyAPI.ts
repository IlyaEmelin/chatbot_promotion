// src/api/surveyAPI.ts - С АВТОРИЗАЦИЕЙ И ПРАВИЛЬНЫМИ ПУТЯМИ
import { 
  CreateSurveyRequest, 
  CreateSurveyResponse, 
  Survey, 
  SubmitAnswerRequest, 
  SubmitAnswerResponse 
} from '../types';

// Функция для получения куки
function getCookie(name: string): string | undefined {
  const matches = document.cookie.match(
    new RegExp('(?:^|; )' + name.replace(/([$?*|{}()[\]\\/+^])/g, '\\$1') + '=([^;]*)')
  );
  return matches ? decodeURIComponent(matches[1]) : undefined;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

console.log('🔧 API Configuration:', { API_BASE_URL });

// Функция для получения заголовков с авторизацией
function getAuthHeaders(extraHeaders: Record<string, string> = {}): Record<string, string> {
  const accessToken = getCookie('auth_token');
  
  return {
    ...extraHeaders,
    ...(accessToken ? { Authorization: `Token ${accessToken}` } : {}),
  };
}

export const surveyAPI = {
  // POST /api/v1/surveys/ - создание/перезапуск опроса
  createSurvey: async (restart_question: boolean = false): Promise<CreateSurveyResponse> => {
    const requestBody: CreateSurveyRequest = {
      restart_question,
      status: "new",
      result: {}
    };

    console.log('📤 API Request: POST /v1/surveys/', requestBody);

    const response = await fetch(`${API_BASE_URL}/v1/surveys/`, {
      method: 'POST',
      headers: getAuthHeaders({
        'Content-Type': 'application/json',
      }),
      body: JSON.stringify(requestBody),
    });
    
    if (!response.ok) {
      const errorData = await response.text();
      console.error('❌ API Error:', response.status, errorData);
      throw new Error(`Ошибка создания опроса: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('📥 API Response: POST /v1/surveys/', data);
    return data;
  },

  // GET /api/v1/surveys/ - получение списка опросов
  getSurveys: async (): Promise<Survey[]> => {
    console.log('📤 API Request: GET /v1/surveys/');

    const response = await fetch(`${API_BASE_URL}/v1/surveys/`, {
      method: 'GET',
      headers: getAuthHeaders({
        'Content-Type': 'application/json',
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.text();
      console.error('❌ API Error:', response.status, errorData);
      throw new Error(`Ошибка получения опросов: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('📥 API Response: GET /v1/surveys/', data);
    return data;
  },

  // PUT /api/v1/surveys/{id}/ - отправка ответа
  submitAnswer: async (surveyId: string, answer: string): Promise<SubmitAnswerResponse> => {
    const requestBody: SubmitAnswerRequest = {
      answer
    };

    console.log(`📤 API Request: PUT /v1/surveys/${surveyId}/`, requestBody);

    const response = await fetch(`${API_BASE_URL}/v1/surveys/${surveyId}/`, {
      method: 'PUT',
      headers: getAuthHeaders({
        'Content-Type': 'application/json',
      }),
      body: JSON.stringify(requestBody),
    });
    
    if (!response.ok) {
      const errorData = await response.text();
      console.error('❌ API Error:', response.status, errorData);
      throw new Error(`Ошибка отправки ответа: ${response.status}`);
    }
    
    const data = await response.json();
    console.log(`📥 API Response: PUT /v1/surveys/${surveyId}/`, data);
    return data;
  },

  // POST /api/v1/upload/ - загрузка файлов
  uploadFile: async (file: File): Promise<{ url: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    
    console.log('📤 API Request: POST /v1/upload/', { fileName: file.name, fileSize: file.size });
    
    const response = await fetch(`${API_BASE_URL}/v1/upload/`, {
      method: 'POST',
      headers: getAuthHeaders(), // Не добавляем Content-Type для FormData
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.text();
      console.error('❌ API Error:', response.status, errorData);
      throw new Error(`Ошибка загрузки файла: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('📥 API Response: POST /v1/upload/', data);
    return data;
  },
};

// Экспортируем вспомогательные функции для использования в других местах
export { getCookie, getAuthHeaders };