"""
Shared Common Utilities
Common utility functions for ID generation, validation, file handling, text processing, and more
"""
import uuid
import re
import os
import hashlib
import time
import functools
import asyncio
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlparse, urlencode
import mimetypes
import math

class IDGenerator:
    """Utility class for generating various types of IDs"""
    
    @staticmethod
    def generate_uuid() -> str:
        """Generate a UUID4 string"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_short_id(length: int = 8) -> str:
        """Generate a short alphanumeric ID"""
        import random
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def generate_slug(text: str, max_length: int = 50) -> str:
        """Generate a URL-friendly slug from text"""
        # Convert to lowercase and replace spaces with hyphens
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:max_length].strip('-')
    
    @staticmethod
    def generate_timestamp_id() -> str:
        """Generate an ID based on timestamp"""
        return str(int(time.time() * 1000))

class ValidationUtils:
    """Utility class for validation functions"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email address format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Validate phone number format"""
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        # Check if it's a valid length (7-15 digits)
        return 7 <= len(digits) <= 15
    
    @staticmethod
    def is_valid_password(password: str, min_length: int = 8) -> bool:
        """Validate password strength"""
        if len(password) < min_length:
            return False
        
        # Check for at least one uppercase, lowercase, digit, and special character
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        return has_upper and has_lower and has_digit and has_special

class FileUtils:
    """Utility class for file handling operations"""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename by removing dangerous characters"""
        # Remove or replace dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        return filename
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension from filename"""
        return os.path.splitext(filename)[1].lower()
    
    @staticmethod
    def get_mime_type(filename: str) -> str:
        """Get MIME type for file"""
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    @staticmethod
    def calculate_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
        """Calculate hash of a file"""
        hash_obj = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    
    @staticmethod
    def is_safe_file_type(filename: str, allowed_extensions: List[str] = None) -> bool:
        """Check if file type is safe/allowed"""
        if allowed_extensions is None:
            allowed_extensions = ['.txt', '.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif']
        
        ext = FileUtils.get_file_extension(filename)
        return ext in allowed_extensions

class TextUtils:
    """Utility class for text processing operations"""
    
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text to specified length"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int, overlap: int = 0) -> List[str]:
        """Split text into chunks with optional overlap"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text by removing extra whitespace and special characters"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        return text.strip()
    
    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """Extract hashtags from text"""
        return re.findall(r'#\w+', text)
    
    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """Extract mentions from text"""
        return re.findall(r'@\w+', text)
    
    @staticmethod
    def word_count(text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    @staticmethod
    def reading_time(text: str, words_per_minute: int = 200) -> int:
        """Calculate estimated reading time in minutes"""
        words = TextUtils.word_count(text)
        return max(1, words // words_per_minute)

class DictUtils:
    """Utility class for dictionary operations"""
    
    @staticmethod
    def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = DictUtils.deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    @staticmethod
    def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """Flatten a nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(DictUtils.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    @staticmethod
    def get_nested_value(d: Dict, key_path: str, default: Any = None) -> Any:
        """Get value from nested dictionary using dot notation"""
        keys = key_path.split('.')
        value = d
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    @staticmethod
    def set_nested_value(d: Dict, key_path: str, value: Any) -> None:
        """Set value in nested dictionary using dot notation"""
        keys = key_path.split('.')
        current = d
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value

class RetryUtils:
    """Utility class for retry operations"""
    
    @staticmethod
    def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0, exceptions: Tuple = (Exception,)):
        """Decorator for retrying functions with exponential backoff"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            time.sleep(delay * (backoff ** attempt))
                        else:
                            raise last_exception
                
                return None
            return wrapper
        return decorator
    
    @staticmethod
    def retry_async(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0, exceptions: Tuple = (Exception,)):
        """Decorator for retrying async functions with exponential backoff"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_attempts):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            await asyncio.sleep(delay * (backoff ** attempt))
                        else:
                            raise last_exception
                
                return None
            return wrapper
        return decorator

class PerformanceUtils:
    """Utility class for performance monitoring"""
    
    @staticmethod
    def timing_decorator(func: Callable) -> Callable:
        """Decorator to measure function execution time"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            execution_time = end_time - start_time
            print(f"{func.__name__} executed in {execution_time:.4f} seconds")
            
            return result
        return wrapper
    
    @staticmethod
    def async_timing_decorator(func: Callable) -> Callable:
        """Decorator to measure async function execution time"""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            
            execution_time = end_time - start_time
            print(f"{func.__name__} executed in {execution_time:.4f} seconds")
            
            return result
        return wrapper

class PaginationUtils:
    """Utility class for pagination operations"""
    
    @staticmethod
    def paginate(items: List[Any], page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Paginate a list of items"""
        total_items = len(items)
        total_pages = math.ceil(total_items / per_page)
        
        # Validate page number
        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages
        
        # Calculate start and end indices
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        
        # Get items for current page
        page_items = items[start_index:end_index]
        
        return {
            "items": page_items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_prev": page > 1,
                "has_next": page < total_pages,
                "prev_page": page - 1 if page > 1 else None,
                "next_page": page + 1 if page < total_pages else None
            }
        }
    
    @staticmethod
    def create_pagination_links(base_url: str, page: int, total_pages: int, params: Dict[str, Any] = None) -> Dict[str, str]:
        """Create pagination links"""
        if params is None:
            params = {}
        
        links = {}
        
        if page > 1:
            prev_params = params.copy()
            prev_params['page'] = page - 1
            links['prev'] = f"{base_url}?{urlencode(prev_params)}"
        
        if page < total_pages:
            next_params = params.copy()
            next_params['page'] = page + 1
            links['next'] = f"{base_url}?{urlencode(next_params)}"
        
        return links

# Convenience functions
def generate_uuid() -> str:
    """Generate a UUID4 string"""
    return IDGenerator.generate_uuid()

def generate_short_id(length: int = 8) -> str:
    """Generate a short alphanumeric ID"""
    return IDGenerator.generate_short_id(length)

def is_valid_email(email: str) -> bool:
    """Validate email address format"""
    return ValidationUtils.is_valid_email(email)

def is_valid_url(url: str) -> bool:
    """Validate URL format"""
    return ValidationUtils.is_valid_url(url)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing dangerous characters"""
    return FileUtils.sanitize_filename(filename)

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    return FileUtils.format_file_size(size_bytes)

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    return TextUtils.truncate_text(text, max_length, suffix)

def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries"""
    return DictUtils.deep_merge(dict1, dict2)

def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0, exceptions: Tuple = (Exception,)):
    """Decorator for retrying functions with exponential backoff"""
    return RetryUtils.retry(max_attempts, delay, backoff, exceptions)

def timing_decorator(func: Callable) -> Callable:
    """Decorator to measure function execution time"""
    return PerformanceUtils.timing_decorator(func)

def paginate(items: List[Any], page: int = 1, per_page: int = 10) -> Dict[str, Any]:
    """Paginate a list of items"""
    return PaginationUtils.paginate(items, page, per_page)
