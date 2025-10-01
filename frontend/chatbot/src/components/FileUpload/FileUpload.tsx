import React, { useState, useRef } from 'react';
import { X, Upload, FileText, Image as ImageIcon } from 'lucide-react';
import { useAppSelector } from '../../hooks/redux';
import { surveyAPI } from '../../api/surveyAPI';
import { FileWithPreview, UploadedDocument } from '../../types';
import styles from './FileUpload.module.css';

interface FileUploadProps {
  onUploadComplete?: (documents: UploadedDocument[]) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onUploadComplete }) => {
  const { surveyId } = useAppSelector(state => state.survey);
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [uploadedDocs, setUploadedDocs] = useState<UploadedDocument[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const isImage = (file: File) => {
    return file.type.startsWith('image/');
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = event.target.files;
    if (!selectedFiles || selectedFiles.length === 0 || !surveyId) return;

    const newFiles: FileWithPreview[] = Array.from(selectedFiles).map(file => ({
      file,
      preview: isImage(file) ? URL.createObjectURL(file) : '',
      isUploading: false,
    }));

    setFiles(prev => [...prev, ...newFiles]);

    // Автоматически загружаем файлы
    for (const fileWithPreview of newFiles) {
      await uploadFile(fileWithPreview);
    }

    // Очищаем input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const uploadFile = async (fileWithPreview: FileWithPreview) => {
    if (!surveyId) return;

    // Устанавливаем статус загрузки
    setFiles(prev => prev.map(f => 
      f.file === fileWithPreview.file 
        ? { ...f, isUploading: true, uploadError: undefined }
        : f
    ));

    try {
      const uploadedDoc = await surveyAPI.uploadDocument(surveyId, fileWithPreview.file);
      
      // Обновляем файл с ID загруженного документа
      setFiles(prev => prev.map(f => 
        f.file === fileWithPreview.file 
          ? { ...f, isUploading: false, uploadedId: uploadedDoc.id }
          : f
      ));

      // Добавляем в список загруженных
      setUploadedDocs(prev => [...prev, uploadedDoc]);
      
      // Уведомляем родительский компонент
      if (onUploadComplete) {
        onUploadComplete([...uploadedDocs, uploadedDoc]);
      }

      console.log('✅ File uploaded successfully:', uploadedDoc);
    } catch (error) {
      console.error('❌ Error uploading file:', error);
      
      setFiles(prev => prev.map(f => 
        f.file === fileWithPreview.file 
          ? { 
              ...f, 
              isUploading: false, 
              uploadError: error instanceof Error ? error.message : 'Ошибка загрузки'
            }
          : f
      ));
    }
  };

  const handleRemoveFile = async (fileWithPreview: FileWithPreview) => {
    // Если файл был загружен на сервер, удаляем его
    if (fileWithPreview.uploadedId && surveyId) {
      try {
        await surveyAPI.deleteDocument(surveyId, fileWithPreview.uploadedId);
        
        // Удаляем из списка загруженных
        setUploadedDocs(prev => prev.filter(doc => doc.id !== fileWithPreview.uploadedId));
        
        console.log('✅ Document deleted from server');
      } catch (error) {
        console.error('❌ Error deleting document:', error);
        alert('Не удалось удалить файл с сервера');
        return;
      }
    }

    // Освобождаем URL превью
    if (fileWithPreview.preview) {
      URL.revokeObjectURL(fileWithPreview.preview);
    }

    // Удаляем из локального состояния
    setFiles(prev => prev.filter(f => f.file !== fileWithPreview.file));
  };

  return (
    <div className={styles.container}>
      {/* Кнопка загрузки */}
      <button
        type="button"
        className={styles.uploadButton}
        onClick={() => fileInputRef.current?.click()}
      >
        <Upload size={20} />
        <span>Загрузить файлы</span>
      </button>

      {/* Скрытый input */}
      <input
        ref={fileInputRef}
        type="file"
        onChange={handleFileSelect}
        multiple
        accept="image/*,.pdf,.doc,.docx"
        className={styles.hiddenInput}
      />

      {/* Список файлов с превью */}
      {files.length > 0 && (
        <div className={styles.filesList}>
          {files.map((fileWithPreview, index) => (
            <div key={index} className={styles.fileItem}>
              {/* Превью */}
              <div className={styles.filePreview}>
                {isImage(fileWithPreview.file) ? (
                  <img 
                    src={fileWithPreview.preview} 
                    alt={fileWithPreview.file.name}
                    className={styles.previewImage}
                  />
                ) : (
                  <div className={styles.fileIcon}>
                    <FileText size={32} color="#6B7280" />
                  </div>
                )}
                
                {/* Индикатор загрузки */}
                {fileWithPreview.isUploading && (
                  <div className={styles.uploadingOverlay}>
                    <div className={styles.spinner}></div>
                  </div>
                )}
              </div>

              {/* Информация о файле */}
              <div className={styles.fileInfo}>
                <p className={styles.fileName} title={fileWithPreview.file.name}>
                  {fileWithPreview.file.name}
                </p>
                <p className={styles.fileSize}>
                  {formatFileSize(fileWithPreview.file.size)}
                </p>
                
                {fileWithPreview.uploadError && (
                  <p className={styles.uploadError}>
                    {fileWithPreview.uploadError}
                  </p>
                )}
                
                {fileWithPreview.uploadedId && (
                  <p className={styles.uploadSuccess}>
                    ✓ Загружено
                  </p>
                )}
              </div>

              {/* Кнопка удаления */}
              <button
                type="button"
                className={styles.removeButton}
                onClick={() => handleRemoveFile(fileWithPreview)}
                disabled={fileWithPreview.isUploading}
                title="Удалить файл"
              >
                <X size={18} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileUpload;