# BGSBU Data Import - SQL Server 2022

## Overview
This SQL script imports data from CSV files into the `bgsbu` database's `uploads` table.

## Files Included

### Main SQL File
- **BGSBU_Data_Import.sql** - Ready-to-execute SQL Server 2022 script

### Source CSV Files
1. `notifications.csv` - 1,000 notification records
2. `circular.csv` - 178 circular records
3. `result.csv` - 975 result records
4. `tender.csv` - 103 tender records
5. `admission.csv` - 337 admission records
6. `Datesheet.csv` - 424 datesheet records

**Total Records: 3,017**

## Database Schema
The script inserts data into the `dbo.uploads` table with the following columns:
- `id` - Unique identifier (from CSV)
- `fileName` - File name
- `filePath` - Path to the file
- `fileType` - Type (Notification, Circular, Result, Tender, Admission, Datesheet)
- `mimeType` - MIME type (application/pdf, image/jpeg, etc.)
- `size` - File size (default 0)
- `caption` - Display caption with date
- `description` - Additional description (NULL)
- `academicYear` - Academic year (e.g., 2024-25)
- `visibility` - Public/Private (default Public)
- `publishDate` - Extracted from caption date [DD-MM-YYYY]
- `tags` - Tags (NULL)
- `uploadedBy` - Uploaded by user (default 'system')
- `createdAt` - Creation timestamp (GETDATE())
- `updatedAt` - Update timestamp (GETDATE())

## Features
- ✓ SQL Server 2022 compatible syntax
- ✓ Uses `IDENTITY_INSERT ON/OFF` for explicit ID values
- ✓ Proper string escaping for single quotes
- ✓ Unicode string support (N'...')
- ✓ Date extraction from caption format [DD-MM-YYYY]
- ✓ Academic year auto-detection
- ✓ MIME type detection from file extensions

## How to Execute

### Option 1: SQL Server Management Studio (SSMS)
1. Open SQL Server Management Studio
2. Connect to your SQL Server 2022 instance
3. Open `BGSBU_Data_Import.sql`
4. Ensure the `bgsbu` database exists
5. Execute the script (F5)

### Option 2: Command Line (sqlcmd)
```bash
sqlcmd -S localhost -d bgsbu -i BGSBU_Data_Import.sql
```

### Option 3: Azure Data Studio
1. Open Azure Data Studio
2. Connect to your server
3. Open `BGSBU_Data_Import.sql`
4. Run the script

## Prerequisites
1. SQL Server 2022 (or compatible version)
2. Database `bgsbu` must exist
3. Table `dbo.uploads` must exist (see db.sql for schema)
4. User must have INSERT permissions on `dbo.uploads` table

## Sample Data Examples

### Notification Record
```sql
INSERT INTO dbo.uploads (...) VALUES (
  7075,
  N'7075.pdf',
  N'unidata/notification/7075.pdf',
  N'Notification',
  N'application/pdf',
  0,
  N'[09-03-2026] Ph. D Entrance syllabus of Civil Engineering',
  NULL,
  N'2025-26',
  N'Public',
  N'2026-03-09',
  NULL,
  N'system',
  GETDATE(),
  GETDATE()
);
```

### Circular Record
```sql
INSERT INTO dbo.uploads (...) VALUES (
  3280,
  N'Circular Pooja Holidays.pdf',
  N'researchfile/Circular Pooja Holidays.pdf',
  N'Circular',
  N'application/pdf',
  0,
  N'[17-10-2025] Circular Pooja Holidays',
  NULL,
  N'2025-26',
  N'Public',
  N'2025-10-17',
  NULL,
  N'system',
  GETDATE(),
  GETDATE()
);
```

## Notes
- All records use `IDENTITY_INSERT ON` to preserve original IDs
- Dates are extracted from caption format `[DD-MM-YYYY]` and converted to ISO format
- Academic year is auto-detected from dates or caption text
- Empty file paths are handled gracefully
- All strings are properly escaped for SQL injection protection

## Verification Queries

After import, verify the data:

```sql
-- Check total records
SELECT COUNT(*) FROM dbo.uploads;

-- Check by file type
SELECT fileType, COUNT(*) as Count
FROM dbo.uploads
GROUP BY fileType
ORDER BY fileType;

-- Check recent records
SELECT TOP 10 id, caption, fileType, publishDate, academicYear
FROM dbo.uploads
ORDER BY id DESC;

-- Check date range
SELECT MIN(publishDate) as EarliestDate,
       MAX(publishDate) as LatestDate
FROM dbo.uploads
WHERE publishDate IS NOT NULL;
```

## File Information
- **Generated:** 2026-03-15
- **File Size:** ~1.5 MB
- **Lines:** 3,048
- **Character Encoding:** UTF-8
- **SQL Server Version:** 2022 (compatible with 2019, 2017)

## Support
For issues or questions, please check:
1. Database `bgsbu` exists
2. Table schema matches db.sql
3. User has appropriate permissions
4. SQL Server version is compatible
