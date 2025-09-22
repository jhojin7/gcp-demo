import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base-page';

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

export class VersionHistoryPage extends BasePage {
  // Page header
  readonly pageTitle: Locator;
  readonly fileName: Locator;
  readonly backToFileBrowserButton: Locator;

  // Version list
  readonly versionList: Locator;
  readonly versionItem: Locator;
  readonly currentVersionBadge: Locator;
  readonly versionTimeline: Locator;

  // Version actions
  readonly downloadVersionButton: Locator;
  readonly restoreVersionButton: Locator;
  readonly compareVersionsButton: Locator;
  readonly deleteVersionButton: Locator;

  // Version details
  readonly versionDetails: Locator;
  readonly versionMetadata: Locator;
  readonly versionSize: Locator;
  readonly versionTimestamp: Locator;
  readonly versionUploader: Locator;

  // Comparison view
  readonly comparisonView: Locator;
  readonly versionSelectDropdown: Locator;
  readonly compareButton: Locator;

  // Confirmation dialogs
  readonly restoreConfirmDialog: Locator;
  readonly deleteConfirmDialog: Locator;
  readonly confirmRestoreButton: Locator;
  readonly confirmDeleteButton: Locator;
  readonly cancelButton: Locator;

  constructor(page: Page) {
    super(page, '/versions');

    // Page header
    this.pageTitle = page.locator('[data-testid="page-title"], .page-title, h1');
    this.fileName = page.locator('[data-testid="file-name"], .file-name');
    this.backToFileBrowserButton = page.locator('[data-testid="back-to-browser"], .back-to-browser');

    // Version list
    this.versionList = page.locator('[data-testid="version-list"], .version-list');
    this.versionItem = page.locator('[data-testid="version-item"], .version-item');
    this.currentVersionBadge = page.locator('[data-testid="current-version"], .current-version');
    this.versionTimeline = page.locator('[data-testid="version-timeline"], .version-timeline');

    // Version actions
    this.downloadVersionButton = page.locator('[data-testid="download-version"], .download-version');
    this.restoreVersionButton = page.locator('[data-testid="restore-version"], .restore-version');
    this.compareVersionsButton = page.locator('[data-testid="compare-versions"], .compare-versions');
    this.deleteVersionButton = page.locator('[data-testid="delete-version"], .delete-version');

    // Version details
    this.versionDetails = page.locator('[data-testid="version-details"], .version-details');
    this.versionMetadata = page.locator('[data-testid="version-metadata"], .version-metadata');
    this.versionSize = page.locator('[data-testid="version-size"], .version-size');
    this.versionTimestamp = page.locator('[data-testid="version-timestamp"], .version-timestamp');
    this.versionUploader = page.locator('[data-testid="version-uploader"], .version-uploader');

    // Comparison view
    this.comparisonView = page.locator('[data-testid="comparison-view"], .comparison-view');
    this.versionSelectDropdown = page.locator('[data-testid="version-select"], .version-select');
    this.compareButton = page.locator('[data-testid="compare-button"], .compare-button');

    // Confirmation dialogs
    this.restoreConfirmDialog = page.locator('[data-testid="restore-confirm"], .restore-confirm');
    this.deleteConfirmDialog = page.locator('[data-testid="delete-confirm"], .delete-confirm');
    this.confirmRestoreButton = page.locator('[data-testid="confirm-restore"], .confirm-restore');
    this.confirmDeleteButton = page.locator('[data-testid="confirm-delete"], .confirm-delete');
    this.cancelButton = page.locator('[data-testid="cancel"], .cancel');
  }

  /**
   * Get list of all versions
   */
  async getVersionList(): Promise<VersionInfo[]> {
    await this.waitForElement(this.versionList);
    const versionItems = await this.versionItem.all();
    const versions: VersionInfo[] = [];

    for (const item of versionItems) {
      const versionNumber = parseInt(await item.getAttribute('data-version') || '0', 10);
      const timestamp = await item.getAttribute('data-timestamp') || '';
      const size = await item.getAttribute('data-size') || '';
      const isCurrentVersion = await item.locator('.current-version').isVisible();

      versions.push({
        versionNumber,
        timestamp,
        size,
        isCurrentVersion
      });
    }

    return versions.sort((a, b) => b.versionNumber - a.versionNumber);
  }

  /**
   * Get version count
   */
  async getVersionCount(): Promise<number> {
    const versions = await this.getVersionList();
    return versions.length;
  }

  /**
   * Select a specific version
   */
  async selectVersion(versionNumber: number): Promise<void> {
    const version = this.page.locator(`[data-testid="version-${versionNumber}"], .version-item[data-version="${versionNumber}"]`);
    await version.click();
    await this.waitForElement(this.versionDetails);
  }

  /**
   * Download a specific version
   */
  async downloadVersion(versionNumber: number): Promise<void> {
    await this.selectVersion(versionNumber);

    const downloadPromise = this.page.waitForDownload();
    await this.downloadVersionButton.click();
    const download = await downloadPromise;

    // Verify download started
    expect(download).toBeTruthy();
  }

