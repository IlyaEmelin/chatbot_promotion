import { getCookie } from "./cookie";
import type { TLoginData, TRegisterData } from "./types";

const URL = import.meta.env.VITE_API_URL || 'https://pro-dvizhenie.ddns.net/api';

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
    return fetch(`${URL}/auth/users/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json; charset=utf-8',
        },
        body: JSON.stringify(user),
    })
    .then((res) => {
        return checkResponse<TRegisterResponse>(res)
    })
    .then((res) => {
        return res;
    })
    .catch((err) => {
        return Promise.reject(err);
    });
};

export const loginUserApi = (user: TLoginData): Promise<TAuthResponse> => {
    return fetch(`${URL}/auth/token/login/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json; charset=utf-8',
        },
        body: JSON.stringify(user),
    })
    .then((res) => checkResponse<TAuthResponse>(res))
    .then((res) => {
        return res;
    })
    .catch((err) => {
        return Promise.reject(err);
    });
};

export const logoutApi = () => {
    return fetch(`${URL}/auth/token/logout/`, {
        method: 'POST',
        headers: {
            Authorization: `Token ${sessionStorage.getItem('auth_token')}`
        },
    })
};

export const getUserApi = (): Promise<TRegisterResponse> =>
    fetch(`${URL}/auth/users/me/`, {
        headers: {
            Authorization: `Token ${sessionStorage.getItem('auth_token')}`
        } as HeadersInit
    })
    .then((res) => checkResponse(res));