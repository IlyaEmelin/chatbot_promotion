import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { surveyAPI } from '../utils/surveyAPI';
import { SurveyState, Message } from '../types';

// Функция для определения, есть ли опции у текущего вопроса
const hasValidOptions = (answers: string[]): boolean => {
  if (!answers || answers.length === 0) return false;
  
  // Фильтруем null и пустые строки
  const validAnswers = answers.filter(answer => 
    answer !== null && 
    answer !== undefined && 
    String(answer).trim() !== '' &&
    String(answer).toLowerCase() !== 'none'
  );
  // Если нет валидных ответов - не показываем кнопки
  return validAnswers.length >= 1;
};

// Async thunks для работы с новым API
export const startSurveyAsync = createAsyncThunk(
  'survey/startSurvey',
  async (restart: boolean = false, { rejectWithValue }) => {
    try {
      console.log(`🔄 Starting survey with restart=${restart}`);
      
      // Создаем опрос с правильным параметром restart_question
      const createResponse = await surveyAPI.createSurvey(restart);
      
      // Затем получаем список опросов для получения ID и текущего вопроса
      const surveys = await surveyAPI.getSurveys();
      
      // Берем последний созданный опрос
      const currentSurvey = surveys[surveys.length - 1];
      
      return {
        createResponse,
        currentSurvey,
        isRestart: restart
      };
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Unknown error');
    }
  }
);

export const submitAnswerAsync = createAsyncThunk(
  'survey/submitAnswer',
  async ({ surveyId, answer }: { surveyId: string; answer: string }, { rejectWithValue }) => {
    try {
      const response = await surveyAPI.submitAnswer(surveyId, answer);
      
      // После отправки ответа получаем обновленную информацию об опросе
      const surveys = await surveyAPI.getSurveys();
      const currentSurvey = surveys.find(s => s.id === surveyId);
      
      return {
        submitResponse: response,
        updatedSurvey: currentSurvey
      };
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Unknown error');
    }
  }
);

export const loadExistingSurveysAsync = createAsyncThunk(
  'survey/loadExistingSurveys',
  async (_, { rejectWithValue }) => {
    try {
      return await surveyAPI.getSurveys();
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Unknown error');
    }
  }
);

const initialState: SurveyState = {
  surveyId: null,
  messages: [],
  currentQuestion: '',
  isLoading: false,
  error: null,
  isCompleted: false,
  answers: [],
  result: {},
  questionsVersionUuid: null,
};

