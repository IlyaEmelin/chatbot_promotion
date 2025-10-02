export interface UploadedDocument {
  id: number;
  file: string; // URL файла
  uploaded_at?: string;
  file_name?: string;
  file_size?: number;
}

export interface FileWithPreview {
  file: File;
  preview: string;
  uploadedId?: number; // ID после загрузки на сервер
  isUploading?: boolean;
  uploadError?: string;
}

export interface Message {
  id: string;
  text: string;
  isBot: boolean;
  timestamp: Date;
  attachments?: File[];
  options?: string[];
}

export interface CreateSurveyRequest {
  restart_question: boolean;
  status: "new";
  result: Record<string, any>;
}

export interface CreateSurveyResponse {
  restart_question: boolean;
  status: "new" | "waiting_docs" | "processing";
  result: Record<string, any>;
  questions_version_uuid: string;
}

export interface Survey {
  id: string;
  current_question_text: string;
  answers: string[];
  result: Record<string, any> | string[]; // МОЖЕТ БЫТЬ ОБЪЕКТ ИЛИ МАССИВ
  status?: "new" | "waiting_docs" | "processing";
}

export interface SubmitAnswerRequest {
  answer: string;
}

export interface SubmitAnswerResponse {
  answer: string;
  current_question_text: string;
  answers: string;
}

export interface UploadedDocument {
  id: number;
  image?: string; // base64
  uploaded_at?: string;
  file_name?: string;
  file_size?: number;
}

export interface FileWithPreview {
  file: File;
  preview: string;
  uploadedId?: number;
  isUploading?: boolean;
  uploadError?: string;
}

export interface ProcessingRequest {
  result: Record<string, any>;
  status: "processing";
}

export interface SurveyState {
  surveyId: string | null;
  messages: Message[];
  currentQuestion: string;
  isLoading: boolean;
  error: string | null;
  isCompleted: boolean;
  answers: string[];
  result: Record<string, any> | string[];
  questionsVersionUuid: string | null;
  status?: "new" | "waiting_docs" | "processing";
}

export interface StoredMessage {
  id: string;
  text: string;
  isBot: boolean;
  timestamp: string;
  attachments?: { name: string; size: number }[];
  options?: string[];
}

export interface StoredState {
  surveyId: string | null;
  messages: StoredMessage[];
  answers: string[];
  result: Record<string, any> | string[];
  questionsVersionUuid: string | null;
  status?: "new" | "waiting_docs" | "processing";
  lastUpdated: string;
}