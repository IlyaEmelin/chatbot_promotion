export const PWD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,30}$/;
export const EMAIL_REGEX = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
// eslint-disable-next-line no-misleading-character-class
export const NAME_REGEX = /^[a-zA-Zа-яА-ЯёЁ0-9@./+/-/_]+$/;

export const formValidators = {
    name: {
        validator: (value: string) => NAME_REGEX.test(value),
        message: "Имя может содержать только буквы, цифры и символы @.+-_",
    },
    email: {
        validator: (value: string) => EMAIL_REGEX.test(value),
        message: "Укажите корректный email.",
    },
    password: {
        validator: (value: string) => PWD_REGEX.test(value),
        message: "Пароль должен содержать заглавные и строчные латинские буквы, цифры, специальные символы: @$!%*?& и быть длиной не менее 8 символов.",
    }
}; 