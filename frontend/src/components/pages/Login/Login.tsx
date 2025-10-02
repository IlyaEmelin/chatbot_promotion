
import { useState } from 'react';
import { useDispatch } from '../../../hooks/store';
import styles from './Login.module.css';
import { loginUser } from '../../../services/auth/action';
// import { getError } from '../../../services/auth/slice';
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
    // const error = useSelector(getError);
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
            <div className={styles.inputs}>
                <Input 
                    label="Имя" 
                    type="text" 
                    name="username" 
                    placeholder="Введите имя" 
                    handleChangeInput={handleChangeInput}
                     />
                <div className={styles.passwordWrapper}>
                    <Input 
                        label="Пароль" 
                        type={showPassword ? "text" : "password"} 
                        name="password" 
                        placeholder="Введите пароль" 
                        handleChangeInput={handleChangeInput}
                         />
                    <button 
                        className={styles.showPasswordButton} 
                        type="button" 
                        onClick={() => setShowPassword(!showPassword)}>
                        {showPassword ? 
                            <img 
                                className={styles.iconPassword} 
                                src="src/assets/hide-password.svg" 
                                alt="скрыть пароль"
                            /> 
                            : 
                            <img 
                                className={styles.iconPassword} 
                                src="src/assets/show-password.svg" 
                                alt="показать пароль" 
                            />
                        }
                    </button>
                </div>
            </div>
            <div className={styles.buttons}>
                <Link to="/register" replace className={styles.link}>Зарегистрироваться</Link>
                <FormButton text="Войти" />
            </div>
        </form>
    )
};