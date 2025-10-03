import { 
  UploadedDocument,
  CreateSurveyRequest, 
  CreateSurveyResponse, 
  Survey, 
  SubmitAnswerRequest, 
  SubmitAnswerResponse, 
  ProcessingRequest
} from '../types';

function getCookie(name: string): string | undefined {
  const matches = document.cookie.match(
    new RegExp('(?:^|; )' + name.replace(/([$?*|{}()[\]\\/+^])/g, '\\$1') + '=([^;]*)')
  );
  return matches ? decodeURIComponent(matches[1]) : undefined;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

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

  getDocuments: async (surveyId: string): Promise<UploadedDocument[]> => {
    console.log(`📤 API Request: GET /v1/surveys/${surveyId}/docs/`);

    const response = await fetch(`${API_BASE_URL}/v1/surveys/${surveyId}/docs/`, {
      method: 'GET',
      headers: getAuthHeaders({
        'Content-Type': 'application/json',
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.text();
      console.error('❌ API Error:', response.status, errorData);
      throw new Error(`Ошибка получения документов: ${response.status}`);
    }
    
    const data = await response.json();
    console.log(`📥 API Response: GET /v1/surveys/${surveyId}/docs/`, data);
    return data;
  },

  // POST /api/v1/surveys/{survey_pk}/docs/ - загрузить документ
  uploadDocument: async (surveyId: string, file: File): Promise<UploadedDocument> => {
  // Читаем файл как dataURL (с префиксом data:image/png;base64,...)
  const toDataUrl = (file: File): Promise<string> =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = (error) => reject(error);
    });

  const base64WithPrefix = await toDataUrl(file);

  const requestBody = {
    image: base64WithPrefix,  
  };

  console.log(`📤 API Request: POST /v1/surveys/${surveyId}/docs/`, requestBody);

  const response = await fetch(`${API_BASE_URL}/v1/surveys/${surveyId}/docs/`, {
    method: 'POST',
    headers: getAuthHeaders({
      'Content-Type': 'application/json',
    }),
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    const errorData = await response.text();
    console.error('❌ API Error:', response.status, errorData);
    throw new Error(`Ошибка загрузки документа: ${response.status}`);
  }

  const data = await response.json();
  console.log(`📥 API Response: POST /v1/surveys/${surveyId}/docs/`, data);
  return data;
},



  // DELETE /api/v1/surveys/{survey_pk}/docs/{id}/ - удалить документ
  deleteDocument: async (surveyId: string, documentId: number): Promise<void> => {
    console.log(`📤 API Request: DELETE /v1/surveys/${surveyId}/docs/${documentId}/`);
    
    const response = await fetch(`${API_BASE_URL}/v1/surveys/${surveyId}/docs/${documentId}/`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    
    if (!response.ok) {
      const errorData = await response.text();
      console.error('❌ API Error:', response.status, errorData);
      throw new Error(`Ошибка удаления документа: ${response.status}`);
    }
    
    console.log(`✅ Document ${documentId} deleted`);
  },

    // PATCH /api/v1/surveys/{id}/processing/ - завершить опрос
  finishSurvey: async (surveyId: string): Promise<void> => {
    const requestBody: ProcessingRequest = {
      result: {},
      status: 'processing'
    };

    console.log(`📤 API Request: PATCH /v1/surveys/${surveyId}/processing/`, requestBody);

    const response = await fetch(`${API_BASE_URL}/v1/surveys/${surveyId}/processing/`, {
      method: 'PATCH',
      headers: getAuthHeaders({
        'Content-Type': 'application/json',
      }),
      body: JSON.stringify(requestBody),
    });
    
    if (!response.ok) {
      const errorData = await response.text();
      console.error('❌ API Error:', response.status, errorData);
      throw new Error(`Ошибка завершения опроса: ${response.status}`);
    }
    
    console.log('✅ Survey finished successfully');
  },
};

// Экспортируем вспомогательные функции для использования в других местах
export { getCookie, getAuthHeaders };