export const surveySlice = createSlice({
  name: 'survey',
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<Omit<Message, 'id' | 'timestamp'>>) => {
      const message: Message = {
        ...action.payload,
        id: `${Date.now()}-${Math.random()}`,
        timestamp: new Date(),
      };
      state.messages.push(message);
    },
    
    clearError: (state) => {
      state.error = null;
    },
    
    resetSurvey: () => {
      return { ...initialState };
    },
    
    loadFromStorage: (state, action: PayloadAction<Partial<SurveyState>>) => {
      Object.assign(state, action.payload);
    },
  },
  
  extraReducers: (builder) => {
    builder
      // Start Survey
      .addCase(startSurveyAsync.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(startSurveyAsync.fulfilled, (state, action) => {
        state.isLoading = false;
        
        const { createResponse, currentSurvey, isRestart } = action.payload;
        
        state.questionsVersionUuid = createResponse.questions_version_uuid;
        state.surveyId = currentSurvey.id;
        state.currentQuestion = currentSurvey.current_question_text;
        state.answers = currentSurvey.answers;
        state.result = currentSurvey.result;
        
        // При рестарте очищаем историю сообщений
        if (isRestart) {
          state.messages = [];
          console.log('🔄 Survey restarted, messages cleared');
        }
        
        // Восстанавливаем сообщения из result если есть история
        if (!isRestart && Array.isArray(currentSurvey.result) && currentSurvey.result.length > 0) {
          const messages: Message[] = [];
          
          for (let i = 0; i < currentSurvey.result.length; i += 2) {
            if (currentSurvey.result[i]) {
              messages.push({
                id: `restored-q-${i}`,
                text: currentSurvey.result[i],
                isBot: true,
                timestamp: new Date(Date.now() - (currentSurvey.result.length - i) * 1000),
              });
            }
            if (currentSurvey.result[i + 1]) {
              messages.push({
                id: `restored-a-${i}`,
                text: currentSurvey.result[i + 1],
                isBot: false,
                timestamp: new Date(Date.now() - (currentSurvey.result.length - i - 1) * 1000),
              });
            }
          }
          
          state.messages = messages;
        }
        
        // Добавляем текущий вопрос
        if (currentSurvey.current_question_text && 
            !state.messages.some(m => m.text === currentSurvey.current_question_text)) {
          
          const hasOptions = hasValidOptions(currentSurvey.answers);
          const options = hasOptions ? currentSurvey.answers.filter(answer => answer === null || answer.trim() !== '') : undefined;
          
          const currentMessage: Message = {
            id: `current-${Date.now()}`,
            text: currentSurvey.current_question_text,
            isBot: true,
            timestamp: new Date(),
            options: options
          };
          
          state.messages.push(currentMessage);
        }
      })
      .addCase(startSurveyAsync.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Submit Answer
      .addCase(submitAnswerAsync.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(submitAnswerAsync.fulfilled, (state, action) => {
        state.isLoading = false;
        
        const { submitResponse, updatedSurvey } = action.payload;
        
        if (updatedSurvey) {
          state.currentQuestion = updatedSurvey.current_question_text;
          state.answers = updatedSurvey.answers;
          state.result = updatedSurvey.result;
        }
        
        const isCompleted = !submitResponse.current_question_text || 
                           submitResponse.current_question_text.trim() === '' ||
                           (updatedSurvey && !updatedSurvey.current_question_text);
        
        if (isCompleted) {
          state.isCompleted = true;
          const completionMessage: Message = {
            id: `completion-${Date.now()}`,
            text: 'Спасибо за заполнение анкеты! Все данные сохранены.',
            isBot: true,
            timestamp: new Date(),
          };
          state.messages.push(completionMessage);
        } else {
          const questionText = updatedSurvey?.current_question_text || submitResponse.current_question_text;
          
          if (questionText) {
            const hasOptions = updatedSurvey && hasValidOptions(updatedSurvey.answers);
            const options = hasOptions && updatedSurvey ? 
              updatedSurvey.answers.filter(answer => answer === null || answer.trim() !== '') : 
              undefined;
            
            const newMessage: Message = {
              id: `question-${Date.now()}`,
              text: questionText,
              isBot: true,
              timestamp: new Date(),
              options: options
            };
            
            state.messages.push(newMessage);
            state.currentQuestion = questionText;
          }
        }
      })
      .addCase(submitAnswerAsync.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Load Existing Surveys
      .addCase(loadExistingSurveysAsync.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loadExistingSurveysAsync.fulfilled, (state, action) => {
        state.isLoading = false;
        
        const surveys = action.payload;
        if (surveys.length > 0) {
          const lastSurvey = surveys[surveys.length - 1];
          
          state.surveyId = lastSurvey.id;
          state.currentQuestion = lastSurvey.current_question_text;
          state.answers = lastSurvey.answers;
          state.result = lastSurvey.result;
          
          if (Array.isArray(lastSurvey.result) && lastSurvey.result.length > 0) {
            const messages: Message[] = [];
            
            for (let i = 0; i < lastSurvey.result.length; i += 2) {
              if (lastSurvey.result[i]) {
                messages.push({
                  id: `restored-q-${i}`,
                  text: lastSurvey.result[i],
                  isBot: true,
                  timestamp: new Date(Date.now() - (lastSurvey.result.length - i) * 1000),
                });
              }
              if (lastSurvey.result[i + 1]) {
                messages.push({
                  id: `restored-a-${i}`,
                  text: lastSurvey.result[i + 1],
                  isBot: false,
                  timestamp: new Date(Date.now() - (lastSurvey.result.length - i - 1) * 1000),
                });
              }
            }
            
            state.messages = messages;
          }
          
          if (lastSurvey.current_question_text && 
              !state.messages.some(m => m.text === lastSurvey.current_question_text)) {
            
            const hasOptions = hasValidOptions(lastSurvey.answers);
            const options = hasOptions ? lastSurvey.answers.filter(answer => answer !== null || answer.trim() !== '') : undefined;
            
            const currentMessage: Message = {
              id: `current-${Date.now()}`,
              text: lastSurvey.current_question_text,
              isBot: true,
              timestamp: new Date(),
              options: options
            };
            
            state.messages.push(currentMessage);
          }
        }
      })
      .addCase(loadExistingSurveysAsync.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { addMessage, clearError, resetSurvey, loadFromStorage } = surveySlice.actions;