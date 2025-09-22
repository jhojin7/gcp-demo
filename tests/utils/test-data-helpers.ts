import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';

export interface TestFile {
  name: string;
  path: string;
  size: number;
  type: string;
  content: Buffer | string;
}

export interface TestUser {
  username: string;
  password: string;
  email: string;
}

export interface MockFileResponse {
  id: string;
  name: string;
  size: number;
  contentType: string;
  lastModified: string;
  versions: number;
  url?: string;
}

export class TestDataHelpers {
  private static readonly FIXTURES_DIR = path.join(__dirname, '../fixtures');
  private static readonly TEMP_DIR = path.join(__dirname, '../temp');

  /**
   * Ensure temp directory exists
   */
  static ensureTempDir(): void {
    if (!fs.existsSync(this.TEMP_DIR)) {
      fs.mkdirSync(this.TEMP_DIR, { recursive: true });
    }
  }

  /**
   * Clean up temp directory
   */
  static cleanupTempDir(): void {
    if (fs.existsSync(this.TEMP_DIR)) {
      fs.rmSync(this.TEMP_DIR, { recursive: true, force: true });
    }
  }

  /**
   * Create a test file with specified content
   */
  static createTestFile(fileName: string, content: string | Buffer, size?: number): TestFile {
    this.ensureTempDir();

    const filePath = path.join(this.TEMP_DIR, fileName);
    const fileContent = size ? this.generateContentOfSize(size) : content;

    fs.writeFileSync(filePath, fileContent);

    const stats = fs.statSync(filePath);
    const type = this.getFileType(fileName);

    return {
      name: fileName,
      path: filePath,
      size: stats.size,
      type,
      content: fileContent
    };
  }

  /**
   * Create a large test file
   */
  static createLargeTestFile(fileName: string, sizeInMB: number): TestFile {
    const sizeInBytes = sizeInMB * 1024 * 1024;
    return this.createTestFile(fileName, '', sizeInBytes);
  }

  /**
   * Create multiple test files
   */
  static createMultipleTestFiles(count: number, prefix = 'test-file'): TestFile[] {
    const files: TestFile[] = [];

    for (let i = 1; i <= count; i++) {
      const fileName = `${prefix}-${i}.txt`;
      const content = `This is test file number ${i}\nCreated at: ${new Date().toISOString()}`;
      files.push(this.createTestFile(fileName, content));
    }

    return files;
  }

  /**
   * Create test files of different types
   */
  static createDifferentFileTypes(): TestFile[] {
    const files: TestFile[] = [];

    // Text file
    files.push(this.createTestFile('document.txt', 'This is a text document.'));

    // JSON file
    files.push(this.createTestFile('data.json', JSON.stringify({
      name: 'Test Data',
      timestamp: new Date().toISOString(),
      items: [1, 2, 3, 4, 5]
    }, null, 2)));

    // CSV file
    files.push(this.createTestFile('data.csv', 'Name,Age,City\nJohn,25,New York\nJane,30,Los Angeles'));

    // Image file (minimal PNG)
    const pngContent = Buffer.from([
      0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
      0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
      0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
      0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,
      0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,
      0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
      0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,
      0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,
      0x42, 0x60, 0x82
    ]);
    files.push(this.createTestFile('image.png', pngContent));

    return files;
  }

  /**
   * Get test user data
   */
  static getTestUsers(): { valid: TestUser; invalid: TestUser } {
    return {
      valid: {
        username: 'testuser',
        password: 'testpassword123',
        email: 'test@example.com'
      },
      invalid: {
        username: 'invalid',
        password: 'wrong',
        email: 'invalid@test.com'
      }
    };
  }

  /**
   * Generate mock file response data
   */
  static generateMockFileResponse(fileName: string, overrides: Partial<MockFileResponse> = {}): MockFileResponse {
    const id = crypto.randomUUID();
    const size = Math.floor(Math.random() * 1000000) + 1000; // 1KB to 1MB
    const contentType = this.getContentType(fileName);
    const lastModified = new Date().toISOString();

    return {
      id,
      name: fileName,
      size,
      contentType,
      lastModified,
      versions: 1,
      ...overrides
    };
  }

  /**
   * Generate multiple mock file responses
   */
  static generateMockFileList(count: number): MockFileResponse[] {
    const files: MockFileResponse[] = [];
    const fileTypes = ['.txt', '.pdf', '.png', '.jpg', '.docx', '.csv'];

    for (let i = 1; i <= count; i++) {
      const extension = fileTypes[Math.floor(Math.random() * fileTypes.length)];
      const fileName = `file-${i}${extension}`;
      files.push(this.generateMockFileResponse(fileName));
    }

    return files;
  }

