# 📁 File Upload & Storage System

This document explains how to set up and use the comprehensive file storage system with Google Cloud Storage integration in the Agentic MicroSaaS platform.

## 🚀 Features

- **Google Cloud Storage Integration**: Scalable, secure file storage
- **Multi-file Upload**: Drag & drop, multiple file selection
- **Chunked Upload**: Support for large files with resumable uploads
- **File Sharing**: Public and private file sharing with expiration
- **File Management**: Organize files with tags, metadata, and search
- **Team Integration**: Share files within teams
- **Access Control**: Role-based file access permissions
- **File Analytics**: Download tracking and usage statistics
- **Security**: File validation, virus scanning (optional), encryption support

## 📋 Setup Instructions

### 1. Google Cloud Platform Setup

#### Create a GCP Project
```bash
# Create a new GCP project
gcloud projects create your-project-id --name="Agentic MicroSaaS"

# Set the project
gcloud config set project your-project-id

# Enable required APIs
gcloud services enable storage.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable iam.googleapis.com
```

#### Create a Storage Bucket
```bash
# Create a storage bucket
gsutil mb gs://your-project-id-files

# Set bucket permissions
gsutil iam ch allUsers:objectViewer gs://your-project-id-files
```

#### Create Service Account
```bash
# Create service account
gcloud iam service-accounts create file-storage-sa \
    --display-name="File Storage Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:file-storage-sa@your-project-id.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Create and download key
gcloud iam service-accounts keys create ./service-account-key.json \
    --iam-account=file-storage-sa@your-project-id.iam.gserviceaccount.com
```

### 2. Environment Configuration

Copy the example environment file:
```bash
cp gcp-storage.env.example .env
```

Update the `.env` file with your GCP configuration:
```env
GCP_PROJECT_ID=your-project-id
GCS_BUCKET_NAME=your-project-id-files
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json
```

### 3. Database Migration

Run the database migration to create the file storage tables:

```bash
# For the API (SQLAlchemy)
cd apps/api
alembic upgrade head

# For the web app (Prisma)
cd apps/web
npx prisma db push
```

### 4. Install Dependencies

```bash
# Backend dependencies (already included)
cd apps/api
pip install -r requirements.txt

# Frontend dependencies (already included)
cd apps/web
npm install
```

## 🔧 API Endpoints

### Authentication Required
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

### File Upload

#### Upload Single File
```http
POST /files/upload
Content-Type: multipart/form-data

file: <file>
team_id: <optional-team-id>
is_public: false
tags: ["tag1", "tag2"]
metadata: {"key": "value"}
```

#### Create Upload Session (for large files)
```http
POST /files/upload/session
Content-Type: application/json

{
  "filename": "large-file.zip",
  "file_size": 104857600,
  "mime_type": "application/zip",
  "chunk_size": 1048576
}
```

#### Upload Chunk
```http
POST /files/upload/chunk?session_token=<token>&chunk_number=<number>
Content-Type: application/octet-stream

<chunk-data>
```

### File Management

#### Get User Files
```http
GET /files?team_id=<id>&tags=tag1,tag2&mime_type=image&limit=50&offset=0
```

#### Get File Information
```http
GET /files/{file_id}
```

#### Download File
```http
GET /files/{file_id}/download
```

#### Get File URL (signed URL)
```http
GET /files/{file_id}/url?expires_in=3600
```

#### Delete File
```http
DELETE /files/{file_id}
```

### File Sharing

#### Share File
```http
POST /files/{file_id}/share
Content-Type: application/json

{
  "shared_with_user_id": "user_id",
  "shared_with_team_id": "team_id",
  "permission": "read",
  "expires_at": "2024-12-31T23:59:59Z"
}
```

#### Download Shared File
```http
GET /files/shared/{share_token}
```

### Storage Statistics

#### Get Storage Stats
```http
GET /files/stats
```

## 🎨 Frontend Components

### FileManager Component

The `FileManager` component provides a complete file management interface:

```tsx
import { FileManager } from '@/components/FileManager';

export default function Files() {
  return (
    <div>
      <h1>File Manager</h1>
      <FileManager />
    </div>
  );
}
```

### Features:
- **Drag & Drop Upload**: Intuitive file upload interface
- **File Grid View**: Visual file browser with thumbnails
- **Search & Filter**: Find files by name, type, tags
- **File Actions**: Download, share, delete files
- **Storage Stats**: Usage statistics and analytics
- **Team Integration**: Share files with team members

## 🏗️ Database Schema

