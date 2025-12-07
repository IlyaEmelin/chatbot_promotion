import { createAsyncThunk } from '@reduxjs/toolkit';
import {
  getUserApi,
  loginUserApi,
  logoutApi,
  registerUserApi,
} from '../../utils/api';
import { type TLoginData, type TRegisterData } from '../../utils/types';

const handleError = (err) => {
  let errorMessage = err.message || '';
  if (typeof err === 'object') {
    const arrayErrorMessage = Object.values(err).map(value => Array.isArray(value) ? value : [value]);
    errorMessage = arrayErrorMessage.flat().join('\n');
  }
  throw new Error(errorMessage);
}

export const registerUser = createAsyncThunk(
  'auth/register',
  async ({ email, password, username }: TRegisterData) => {
    try {
      await registerUserApi({
      email,
      username,
      password
    });
    const token = await loginUserApi({username, password});
    sessionStorage.setItem('auth_token', token.auth_token);
    const user = await getUserApi();
    return user;
    } catch (err) {
      handleError(err);
    }
  }
);

export const loginUser = createAsyncThunk(
  'auth/login',
  async ({ username, password }: TLoginData) => {
    try {
      const response = await loginUserApi({ username, password });
      sessionStorage.setItem('auth_token', response.auth_token);
      const user = await getUserApi();
      return user;
    } catch (err) {
      handleError(err);
    }
  }
);

export const logoutUser = createAsyncThunk('auth/logout', async () => {
  try {
    const response = await logoutApi();

    if (response.ok) {
      sessionStorage.removeItem('auth_token');
      localStorage.removeItem('survey_chat_bot_state');
      console.log('Successfully logout', localStorage.getItem('survey_chat_bot_state'));
      return;
    } 
    throw new Error('Failed to logout');
  } catch (e) {
    console.warn('Failed to clear widget storage:', e);
  }
});