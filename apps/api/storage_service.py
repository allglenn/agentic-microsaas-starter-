import sys
import hashlib
import secrets
import logging
from typing import Optional, Dict, Any, List, BinaryIO
from datetime import datetime, timedelta
from io import BytesIO
import mimetypes

from google.cloud import storage
from google.cloud.exceptions import NotFound, GoogleCloudError
from google.oauth2 import service_account
from sqlalchemy.orm import Session
import json

# Add project root to path for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from libs.shared.models import File, FileShare, FileUploadSession, FileAccessLog, User
from libs.shared.config import get_gcp_config

logger = logging.getLogger(__name__)

class StorageService:
    """Service class for handling file storage operations with Google Cloud Storage"""
    
    def __init__(self):
        # Get GCP configuration from shared config
        gcp_config = get_gcp_config()
        self.bucket_name = gcp_config["bucket_name"]
        self.project_id = gcp_config["project_id"]
        
        # Initialize GCS client
        if gcp_config.get("credentials_path"):
            # Use service account key file
            credentials = service_account.Credentials.from_service_account_file(
                gcp_config["credentials_path"]
            )
            self.client = storage.Client(credentials=credentials, project=self.project_id)
        else:
            # Use default credentials (for Cloud Run, etc.)
            self.client = storage.Client(project=self.project_id)
        
        self.bucket = self.client.bucket(self.bucket_name)
    
    def upload_file(
        self,
        file_content: bytes,
        filename: str,
        user: User,
        team_id: Optional[str] = None,
        is_public: bool = False,
        file_metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        db: Session = None
    ) -> File:
        """Upload a file to Google Cloud Storage"""
        try:
            # Generate unique filename to prevent conflicts
            file_hash = hashlib.sha256(file_content).hexdigest()
            file_extension = os.path.splitext(filename)[1]
            unique_filename = f"{file_hash[:16]}{file_extension}"
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type:
                mime_type = "application/octet-stream"
            
            # Create GCS path
            user_folder = f"users/{user.id}"
            team_folder = f"teams/{team_id}" if team_id else "personal"
            gcs_path = f"{user_folder}/{team_folder}/{unique_filename}"
            
            # Upload to GCS
            blob = self.bucket.blob(gcs_path)
            blob.upload_from_string(
                file_content,
                content_type=mime_type,
                file_metadata={
                    "original_filename": filename,
                    "user_id": user.id,
                    "team_id": team_id or "",
                    "uploaded_at": datetime.utcnow().isoformat()
                }
            )
            
            # Set public access if requested
            if is_public:
                blob.make_public()
            
            # Create database record
            file_record = File(
                user_id=user.id,
                team_id=team_id,
                filename=unique_filename,
                original_filename=filename,
                file_path=gcs_path,
                file_size=len(file_content),
                mime_type=mime_type,
                file_hash=file_hash,
                is_public=is_public,
                file_metadata=file_metadata or {},
                tags=tags or []
            )
            
            db.add(file_record)
            db.commit()
            db.refresh(file_record)
            
            # Log access
            self._log_access(file_record.id, user.id, "upload", db)
            
            logger.info(f"Uploaded file {filename} for user {user.email}")
            return file_record
            
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise
    
    def download_file(self, file_id: str, user: User, db: Session) -> tuple[bytes, File]:
        """Download a file from Google Cloud Storage"""
        try:
            # Get file record
            file_record = db.query(File).filter(File.id == file_id).first()
            if not file_record:
                raise ValueError("File not found")
            
            # Check permissions
            if not self._has_file_access(file_record, user, db):
                raise ValueError("Access denied")
            
            # Download from GCS
            blob = self.bucket.blob(file_record.file_path)
            file_content = blob.download_as_bytes()
            
            # Update access stats
            file_record.download_count += 1
            file_record.last_accessed = datetime.utcnow()
            db.commit()
            
            # Log access
            self._log_access(file_record.id, user.id, "download", db)
            
            logger.info(f"Downloaded file {file_record.original_filename} for user {user.email}")
            return file_content, file_record
            
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            raise
    
    def get_file_url(self, file_id: str, user: User, db: Session, expires_in: int = 3600) -> str:
        """Get a signed URL for file access"""
        try:
            file_record = db.query(File).filter(File.id == file_id).first()
            if not file_record:
                raise ValueError("File not found")
            
            # Check permissions
            if not self._has_file_access(file_record, user, db):
                raise ValueError("Access denied")
            
            # Generate signed URL
            blob = self.bucket.blob(file_record.file_path)
            url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.utcnow() + timedelta(seconds=expires_in),
                method="GET"
            )
            
            # Log access
            self._log_access(file_record.id, user.id, "view", db)
            
            return url
            
        except Exception as e:
            logger.error(f"Error generating file URL: {e}")
            raise
    
    def delete_file(self, file_id: str, user: User, db: Session) -> bool:
        """Delete a file from both GCS and database"""
        try:
            file_record = db.query(File).filter(File.id == file_id).first()
            if not file_record:
                raise ValueError("File not found")
            
            # Check ownership
            if file_record.user_id != user.id:
                raise ValueError("Access denied")
            
            # Delete from GCS
            blob = self.bucket.blob(file_record.file_path)
            blob.delete()
            
            # Delete from database
            db.delete(file_record)
            db.commit()
            
            # Log access
            self._log_access(file_record.id, user.id, "delete", db)
            
            logger.info(f"Deleted file {file_record.original_filename} for user {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            raise
    
    def share_file(
        self,
        file_id: str,
        user: User,
        shared_with_user_id: Optional[str] = None,
        shared_with_team_id: Optional[str] = None,
        permission: str = "read",
        expires_at: Optional[datetime] = None,
        db: Session = None
    ) -> FileShare:
        """Share a file with a user or team"""
        try:
            file_record = db.query(File).filter(File.id == file_id).first()
            if not file_record:
                raise ValueError("File not found")
            
            # Check ownership
            if file_record.user_id != user.id:
                raise ValueError("Access denied")
            
            # Generate share token
            share_token = secrets.token_urlsafe(32)
            
            # Create share record
            file_share = FileShare(
                file_id=file_id,
                shared_by_id=user.id,
                shared_with_user_id=shared_with_user_id,
                shared_with_team_id=shared_with_team_id,
                share_token=share_token,
                permission=permission,
                expires_at=expires_at
            )
            
            db.add(file_share)
            db.commit()
            db.refresh(file_share)
            
            logger.info(f"Shared file {file_record.original_filename} with token {share_token}")
            return file_share
            
        except Exception as e:
            logger.error(f"Error sharing file: {e}")
            raise
    
    def get_shared_file(self, share_token: str, db: Session) -> tuple[bytes, File]:
        """Download a file using a share token"""
        try:
            # Get share record
            file_share = db.query(FileShare).filter(
                FileShare.share_token == share_token,
                FileShare.is_active == True
            ).first()
            
            if not file_share:
                raise ValueError("Invalid or expired share token")
            
            # Check expiration
            if file_share.expires_at and file_share.expires_at < datetime.utcnow():
                raise ValueError("Share token has expired")
            
            # Get file record
            file_record = file_share.file
            
            # Download from GCS
            blob = self.bucket.blob(file_record.file_path)
            file_content = blob.download_as_bytes()
            
            # Update access stats
            file_share.access_count += 1
            file_share.last_accessed = datetime.utcnow()
            file_record.download_count += 1
            file_record.last_accessed = datetime.utcnow()
            db.commit()
            
            # Log access
            self._log_access(file_record.id, None, "download", db, share_token=share_token)
            
            logger.info(f"Downloaded shared file {file_record.original_filename}")
            return file_content, file_record
            
        except Exception as e:
            logger.error(f"Error downloading shared file: {e}")
            raise
    
    def get_user_files(
        self,
        user: User,
        team_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        mime_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        db: Session = None
    ) -> List[File]:
        """Get files for a user with optional filtering"""
        try:
            query = db.query(File).filter(File.user_id == user.id)
            
            if team_id:
                query = query.filter(File.team_id == team_id)
            
            if tags:
                # Filter by tags using JSON contains
                for tag in tags:
                    query = query.filter(File.tags.contains([tag]))
            
            if mime_type:
                query = query.filter(File.mime_type.like(f"{mime_type}%"))
            
            files = query.order_by(File.created_at.desc()).offset(offset).limit(limit).all()
            return files
            
        except Exception as e:
            logger.error(f"Error getting user files: {e}")
            raise
    
    def create_upload_session(
        self,
        filename: str,
        file_size: int,
        mime_type: str,
        user: User,
        chunk_size: int = 1048576,  # 1MB
        db: Session = None
    ) -> FileUploadSession:
        """Create a resumable upload session for large files"""
        try:
            # Calculate total chunks
            total_chunks = (file_size + chunk_size - 1) // chunk_size
            
            # Generate session token
            session_token = secrets.token_urlsafe(32)
            
            # Create upload session
            upload_session = FileUploadSession(
                user_id=user.id,
                session_token=session_token,
                filename=filename,
                file_size=file_size,
                mime_type=mime_type,
                chunk_size=chunk_size,
                total_chunks=total_chunks,
                uploaded_chunks=[],
                expires_at=datetime.utcnow() + timedelta(hours=24)  # 24 hour expiration
            )
            
            db.add(upload_session)
            db.commit()
            db.refresh(upload_session)
            
            logger.info(f"Created upload session for {filename} with {total_chunks} chunks")
            return upload_session
            
        except Exception as e:
            logger.error(f"Error creating upload session: {e}")
            raise
    
    def upload_chunk(
        self,
        session_token: str,
        chunk_number: int,
        chunk_data: bytes,
        db: Session
    ) -> Dict[str, Any]:
        """Upload a chunk of a file"""
        try:
            # Get upload session
            upload_session = db.query(FileUploadSession).filter(
                FileUploadSession.session_token == session_token,
                FileUploadSession.status.in_(["pending", "uploading"])
            ).first()
            
            if not upload_session:
                raise ValueError("Invalid or expired upload session")
            
            # Check if chunk already uploaded
            if chunk_number in (upload_session.uploaded_chunks or []):
                return {"status": "already_uploaded", "chunk_number": chunk_number}
            
            # Upload chunk to GCS
            chunk_path = f"uploads/{upload_session.id}/chunk_{chunk_number}"
            blob = self.bucket.blob(chunk_path)
            blob.upload_from_string(chunk_data)
            
            # Update session
            uploaded_chunks = upload_session.uploaded_chunks or []
            uploaded_chunks.append(chunk_number)
            upload_session.uploaded_chunks = uploaded_chunks
            upload_session.status = "uploading"
            db.commit()
            
            # Check if all chunks uploaded
            if len(uploaded_chunks) == upload_session.total_chunks:
                return self._finalize_upload(upload_session, db)
            
            return {
                "status": "chunk_uploaded",
                "chunk_number": chunk_number,
                "total_chunks": upload_session.total_chunks,
                "uploaded_chunks": len(uploaded_chunks)
            }
            
        except Exception as e:
            logger.error(f"Error uploading chunk: {e}")
            raise
    
    def _finalize_upload(self, upload_session: FileUploadSession, db: Session) -> Dict[str, Any]:
        """Finalize a multi-chunk upload by combining chunks"""
        try:
            # Download all chunks and combine
            combined_data = BytesIO()
            for chunk_number in range(upload_session.total_chunks):
                chunk_path = f"uploads/{upload_session.id}/chunk_{chunk_number}"
                blob = self.bucket.blob(chunk_path)
                chunk_data = blob.download_as_bytes()
                combined_data.write(chunk_data)
            
            # Upload final file
            file_content = combined_data.getvalue()
            user = db.query(User).filter(User.id == upload_session.user_id).first()
            
            file_record = self.upload_file(
                file_content=file_content,
                filename=upload_session.filename,
                user=user,
                db=db
            )
            
            # Clean up chunks
            for chunk_number in range(upload_session.total_chunks):
                chunk_path = f"uploads/{upload_session.id}/chunk_{chunk_number}"
                blob = self.bucket.blob(chunk_path)
                blob.delete()
            
            # Update session
            upload_session.status = "completed"
            db.commit()
            
            return {
                "status": "completed",
                "file_id": file_record.id,
                "filename": file_record.original_filename
            }
            
        except Exception as e:
            logger.error(f"Error finalizing upload: {e}")
            upload_session.status = "failed"
            db.commit()
            raise
    
    def _has_file_access(self, file_record: File, user: User, db: Session) -> bool:
        """Check if user has access to a file"""
        # Owner always has access
        if file_record.user_id == user.id:
            return True
        
        # Check if file is public
        if file_record.is_public:
            return True
        
        # Check team access
        if file_record.team_id:
            from team_service import TeamService
            return TeamService.has_permission(user.id, file_record.team_id, "files:read", db)
        
        # Check shared access
        share = db.query(FileShare).filter(
            FileShare.file_id == file_record.id,
            FileShare.is_active == True,
            FileShare.shared_with_user_id == user.id
        ).first()
        
        return share is not None
    
    def _log_access(
        self,
        file_id: str,
        user_id: Optional[str],
        action: str,
        db: Session,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        share_token: Optional[str] = None
    ):
        """Log file access for auditing"""
        try:
            access_log = FileAccessLog(
                file_id=file_id,
                user_id=user_id,
                action=action,
                ip_address=ip_address,
                user_agent=user_agent,
                access_metadata={"share_token": share_token} if share_token else None
            )
            db.add(access_log)
            db.commit()
        except Exception as e:
            logger.error(f"Error logging file access: {e}")
    
    def get_storage_stats(self, user: User, db: Session) -> Dict[str, Any]:
        """Get storage statistics for a user"""
        try:
            files = db.query(File).filter(File.user_id == user.id).all()
            
            total_size = sum(file.file_size for file in files)
            total_files = len(files)
            
            # Group by MIME type
            mime_types = {}
            for file in files:
                mime_type = file.mime_type.split('/')[0]  # Get main type (image, video, etc.)
                mime_types[mime_type] = mime_types.get(mime_type, 0) + 1
            
            return {
                "total_files": total_files,
                "total_size": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "mime_types": mime_types,
                "files": files
            }
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            raise
