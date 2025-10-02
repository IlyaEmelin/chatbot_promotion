import { CloseButton } from '../CloseButton/CloseButton';
import styles from './Modal.module.css';

type ModalProps = {
    title: string;
    onClose: () => void;
    children: React.ReactNode;
}

export const Modal: React.FC<ModalProps> = ({ title, onClose, children }) => {
    return (
        <div className={styles.overlay} data-cy='modalOverlay'>
            <div className={styles.modal}>
                <div className={styles.modalHeader}>
                    <h1 className={styles.title}>{title}</h1>
                    <CloseButton onClick={onClose} color='black' />
                </div>
                <div className={styles.modalContent}>
                    {children}
                </div>
            </div>
        </div>
    )
}