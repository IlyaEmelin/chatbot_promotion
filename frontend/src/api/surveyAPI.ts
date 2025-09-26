import { 
  CreateSurveyRequest, 
  CreateSurveyResponse, 
  Survey, 
  SubmitAnswerRequest, 
  SubmitAnswerResponse 
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

console.log('🔧 API Configuration:', { API_BASE_URL });

export const surveyAPI = {
  // POST /api/v1/surveys/ - создание/перезапуск опроса
  createSurvey: async (restart_question: boolean = false): Promise<CreateSurveyResponse> => {
    const requestBody: CreateSurveyRequest = {
      restart_question,
      status: "new",
      result: {}
    };

    console.log('📤 API Request: POST /surveys/', requestBody);

    const response = await fetch(`${API_BASE_URL}/surveys/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });
    
    if (!response.ok) {
      const errorData = await response.text();
      console.error('❌ API Error:', response.status, errorData);
      throw new Error(`Ошибка создания опроса: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('📥 API Response: POST /surveys/', data);
    return data;
  },

  // GET /api/v1/surveys/ - получение списка опросов
  getSurveys: async (): Promise<Survey[]> => {
    console.log('📤 API Request: GET /surveys/');

    const response = await fetch(`${API_BASE_URL}/surveys/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.text();
      console.error('❌ API Error:', response.status, errorData);
      throw new Error(`Ошибка получения опросов: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('📥 API Response: GET /surveys/', data);
    return data;
  },

  // PUT /api/v1/surveys/{id}/ - отправка ответа
  submitAnswer: async (surveyId: string, answer: string): Promise<SubmitAnswerResponse> => {
    const requestBody: SubmitAnswerRequest = {
      answer
    };

    console.log(`📤 API Request: PUT /surveys/${surveyId}/`, requestBody);

    const response = await fetch(`${API_BASE_URL}/surveys/${surveyId}/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });
    
    if (!response.ok) {
      const errorData = await response.text();
      console.error('❌ API Error:', response.status, errorData);
      throw new Error(`Ошибка отправки ответа: ${response.status}`);
    }
    
    const data = await response.json();
    console.log(`📥 API Response: PUT /surveys/${surveyId}/`, data);
    return data;
  },

  // Загрузка файлов (если есть endpoint)
  uploadFile: async (file: File): Promise<{ url: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    
    console.log('📤 API Request: POST /upload/', { fileName: file.name, fileSize: file.size });
    
    const response = await fetch(`${API_BASE_URL}/upload/`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.text();
      console.error('❌ API Error:', response.status, errorData);
      throw new Error(`Ошибка загрузки файла: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('📥 API Response: POST /upload/', data);
    return data;
  },
};
