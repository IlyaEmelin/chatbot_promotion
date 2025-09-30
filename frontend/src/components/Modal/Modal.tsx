
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
                    <h2>{title}</h2>
                    <button onClick={onClose}>X
                    </button> {/* CloseButton */}
                </div>
                <div className={styles.modalContent}>
                    {children}
                </div>
            </div>
        </div>
    )
}