"""
Account Manager - Manages Suno accounts
"""
import shutil
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from config.settings import ACCOUNTS_FILE, PROFILES_DIR
from src.models import Account
from src.utils import load_json, save_json, logger


class AccountManager:
    """Manages Suno accounts and their metadata"""
    
    def __init__(self):
        self.accounts: Dict[str, Account] = {}
        self.load_accounts()
    
    def load_accounts(self) -> None:
        """Load account list from JSON file"""
        data = load_json(ACCOUNTS_FILE, {})
        self.accounts = {}
        for name, info in data.items():
            # Add name to info dict
            info['name'] = name
            self.accounts[name] = Account.from_dict(info)
        logger.info(f"Loaded {len(self.accounts)} accounts")
    
    def save_accounts(self) -> bool:
        """Save account list to JSON file"""
        data = {}
        for name, account in self.accounts.items():
            account_dict = account.to_dict()
            # Remove name from dict since it's the key
            account_dict.pop('name', None)
            data[name] = account_dict
        
        if save_json(ACCOUNTS_FILE, data):
            logger.info("Accounts saved successfully")
            return True
        return False
    
    def add_account(self, name: str, email: str) -> bool:
        """Add new account"""
        if name in self.accounts:
            logger.warning(f"Account {name} already exists")
            return False
        
        account = Account(
            name=name,
            email=email,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            status="active"
        )
        
        self.accounts[name] = account
        self.save_accounts()
        logger.info(f"Added account: {name}")
        return True
    
    def get_account(self, name: str) -> Optional[Account]:
        """Get account information"""
        return self.accounts.get(name)
    
    def update_account(self, name: str, **kwargs) -> bool:
        """Update account information"""
        if name not in self.accounts:
            return False
        
        account = self.accounts[name]
        for key, value in kwargs.items():
            if hasattr(account, key):
                setattr(account, key, value)
        
        self.save_accounts()
        logger.info(f"Updated account: {name}")
        return True
    
    def rename_account(self, old_name: str, new_name: str) -> bool:
        """Rename account"""
        if old_name not in self.accounts:
            logger.warning(f"Account {old_name} not found")
            return False
        
        if new_name in self.accounts:
            logger.warning(f"Account {new_name} already exists")
            return False
        
        # Rename profile directory
        old_profile = PROFILES_DIR / old_name
        new_profile = PROFILES_DIR / new_name
        
        if old_profile.exists():
            try:
                old_profile.rename(new_profile)
            except Exception as e:
                logger.error(f"Failed to rename profile: {e}")
                return False
        
        # Update account
        account = self.accounts.pop(old_name)
        account.name = new_name
        self.accounts[new_name] = account
        
        self.save_accounts()
        logger.info(f"Renamed account: {old_name} -> {new_name}")
        return True
    
    def delete_account(self, name: str, delete_profile: bool = False) -> bool:
        """Delete account"""
        if name not in self.accounts:
            return False
        
        # Delete from accounts
        del self.accounts[name]
        self.save_accounts()
        
        # Delete profile if requested
        if delete_profile:
            profile_dir = PROFILES_DIR / name
            if profile_dir.exists():
                try:
                    shutil.rmtree(profile_dir)
                    logger.info(f"Deleted profile for {name}")
                except Exception as e:
                    logger.error(f"Failed to delete profile: {e}")
        
        logger.info(f"Deleted account: {name}")
        return True
    
    def get_all_accounts(self) -> List[Account]:
        """Get all accounts"""
        return list(self.accounts.values())
    
    def update_last_used(self, name: str) -> None:
        """Update last used timestamp"""
        if name in self.accounts:
            self.accounts[name].last_used = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save_accounts()
    
    def get_profile_path(self, name: str) -> Optional[Path]:
        """Get account profile path"""
        if name not in self.accounts:
            return None
        
        profile_path = PROFILES_DIR / name
        return profile_path if profile_path.exists() else None
