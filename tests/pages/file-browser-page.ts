import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base-page';

export interface FileMetadata {
  name: string;
  size: string;
  lastModified: string;
  type: string;
  versionCount: number;
}

export class FileBrowserPage extends BasePage {
  // Navigation elements
  readonly navigationBreadcrumb: Locator;
  readonly upButton: Locator;
  readonly homeButton: Locator;

  // File operations
  readonly uploadButton: Locator;
  readonly uploadInput: Locator;
  readonly uploadArea: Locator;
  readonly createFolderButton: Locator;
  readonly refreshButton: Locator;

  // File list
  readonly fileList: Locator;
  readonly fileItem: Locator;
  readonly folderItem: Locator;
  readonly emptyStateMessage: Locator;

  // File actions
  readonly downloadButton: Locator;
  readonly deleteButton: Locator;
  readonly renameButton: Locator;
  readonly viewVersionsButton: Locator;

  // Selection
  readonly selectAllCheckbox: Locator;
  readonly selectedItemsCount: Locator;

  // Search and filter
  readonly searchInput: Locator;
  readonly filterDropdown: Locator;

  constructor(page: Page) {
    super(page, '/');

    // Navigation
    this.navigationBreadcrumb = page.locator('[data-testid="breadcrumb"], .breadcrumb');
    this.upButton = page.locator('[data-testid="up-button"], .up-button');
    this.homeButton = page.locator('[data-testid="home-button"], .home-button');

    // File operations
    this.uploadButton = page.locator('[data-testid="upload-button"], .upload-button');
    this.uploadInput = page.locator('input[type="file"]');
    this.uploadArea = page.locator('[data-testid="upload-area"], .upload-area');
    this.createFolderButton = page.locator('[data-testid="create-folder"], .create-folder');
    this.refreshButton = page.locator('[data-testid="refresh"], .refresh');

    // File list
    this.fileList = page.locator('[data-testid="file-list"], .file-list');
    this.fileItem = page.locator('[data-testid="file-item"], .file-item');
    this.folderItem = page.locator('[data-testid="folder-item"], .folder-item');
    this.emptyStateMessage = page.locator('[data-testid="empty-state"], .empty-state');

    // File actions
    this.downloadButton = page.locator('[data-testid="download"], .download');
    this.deleteButton = page.locator('[data-testid="delete"], .delete');
    this.renameButton = page.locator('[data-testid="rename"], .rename');
    this.viewVersionsButton = page.locator('[data-testid="view-versions"], .view-versions');

    // Selection
    this.selectAllCheckbox = page.locator('[data-testid="select-all"], .select-all');
    this.selectedItemsCount = page.locator('[data-testid="selected-count"], .selected-count');

    // Search and filter
    this.searchInput = page.locator('[data-testid="search"], .search');
    this.filterDropdown = page.locator('[data-testid="filter"], .filter');
  }

  /**
   * Navigate to a specific folder
   */
  async navigateToFolder(folderName: string): Promise<void> {
    const folder = this.page.locator(`[data-testid="folder-${folderName}"], .folder[data-name="${folderName}"]`);
    await folder.dblclick();
    await this.waitForLoad();
  }

  /**
   * Navigate up one level
   */
  async navigateUp(): Promise<void> {
    if (await this.isElementVisible(this.upButton)) {
      await this.upButton.click();
      await this.waitForLoad();
    }
  }

  /**
   * Go to root directory
   */
  async goToRoot(): Promise<void> {
    if (await this.isElementVisible(this.homeButton)) {
      await this.homeButton.click();
      await this.waitForLoad();
    }
  }

  /**
   * Upload a file using the upload button
   */
  async uploadFile(filePath: string): Promise<void> {
    await this.uploadFile(this.uploadInput, filePath);
    await this.waitForLoadingToComplete();
  }

  /**
   * Upload file using drag and drop
   */
  async uploadFileViaDragDrop(filePath: string): Promise<void> {
    // Create a file input element for drag and drop simulation
    const dataTransfer = await this.page.evaluateHandle(() => {
      const dt = new DataTransfer();
      return dt;
    });

    await this.uploadArea.dispatchEvent('dragover', { dataTransfer });
    await this.uploadArea.dispatchEvent('drop', { dataTransfer });
    await this.waitForLoadingToComplete();
  }

  /**
   * Download a file
   */
  async downloadFile(fileName: string): Promise<void> {
    await this.selectFile(fileName);

    const downloadPromise = this.page.waitForDownload();
    await this.downloadButton.click();
    const download = await downloadPromise;

    // Verify download completed
    expect(download.suggestedFilename()).toBe(fileName);
  }

  /**
   * Delete a file
   */
  async deleteFile(fileName: string): Promise<void> {
    await this.selectFile(fileName);
    await this.deleteButton.click();

    // Confirm deletion if confirmation dialog appears
    const confirmButton = this.page.locator('[data-testid="confirm-delete"], .confirm-delete');
    if (await this.isElementVisible(confirmButton)) {
      await confirmButton.click();
    }

    await this.waitForLoadingToComplete();
  }

  /**
   * Select a file
   */
  async selectFile(fileName: string): Promise<void> {
    const file = this.page.locator(`[data-testid="file-${fileName}"], .file[data-name="${fileName}"]`);
    await file.click();
  }

