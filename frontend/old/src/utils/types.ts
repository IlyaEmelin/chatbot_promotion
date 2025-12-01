import type { ChangeEvent } from "react";

export type TLoginData = {
  username: string;
  password: string;
};

export type TFieldType<T> = {
    field: keyof T;
    value: string;
}

export type TUser = {
    id?: number;
    email: string;
    username: string;
    is_superuser?: boolean;
}

export type TRegisterData = TLoginData & {
  email?: string;
};

export type TUseFormWithValidation<T> = {
  values: T, 
  handleChange: (e: ChangeEvent<HTMLInputElement>) => void, 
  errors: TErrorState<T>, 
  isValid: boolean};

export type TFormValidators<T> ={
    [key in keyof T]: {
        validator: (value: string) => boolean;
        message: string;
    }
}

export type TErrorState<T> = {[key in keyof T]?: string};