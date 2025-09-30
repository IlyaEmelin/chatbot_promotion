import type { ActionCreatorWithPayload } from "@reduxjs/toolkit";
import { useDispatch, useSelector, type RootState } from "./store";
import { useState, type ChangeEvent } from "react";
import type { TErrorState, TFieldType, TFormValidators, TUseFormWithValidation } from "../utils/types";

export function useFormWithValidation<T>(
    selector: (state: RootState) => T,
    setFormValue: ActionCreatorWithPayload<TFieldType<T>>,
    validators: TFormValidators<T>
): TUseFormWithValidation<T> {
    const values = useSelector(selector);
    const [errors, setErrors] = 
                useState<TErrorState<T>>(initError<T>(values));
    const [isValid, setIsValid] = useState(false);
    const dispatch = useDispatch();

    const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
        const input = e.target;
        const value = input.value;
        const name = input.name as keyof T;
        const isValid = validators[name]?.validator(value) ?? true;
        dispatch(setFormValue({ field: name, value}));
        setErrors({
        ...errors,
        [name]: !isValid ? validators[name]!.message : undefined
        });
        setIsValid(isValid);
    };

    return { values, handleChange, errors, isValid };
}

function initError<T>(a: T): TErrorState<T> {
    return Object.keys(a as object).reduce((acc, k) => {
        acc[k as keyof T] = ""; return acc
    }, {} as TErrorState<T>);
} 