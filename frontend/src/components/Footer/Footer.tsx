import { Link } from "react-router-dom";
import styles from "./Footer.module.css";

export const Footer = () => {
    return (
        <footer className={styles.footer}>
            <div className={styles.info}>
                <p className={styles.copyright}>&copy; 2021-2025. 0+</p>
                <p>
                    АНО БО «ПРОДВИЖЕНИЕ»<br />
                    ИНН 7713482487<br />
                    КПП 771301001<br />
                    ОГРН 1217700251548<br />
                    БИК 044525411<br />
                    К/С 30101810145250000411<br />
                    Р/С 40703810616100000001 в Филиал "ЦЕНТРАЛЬНЫЙ"<br />
                    Банка ВТБ ПАО Г. МОСКВА<br />
                    27422, Москва, ул. Тимирязевская, д. 2/3, оф 200A<br />
                </p>

            </div>
            <div>
                <nav className={styles.nav}>
                    <Link to="#" className={styles.nav__link}>Подопечным</Link>
                    <Link to="#" className={styles.nav__link}>Политика конфиденциальности</Link>
                    <Link to="#" className={styles.nav__link}>Оферта о благотворительном пожертвовании</Link>
                    <Link to="#" className={styles.nav__link}>СМС-пожертвование</Link>
                    <div className={styles.contacts}>
                        <Link to="#" className={styles.nav__link}>Написать нам в ТГ</Link>
                        <div style={{ display: "flex", gap: "20px" }}>
                            <Link to="#" className={styles.nav__link}>8 800 550 17 82</Link>
                            <Link to="#" className={styles.nav__link}>pro@dvizhenie.life</Link>
                        </div>
                    </div>
                </nav>
                <button className={styles.button}>Войти</button>
            </div>
        </footer>
    );
};