import React from 'react';
import styles from './Loading.module.css';

export const Loading: React.FC = () => {
  return (
    <div className={styles.container}>
      <div className={styles.message}>
        <div className={styles.dots}>
          <div className={styles.dot}></div>
          <div className={styles.dot}></div>
          <div className={styles.dot}></div>
        </div>
      </div>
    </div>
  );
};

export default Loading;