# User Data Backup Scripts

These scripts provide disaster recovery capabilities for Django user data.

## Scripts

### export_user_data.py

Exports all user-related data from the Django SQLite database to a JSON file.

**Exports:**
- All users (including hashed passwords, permissions, groups)
- All groups and their permissions
- All permissions
- All OpenAI models and user assignments

**Usage:**
```bash
# Export to default timestamped file
python scripts/backup/export_user_data.py

# Export to specific file
python scripts/backup/export_user_data.py /path/to/backup.json
```

**Output:** JSON file with all user data (default: `user_data_backup_YYYYMMDD_HHMMSS.json`)

### import_user_data.py

Imports user-related data from a JSON backup file to recreate database state.

**Imports:**
- Users with all attributes and relationships
- Groups with permissions
- OpenAI model assignments

**Usage:**
```bash
python scripts/backup/import_user_data.py <backup_file.json>
```

**Warning:** This will overwrite existing data. You will be prompted for confirmation.

## Disaster Recovery Procedure

### Creating a Backup

```bash
cd /Users/kenny.w.philp/training/djangotest
source .venv/bin/activate
python scripts/backup/export_user_data.py
```

### Restoring from Backup

```bash
cd /Users/kenny.w.philp/training/djangotest
source .venv/bin/activate
python scripts/backup/import_user_data.py scripts/backup/user_data_backup_YYYYMMDD_HHMMSS.json
```

## Data Structure

The backup JSON file contains:
- `export_date`: Timestamp of when backup was created
- `django_version`: Django version used to create backup
- `users`: Array of user objects with all attributes
- `groups`: Array of groups with permissions
- `permissions`: Array of all permissions with content types
- `openai_models`: Array of OpenAI models with user assignments

## Best Practices

1. **Regular Backups**: Run export script regularly (daily/weekly)
2. **Version Control**: Keep backup files in a secure location
3. **Test Restores**: Periodically test the import process in a test environment
4. **Before Major Changes**: Always create a backup before making significant changes
5. **Secure Storage**: Backup files contain password hashes - store securely

## Notes

- Password hashes are preserved during export/import
- User IDs are maintained to preserve relationships
- Import is transactional - either all data imports or none
- Existing users/groups will be updated with backup data