  /**
   * Create mock version history data
   */
  static generateMockVersionHistory(fileName: string, versionCount: number): any[] {
    const versions = [];
    const baseDate = new Date();

    for (let i = versionCount; i >= 1; i--) {
      const versionDate = new Date(baseDate.getTime() - (versionCount - i) * 24 * 60 * 60 * 1000);
      versions.push({
        version: i,
        timestamp: versionDate.toISOString(),
        size: Math.floor(Math.random() * 1000000) + 1000,
        uploadedBy: i === versionCount ? 'testuser' : 'otheruser',
        isCurrent: i === versionCount,
        checksum: crypto.randomBytes(16).toString('hex')
      });
    }

    return versions;
  }

  /**
   * Generate content of specific size
   */
  static generateContentOfSize(sizeInBytes: number): Buffer {
    const chunk = 'This is test content that will be repeated to reach the desired file size. ';
    const chunkSize = Buffer.byteLength(chunk);
    const chunksNeeded = Math.ceil(sizeInBytes / chunkSize);

    let content = '';
    for (let i = 0; i < chunksNeeded; i++) {
      content += chunk;
    }

    return Buffer.from(content.slice(0, sizeInBytes));
  }

  /**
   * Get file type based on extension
   */
  static getFileType(fileName: string): string {
    const ext = path.extname(fileName).toLowerCase();

    const typeMap: { [key: string]: string } = {
      '.txt': 'text',
      '.pdf': 'document',
      '.doc': 'document',
      '.docx': 'document',
      '.png': 'image',
      '.jpg': 'image',
      '.jpeg': 'image',
      '.gif': 'image',
      '.csv': 'spreadsheet',
      '.xls': 'spreadsheet',
      '.xlsx': 'spreadsheet',
      '.json': 'data',
      '.xml': 'data'
    };

    return typeMap[ext] || 'unknown';
  }

  /**
   * Get content type for HTTP headers
   */
  static getContentType(fileName: string): string {
    const ext = path.extname(fileName).toLowerCase();

    const mimeMap: { [key: string]: string } = {
      '.txt': 'text/plain',
      '.pdf': 'application/pdf',
      '.doc': 'application/msword',
      '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      '.png': 'image/png',
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
      '.gif': 'image/gif',
      '.csv': 'text/csv',
      '.json': 'application/json',
      '.xml': 'application/xml'
    };

    return mimeMap[ext] || 'application/octet-stream';
  }

  /**
   * Wait for a specified duration
   */
  static async wait(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Generate random string
   */
  static generateRandomString(length: number): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }

  /**
   * Generate random file name
   */
  static generateRandomFileName(extension = '.txt'): string {
    const randomName = this.generateRandomString(8);
    return `test-${randomName}${extension}`;
  }

  /**
   * Create temporary file with automatic cleanup
   */
  static createTempFile(fileName?: string, content?: string): { path: string; cleanup: () => void } {
    this.ensureTempDir();

    const actualFileName = fileName || this.generateRandomFileName();
    const filePath = path.join(this.TEMP_DIR, actualFileName);
    const actualContent = content || `Temporary test file created at ${new Date().toISOString()}`;

    fs.writeFileSync(filePath, actualContent);

    return {
      path: filePath,
      cleanup: () => {
        if (fs.existsSync(filePath)) {
          fs.unlinkSync(filePath);
        }
      }
    };
  }

  /**
   * Get fixture file path
   */
  static getFixturePath(fileName: string): string {
    return path.join(this.FIXTURES_DIR, fileName);
  }

  /**
   * Check if fixture file exists
   */
  static fixtureExists(fileName: string): boolean {
    return fs.existsSync(this.getFixturePath(fileName));
  }

  /**
   * Load fixture file content
   */
  static loadFixture(fileName: string): Buffer {
    const fixturePath = this.getFixturePath(fileName);
    if (!fs.existsSync(fixturePath)) {
      throw new Error(`Fixture file not found: ${fileName}`);
    }
    return fs.readFileSync(fixturePath);
  }

  /**
   * Format file size for display
   */
  static formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 B';

    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Parse file size string to bytes
   */
  static parseFileSize(sizeStr: string): number {
    const match = sizeStr.match(/^(\d+\.?\d*)\s*(B|KB|MB|GB)$/i);
    if (!match) return 0;

    const value = parseFloat(match[1]);
    const unit = match[2].toUpperCase();

    switch (unit) {
      case 'GB': return value * 1024 * 1024 * 1024;
      case 'MB': return value * 1024 * 1024;
      case 'KB': return value * 1024;
      default: return value;
    }
  }

  /**
   * Generate timestamp in various formats
   */
  static generateTimestamp(format: 'iso' | 'relative' | 'human' = 'iso'): string {
    const now = new Date();

    switch (format) {
      case 'iso':
        return now.toISOString();
      case 'relative':
        return 'just now';
      case 'human':
        return now.toLocaleString();
      default:
        return now.toISOString();
    }
  }
}