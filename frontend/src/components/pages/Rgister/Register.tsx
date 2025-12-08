import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "../../../hooks/store";
import { Input } from "../../Input/Input";
import styles from "./Register.module.css";
import { getError, getUser, setError } from "../../../services/auth/slice";
import { registerUser } from "../../../services/auth/action";
import { FormButton } from "../../FormButton/FormButton";
import { Link, useNavigate } from "react-router-dom";
import { formValidators } from "../../../utils/formValidators";

export  const Register = () => {
    const dispatch = useDispatch();
    const [userData, setUserData] = useState({
        username: '',
        email: '',
        password: ''
    });
    const [validationErrors, setValidationErrors] = useState({
        username: '',
        email: '',
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

        if (e.target.name === 'email') {
            const emailError = formValidators.email.validator(e.target.value) ? '' : formValidators.email.message;
            setValidationErrors({ ...validationErrors, email: emailError });
            // eslint-disable-next-line @typescript-eslint/no-unused-expressions
            e.target.value === '' ? setValidationErrors({ ...validationErrors, email: '' }) : null;
        } else if (e.target.name === 'password') {
            const passwordError = formValidators.password.validator(e.target.value) ? '' : formValidators.password.message;
            setValidationErrors({ ...validationErrors, password: passwordError });
            // eslint-disable-next-line @typescript-eslint/no-unused-expressions
            e.target.value === '' ? setValidationErrors({ ...validationErrors, password: '' }) : null;
        } else if (e.target.name === 'username') {
            const usernameError = formValidators.name.validator(e.target.value) ? '' : formValidators.name.message;
            setValidationErrors({ ...validationErrors, username: usernameError });
            // eslint-disable-next-line @typescript-eslint/no-unused-expressions
            e.target.value === '' ? setValidationErrors({ ...validationErrors, username: '' }) : null;
        }
        
        dispatch(setError(null));
    }

    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!userData.password || !userData.username) {
            return;
        }
        dispatch(registerUser(userData));
        if (!user) {
            return;
        }
        window.parent.postMessage({ type: "modalClosed" }, "*");
        navigate('/');
    }
    
    useEffect(() => {
        return () => {
            dispatch(setError(null));
        }
    }, [dispatch]);

    return (
        <form className={styles.register} onSubmit={handleSubmit}>
            <div className={styles.inputs}>
                <Input 
                    label="Имя*" 
                    type="text" 
                    name="username" 
                    placeholder="Введите имя" 
                    handleChangeInput={handleChangeInput}
                    error={validationErrors.username} />
                <Input 
                    label="Email" 
                    type="email" 
                    name="email" 
                    placeholder="Введите email" 
                    handleChangeInput={handleChangeInput} 
                    error={validationErrors.email}/>
                <Input 
                    label="Пароль*" 
                    type={showPassword ? "text" : "password"} 
                    name="password" 
                    placeholder="Введите пароль" 
                    handleChangeInput={handleChangeInput}
                    error={validationErrors.password}
                    setShowPassword={setShowPassword}
                    showPassword={showPassword}
                    />
                
            </div>
            <div className={styles.buttons}>
                <Link to="/login" replace className={styles.link}>Войти</Link>
                <FormButton text="Зарегистрироваться" disabled={!userData.password || !userData.username || validationErrors.email !== '' || validationErrors.password !== '' || validationErrors.username !== '' || (error ? true : false)} />
            </div>
            {error && <span className={styles.error}>{error}</span>}
        </form>
    )
}