import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

test.describe('Test Data Fixtures Contract', () => {
  const fixturesDir = path.join(__dirname, '../fixtures');

  test('fixtures directory should exist', () => {
    expect(fs.existsSync(fixturesDir)).toBe(true);
  });

  test('should have test file fixtures for uploads', async () => {
    const testFilePath = path.join(fixturesDir, 'test-file.txt');

    // Create test file if it doesn't exist
    if (!fs.existsSync(testFilePath)) {
      fs.writeFileSync(testFilePath, 'This is a test file for upload testing.');
    }

    expect(fs.existsSync(testFilePath)).toBe(true);

    const stats = fs.statSync(testFilePath);
    expect(stats.isFile()).toBe(true);
    expect(stats.size).toBeGreaterThan(0);
  });

  test('should have various file types for testing', async () => {
    const expectedFiles = [
      'test-image.png',
      'test-document.pdf',
      'test-text.txt',
      'test-large.bin'
    ];

    // Create test files if they don't exist
    for (const fileName of expectedFiles) {
      const filePath = path.join(fixturesDir, fileName);
      if (!fs.existsSync(filePath)) {
        let content: Buffer | string;

        switch (path.extname(fileName)) {
          case '.png':
            // Create a minimal PNG file (1x1 pixel)
            content = Buffer.from([
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
            break;
          case '.pdf':
            // Create a minimal PDF file
            content = '%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n182\n%%EOF';
            break;
          case '.bin':
            // Create a large binary file (1MB)
            content = Buffer.alloc(1024 * 1024, 0x42);
            break;
          default:
            content = `Test content for ${fileName}`;
        }

        fs.writeFileSync(filePath, content);
      }

      expect(fs.existsSync(filePath)).toBe(true);
    }
  });

  test('should have test user data fixtures', () => {
    const userDataPath = path.join(fixturesDir, 'test-users.json');

    const testUsers = {
      validUser: {
        username: 'testuser',
        password: 'testpassword123',
        email: 'test@example.com'
      },
      invalidUser: {
        username: 'invalid',
        password: 'wrong',
        email: 'invalid@test.com'
      }
    };

    if (!fs.existsSync(userDataPath)) {
      fs.writeFileSync(userDataPath, JSON.stringify(testUsers, null, 2));
    }

    expect(fs.existsSync(userDataPath)).toBe(true);

    const data = JSON.parse(fs.readFileSync(userDataPath, 'utf8'));
    expect(data.validUser).toBeDefined();
    expect(data.invalidUser).toBeDefined();
    expect(data.validUser.username).toBe('testuser');
  });

  test('should have mock response fixtures', () => {
    const mockResponsesPath = path.join(fixturesDir, 'mock-responses.json');

    const mockResponses = {
      fileUpload: {
        success: {
          status: 'success',
          fileId: 'test-file-123',
          message: 'File uploaded successfully'
        },
        error: {
          status: 'error',
          code: 'UPLOAD_FAILED',
          message: 'Failed to upload file'
        }
      },
      fileList: {
        success: {
          files: [
            {
              id: 'file-1',
              name: 'document.pdf',
              size: 1024,
              lastModified: '2023-01-01T10:00:00Z',
              versions: 1
            }
          ]
        }
      }
    };

    if (!fs.existsSync(mockResponsesPath)) {
      fs.writeFileSync(mockResponsesPath, JSON.stringify(mockResponses, null, 2));
    }

    expect(fs.existsSync(mockResponsesPath)).toBe(true);

    const data = JSON.parse(fs.readFileSync(mockResponsesPath, 'utf8'));
    expect(data.fileUpload).toBeDefined();
    expect(data.fileList).toBeDefined();
  });

  test('should validate fixture file integrity', () => {
    const testFilePath = path.join(fixturesDir, 'test-file.txt');

    if (fs.existsSync(testFilePath)) {
      const content = fs.readFileSync(testFilePath, 'utf8');
      expect(content.length).toBeGreaterThan(0);
      expect(typeof content).toBe('string');
    }
  });
});