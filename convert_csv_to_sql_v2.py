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
    value_str = str(value).replace("'", "''")
    return "N'" + value_str + "'"

def determine_academic_year(caption, publish_date):
    """Determine academic year from caption or date"""
    # Try to find year pattern in caption
    year_match = re.search(r'202[0-9][-/]?2[0-9]', caption)
    if year_match:
        return year_match.group(0).replace('/', '-')

    # Try to determine from publish date
    if publish_date:
        year = int(publish_date.split('-')[0])
        month = int(publish_date.split('-')[1])
        # Academic year typically starts in July/August
        if month >= 7:
            return f"{year}-{str(year+1)[-2:]}"
        else:
            return f"{year-1}-{str(year)[-2:]}"

    return '2024-25'  # Default

def generate_sql_insert(csv_file, file_type):
    """Generate SQL INSERT statements from CSV file"""
    sql_statements = []

    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    # Remove Windows line endings
    lines = [line.strip().replace('\r', '') for line in lines if line.strip()]

    for line_num, line in enumerate(lines, 1):
        try:
            # Parse CSV manually to handle different formats
            parts = []
            in_quotes = False
            current_part = ''

            for char in line:
                if char == '"':
                    in_quotes = not in_quotes
                elif char == ',' and not in_quotes:
                    parts.append(current_part.strip())
                    current_part = ''
                else:
                    current_part += char

            # Add last part
            if current_part:
                parts.append(current_part.strip())

            if len(parts) < 2:
                continue

            # Determine format based on file type and content
            if file_type in ['Notification', 'Result'] and len(parts) >= 4:
                # Format: id, filename, caption, extension, filename
                try:
                    csv_id = int(parts[0])
                except:
                    continue

                file_name = parts[1]
                caption = parts[2]
                file_path = f"unidata/{file_type.lower()}/{file_name}"

            else:
                # Format: id, caption, filepath, [icon]
                try:
                    csv_id = int(parts[0])
                except:
                    continue

                caption = parts[1]
                file_path = parts[2] if len(parts) > 2 else ''
                file_name = file_path.split('/')[-1] if file_path else f"{csv_id}.pdf"

            if not caption:
                continue

            # Extract date from caption
            publish_date = parse_caption_date(caption)

            # Determine academic year
            academic_year = determine_academic_year(caption, publish_date)

            # Determine MIME type from filename
            mime_type = 'application/pdf'
            if file_name.lower().endswith(('.jpg', '.jpeg')):
                mime_type = 'image/jpeg'
            elif file_name.lower().endswith('.png'):
                mime_type = 'image/png'
            elif file_name.lower().endswith('.docx'):
                mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif file_name.lower().endswith('.xlsx'):
                mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

            # Build SQL INSERT
            sql = f"INSERT INTO dbo.uploads (id, fileName, filePath, fileType, mimeType, [size], caption, description, academicYear, visibility, publishDate, tags, uploadedBy, createdAt, updatedAt) VALUES ({csv_id}, {escape_sql_string(file_name)}, {escape_sql_string(file_path)}, {escape_sql_string(file_type)}, {escape_sql_string(mime_type)}, 0, {escape_sql_string(caption)}, NULL, {escape_sql_string(academic_year)}, N'Public', {'NULL' if not publish_date else escape_sql_string(publish_date)}, NULL, N'system', GETDATE(), GETDATE());"

            sql_statements.append(sql)

        except Exception as e:
            print(f"Error processing line {line_num} in {csv_file}: {e}")
            continue

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
all_sql.append("-- Set IDENTITY_INSERT ON to insert explicit ID values")
all_sql.append("SET IDENTITY_INSERT dbo.uploads ON;")
all_sql.append("GO")
all_sql.append("")

total_records = 0

for csv_file, file_type in file_mapping.items():
    try:
        all_sql.append(f"-- {file_type} data from {csv_file}")
        statements = generate_sql_insert(csv_file, file_type)
        all_sql.extend(statements)
        all_sql.append("")
        total_records += len(statements)
        print(f"✓ Processed {csv_file}: {len(statements)} records")
    except Exception as e:
        print(f"✗ Error processing {csv_file}: {e}")

all_sql.append("-- Reset IDENTITY_INSERT")
all_sql.append("SET IDENTITY_INSERT dbo.uploads OFF;")
all_sql.append("GO")
all_sql.append("")
all_sql.append(f"-- Total records inserted: {total_records}")
all_sql.append("PRINT 'Data import completed successfully!';")
all_sql.append("GO")

# Write to output file
output_file = 'BGSBU_Data_Import.sql'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(all_sql))

print(f"\n✓ SQL file generated: {output_file}")
print(f"✓ Total records: {total_records}")
print(f"✓ Ready to execute on SQL Server 2022")
