import csv
import re
from datetime import datetime

def parse_caption_date(caption):
    """Extract date from caption format like [DD-MM-YYYY]"""
    match = re.search(r'\[(\d{2})-(\d{2})-(\d{4})\]', caption)
    if match:
        day, month, year = match.groups()
        try:
            return datetime.strptime(f"{day}-{month}-{year}", "%d-%m-%Y").strftime("%Y-%m-%d")
        except:
            return None
    return None

def escape_sql_string(value):
    """Escape single quotes for SQL Server"""
    if value is None:
        return 'NULL'
    return "N'" + str(value).replace("'", "''") + "'"

def generate_sql_insert(csv_file, file_type, start_id=20000):
    """Generate SQL INSERT statements from CSV file"""
    sql_statements = []

    with open(csv_file, 'r', encoding='utf-8') as f:
        # Read first line to determine format
        first_line = f.readline().strip()
        f.seek(0)

        reader = csv.reader(f)

        # Skip header if exists
        if 'caption' in first_line.lower() or 'type' in first_line.lower():
            next(reader)

        current_id = start_id

        for row in reader:
            if not row or len(row) < 2:
                continue

            # Format: id,caption,filepath,[icon]
            try:
                csv_id = int(row[0])
            except:
                continue

            caption = row[1].strip() if len(row) > 1 else ''
            file_path = row[2].strip() if len(row) > 2 else ''

            if not caption:
                continue

            # Extract date from caption
            publish_date = parse_caption_date(caption)

            # Generate filename from path
            file_name = file_path.split('/')[-1] if file_path else f"{file_type}_{csv_id}.pdf"

            # Determine academic year from caption and date
            academic_year = '2024-25'  # Default
            year_match = re.search(r'202[0-9][-/]?2[0-9]', caption)
            if year_match:
                academic_year = year_match.group(0).replace('/', '-')
            elif publish_date:
                year = int(publish_date.split('-')[0])
                academic_year = f"{year}-{(year+1) % 100:02d}"

            # Build SQL INSERT
            sql = f"""INSERT INTO dbo.uploads (id, fileName, filePath, fileType, mimeType, [size], caption, description, academicYear, visibility, publishDate, tags, uploadedBy, createdAt, updatedAt)
VALUES ({csv_id}, {escape_sql_string(file_name)}, {escape_sql_string(file_path)}, {escape_sql_string(file_type)}, N'application/pdf', 0, {escape_sql_string(caption)}, NULL, {escape_sql_string(academic_year)}, N'Public', {escape_sql_string(publish_date) if publish_date else 'NULL'}, NULL, N'system', GETDATE(), GETDATE());"""

            sql_statements.append(sql)

    return sql_statements

# Process all CSV files
file_mapping = {
    'notifications.csv': 'Notification',
    'circular.csv': 'Circular',
    'result.csv': 'Result',
    'tender.csv': 'Tender',
    'admission.csv': 'Admission',
    'Datesheet.csv': 'Datesheet'
}

all_sql = []
all_sql.append("USE bgsbu;")
all_sql.append("GO")
all_sql.append("")
all_sql.append("-- ============================================")
all_sql.append("-- Insert Data into uploads table")
all_sql.append("-- Generated from CSV files")
all_sql.append(f"-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
all_sql.append("-- ============================================")
all_sql.append("")

for csv_file, file_type in file_mapping.items():
    try:
        all_sql.append(f"-- {file_type} data from {csv_file}")
        statements = generate_sql_insert(csv_file, file_type)
        all_sql.extend(statements)
        all_sql.append("")
        print(f"Processed {csv_file}: {len(statements)} records")
    except Exception as e:
        print(f"Error processing {csv_file}: {e}")

# Write to output file
with open('data_import.sql', 'w', encoding='utf-8') as f:
    f.write('\n'.join(all_sql))

print("\n✓ SQL file generated: data_import.sql")
