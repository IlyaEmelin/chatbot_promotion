import { createAsyncThunk } from '@reduxjs/toolkit';
import {
  getUserApi,
  loginUserApi,
  logoutApi,
  registerUserApi,
} from '../../utils/api';
import { type TLoginData, type TRegisterData } from '../../utils/types';
import { setCookie, deleteCookie } from '../../utils/cookie';

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
    setCookie('auth_token', token.auth_token);
    const user = await getUserApi();
    return user;
    } catch (err) {
      let errorMessage = err.details?.[0] || err.message || '';
      if (err.username) {
        errorMessage = err.username?.[0];
      }
      if (err.email) {
        const emailError = err.email?.[0];
        errorMessage = errorMessage + (emailError ? ` ${emailError}` : '');
      }
      if (err.password) {
        const passwordError = err.password?.[0];
        errorMessage = errorMessage + (passwordError ? ` ${passwordError}` : '');
      }
      throw new Error(errorMessage);
    }
  }
);

export const loginUser = createAsyncThunk(
  'auth/login',
  async ({ username, password }: TLoginData) => {
    try {
      const response = await loginUserApi({ username, password });
      setCookie('auth_token', response.auth_token);
      const user = await getUserApi();
      return user;
    } catch (err) {
      let errorMessage = err.details?.[0] || err.message;
      errorMessage = err.non_field_errors?.[0] || errorMessage;
      throw new Error(errorMessage);
    }
  }
);

export const logoutUser = createAsyncThunk('auth/logout', async () => {
  const response = await logoutApi();
  deleteCookie('auth_token');

  try {
    localStorage.removeItem('survey_chat_bot_state');
  } catch (e) {
    console.warn('Failed to clear widget storage:', e);
  }

  return response;
});