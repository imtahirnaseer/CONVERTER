USE bgsbu;
GO

-- ============================================
-- 1. File/Upload Table
-- ============================================
IF OBJECT_ID('dbo.uploads', 'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.uploads;
    PRINT '✓ Dropped existing table: uploads';
END
GO

CREATE TABLE dbo.uploads (
    id INT IDENTITY(20000,1) PRIMARY KEY NOT NULL,
    fileName NVARCHAR(500) NOT NULL,
    filePath NVARCHAR(1024) NOT NULL,
    fileType NVARCHAR(100) NOT NULL,
    mimeType NVARCHAR(255) NULL,
    [size] INT NOT NULL DEFAULT 0,
    caption NVARCHAR(255) NULL,
    description NVARCHAR(MAX) NULL,
    academicYear NVARCHAR(50) NULL,
    visibility NVARCHAR(50) NOT NULL DEFAULT 'Public',
    publishDate DATETIME2(7) NULL,
    expiryDate DATETIME2(7) NULL,
    tags NVARCHAR(1024) NULL,
    uploadedBy NVARCHAR(255) NULL,
    createdAt DATETIME2(7) NOT NULL DEFAULT GETDATE(),
    updatedAt DATETIME2(7) NOT NULL DEFAULT GETDATE(),
    deletedAt DATETIME2(7) NULL,
    CONSTRAINT CK_uploads_visibility CHECK (visibility IN ('Public', 'Private', 'Internal'))
);
GO

-- Create indexes for uploads table
CREATE NONCLUSTERED INDEX IX_uploads_fileType ON dbo.uploads(fileType);
CREATE NONCLUSTERED INDEX IX_uploads_visibility ON dbo.uploads(visibility);
CREATE NONCLUSTERED INDEX IX_uploads_publishDate ON dbo.uploads(publishDate);
CREATE NONCLUSTERED INDEX IX_uploads_createdAt ON dbo.uploads(createdAt);
CREATE NONCLUSTERED INDEX IX_uploads_deletedAt ON dbo.uploads(deletedAt) WHERE deletedAt IS NOT NULL;
CREATE NONCLUSTERED INDEX IX_uploads_uploadedBy ON dbo.uploads(uploadedBy);
CREATE NONCLUSTERED INDEX IX_uploads_fileName ON dbo.uploads(fileName);

PRINT '✓ Table created: uploads (Files)';
GO