  /**
   * Select multiple files
   */
  async selectMultipleFiles(fileNames: string[]): Promise<void> {
    for (const fileName of fileNames) {
      const file = this.page.locator(`[data-testid="file-${fileName}"], .file[data-name="${fileName}"]`);
      await file.click({ modifiers: ['Control'] });
    }
  }

  /**
   * Create a new folder
   */
  async createFolder(folderName: string): Promise<void> {
    await this.createFolderButton.click();

    const folderNameInput = this.page.locator('[data-testid="folder-name-input"], .folder-name-input');
    await this.fillInput(folderNameInput, folderName);

    const createButton = this.page.locator('[data-testid="confirm-create"], .confirm-create');
    await createButton.click();

    await this.waitForLoadingToComplete();
  }

  /**
   * Rename a folder
   */
  async renameFolder(oldName: string, newName: string): Promise<void> {
    const folder = this.page.locator(`[data-testid="folder-${oldName}"], .folder[data-name="${oldName}"]`);
    await folder.click({ button: 'right' });

    const renameOption = this.page.locator('[data-testid="rename-option"], .rename-option');
    await renameOption.click();

    const nameInput = this.page.locator('[data-testid="rename-input"], .rename-input');
    await this.fillInput(nameInput, newName);

    const saveButton = this.page.locator('[data-testid="save-rename"], .save-rename');
    await saveButton.click();

    await this.waitForLoadingToComplete();
  }

  /**
   * Delete a folder
   */
  async deleteFolder(folderName: string): Promise<void> {
    const folder = this.page.locator(`[data-testid="folder-${folderName}"], .folder[data-name="${folderName}"]`);
    await folder.click();
    await this.deleteButton.click();

    const confirmButton = this.page.locator('[data-testid="confirm-delete"], .confirm-delete');
    if (await this.isElementVisible(confirmButton)) {
      await confirmButton.click();
    }

    await this.waitForLoadingToComplete();
  }

  /**
   * Get list of files
   */
  async getFileList(): Promise<string[]> {
    await this.waitForElement(this.fileList);
    const files = await this.fileItem.all();
    const fileNames: string[] = [];

    for (const file of files) {
      const name = await file.getAttribute('data-name') || await file.textContent();
      if (name) {
        fileNames.push(name.trim());
      }
    }

    return fileNames;
  }

  /**
   * Get file count
   */
  async getFileCount(): Promise<number> {
    const files = await this.getFileList();
    return files.length;
  }

  /**
   * Check if a specific file is visible
   */
  async isFileVisible(fileName: string): Promise<boolean> {
    const file = this.page.locator(`[data-testid="file-${fileName}"], .file[data-name="${fileName}"]`);
    return await this.isElementVisible(file);
  }

  /**
   * Get file metadata
   */
  async getFileMetadata(fileName: string): Promise<FileMetadata> {
    const file = this.page.locator(`[data-testid="file-${fileName}"], .file[data-name="${fileName}"]`);
    await this.waitForElement(file);

    // Extract metadata from data attributes or text content
    const name = await file.getAttribute('data-name') || fileName;
    const size = await file.getAttribute('data-size') || '0';
    const lastModified = await file.getAttribute('data-modified') || '';
    const type = await file.getAttribute('data-type') || '';
    const versionCount = parseInt(await file.getAttribute('data-versions') || '1', 10);

    return {
      name,
      size,
      lastModified,
      type,
      versionCount
    };
  }

  /**
   * View file versions
   */
  async viewFileVersions(fileName: string): Promise<void> {
    await this.selectFile(fileName);
    await this.viewVersionsButton.click();
    await this.waitForLoad();
  }

  /**
   * Get version count for a file
   */
  async getVersionCount(fileName: string): Promise<number> {
    const metadata = await this.getFileMetadata(fileName);
    return metadata.versionCount;
  }

  /**
   * Check if upload area is visible
   */
  async isUploadAreaVisible(): Promise<boolean> {
    return await this.isElementVisible(this.uploadArea);
  }

  /**
   * Check if file list is visible
   */
  async isFileListVisible(): Promise<boolean> {
    return await this.isElementVisible(this.fileList);
  }

  /**
   * Check if loading indicator is visible
   */
  async isLoadingIndicatorVisible(): Promise<boolean> {
    return await this.isElementVisible(this.loadingSpinner);
  }

  /**
   * Search for files
   */
  async searchFiles(searchTerm: string): Promise<void> {
    await this.fillInput(this.searchInput, searchTerm);
    await this.page.keyboard.press('Enter');
    await this.waitForLoadingToComplete();
  }

  /**
   * Clear search
   */
  async clearSearch(): Promise<void> {
    await this.searchInput.clear();
    await this.page.keyboard.press('Enter');
    await this.waitForLoadingToComplete();
  }

  /**
   * Check if empty state is shown
   */
  async isEmptyStateVisible(): Promise<boolean> {
    return await this.isElementVisible(this.emptyStateMessage);
  }

  /**
   * Get current folder path from breadcrumb
   */
  async getCurrentPath(): Promise<string> {
    if (await this.isElementVisible(this.navigationBreadcrumb)) {
      return await this.getElementText(this.navigationBreadcrumb);
    }
    return '/';
  }
}