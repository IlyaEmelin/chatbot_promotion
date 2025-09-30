import { getCookie } from "./cookie";
import type { TLoginData, TRegisterData } from "./types";

const URL = import.meta.env.VITE_API_URL || 'http://dvizhenie.myftp.biz:580/api';

const checkResponse = <T>(res: Response): Promise<T> => {
    return res.ok ? res.json() : res.json().then((res) => Promise.reject(res));
};

type TAuthResponse = {
    auth_token: string;
}

type TRegisterResponse = {
    id: number;
    email: string;
    username: string;
}

export const registerUserApi = (user: TRegisterData): Promise<TRegisterResponse> => {
    console.log('register api', JSON.stringify(user));
    return fetch(`${URL}/auth/users/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json; charset=utf-8',
        },
        body: JSON.stringify(user),
    })
    .then((res) => {
        console.log('register api res', res);
        return checkResponse<TRegisterResponse>(res)
    })
    .then((res) => {
        console.log('register api', res);
        return res;
    })
    .catch((err) => {
        console.log('register api err', err);
        return Promise.reject(err);
    });
};

export const loginUserApi = (user: TLoginData): Promise<TAuthResponse> => {
    return fetch(`${URL}/auth/token/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json; charset=utf-8',
        },
        body: JSON.stringify(user),
    })
    .then((res) => checkResponse<TAuthResponse>(res))
    .then((res) => {
        console.log('login api', res);
        return res;
    })
    .catch((err) => {
        console.log('login api err', err);
        return Promise.reject(err);
    });
};

type TLogoutResponse = {
    message: string;
}

export const logoutApi = (): Promise<TLogoutResponse> => {
    return fetch(`${URL}/auth/token/logout/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json; charset=utf-8',
            Authorization: `Token ${getCookie('auth_token')}`
        },
    })
    .then((res) => checkResponse(res))
};

export const getUserApi = (): Promise<TRegisterResponse> =>
    fetch(`${URL}/auth/users/me/`, {
        headers: {
        Authorization: `Token ${getCookie('auth_token')}`
        } as HeadersInit
    })
    .then((res) => checkResponse(res));