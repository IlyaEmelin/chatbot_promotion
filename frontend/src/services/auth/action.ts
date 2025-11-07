import { createAsyncThunk } from '@reduxjs/toolkit';
import {
  getUserApi,
  loginUserApi,
  logoutApi,
  registerUserApi,
} from '../../utils/api';
import { type TLoginData, type TRegisterData } from '../../utils/types';
import { getCookie, setCookie, deleteCookie } from '../../utils/cookie';
import { setIsAuthChecked, setUser } from './slice';

export const registerUser = createAsyncThunk(
  'auth/register',
  async ({ email, password, username }: TRegisterData) => {
    await registerUserApi({
      email,
      username,
      password
    });
    const token = await loginUserApi({username, password});
    setCookie('auth_token', token.auth_token);
    const user = await getUserApi();
    return user;
  }
);

export const loginUser = createAsyncThunk(
  'auth/login',
  async ({ username, password }: TLoginData) => {
    try {
      const response = await loginUserApi({ username, password });
      setCookie('auth_token', response.auth_token);
      const user = await getUserApi();
      console.log('login action', user)
      return user;
    } catch (err) {
      return Promise.reject(err);
    }
  }
);

export const logoutUser = createAsyncThunk('auth/logout', async () => {
  console.log('logout action 1');
  const response = await logoutApi();
  console.log('logout action', response);
  deleteCookie('auth_token');

  try {
    localStorage.removeItem('survey_chat_bot_state');
  } catch (e) {
    console.warn('Failed to clear widget storage:', e);
  }

  return response;
});

export const checkUserAuth = createAsyncThunk(
  'auth/checkUserAuth',
  async (_, { dispatch }) => {
    if (getCookie('auth_token')) {
      try {
        const response = await getUserApi();
        dispatch(setUser(response));
      } catch (err) {
        console.error(err);
      } finally {
        dispatch(setIsAuthChecked(true));
      }
    } else {
      dispatch(setIsAuthChecked(true));
    }
  }
);