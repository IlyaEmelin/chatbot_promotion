export interface UploadedDocument {
  id: number;
  file: string; // URL файла
  uploaded_at?: string;
  file_name?: string;
  file_size?: number;
}

export interface FileWithPreview {
  file: File;
  preview: string;
  uploadedId?: number; // ID после загрузки на сервер
  isUploading?: boolean;
  uploadError?: string;
}