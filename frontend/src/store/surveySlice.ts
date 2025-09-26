import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { surveyAPI } from '../api/surveyAPI';
import { SurveyState, Message } from '../types';

// Async thunks для работы с новым API
export const startSurveyAsync = createAsyncThunk(
  'survey/startSurvey',
  async (restart: boolean = false, { rejectWithValue }) => {
    try {
      // Сначала создаем опрос
      const createResponse = await surveyAPI.createSurvey(restart);
      
      // Затем получаем список опросов для получения ID и текущего вопроса
      const surveys = await surveyAPI.getSurveys();
      
      // Берем последний созданный опрос (или можно по questions_version_uuid)
      const currentSurvey = surveys[surveys.length - 1];
      
      return {
        createResponse,
        currentSurvey
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
      return await surveyAPI.submitAnswer(surveyId, answer);
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

const surveySlice = createSlice({
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
    
    resetSurvey: (state) => {
      Object.assign(state, initialState);
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
        
        const { createResponse, currentSurvey } = action.payload;
        
        state.questionsVersionUuid = createResponse.questions_version_uuid;
        state.surveyId = currentSurvey.id;
        state.currentQuestion = currentSurvey.current_question_text;
        state.answers = currentSurvey.answers;
        state.result = currentSurvey.result;
        
        // Восстанавливаем или создаем первое сообщение
        if (state.messages.length === 0 && currentSurvey.current_question_text) {
          const welcomeMessage: Message = {
            id: `question-${Date.now()}`,
            text: currentSurvey.current_question_text,
            isBot: true,
            timestamp: new Date(),
          };
          state.messages.push(welcomeMessage);
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
        
        const response = action.payload;
        
        // Проверяем, завершен ли опрос
        if (!response.current_question_text || response.current_question_text.trim() === '') {
          state.isCompleted = true;
          const completionMessage: Message = {
            id: `completion-${Date.now()}`,
            text: 'Спасибо за заполнение анкеты! Все данные сохранены.',
            isBot: true,
            timestamp: new Date(),
          };
          state.messages.push(completionMessage);
        } else {
          // Добавляем следующий вопрос
          const newMessage: Message = {
            id: `question-${Date.now()}`,
            text: response.current_question_text,
            isBot: true,
            timestamp: new Date(),
          };
          state.messages.push(newMessage);
          state.currentQuestion = response.current_question_text;
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
          // Берем последний опрос
          const lastSurvey = surveys[surveys.length - 1];
          
          state.surveyId = lastSurvey.id;
          state.currentQuestion = lastSurvey.current_question_text;
          state.answers = lastSurvey.answers;
          state.result = lastSurvey.result;
          
          // Восстанавливаем сообщения из answers (если это возможно)
          if (state.messages.length === 0) {
            // Создаем сообщения на основе полученных данных
            const messages: Message[] = [];
            
            // Если есть ответы, создаем историю
            if (lastSurvey.answers.length > 0) {
              lastSurvey.answers.forEach((answer, index) => {
                if (answer) {
                  // Добавляем пользовательский ответ
                  messages.push({
                    id: `restored-answer-${index}`,
                    text: answer,
                    isBot: false,
                    timestamp: new Date(Date.now() - (lastSurvey.answers.length - index) * 1000),
                  });
                }
              });
            }
            
            // Добавляем текущий вопрос
            if (lastSurvey.current_question_text) {
              messages.push({
                id: `current-${Date.now()}`,
                text: lastSurvey.current_question_text,
                isBot: true,
                timestamp: new Date(),
              });
            }
            
            state.messages = messages;
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
export default surveySlice.reducer;