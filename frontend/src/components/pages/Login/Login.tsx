
import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from '../../../hooks/store';
import styles from './Login.module.css';
import { loginUser } from '../../../services/auth/action';
import { getError, getUser, setError } from '../../../services/auth/slice';
import { Input } from '../../Input/Input';
import { Link, useNavigate } from 'react-router-dom';
import { FormButton } from '../../FormButton/FormButton';

export const Login = () => {
    const dispatch = useDispatch();
    const [userData, setUserData] = useState({
        username: '',
        password: ''
    });
    const [showPassword, setShowPassword] = useState(false);
    const error = useSelector(getError);
    const user = useSelector(getUser);
    const navigate = useNavigate();

    const handleChangeInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        setUserData({
            ...userData,
            [e.target.name]: e.target.value
        });
        dispatch(setError(null));
    }

    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!userData.username || !userData.password || error) {
            return;
        }
        dispatch(loginUser(userData));
        if (!user) {
            return;
        }
        navigate(-1);
    }

    useEffect(() => {
        return () => {
            dispatch(setError(null));
        }
    }, [dispatch]);

    return (
        <form className={styles.login} onSubmit={handleSubmit}>
            <div className={styles.inputs}>
                <Input 
                    label="Имя*" 
                    type="text" 
                    name="username" 
                    placeholder="Введите имя" 
                    handleChangeInput={handleChangeInput}
                     />
                <Input 
                    label="Пароль*" 
                    type={showPassword ? 'text' : 'password'} 
                    name="password" 
                    placeholder="Введите пароль" 
                    handleChangeInput={handleChangeInput}
                    setShowPassword={setShowPassword}
                    showPassword={showPassword}
                     />
            </div>
            <div className={styles.buttons}>
                <Link to="/register" replace className={styles.link}>Зарегистрироваться</Link>
                <FormButton text="Войти" disabled={!userData.username || !userData.password || (error ? true : false)} />
            </div>
            {error && <span className={styles.error}>{error}</span>}
        </form>
    )
};