### Files Table
```sql
CREATE TABLE files (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id),
    team_id VARCHAR REFERENCES teams(id),
    filename VARCHAR NOT NULL,
    original_filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR NOT NULL,
    file_hash VARCHAR NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    is_encrypted BOOLEAN DEFAULT FALSE,
    metadata JSON,
    tags JSON,
    download_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### File Shares Table
```sql
CREATE TABLE file_shares (
    id VARCHAR PRIMARY KEY,
    file_id VARCHAR NOT NULL REFERENCES files(id),
    shared_by_id VARCHAR NOT NULL REFERENCES users(id),
    shared_with_user_id VARCHAR REFERENCES users(id),
    shared_with_team_id VARCHAR REFERENCES teams(id),
    share_token VARCHAR UNIQUE NOT NULL,
    permission VARCHAR DEFAULT 'read',
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### File Upload Sessions Table
```sql
CREATE TABLE file_upload_sessions (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id),
    session_token VARCHAR UNIQUE NOT NULL,
    filename VARCHAR NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR NOT NULL,
    chunk_size INTEGER DEFAULT 1048576,
    total_chunks INTEGER NOT NULL,
    uploaded_chunks JSON,
    status VARCHAR DEFAULT 'pending',
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🔐 Security Features

### File Validation
- **File Type Validation**: Check MIME types against allowed list
- **File Size Limits**: Configurable maximum file sizes
- **Virus Scanning**: Optional integration with virus scanning services
- **Content Validation**: Verify file content matches declared type

### Access Control
- **User Ownership**: Users can only access their own files
- **Team Permissions**: Team members can access team files based on roles
- **Public Files**: Optional public file sharing
- **Share Tokens**: Secure token-based file sharing with expiration

### Data Protection
- **Encryption at Rest**: Files encrypted in Google Cloud Storage
- **Encryption in Transit**: HTTPS for all file transfers
- **Access Logging**: Complete audit trail of file access
- **Secure Deletion**: Proper cleanup of deleted files

## 🚀 Production Deployment

### 1. Terraform Infrastructure

The Terraform configuration includes:
- **Storage Bucket**: Configured with versioning and lifecycle rules
- **Service Account**: Dedicated service account for file operations
- **IAM Permissions**: Proper role-based access control
- **CORS Configuration**: Web upload support

Deploy with:
```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

### 2. Environment Variables

Set the following environment variables in your Cloud Run services:
```env
GCS_BUCKET_NAME=your-bucket-name
GCP_PROJECT_ID=your-project-id
```

### 3. Service Account

The Cloud Run services will automatically use the attached service account for GCS access.

## 📊 Monitoring & Analytics

### File Usage Metrics
- **Upload Statistics**: Files uploaded per user/team
- **Download Tracking**: File access patterns
- **Storage Usage**: Total storage consumed
- **File Type Distribution**: Most common file types

### Performance Monitoring
- **Upload Speed**: Track upload performance
- **Download Speed**: Monitor download times
- **Error Rates**: Track failed uploads/downloads
- **Storage Costs**: Monitor GCS usage costs

## 🧪 Testing

### Test File Upload
```python
# Test file upload
with open('test-file.txt', 'rb') as f:
    response = requests.post(
        '/api/files/upload',
        files={'file': f},
        headers={'Authorization': f'Bearer {token}'}
    )
```

### Test File Sharing
```python
# Test file sharing
response = requests.post(
    f'/api/files/{file_id}/share',
    json={
        'permission': 'read',
        'expires_at': '2024-12-31T23:59:59Z'
    },
    headers={'Authorization': f'Bearer {token}'}
)
```

### Test Chunked Upload
```python
# Test chunked upload
session_response = requests.post(
    '/api/files/upload/session',
    json={
        'filename': 'large-file.zip',
        'file_size': 10485760,
        'mime_type': 'application/zip'
    },
    headers={'Authorization': f'Bearer {token}'}
)

session_token = session_response.json()['session_token']

# Upload chunks
for i in range(total_chunks):
    chunk_data = read_chunk(i)
    requests.post(
        f'/api/files/upload/chunk?session_token={session_token}&chunk_number={i}',
        data=chunk_data,
        headers={'Authorization': f'Bearer {token}'}
    )
```

## 🔍 Troubleshooting

### Common Issues

1. **Upload Failures**:
   - Check GCS bucket permissions
   - Verify service account credentials
   - Check file size limits

2. **Download Issues**:
   - Verify file exists in GCS
   - Check user permissions
   - Verify share token validity

3. **Permission Errors**:
   - Check IAM roles
   - Verify service account permissions
   - Check bucket policies

### Debug Mode

Enable debug logging:
```python
import logging
logging.getLogger('storage_service').setLevel(logging.DEBUG)
```

## 📚 Additional Resources

- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [Terraform GCS Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket)
- [File Upload Best Practices](https://cloud.google.com/storage/docs/best-practices)
- [CORS Configuration](https://cloud.google.com/storage/docs/configuring-cors)
