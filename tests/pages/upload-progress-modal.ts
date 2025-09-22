import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base-page';

export enum UploadStatus {
  PENDING = 'pending',
  UPLOADING = 'uploading',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export interface UploadProgressInfo {
  fileName: string;
  progress: number;
  status: UploadStatus;
  uploadedBytes: number;
  totalBytes: number;
  speed: string;
  timeRemaining: string;
}

export class UploadProgressModal extends BasePage {
  // Modal container
  readonly modal: Locator;
  readonly modalOverlay: Locator;
  readonly modalContent: Locator;

  // Modal header
  readonly modalTitle: Locator;
  readonly closeButton: Locator;
  readonly minimizeButton: Locator;

  // File information
  readonly fileName: Locator;
  readonly fileSize: Locator;
  readonly fileType: Locator;

  // Progress indicators
  readonly progressBar: Locator;
  readonly progressPercentage: Locator;
  readonly progressText: Locator;
  readonly uploadedBytes: Locator;
  readonly totalBytes: Locator;

  // Upload statistics
  readonly uploadSpeed: Locator;
  readonly timeRemaining: Locator;
  readonly uploadStartTime: Locator;

  // Status indicators
  readonly statusIcon: Locator;
  readonly statusText: Locator;
  readonly uploadingIcon: Locator;
  readonly completedIcon: Locator;
  readonly errorIcon: Locator;

  // Action buttons
  readonly cancelButton: Locator;
  readonly pauseButton: Locator;
  readonly resumeButton: Locator;
  readonly retryButton: Locator;
  readonly doneButton: Locator;

  // Error handling
  readonly errorMessage: Locator;
  readonly errorDetails: Locator;
  readonly uploadErrorText: Locator;

  // Multiple file upload
  readonly fileList: Locator;
  readonly fileItem: Locator;
  readonly overallProgress: Locator;
  readonly completedCount: Locator;
  readonly totalCount: Locator;

  constructor(page: Page) {
    super(page, ''); // Modal doesn't have its own URL

    // Modal container
    this.modal = page.locator('[data-testid="upload-modal"], .upload-modal');
    this.modalOverlay = page.locator('[data-testid="modal-overlay"], .modal-overlay');
    this.modalContent = page.locator('[data-testid="modal-content"], .modal-content');

    // Modal header
    this.modalTitle = page.locator('[data-testid="modal-title"], .modal-title');
    this.closeButton = page.locator('[data-testid="close-modal"], .close-modal');
    this.minimizeButton = page.locator('[data-testid="minimize-modal"], .minimize-modal');

    // File information
    this.fileName = page.locator('[data-testid="upload-filename"], .upload-filename');
    this.fileSize = page.locator('[data-testid="upload-filesize"], .upload-filesize');
    this.fileType = page.locator('[data-testid="upload-filetype"], .upload-filetype');

    // Progress indicators
    this.progressBar = page.locator('[data-testid="progress-bar"], .progress-bar');
    this.progressPercentage = page.locator('[data-testid="progress-percentage"], .progress-percentage');
    this.progressText = page.locator('[data-testid="progress-text"], .progress-text');
    this.uploadedBytes = page.locator('[data-testid="uploaded-bytes"], .uploaded-bytes');
    this.totalBytes = page.locator('[data-testid="total-bytes"], .total-bytes');

    // Upload statistics
    this.uploadSpeed = page.locator('[data-testid="upload-speed"], .upload-speed');
    this.timeRemaining = page.locator('[data-testid="time-remaining"], .time-remaining');
    this.uploadStartTime = page.locator('[data-testid="upload-start-time"], .upload-start-time');

    // Status indicators
    this.statusIcon = page.locator('[data-testid="status-icon"], .status-icon');
    this.statusText = page.locator('[data-testid="status-text"], .status-text');
    this.uploadingIcon = page.locator('[data-testid="uploading-icon"], .uploading-icon');
    this.completedIcon = page.locator('[data-testid="completed-icon"], .completed-icon');
    this.errorIcon = page.locator('[data-testid="error-icon"], .error-icon');

    // Action buttons
    this.cancelButton = page.locator('[data-testid="cancel-upload"], .cancel-upload');
    this.pauseButton = page.locator('[data-testid="pause-upload"], .pause-upload');
    this.resumeButton = page.locator('[data-testid="resume-upload"], .resume-upload');
    this.retryButton = page.locator('[data-testid="retry-upload"], .retry-upload');
    this.doneButton = page.locator('[data-testid="done-upload"], .done-upload');

    // Error handling
    this.errorMessage = page.locator('[data-testid="upload-error"], .upload-error');
    this.errorDetails = page.locator('[data-testid="error-details"], .error-details');
    this.uploadErrorText = page.locator('[data-testid="upload-error-text"], .upload-error-text');

    // Multiple file upload
    this.fileList = page.locator('[data-testid="upload-file-list"], .upload-file-list');
    this.fileItem = page.locator('[data-testid="upload-file-item"], .upload-file-item');
    this.overallProgress = page.locator('[data-testid="overall-progress"], .overall-progress');
    this.completedCount = page.locator('[data-testid="completed-count"], .completed-count');
    this.totalCount = page.locator('[data-testid="total-count"], .total-count');
  }

