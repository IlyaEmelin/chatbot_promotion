import { Link, useNavigate } from "react-router-dom";
import styles from "./Header.module.css";
import clsx from "clsx";
import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "../../hooks/store";
import { getUser } from "../../services/auth/slice";
import { logoutUser } from "../../services/auth/action";

export const Header = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const navigate = useNavigate();
    const dispatch = useDispatch();
    const user = useSelector(getUser);
    console.log("пользователь в шапке", user);

    const toggleMenu = () => setIsMenuOpen(!isMenuOpen);
    useEffect(() => {
        if (isMenuOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
        }
    }, [isMenuOpen]);

    return (
        <>
            <header className={clsx(styles.header, isMenuOpen && styles.active)}>
                <div className={styles.logo}>
                    <img src="src/assets/logo.svg" alt="логотип" />
                </div>
                <nav>
                    <ul className={styles.menu}>
                        <li className={clsx(styles.menu__item, styles.menu__item_active)}>
                            <Link to="#">Создать анкету</Link>
                        </li>
                    </ul>
                </nav>
                { user ? (
                    <button 
                        className={styles.button} 
                        onClick={() => {console.log('выходим'); dispatch(logoutUser())}}>
                            Выйти
                    </button>
                ) : (
                    <button 
                        className={styles.button} 
                        onClick={() => {navigate('/login')}}>
                            Войти
                    </button>
                )}
                </header>
            <div className={clsx(styles.burger, isMenuOpen && styles.active)} onClick={toggleMenu}>
                <div className={styles.bar}></div>
                <div className={styles.bar}></div>
                <div className={styles.bar}></div>
            </div>
            <div className={clsx(styles.closeMenu, isMenuOpen && styles.active)} onClick={toggleMenu}>
                <div className={styles.line}></div>
                <div className={styles.line}></div>
            </div>
        </>
    );
};
