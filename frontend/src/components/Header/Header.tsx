import { Link } from "react-router-dom";
import styles from "./Header.module.css";
import clsx from "clsx";

export const Header = () => {
    return (
        <header className={styles.header}>
            <Link className={styles.logo} to="/">
                <img src="https://static.tildacdn.com/tild6663-3332-4332-b962-613834656535/__2.svg" alt="логотип" />
            </Link>
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
    );
};