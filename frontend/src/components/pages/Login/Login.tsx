
import { useState } from 'react';
import { useDispatch, useSelector } from '../../../hooks/store';
import styles from './Login.module.css';
import { loginUser } from '../../../services/auth/action';
import { getError } from '../../../services/auth/slice';
import { Input } from '../../Input/Input';
import { Link, useNavigate } from 'react-router-dom';
import { FormButton } from '../../FormButton/FormButton';

export const Login = () => {
    const dispatch = useDispatch();
    const [userData, setUserData] = useState({
        username: '',
        password: ''
    });
    const error = useSelector(getError);
    const navigate = useNavigate();

    const handleChangeInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        setUserData({
            ...userData,
            [e.target.name]: e.target.value
        });
    }

    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!userData.username || !userData.password) {
            return;
        }
        console.log('login submit', userData);
        dispatch(loginUser(userData));
        navigate(-1)
    }

    return (
        <form className={styles.login} onSubmit={handleSubmit}>
            <Input label="Имя" type="text" name="username" placeholder="Введите имя" handleChangeInput={handleChangeInput} />
            <Input label="Пароль" type="password" name="password" placeholder="Введите пароль" handleChangeInput={handleChangeInput} />
            <FormButton text="Войти" />
            <span className={styles.error}>{error}</span>
            <div className={styles.links}>
                <Link to="/register" replace className={styles.link}>Регистрация</Link>
                <Link to="/reset-password" className={styles.link}>Забыли пароль?</Link>
            </div>
        </form>
    )
};