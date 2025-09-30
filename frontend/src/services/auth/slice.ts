import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { TUser } from "../../utils/types";
import { loginUser, logoutUser, registerUser } from "./action";

type TAuthState = {
  user: TUser | null;
  isAuthChecked: boolean;
  error: string | null;
  isLoading: boolean;
};

export const initialState: TAuthState = {
  user: null,
  isAuthChecked: false,
  error: null,
  isLoading: false
};

export const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        setUser(state, action: PayloadAction<TUser | null>) {
        state.user = action.payload;
        },
        setIsAuthChecked(state, action: PayloadAction<boolean>) {
        state.isAuthChecked = action.payload;
        }
    },
    selectors: {
        getUser: (state) => state.user,
        getIsAuthChecked: (state) => state.isAuthChecked,
        getError: (state) => state.error,
        getIsLoading: (state) => state.isLoading
    },
    extraReducers: (builder) => {
        builder
        .addCase(registerUser.pending, (state) => {
            state.isAuthChecked = false;
            state.isLoading = true;
            state.error = null;
        })
        .addCase(registerUser.fulfilled, (state, action) => {
            state.user = action.payload;
            console.log('slice', state.user);
            state.isAuthChecked = true;
            state.isLoading = false;
            state.error = null;
        })
        .addCase(registerUser.rejected, (state, action) => {
            state.isAuthChecked = true;
            state.isLoading = false;
            state.error = action.error.message ?? null;
        })
        .addCase(loginUser.pending, (state) => {
            state.isAuthChecked = false;
            state.isLoading = true;
            state.error = null;
        })
        .addCase(loginUser.fulfilled, (state) => {
            state.isLoading = false;
            state.isAuthChecked = true;
            state.error = null;
        })
        .addCase(loginUser.rejected, (state, action) => {
            state.isLoading = false;
            state.isAuthChecked = true;
            state.error = action.error.message ?? null;
        })
        .addCase(logoutUser.pending, (state) => {
            state.isAuthChecked = true;
            state.isLoading = true;
        })
        .addCase(logoutUser.fulfilled, (state) => {
            state.user = null;
            state.isLoading = false;
            state.isAuthChecked = true;
        })
        .addCase(logoutUser.rejected, (state, action) => {
            state.isLoading = false;
            state.isAuthChecked = true;
            state.error = action.error.message ?? null;
        });
    }
});

export const { setUser, setIsAuthChecked } = authSlice.actions;
export const { getUser, getIsAuthChecked, getIsLoading, getError } =
  authSlice.selectors;