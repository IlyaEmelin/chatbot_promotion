export interface Message {
  id: string;
  text: string;
  isBot: boolean;
  timestamp: Date;
  attachments?: File[];
  options?: string[];
}

// Новые типы под ваш API
export interface CreateSurveyRequest {
  restart_question: boolean;
  status: "new";
  result: Record<string, any>;
}

export interface CreateSurveyResponse {
  restart_question: boolean;
  status: "new";
  result: Record<string, any>;
  questions_version_uuid: string;
}

export interface Survey {
  id: string;
  current_question_text: string;
  answers: string[];
  result: Record<string, any>;
}

export interface SubmitAnswerRequest {
  answer: string;
}

export interface SubmitAnswerResponse {
  answer: string;
  current_question_text: string;
  answers: string;
}

export interface SurveyState {
  surveyId: string | null;
  messages: Message[];
  currentQuestion: string;
  isLoading: boolean;
  error: string | null;
  isCompleted: boolean;
  answers: string[];
  result: Record<string, any>;
  questionsVersionUuid: string | null;
}

// Типы для storage
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
  result: Record<string, any>;
  questionsVersionUuid: string | null;
  lastUpdated: string;
}