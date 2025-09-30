export const PWD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,20}$/;
export const EMAIL_REGEX = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;

export const formValidators = {
    email: {
        validator: (value: string) => EMAIL_REGEX.test(value),
        message: "Укажите корректный email.",
    },
    password: {
        validator: (value: string) => PWD_REGEX.test(value),
        message: "Пароль должен содержать заглавные и строчные латинские буквы, цифры, специальные символы: @$!%*?& и быть длиной не менее 8 символов.",
    }
}; 