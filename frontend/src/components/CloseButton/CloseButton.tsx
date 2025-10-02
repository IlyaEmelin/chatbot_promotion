import styles from "./CloseButton.module.css";

    export const CloseButton = ({ onClick, color }) => {
        return (
                <div className={styles.closeMenu} onClick={onClick}>
                    {
                        color === 'black' ?
                        <img src="src/assets/X-black.svg" alt = "иконка закрытия окна" />
                        :
                        <img src="src/assets/X-white.svg" alt = "иконка закрытия окна" />
                    }
                </div>
        )
    }