  /**
   * Wait for modal to appear
   */
  async waitForModal(): Promise<void> {
    await this.waitForElement(this.modal);
  }

  /**
   * Check if modal is visible
   */
  async isModalVisible(): Promise<boolean> {
    return await this.isElementVisible(this.modal);
  }

  /**
   * Get upload progress percentage
   */
  async getUploadProgress(): Promise<number> {
    const progressText = await this.getElementText(this.progressPercentage);
    const match = progressText.match(/(\d+)%/);
    return match ? parseInt(match[1], 10) : 0;
  }

  /**
   * Get upload status
   */
  async getUploadStatus(): Promise<UploadStatus> {
    const statusText = await this.getElementText(this.statusText);

    switch (statusText.toLowerCase()) {
      case 'uploading':
        return UploadStatus.UPLOADING;
      case 'completed':
      case 'complete':
        return UploadStatus.COMPLETED;
      case 'failed':
      case 'error':
        return UploadStatus.FAILED;
      case 'cancelled':
        return UploadStatus.CANCELLED;
      default:
        return UploadStatus.PENDING;
    }
  }

  /**
   * Get uploaded file name
   */
  async getUploadedFileName(): Promise<string> {
    return await this.getElementText(this.fileName);
  }

  /**
   * Get file size information
   */
  async getFileSize(): Promise<string> {
    return await this.getElementText(this.fileSize);
  }

  /**
   * Get upload speed
   */
  async getUploadSpeed(): Promise<string> {
    return await this.getElementText(this.uploadSpeed);
  }

  /**
   * Get time remaining
   */
  async getTimeRemaining(): Promise<string> {
    return await this.getElementText(this.timeRemaining);
  }

  /**
   * Get detailed upload progress information
   */
  async getUploadProgressInfo(): Promise<UploadProgressInfo> {
    const fileName = await this.getUploadedFileName();
    const progress = await this.getUploadProgress();
    const status = await this.getUploadStatus();
    const speed = await this.getUploadSpeed();
    const timeRemaining = await this.getTimeRemaining();

    // Extract bytes information if available
    const uploadedBytesText = await this.getElementText(this.uploadedBytes);
    const totalBytesText = await this.getElementText(this.totalBytes);

    const uploadedBytes = this.parseBytes(uploadedBytesText);
    const totalBytes = this.parseBytes(totalBytesText);

    return {
      fileName,
      progress,
      status,
      uploadedBytes,
      totalBytes,
      speed,
      timeRemaining
    };
  }

  /**
   * Cancel the upload
   */
  async cancelUpload(): Promise<void> {
    if (await this.isElementVisible(this.cancelButton)) {
      await this.cancelButton.click();
      await this.waitForLoadingToComplete();
    }
  }

  /**
   * Pause the upload
   */
  async pauseUpload(): Promise<void> {
    if (await this.isElementVisible(this.pauseButton)) {
      await this.pauseButton.click();
    }
  }

  /**
   * Resume the upload
   */
  async resumeUpload(): Promise<void> {
    if (await this.isElementVisible(this.resumeButton)) {
      await this.resumeButton.click();
    }
  }

  /**
   * Retry failed upload
   */
  async retryUpload(): Promise<void> {
    if (await this.isElementVisible(this.retryButton)) {
      await this.retryButton.click();
      await this.waitForLoadingToComplete();
    }
  }

  /**
   * Close the modal
   */
  async closeModal(): Promise<void> {
    if (await this.isElementVisible(this.closeButton)) {
      await this.closeButton.click();
    } else if (await this.isElementVisible(this.doneButton)) {
      await this.doneButton.click();
    }

    // Wait for modal to disappear
    await this.waitForElementToHide(this.modal);
  }