  /**
   * Restore a version (make it the current version)
   */
  async restoreVersion(versionNumber: number): Promise<void> {
    await this.selectVersion(versionNumber);
    await this.restoreVersionButton.click();

    // Handle confirmation dialog
    if (await this.isElementVisible(this.restoreConfirmDialog)) {
      await this.confirmRestoreButton.click();
    }

    await this.waitForLoadingToComplete();
  }

  /**
   * Compare two versions
   */
  async compareVersions(version1: number, version2: number): Promise<void> {
    await this.selectVersion(version1);

    // Select second version for comparison
    await this.versionSelectDropdown.click();
    const version2Option = this.page.locator(`[data-testid="version-option-${version2}"], .version-option[data-version="${version2}"]`);
    await version2Option.click();

    await this.compareButton.click();
    await this.waitForElement(this.comparisonView);
  }

  /**
   * Get version metadata for a specific version
   */
  async getVersionMetadata(versionNumber: number): Promise<VersionMetadata> {
    await this.selectVersion(versionNumber);
    await this.waitForElement(this.versionMetadata);

    const timestamp = await this.getElementText(this.versionTimestamp);
    const size = await this.getElementText(this.versionSize);
    const uploadedBy = await this.getElementText(this.versionUploader);

    // Extract checksum from metadata section
    const checksumElement = this.versionMetadata.locator('[data-testid="checksum"], .checksum');
    const checksum = await this.getElementText(checksumElement);

    return {
      versionNumber,
      timestamp,
      size,
      uploadedBy,
      checksum
    };
  }

  /**
   * Get timestamp for a specific version
   */
  async getVersionTimestamp(versionNumber: number): Promise<string> {
    const metadata = await this.getVersionMetadata(versionNumber);
    return metadata.timestamp;
  }

  /**
   * Get size for a specific version
   */
  async getVersionSize(versionNumber: number): Promise<string> {
    const metadata = await this.getVersionMetadata(versionNumber);
    return metadata.size;
  }

  /**
   * Return to file browser
   */
  async returnToFileBrowser(): Promise<void> {
    await this.backToFileBrowserButton.click();
    await this.waitForLoad();
  }

  /**
   * Check if a version is marked as current
   */
  async isCurrentVersion(versionNumber: number): Promise<boolean> {
    const version = this.page.locator(`[data-testid="version-${versionNumber}"], .version-item[data-version="${versionNumber}"]`);
    const currentBadge = version.locator('.current-version, [data-testid="current-version"]');
    return await this.isElementVisible(currentBadge);
  }

  /**
   * Get the current version number
   */
  async getCurrentVersionNumber(): Promise<number> {
    const versions = await this.getVersionList();
    const currentVersion = versions.find(v => v.isCurrentVersion);
    return currentVersion?.versionNumber || 0;
  }

  /**
   * Delete a specific version
   */
  async deleteVersion(versionNumber: number): Promise<void> {
    await this.selectVersion(versionNumber);
    await this.deleteVersionButton.click();

    // Handle confirmation dialog
    if (await this.isElementVisible(this.deleteConfirmDialog)) {
      await this.confirmDeleteButton.click();
    }

    await this.waitForLoadingToComplete();
  }

  /**
   * Check if version timeline is visible
   */
  async isVersionTimelineVisible(): Promise<boolean> {
    return await this.isElementVisible(this.versionTimeline);
  }

  /**
   * Get file name being viewed
   */
  async getFileName(): Promise<string> {
    return await this.getElementText(this.fileName);
  }

  /**
   * Check if comparison view is active
   */
  async isComparisonViewVisible(): Promise<boolean> {
    return await this.isElementVisible(this.comparisonView);
  }

  /**
   * Cancel any pending action
   */
  async cancelAction(): Promise<void> {
    if (await this.isElementVisible(this.cancelButton)) {
      await this.cancelButton.click();
    }
  }

  /**
   * Check if restore is allowed for a version
   */
  async canRestoreVersion(versionNumber: number): Promise<boolean> {
    await this.selectVersion(versionNumber);
    return await this.isElementVisible(this.restoreVersionButton) &&
           await this.restoreVersionButton.isEnabled();
  }

  /**
   * Check if version can be deleted
   */
  async canDeleteVersion(versionNumber: number): Promise<boolean> {
    await this.selectVersion(versionNumber);
    return await this.isElementVisible(this.deleteVersionButton) &&
           await this.deleteVersionButton.isEnabled();
  }

  /**
   * Wait for version list to load
   */
  async waitForVersionListToLoad(): Promise<void> {
    await this.waitForElement(this.versionList);
    await this.waitForLoadingToComplete();
  }

  /**
   * Refresh version list
   */
  async refreshVersionList(): Promise<void> {
    await this.refresh();
    await this.waitForVersionListToLoad();
  }
}