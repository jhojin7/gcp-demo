// Page Object Model Contract
// Defines the structure and interface for page object classes

export interface PageObjectContract {
  // Every page object must have these base methods
  goto(): Promise<void>;
  isLoaded(): Promise<boolean>;
  getTitle(): Promise<string>;
}

// File Browser Page Contract
export interface FileBrowserPageContract extends PageObjectContract {
  // Navigation methods
  navigateToFolder(folderName: string): Promise<void>;
  navigateUp(): Promise<void>;
  goToRoot(): Promise<void>;

  // File operations
  uploadFile(filePath: string): Promise<void>;
  uploadFileViaDragDrop(filePath: string): Promise<void>;
  downloadFile(fileName: string): Promise<void>;
  deleteFile(fileName: string): Promise<void>;
  selectFile(fileName: string): Promise<void>;
  selectMultipleFiles(fileNames: string[]): Promise<void>;

  // Folder operations
  createFolder(folderName: string): Promise<void>;
  renameFolder(oldName: string, newName: string): Promise<void>;
  deleteFolder(folderName: string): Promise<void>;

  // File list interactions
  getFileList(): Promise<string[]>;
  getFileCount(): Promise<number>;
  isFileVisible(fileName: string): Promise<boolean>;
  getFileMetadata(fileName: string): Promise<FileMetadata>;

  // Version management
  viewFileVersions(fileName: string): Promise<void>;
  getVersionCount(fileName: string): Promise<number>;

  // UI state verification
  isUploadAreaVisible(): Promise<boolean>;
  isFileListVisible(): Promise<boolean>;
  isLoadingIndicatorVisible(): Promise<boolean>;
  isErrorMessageVisible(): Promise<boolean>;
  getErrorMessage(): Promise<string>;
}

// Version History Page Contract
export interface VersionHistoryPageContract extends PageObjectContract {
  // Version list operations
  getVersionList(): Promise<VersionInfo[]>;
  getVersionCount(): Promise<number>;
  selectVersion(versionNumber: number): Promise<void>;

  // Version actions
  downloadVersion(versionNumber: number): Promise<void>;
  restoreVersion(versionNumber: number): Promise<void>;
  compareVersions(version1: number, version2: number): Promise<void>;

  // Version metadata
  getVersionMetadata(versionNumber: number): Promise<VersionMetadata>;
  getVersionTimestamp(versionNumber: number): Promise<string>;
  getVersionSize(versionNumber: number): Promise<string>;

  // Navigation
  returnToFileBrowser(): Promise<void>;
}

// Login Page Contract
export interface LoginPageContract extends PageObjectContract {
  // Authentication methods
  login(username: string, password: string): Promise<void>;
  logout(): Promise<void>;
  isLoggedIn(): Promise<boolean>;

  // Form interactions
  enterUsername(username: string): Promise<void>;
  enterPassword(password: string): Promise<void>;
  clickLoginButton(): Promise<void>;

  // Error handling
  isLoginErrorVisible(): Promise<boolean>;
  getLoginErrorMessage(): Promise<string>;
}

// Upload Progress Modal Contract
export interface UploadProgressModalContract extends PageObjectContract {
  // Progress tracking
  getUploadProgress(): Promise<number>;
  getUploadStatus(): Promise<UploadStatus>;
  getUploadedFileName(): Promise<string>;

  // Modal interactions
  cancelUpload(): Promise<void>;
  closeModal(): Promise<void>;
  isModalVisible(): Promise<boolean>;

  // Error handling
  isUploadErrorVisible(): Promise<boolean>;
  getUploadErrorMessage(): Promise<string>;
}

// Common selector patterns that all page objects should follow
export interface PageSelectors {
  // Base page elements
  readonly header: string;
  readonly navigation: string;
  readonly content: string;
  readonly footer: string;

  // Interactive elements
  readonly buttons: Record<string, string>;
  readonly inputs: Record<string, string>;
  readonly links: Record<string, string>;

  // State indicators
  readonly loadingSpinner: string;
  readonly errorMessage: string;
  readonly successMessage: string;
}

// Data types for page object contracts
export interface FileMetadata {
  name: string;
  size: string;
  lastModified: string;
  type: string;
  versionCount: number;
}

export interface VersionInfo {
  versionNumber: number;
  timestamp: string;
  size: string;
  isCurrentVersion: boolean;
}

export interface VersionMetadata {
  versionNumber: number;
  timestamp: string;
  size: string;
  uploadedBy: string;
  checksum: string;
}

export enum UploadStatus {
  PENDING = 'pending',
  UPLOADING = 'uploading',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

// Test helper contracts
export interface TestHelperContract {
  // File system operations
  createTestFile(filename: string, size?: number): Promise<string>;
  deleteTestFile(filePath: string): Promise<void>;
  getTestDataPath(): string;

  // Mock GCP operations
  mockGCPResponse(operation: string, response: any): Promise<void>;
  resetGCPMocks(): Promise<void>;

  // Browser utilities
  waitForFileDownload(fileName: string, timeout?: number): Promise<string>;
  captureNetworkRequests(): Promise<NetworkRequest[]>;
  simulateNetworkFailure(): Promise<void>;
  restoreNetwork(): Promise<void>;
}

export interface NetworkRequest {
  url: string;
  method: string;
  status: number;
  responseTime: number;
  requestHeaders: Record<string, string>;
  responseHeaders: Record<string, string>;
}