import { useState } from "react";
import { useDispatch, useSelector } from "../../../hooks/store";
import { Input } from "../../Input/Input";
import styles from "./Register.module.css";
import { getError } from "../../../services/auth/slice";
import { registerUser } from "../../../services/auth/action";
import { FormButton } from "../../FormButton/FormButton";

export  const Register = () => {
    const dispatch = useDispatch();
    const [userData, setUserData] = useState({
        username: '',
        email: '',
        password: ''
    });
    const error = useSelector(getError);
    

    const handleChangeInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        setUserData({
            ...userData,
            [e.target.name]: e.target.value
        });
    }

    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!userData.email || !userData.password || !userData.username) {
            return;
        }
        console.log('register submit', userData);
        dispatch(registerUser(userData));
    }

    return (
        <form className={styles.register} onSubmit={handleSubmit}>
            <Input label="Имя" type="text" name="username" placeholder="Введите имя" handleChangeInput={handleChangeInput} />
            <Input label="Логин" type="email" name="email" placeholder="Введите email" handleChangeInput={handleChangeInput} />
            <Input label="Пароль" type="password" name="password" placeholder="Введите пароль" handleChangeInput={handleChangeInput} />
            <FormButton text="Зарегистрироваться" />
            <span className={styles.error}>{error}</span>
        </form>
    )
}