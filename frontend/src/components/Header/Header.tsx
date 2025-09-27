import { Link } from "react-router-dom";
import styles from "./Header.module.css";
import clsx from "clsx";
import { useState } from "react";

export const Header = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);

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
                <button className={styles.button}>Войти</button>
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