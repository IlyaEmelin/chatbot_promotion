import React, { useState, useRef, useEffect } from 'react';
import { X, Upload, FileText, Lock } from 'lucide-react';
import { useAppSelector } from '../../hooks/redux';
import { surveyAPI, getCookie } from '../../api/surveyAPI';
import { FileWithPreview, UploadedDocument } from '../../types';
import styles from './FileUpload.module.css';

interface FileUploadProps {
  onUploadComplete?: (documents: UploadedDocument[]) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onUploadComplete }) => {
  const { surveyId } = useAppSelector(state => state.survey);
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  //eslint-disable-next-line  @typescript-eslint/no-unused-vars
  const [_, setUploadedDocs] = useState<UploadedDocument[]>([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // ПРОВЕРКА АВТОРИЗАЦИИ
  useEffect(() => {
    const authToken = getCookie('auth_token');
    setIsAuthenticated(!!authToken);
  }, []);

  const isImage = (file: File) => {
    return file.type.startsWith('image/');
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 10) / 10 + ' ' + sizes[i];
  };

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!isAuthenticated) {
      alert('Необходимо авторизоваться для загрузки файлов');
      return;
    }

    const selectedFiles = event.target.files;
    if (!selectedFiles || selectedFiles.length === 0 || !surveyId) return;

    const newFiles: FileWithPreview[] = Array.from(selectedFiles).map(file => ({
      file,
      preview: isImage(file) ? URL.createObjectURL(file) : '',
      isUploading: true,
    }));

    setFiles(prev => [...prev, ...newFiles]);

    const uploadPromises = newFiles.map(fileWithPreview => uploadFile(fileWithPreview));
    await Promise.all(uploadPromises);

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const uploadFile = async (fileWithPreview: FileWithPreview) => {
    if (!surveyId) return;

    try {
      const uploadedDoc = await surveyAPI.uploadDocument(surveyId, fileWithPreview.file);
      
      setFiles(prev => prev.map(f => 
        f.file === fileWithPreview.file 
          ? { ...f, isUploading: false, uploadedId: uploadedDoc.id }
          : f
      ));

      setUploadedDocs(prev => {
        const updated = [...prev, uploadedDoc];
        if (onUploadComplete) {
          onUploadComplete(updated);
        }
        return updated;
      });

      console.log('✅ File uploaded successfully:', uploadedDoc);
    } catch (error) {
      console.error('❌ Error uploading file:', error);
      
      let errorMessage = 'Ошибка загрузки';
      if (error instanceof Error) {
        errorMessage = error.message;
        if (errorMessage.includes('Учетные данные') || errorMessage.includes('401')) {
          errorMessage = 'Требуется авторизация';
        }
      }
      
      setFiles(prev => prev.map(f => 
        f.file === fileWithPreview.file 
          ? { 
              ...f, 
              isUploading: false, 
              uploadError: errorMessage
            }
          : f
      ));
    }
  };

  const handleRemoveFile = async (fileWithPreview: FileWithPreview) => {
    if (!isAuthenticated) {
      alert('Необходимо авторизоваться');
      return;
    }

    if (fileWithPreview.uploadedId && surveyId) {
      try {
        await surveyAPI.deleteDocument(surveyId, fileWithPreview.uploadedId);
        
        setUploadedDocs(prev => {
          const updated = prev.filter(doc => doc.id !== fileWithPreview.uploadedId);
          if (onUploadComplete) {
            onUploadComplete(updated);
          }
          return updated;
        });
        
        console.log('✅ Document deleted from server');
      } catch (error) {
        console.error('❌ Error deleting document:', error);
        alert('Не удалось удалить файл с сервера');
        return;
      }
    }

    if (fileWithPreview.preview) {
      URL.revokeObjectURL(fileWithPreview.preview);
    }

    setFiles(prev => prev.filter(f => f.file !== fileWithPreview.file));
  };

  const uploadedCount = files.filter(f => f.uploadedId).length;
  const totalCount = files.length;

  if (!isAuthenticated) {
    return (
      <div className={styles.container}>
        <div className={styles.authWarning}>
          <Lock size={20} />
          <p>Для загрузки файлов необходимо авторизоваться</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <button
        type="button"
        className={styles.uploadButton}
        onClick={() => fileInputRef.current?.click()}
      >
        <Upload size={20} />
        <span>Загрузить файлы</span>
      </button>

      <input
        ref={fileInputRef}
        type="file"
        onChange={handleFileSelect}
        multiple
        accept="image/*,.pdf,.doc,.docx"
        className={styles.hiddenInput}
      />

      {files.length > 0 && (
        <>
          <div className={styles.filesList}>
            {files.map((fileWithPreview, index) => (
              <div key={index} className={styles.fileItem}>
                <div className={styles.filePreview}>
                  {isImage(fileWithPreview.file) ? (
                    <img 
                      src={fileWithPreview.preview} 
                      alt={fileWithPreview.file.name}
                      className={styles.previewImage}
                    />
                  ) : (
                    <div className={styles.fileIcon}>
                      <FileText size={24} color="#6B7280" />
                    </div>
                  )}
                  
                  {fileWithPreview.isUploading && (
                    <div className={styles.uploadingOverlay}>
                      <div className={styles.spinner}></div>
                    </div>
                  )}
                </div>

                <div className={styles.fileInfo}>
                  <p className={styles.fileName} title={fileWithPreview.file.name}>
                    {fileWithPreview.file.name.length > 15 
                      ? fileWithPreview.file.name.substring(0, 12) + '...' 
                      : fileWithPreview.file.name}
                  </p>
                  <p className={styles.fileSize}>
                    {formatFileSize(fileWithPreview.file.size)}
                  </p>
                  
                  {fileWithPreview.uploadError && (
                    <p className={styles.uploadError}>Ошибка</p>
                  )}
                  
                  {fileWithPreview.uploadedId && (
                    <p className={styles.uploadSuccess}>✓</p>
                  )}
                </div>

                <button
                  type="button"
                  className={styles.removeButton}
                  onClick={() => handleRemoveFile(fileWithPreview)}
                  disabled={fileWithPreview.isUploading}
                  title="Удалить файл"
                >
                  <X size={14} />
                </button>
              </div>
            ))}
          </div>

          {uploadedCount === totalCount && totalCount > 0 && (
            <div className={styles.uploadSummary}>
              ✓ Загружено файлов: {uploadedCount}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default FileUpload;