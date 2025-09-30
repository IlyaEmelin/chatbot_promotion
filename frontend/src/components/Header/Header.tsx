<<<<<<< HEAD
import React from 'react';
import { RotateCcw, X } from 'lucide-react';
import { useAppDispatch, useAppSelector } from '../../hooks/redux';
import { resetSurvey, startSurveyAsync } from '../../store/surveySlice';
import styles from './Header.module.css';

interface HeaderProps {
  onClose: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onClose }) => {
  const dispatch = useAppDispatch();
  const { isLoading } = useAppSelector(state => state.survey);

  const handleReset = () => {
    dispatch(resetSurvey());
    dispatch(startSurveyAsync(true));
  };

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Анкета-бот</h2>
      <div className={styles.actions}>
        <button
          className={styles.actionButton}
          onClick={handleReset}
          disabled={isLoading}
          title="Начать заново"
          type="button"
        >
          <RotateCcw size={18} />
        </button>
        <button
          className={styles.actionButton}
          onClick={onClose}
          title="Закрыть"
          type="button"
        >
          <X size={18} />
        </button>
      </div>
    </div>
  );
};

export default Header;
=======
import { Link, useNavigate } from "react-router-dom";
import styles from "./Header.module.css";
import clsx from "clsx";
import { useState } from "react";
import { useDispatch, useSelector } from "../../hooks/store";
import { getUser } from "../../services/auth/slice";
import { logoutUser } from "../../services/auth/action";

export const Header = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const navigate = useNavigate();
    const dispatch = useDispatch();
    const user = useSelector(getUser);

    const toggleMenu = () => setIsMenuOpen(!isMenuOpen);

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
                        <li className={styles.menu__item}>
                            <Link to="#">Списки анкет</Link>
                        </li>
                    </ul>
                </nav>
                { user ? (
                    <button 
                        className={styles.button} 
                        onClick={() => {dispatch(logoutUser())}}>
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
>>>>>>> front_Olga
