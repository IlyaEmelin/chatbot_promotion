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
    const response = await registerUserApi({
      email,
      username,
      password
    });
    console.log('register action', response);
    
    const token = await loginUserApi({username, password});
    setCookie('auth_token', token.auth_token);
    console.log('register login action ok', token);
    const user = await getUserApi();
    console.log('getUser', user);
    return user;
  }
);

export const loginUser = createAsyncThunk(
  'auth/login',
  async ({ username, password }: TLoginData) => {
    try {
      const response = await loginUserApi({ username, password });
      setCookie('auth_token', response.auth_token);
      console.log('login action ok', response, getCookie('auth_token'));
      return response;
    } catch (err) {
      console.log('login action err', err);
      return Promise.reject(err);
    }
  }
);

export const logoutUser = createAsyncThunk('auth/logout', async () => {
  const response = await logoutApi();
  deleteCookie('auth_token');
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