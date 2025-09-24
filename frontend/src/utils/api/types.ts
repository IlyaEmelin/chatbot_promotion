import type { TUser } from "../types";

type TServerResponse<T> = {
  success: boolean;
} & T;

type TApiError = {
  error: {
    code: string;
    message: string;
    details?: any;
    timestamp: string;
  }
};

type TRefreshResponse = TServerResponse<{
  refreshToken: string;
  accessToken: string;
}>;

type TAuthResponse = TServerResponse<{
  refreshToken: string;
  accessToken: string;
  user: TUser;
}>;

type TRegisterData = {
  email: string;
  name: string;
  surname?: string;
  password: string;
};

type TLoginData = {
  email: string;
  password: string;
};

// Для варианта ЧАТ-БОТА -----------------------------------------------------

interface ICreateSessionRequest {
  userAgent?: string
  //
}

interface ICreateSessionResponse {
  // sessionId: string
  status: 'active' | 'waiting';
  createdAt: string;
  expiresAt: string;
  config?: {
    maxMessageLength?: number
    allowedFileTypes?: string[]
    maxFileSize?: number
    features?: string[]
  }
};

interface IChatMessage {
  id: string
  // sessionId: string
  type: 'text' | 'file';
  sender: 'user' | 'bot' | 'admin'; //admin?
  content: string;
  timestamp: string; 
  status?: 'sent' | 'delivered' | 'failed';
  file?: {
    id: string
    name: string;
    size: number;
    type: string;
    data: string;
  }
  metadata?: {
    timestamp?: string;
  }
};

interface ISendMessageRequest {
  message: {
    type: 'text' | 'file';
    content: string;
    metadata?: {
      timestamp?: string;
      clientId?: string;
    }
    file?: {
      name: string;
      size: number;
      type: string;
      data: string; //?
    }
  }
};

interface IGetMessagesResponse {
  messages: IChatMessage[];
  // sessionId: string
  status: 'active' | 'waiting';
  createdAt: string;
  expiresAt: string;
};

// Для варианита второй страницы --------------------------------------------

interface IFormData {
  contactPerson: string;
  personStatus: 'himself' | 'parents' | 'caretaker' | 'relative' | 'other';
  residenceName: string;
  residenceDateOfBirth: string;
  email: string;
  phone: string;
  city: string;
  typeOfHelp: string;
  hasTCP: boolean;
  isTCPinIPRA: boolean;
  haveOpenFounds: boolean;
  needHelpWithIPRA: boolean;
  promotionPossibility: boolean;
};