  /**
   * Minimize the modal
   */
  async minimizeModal(): Promise<void> {
    if (await this.isElementVisible(this.minimizeButton)) {
      await this.minimizeButton.click();
    }
  }

  /**
   * Check if upload error is visible
   */
  async isUploadErrorVisible(): Promise<boolean> {
    return await this.isElementVisible(this.errorMessage) ||
           await this.isElementVisible(this.uploadErrorText);
  }

  /**
   * Get upload error message
   */
  async getUploadErrorMessage(): Promise<string> {
    if (await this.isElementVisible(this.errorMessage)) {
      return await this.getElementText(this.errorMessage);
    }
    if (await this.isElementVisible(this.uploadErrorText)) {
      return await this.getElementText(this.uploadErrorText);
    }
    return '';
  }

  /**
   * Get detailed error information
   */
  async getErrorDetails(): Promise<string> {
    if (await this.isElementVisible(this.errorDetails)) {
      return await this.getElementText(this.errorDetails);
    }
    return '';
  }

  /**
   * Wait for upload to complete
   */
  async waitForUploadComplete(timeout = 60000): Promise<void> {
    await expect(async () => {
      const status = await this.getUploadStatus();
      expect([UploadStatus.COMPLETED, UploadStatus.FAILED, UploadStatus.CANCELLED])
        .toContain(status);
    }).toPass({ timeout });
  }

  /**
   * Wait for upload to start
   */
  async waitForUploadStart(timeout = 10000): Promise<void> {
    await expect(async () => {
      const status = await this.getUploadStatus();
      expect(status).toBe(UploadStatus.UPLOADING);
    }).toPass({ timeout });
  }

  /**
   * Check if upload is in progress
   */
  async isUploadInProgress(): Promise<boolean> {
    const status = await this.getUploadStatus();
    return status === UploadStatus.UPLOADING;
  }

  /**
   * Check if upload is completed
   */
  async isUploadCompleted(): Promise<boolean> {
    const status = await this.getUploadStatus();
    return status === UploadStatus.COMPLETED;
  }

  /**
   * Check if upload failed
   */
  async isUploadFailed(): Promise<boolean> {
    const status = await this.getUploadStatus();
    return status === UploadStatus.FAILED;
  }

  /**
   * Get multiple file upload information
   */
  async getMultipleFileUploadInfo(): Promise<{ completed: number; total: number; overall: number }> {
    const completedText = await this.getElementText(this.completedCount);
    const totalText = await this.getElementText(this.totalCount);
    const overallProgress = await this.getUploadProgress();

    const completed = parseInt(completedText, 10) || 0;
    const total = parseInt(totalText, 10) || 0;

    return { completed, total, overall: overallProgress };
  }

  /**
   * Get list of files being uploaded
   */
  async getUploadFileList(): Promise<string[]> {
    if (await this.isElementVisible(this.fileList)) {
      const items = await this.fileItem.all();
      const fileNames: string[] = [];

      for (const item of items) {
        const name = await item.getAttribute('data-filename') || await item.textContent();
        if (name) {
          fileNames.push(name.trim());
        }
      }

      return fileNames;
    }
    return [];
  }

  /**
   * Check if modal can be closed
   */
  async canCloseModal(): Promise<boolean> {
    return await this.isElementVisible(this.closeButton) ||
           await this.isElementVisible(this.doneButton);
  }

  /**
   * Parse bytes from text (e.g., "2.5 MB" -> 2621440)
   */
  private parseBytes(text: string): number {
    if (!text) return 0;

    const match = text.match(/(\d+\.?\d*)\s*(KB|MB|GB|B)?/i);
    if (!match) return 0;

    const value = parseFloat(match[1]);
    const unit = (match[2] || 'B').toUpperCase();

    switch (unit) {
      case 'GB':
        return value * 1024 * 1024 * 1024;
      case 'MB':
        return value * 1024 * 1024;
      case 'KB':
        return value * 1024;
      default:
        return value;
    }
  }

  /**
   * Wait for specific upload progress
   */
  async waitForProgress(targetProgress: number, timeout = 30000): Promise<void> {
    await expect(async () => {
      const currentProgress = await this.getUploadProgress();
      expect(currentProgress).toBeGreaterThanOrEqual(targetProgress);
    }).toPass({ timeout });
  }
}