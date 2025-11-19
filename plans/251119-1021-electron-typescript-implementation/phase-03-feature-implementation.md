# Phase 3: Feature Implementation - Core Functionality Migration

**Phase ID:** 251119-1021-P3
**Duration:** 5 days
**Priority:** High
**Dependencies:** Phase 2 - React Frontend Integration (Complete)

## Overview

Migrate core features from Python CustomTkinter to React components with full backend integration. This phase focuses on implementing account management, song creation with queue system, download management, and history tracking with modern React patterns and real-time updates.

## Objectives

1. **Account Management**: Complete account CRUD operations with session management
2. **Song Creation**: Implement queue-based song creation with real-time progress
3. **Download Management**: Build download interface with batch operations
4. **History Tracking**: Create comprehensive history views with export functionality
5. **Settings Management**: Implement configuration and preferences
6. **Real-time Updates**: Establish live progress tracking and notifications

## Feature Mapping

| Python Component | React Component | Key Features |
|------------------|----------------|--------------|
| `AccountPanel` | `AccountManager` | CRUD operations, session management |
| `MultipleSongsPanel` | `SongCreator` | Queue system, batch creation |
| `DownloadPanel` | `DownloadManager` | Batch download, metadata |
| `HistoryPanel` | `HistoryView` | Creation/download history |
| `CreateMusicPanel` | `QuickCreator` | Simple song creation |

## Daily Breakdown

### Day 1: Account Management Implementation

#### Morning (4 hours)
**Task: Create Account Management Components**

```typescript
// src/components/features/AccountManager.tsx
import React, { useEffect, useState } from 'react';
import { useAccountStore, useAccountActions, useCurrentAccount } from '@/stores/accountStore';
import { useUIStore, useUIActions } from '@/stores/uiStore';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Modal } from '@/components/ui/Modal';
import { Table } from '@/components/ui/Table';
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  ArrowPathIcon,
  UserIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';

interface AccountFormData {
  name: string;
  email: string;
}

export const AccountManager: React.FC = () => {
  const { accounts, currentAccount, isLoading, error } = useAccountStore();
  const { loadAccounts, createAccount, updateAccount, deleteAccount, selectAccount, clearError } = useAccountActions();
  const { addNotification } = useUIActions();

  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null);

  // Form states
  const [formData, setFormData] = useState<AccountFormData>({ name: '', email: '' });
  const [formErrors, setFormErrors] = useState<Partial<AccountFormData>>({});

  useEffect(() => {
    loadAccounts();
  }, [loadAccounts]);

  const handleCreateAccount = async () => {
    if (!validateForm()) return;

    try {
      const newAccount = await createAccount(formData);
      setShowCreateModal(false);
      resetForm();
      addNotification({
        type: 'success',
        title: 'Thành công',
        message: `Tài khoản "${newAccount.name}" đã được tạo`
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Lỗi',
        message: error instanceof Error ? error.message : 'Không thể tạo tài khoản'
      });
    }
  };

  const handleUpdateAccount = async () => {
    if (!selectedAccount || !validateForm()) return;

    try {
      const success = await updateAccount(selectedAccount.id, formData);
      if (success) {
        setShowEditModal(false);
        resetForm();
        setSelectedAccount(null);
        addNotification({
          type: 'success',
          title: 'Thành công',
          message: `Tài khoản "${selectedAccount.name}" đã được cập nhật`
        });
      }
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Lỗi',
        message: error instanceof Error ? error.message : 'Không thể cập nhật tài khoản'
      });
    }
  };

  const handleDeleteAccount = async () => {
    if (!selectedAccount) return;

    try {
      const success = await deleteAccount(selectedAccount.id);
      if (success) {
        setShowDeleteModal(false);
        setSelectedAccount(null);
        addNotification({
          type: 'success',
          title: 'Thành công',
          message: `Tài khoản "${selectedAccount.name}" đã bị xóa`
        });
      }
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Lỗi',
        message: error instanceof Error ? error.message : 'Không thể xóa tài khoản'
      });
    }
  };

  const handleSelectAccount = (account: Account) => {
    selectAccount(account);
    addNotification({
      type: 'info',
      title: 'Đã chọn',
      message: `Đã chọn tài khoản "${account.name}"`
    });
  };

  const handleRefreshSession = async (account: Account) => {
    try {
      const success = await refreshSession(account.id);
      if (success) {
        addNotification({
          type: 'success',
          title: 'Thành công',
          message: `Session cho "${account.name}" đã được làm mới`
        });
      }
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Lỗi',
        message: 'Không thể làm mới session'
      });
    }
  };

  const validateForm = (): boolean => {
    const errors: Partial<AccountFormData> = {};

    if (!formData.name.trim()) {
      errors.name = 'Tên tài khoản không được để trống';
    }

    if (!formData.email.trim()) {
      errors.email = 'Email không được để trống';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Email không hợp lệ';
    }

    if (formData.name.length > 50) {
      errors.name = 'Tên tài khoản không được quá 50 ký tự';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const resetForm = () => {
    setFormData({ name: '', email: '' });
    setFormErrors({});
  };

  const openEditModal = (account: Account) => {
    setSelectedAccount(account);
    setFormData({ name: account.name, email: account.email });
    setShowEditModal(true);
  };

  const openDeleteModal = (account: Account) => {
    setSelectedAccount(account);
    setShowDeleteModal(true);
  };

  const columns = [
    {
      key: 'status' as keyof Account,
      label: 'Trạng thái',
      width: '100px',
      align: 'center' as const,
      render: (value: string) => (
        <div className="flex justify-center">
          {value === 'active' ? (
            <CheckCircleIcon className="w-5 h-5 text-green-500" />
          ) : (
            <XCircleIcon className="w-5 h-5 text-red-500" />
          )}
        </div>
      )
    },
    {
      key: 'name' as keyof Account,
      label: 'Tên tài khoản',
      render: (value: string, account: Account) => (
        <div className="flex items-center space-x-2">
          <UserIcon className="w-4 h-4 text-gray-400" />
          <span className={currentAccount?.id === account.id ? 'font-semibold text-blue-400' : ''}>
            {value}
          </span>
          {currentAccount?.id === account.id && (
            <span className="text-xs bg-blue-500 text-white px-2 py-1 rounded">Đang dùng</span>
          )}
        </div>
      )
    },
    {
      key: 'email' as keyof Account,
      label: 'Email'
    },
    {
      key: 'created_at' as keyof Account,
      label: 'Ngày tạo',
      render: (value: string) => new Date(value).toLocaleDateString('vi-VN')
    },
    {
      key: 'last_used' as keyof Account,
      label: 'Lần dùng cuối',
      render: (value: string) => value ? new Date(value).toLocaleString('vi-VN') : 'Chưa dùng'
    },
    {
      key: 'actions' as keyof Account,
      label: 'Thao tác',
      width: '200px',
      align: 'center' as const,
      render: (_: any, account: Account) => (
        <div className="flex justify-center space-x-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleSelectAccount(account)}
            title="Sử dụng tài khoản"
          >
            <UserIcon className="w-4 h-4" />
          </Button>

          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleRefreshSession(account)}
            title="Làm mới session"
          >
            <ArrowPathIcon className="w-4 h-4" />
          </Button>

          <Button
            size="sm"
            variant="ghost"
            onClick={() => openEditModal(account)}
            title="Chỉnh sửa"
          >
            <PencilIcon className="w-4 h-4" />
          </Button>

          <Button
            size="sm"
            variant="ghost"
            onClick={() => openDeleteModal(account)}
            title="Xóa"
            className="text-red-500 hover:text-red-600"
          >
            <TrashIcon className="w-4 h-4" />
          </Button>
        </div>
      )
    }
  ];

  return (
    <div className="account-manager">
      <div className="page-header">
        <div className="page-title">
          <h1>Quản lý tài khoản</h1>
          <p className="text-gray-400">Thêm, sửa và quản lý các tài khoản Suno</p>
        </div>

        <Button
          variant="primary"
          icon={<PlusIcon className="w-4 h-4" />}
          onClick={() => setShowCreateModal(true)}
        >
          Thêm tài khoản
        </Button>
      </div>

      {error && (
        <div className="error-banner">
          <span className="error-message">{error}</span>
          <button onClick={clearError} className="error-dismiss">×</button>
        </div>
      )}

      <div className="page-content">
        <Table
          data={accounts}
          columns={columns}
          loading={isLoading}
          emptyMessage="Chưa có tài khoản nào. Hãy tạo tài khoản đầu tiên!"
          hoverable
        />
      </div>

      {/* Create Account Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Tạo tài khoản mới"
        size="md"
      >
        <div className="space-y-4">
          <Input
            label="Tên tài khoản"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            error={formErrors.name}
            placeholder="Nhập tên tài khoản (vd: my_account)"
            required
          />

          <Input
            label="Email (tùy chọn)"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            error={formErrors.email}
            placeholder="account@example.com"
          />

          <div className="flex justify-end space-x-3 mt-6">
            <Button
              variant="ghost"
              onClick={() => {
                setShowCreateModal(false);
                resetForm();
              }}
            >
              Hủy
            </Button>

            <Button
              variant="primary"
              onClick={handleCreateAccount}
              loading={isLoading}
            >
              Tạo tài khoản
            </Button>
          </div>
        </div>
      </Modal>

      {/* Edit Account Modal */}
      <Modal
        isOpen={showEditModal}
        onClose={() => setShowEditModal(false)}
        title="Chỉnh sửa tài khoản"
        size="md"
      >
        <div className="space-y-4">
          <Input
            label="Tên tài khoản"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            error={formErrors.name}
            placeholder="Nhập tên tài khoản"
            required
          />

          <Input
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            error={formErrors.email}
            placeholder="account@example.com"
          />

          <div className="flex justify-end space-x-3 mt-6">
            <Button
              variant="ghost"
              onClick={() => {
                setShowEditModal(false);
                resetForm();
                setSelectedAccount(null);
              }}
            >
              Hủy
            </Button>

            <Button
              variant="primary"
              onClick={handleUpdateAccount}
              loading={isLoading}
            >
              Cập nhật
            </Button>
          </div>
        </div>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Xác nhận xóa"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-gray-300">
            Bạn có chắc chắn muốn xóa tài khoản "{selectedAccount?.name}"?
          </p>

          <div className="flex justify-end space-x-3">
            <Button
              variant="ghost"
              onClick={() => {
                setShowDeleteModal(false);
                setSelectedAccount(null);
              }}
            >
              Hủy
            </Button>

            <Button
              variant="danger"
              onClick={handleDeleteAccount}
              loading={isLoading}
            >
              Xóa
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
```

#### Afternoon (4 hours)
**Task: Create Session Management Integration**

```typescript
// src/components/features/SessionManager.tsx
import React, { useState, useEffect } from 'react';
import { useCurrentAccount, useAccountActions } from '@/stores/accountStore';
import { useUIActions } from '@/stores/uiStore';
import { Button } from '@/components/ui/Button';
import { Progress } from '@/components/ui/Progress';
import { electronAPI } from '@/types/electron';
import {
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

interface SessionStatus {
  isValid: boolean;
  expiresAt?: string;
  tokenAge?: number;
  lastCheck: string;
}

export const SessionManager: React.FC = () => {
  const currentAccount = useCurrentAccount();
  const { refreshSession } = useAccountActions();
  const { addNotification } = useUIActions();

  const [sessionStatus, setSessionStatus] = useState<SessionStatus | null>(null);
  const [isChecking, setIsChecking] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    if (currentAccount) {
      checkSessionStatus();
    }
  }, [currentAccount]);

  const checkSessionStatus = async () => {
    if (!currentAccount) return;

    setIsChecking(true);

    try {
      const response = await electronAPI.sendCommand({
        id: `check-session-${Date.now()}`,
        type: 'SESSION_CHECK',
        payload: { account_id: currentAccount.id },
        timestamp: Date.now()
      });

      if (response.success) {
        setSessionStatus(response.data);
      } else {
        setSessionStatus({
          isValid: false,
          lastCheck: new Date().toISOString()
        });
      }
    } catch (error) {
      console.error('Failed to check session:', error);
      setSessionStatus({
        isValid: false,
        lastCheck: new Date().toISOString()
      });
    } finally {
      setIsChecking(false);
    }
  };

  const handleRefreshSession = async () => {
    if (!currentAccount) return;

    setIsRefreshing(true);

    try {
      const success = await refreshSession(currentAccount.id);

      if (success) {
        addNotification({
          type: 'success',
          title: 'Session đã được làm mới',
          message: `Session cho "${currentAccount.name}" đã được làm mới thành công`
        });
        await checkSessionStatus();
      } else {
        addNotification({
          type: 'error',
          title: 'Lỗi',
          message: 'Không thể làm mới session. Vui lòng thử lại.'
        });
      }
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Lỗi',
        message: error instanceof Error ? error.message : 'Không thể làm mới session'
      });
    } finally {
      setIsRefreshing(false);
    }
  };

  const getSessionIcon = () => {
    if (!sessionStatus) {
      return <ClockIcon className="w-5 h-5 text-gray-400" />;
    }

    if (sessionStatus.isValid) {
      return <ShieldCheckIcon className="w-5 h-5 text-green-500" />;
    }

    return <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />;
  };

  const getSessionText = () => {
    if (!sessionStatus) {
      return 'Đang kiểm tra...';
    }

    if (sessionStatus.isValid) {
      if (sessionStatus.expiresAt) {
        const expiresAt = new Date(sessionStatus.expiresAt);
        const now = new Date();
        const hoursUntilExpiry = (expiresAt.getTime() - now.getTime()) / (1000 * 60 * 60);

        if (hoursUntilExpiry < 2) {
          return `Sắp hết hạn (${Math.round(hoursUntilExpiry * 60)} phút)`;
        }

        return `Hết hạn: ${expiresAt.toLocaleString('vi-VN')}`;
      }

      return 'Session hợp lệ';
    }

    return 'Session hết hạn';
  };

  const getSessionProgress = () => {
    if (!sessionStatus || !sessionStatus.expiresAt || !sessionStatus.isValid) {
      return 0;
    }

    const now = new Date();
    const expiresAt = new Date(sessionStatus.expiresAt);
    const createdAt = new Date(sessionStatus.lastCheck);

    // Assume 24 hour session lifetime
    const sessionLifetime = 24 * 60 * 60 * 1000; // 24 hours in ms
    const elapsed = now.getTime() - createdAt.getTime();
    const progress = Math.min((elapsed / sessionLifetime) * 100, 100);

    return progress;
  };

  if (!currentAccount) {
    return (
      <div className="session-manager">
        <div className="session-status">
          <ShieldCheckIcon className="w-5 h-5 text-gray-400" />
          <span className="text-gray-400">Chưa chọn tài khoản</span>
        </div>
      </div>
    );
  }

  return (
    <div className="session-manager">
      <div className="session-header">
        <h3>Trạng thái Session</h3>
        <Button
          size="sm"
          variant="ghost"
          icon={<ArrowPathIcon className="w-4 h-4" />}
          onClick={checkSessionStatus}
          loading={isChecking}
          title="Kiểm tra lại session"
        />
      </div>

      <div className="session-status">
        <div className="status-info">
          <div className="status-icon">{getSessionIcon()}</div>
          <div className="status-details">
            <div className="status-text">{getSessionText()}</div>
            <div className="account-info">
              <span className="account-name">{currentAccount.name}</span>
              <span className="account-email">{currentAccount.email}</span>
            </div>
          </div>
        </div>

        {sessionStatus && sessionStatus.isValid && sessionStatus.expiresAt && (
          <div className="session-progress">
            <Progress
              value={getSessionProgress()}
              size="sm"
              variant="success"
            />
          </div>
        )}

        <div className="session-actions">
          {!sessionStatus?.isValid && (
            <Button
              variant="primary"
              size="sm"
              icon={<ArrowPathIcon className="w-4 h-4" />}
              onClick={handleRefreshSession}
              loading={isRefreshing}
            >
              Làm mới Session
            </Button>
          )}

          {sessionStatus?.isValid && (
            <Button
              variant="secondary"
              size="sm"
              icon={<ArrowPathIcon className="w-4 h-4" />}
              onClick={handleRefreshSession}
              loading={isRefreshing}
            >
              Làm mới
            </Button>
          )}
        </div>
      </div>

      <div className="session-tips">
        <h4>Mẹo:</h4>
        <ul>
          <li>Session có hiệu lực trong 24 giờ sau khi login</li>
          <li>Làm mới session khi nhận được lỗi "401 Unauthorized"</li>
          <li>Cần login lại thủ công qua Chrome browser</li>
          <li>Session được lưu trong Chrome profile</li>
        </ul>
      </div>
    </div>
  );
};
```

### Day 2: Song Creation and Queue System

#### Morning (4 hours)
**Task: Create Song Creator Component**

```typescript
// src/components/features/SongCreator.tsx
import React, { useState, useEffect } from 'react';
import { useSongStore, useSongActions, usePrompts, useQueues } from '@/stores/songStore';
import { useCurrentAccount } from '@/stores/accountStore';
import { useUIActions } from '@/stores/uiStore';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Progress } from '@/components/ui/Progress';
import { Modal } from '@/components/ui/Modal';
import { electronAPI } from '@/types/electron';
import {
  DocumentArrowUpIcon,
  PlusIcon,
  PlayIcon,
  PauseIcon,
  TrashIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';

interface QueueFormData {
  account_name: string;
  total_songs: number;
  songs_per_batch: number;
}

export const SongCreator: React.FC = () => {
  const currentAccount = useCurrentAccount();
  const prompts = usePrompts();
  const queues = useQueues();
  const { currentCreation, isCreating, creationProgress } = useCreationProgress();

  const { loadPromptsFromFile, setPrompts, clearPrompts, createQueue, startSelectedQueues } = useSongActions();
  const { addNotification } = useUIActions();

  // UI States
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showCreateQueueModal, setShowCreateQueueModal] = useState(false);
  const [selectedQueues, setSelectedQueues] = useState<Set<string>>(new Set());
  const [selectedFile, setSelectedFile] = useState<string>('');

  // Form States
  const [queueForm, setQueueForm] = useState<QueueFormData>({
    account_name: '',
    total_songs: 0,
    songs_per_batch: 5
  });

  useEffect(() => {
    if (currentAccount) {
      setQueueForm(prev => ({ ...prev, account_name: currentAccount.name }));
    }
  }, [currentAccount]);

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    try {
      const loadedPrompts = await loadPromptsFromFile(selectedFile);
      setPrompts(loadedPrompts);
      setShowUploadModal(false);
      setSelectedFile('');

      addNotification({
        type: 'success',
        title: 'Upload thành công',
        message: `Đã tải ${loadedPrompts.length} prompts từ file`
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Lỗi upload',
        message: error instanceof Error ? error.message : 'Không thể tải file'
      });
    }
  };

  const handleSelectFile = async () => {
    try {
      const filePath = await electronAPI.selectFile([
        { name: 'XML Files', extensions: ['xml'] },
        { name: 'All Files', extensions: ['*'] }
      ]);

      if (filePath) {
        setSelectedFile(filePath);
      }
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Lỗi',
        message: 'Không thể chọn file'
      });
    }
  };

  const handleCreateQueue = async () => {
    try {
      const newQueue = await createQueue({
        account_name: queueForm.account_name,
        total_songs: queueForm.total_songs,
        songs_per_batch: queueForm.songs_per_batch
      });

      setShowCreateQueueModal(false);
      setQueueForm({
        account_name: currentAccount?.name || '',
        total_songs: 0,
        songs_per_batch: 5
      });

      addNotification({
        type: 'success',
        title: 'Tạo queue thành công',
        message: `Queue "${newQueue.id}" đã được tạo`
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Lỗi',
        message: error instanceof Error ? error.message : 'Không thể tạo queue'
      });
    }
  };

  const handleStartQueues = async () => {
    if (selectedQueues.size === 0) {
      addNotification({
        type: 'warning',
        title: 'Cảnh báo',
        message: 'Vui lòng chọn ít nhất một queue để bắt đầu'
      });
      return;
    }

    try {
      await startSelectedQueues(Array.from(selectedQueues));
      setSelectedQueues(new Set());

      addNotification({
        type: 'success',
        title: 'Bắt đầu tạo nhạc',
        message: `Đang thực thi ${selectedQueues.size} queue`
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Lỗi',
        message: error instanceof Error ? error.message : 'Không thể bắt đầu queues'
      });
    }
  };

  const handleToggleQueueSelection = (queueId: string) => {
    setSelectedQueues(prev => {
      const newSet = new Set(prev);
      if (newSet.has(queueId)) {
        newSet.delete(queueId);
      } else {
        newSet.add(queueId);
      }
      return newSet;
    });
  };

  const getQueueIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <ClockIcon className="w-5 h-5 text-yellow-500" />;
      case 'running':
        return <PlayIcon className="w-5 h-5 text-blue-500" />;
      case 'completed':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircleIcon className="w-5 h-5 text-red-500" />;
      default:
        return <ClockIcon className="w-5 h-5 text-gray-500" />;
    }
  };

  const getAvailablePrompts = () => {
    const usedPrompts = queues.reduce((total, queue) => total + queue.total_songs, 0);
    return Math.max(0, prompts.length - usedPrompts);
  };

  const queueColumns = [
    {
      key: 'status' as keyof any,
      label: 'Trạng thái',
      width: '100px',
      align: 'center' as const,
      render: (status: string) => getQueueIcon(status)
    },
    {
      key: 'account_name' as keyof any,
      label: 'Tài khoản',
      render: (value: string) => (
        <div className="flex items-center space-x-2">
          <span>{value}</span>
          {currentAccount?.name === value && (
            <span className="text-xs bg-blue-500 text-white px-2 py-1 rounded">Hiện tại</span>
          )}
        </div>
      )
    },
    {
      key: 'total_songs' as keyof any,
      label: 'Số bài hát',
      render: (value: number, queue: any) => (
        <div>
          <span>{queue.completed_count}/{value}</span>
          <div className="text-xs text-gray-400">
            {queue.songs_per_batch} bài/batch
          </div>
        </div>
      )
    },
    {
      key: 'progress' as keyof any,
      label: 'Tiến độ',
      render: (_: any, queue: any) => {
        const percentage = queue.total_songs > 0
          ? (queue.completed_count / queue.total_songs) * 100
          : 0;

        return (
          <div className="w-24">
            <Progress
              value={percentage}
              size="sm"
              variant={queue.status === 'completed' ? 'success' : 'default'}
            />
          </div>
        );
      }
    },
    {
      key: 'created_at' as keyof any,
      label: 'Ngày tạo',
      render: (value: string) => new Date(value).toLocaleString('vi-VN')
    }
  ];

  return (
    <div className="song-creator">
      <div className="page-header">
        <div className="page-title">
          <h1>Tạo nhạc hàng loạt</h1>
          <p className="text-gray-400">
            Upload XML file và tạo nhiều bài hát với queue system
          </p>
        </div>

        <div className="header-actions">
          <Button
            variant="secondary"
            icon={<DocumentArrowUpIcon className="w-4 h-4" />}
            onClick={() => setShowUploadModal(true)}
          >
            Upload XML
          </Button>

          <Button
            variant="primary"
            icon={<PlusIcon className="w-4 h-4" />}
            onClick={() => setShowCreateQueueModal(true)}
            disabled={prompts.length === 0}
          >
            Tạo Queue
          </Button>
        </div>
      </div>

      {/* Prompts Status */}
      <div className="prompts-status">
        <div className="status-item">
          <span className="status-label">Prompts đã upload:</span>
          <span className="status-value">{prompts.length}</span>
        </div>

        <div className="status-item">
          <span className="status-label">Prompts khả dụng:</span>
          <span className="status-value">{getAvailablePrompts()}</span>
        </div>

        <div className="status-item">
          <span className="status-label">Queues đang chạy:</span>
          <span className="status-value">
            {queues.filter(q => q.status === 'running').length}
          </span>
        </div>

        {prompts.length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={clearPrompts}
          >
            Xóa prompts
          </Button>
        )}
      </div>

      {/* Current Creation Progress */}
      {currentCreation && (
        <div className="creation-progress">
          <h3>Đang tạo nhạc...</h3>

          <div className="progress-info">
            <div className="progress-details">
              <span>{currentCreation.progress.completed_songs}/{currentCreation.progress.total_songs} bài hát</span>
              {currentCreation.current_queue && (
                <span className="text-gray-400">
                  - Queue: {currentCreation.current_queue}
                </span>
              )}
            </div>

            <div className="progress-percentage">
              {Math.round((currentCreation.progress.completed_songs / currentCreation.progress.total_songs) * 100)}%
            </div>
          </div>

          <Progress
            value={currentCreation.progress.completed_songs}
            max={currentCreation.progress.total_songs}
            size="md"
            variant="success"
            animated
          />

          {creationProgress && (
            <div className="current-operation">
              <span className="operation-message">{creationProgress.message}</span>
            </div>
          )}
        </div>
      )}

      {/* Queues Table */}
      <div className="queues-section">
        <div className="section-header">
          <h2>Queue Management</h2>

          {queues.length > 0 && selectedQueues.size > 0 && (
            <Button
              variant="primary"
              icon={<PlayIcon className="w-4 h-4" />}
              onClick={handleStartQueues}
              disabled={isCreating}
              loading={isCreating}
            >
              Bắt đầu ({selectedQueues.size} queues)
            </Button>
          )}
        </div>

        <Table
          data={queues}
          columns={queueColumns}
          selectable
          selectedRows={selectedQueues}
          onRowSelect={handleToggleQueueSelection}
          emptyMessage="Chưa có queue nào. Hãy upload XML file và tạo queue đầu tiên!"
          hoverable
        />
      </div>

      {/* Upload XML Modal */}
      <Modal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        title="Upload XML File"
        size="md"
      >
        <div className="space-y-4">
          <div className="file-upload-area">
            <input
              type="file"
              accept=".xml"
              onChange={(e) => setSelectedFile(e.target.files?.[0]?.name || '')}
              className="hidden"
              id="xml-file-input"
            />

            <label
              htmlFor="xml-file-input"
              className="file-upload-label"
              onClick={handleSelectFile}
            >
              <DocumentArrowUpIcon className="w-12 h-12 text-gray-400 mb-2" />
              <p className="text-gray-300">
                {selectedFile || 'Chọn file XML để upload'}
              </p>
              <p className="text-sm text-gray-500">
                Hỗ trợ định dạng .xml với cấu trúc TITLE, LYRICS, STYLE
              </p>
            </label>
          </div>

          <div className="flex justify-end space-x-3">
            <Button
              variant="ghost"
              onClick={() => {
                setShowUploadModal(false);
                setSelectedFile('');
              }}
            >
              Hủy
            </Button>

            <Button
              variant="primary"
              onClick={handleFileUpload}
              disabled={!selectedFile}
            >
              Upload
            </Button>
          </div>
        </div>
      </Modal>

      {/* Create Queue Modal */}
      <Modal
        isOpen={showCreateQueueModal}
        onClose={() => setShowCreateQueueModal(false)}
        title="Tạo Queue Mới"
        size="md"
      >
        <div className="space-y-4">
          <div className="form-info">
            <p className="text-sm text-gray-300">
              Prompts khả dụng: <span className="font-semibold text-blue-400">{getAvailablePrompts()}</span>
            </p>
          </div>

          <Input
            label="Tài khoản"
            value={queueForm.account_name}
            onChange={(e) => setQueueForm({ ...queueForm, account_name: e.target.value })}
            placeholder="Tên tài khoản"
            disabled
          />

          <Input
            label="Số bài hát"
            type="number"
            value={queueForm.total_songs}
            onChange={(e) => setQueueForm({ ...queueForm, total_songs: parseInt(e.target.value) || 0 })}
            placeholder="Số bài hát muốn tạo"
            min={1}
            max={getAvailablePrompts()}
            required
          />

          <Input
            label="Số bài mỗi batch"
            type="number"
            value={queueForm.songs_per_batch}
            onChange={(e) => setQueueForm({ ...queueForm, songs_per_batch: parseInt(e.target.value) || 5 })}
            placeholder="Số bài hát mỗi batch (1-10)"
            min={1}
            max={10}
            required
          />

          <div className="form-tips">
            <h4>Lưu ý:</h4>
            <ul>
              <li>Batch size ảnh hưởng đến CAPTCHA rate</li>
              <li>Khuyến nghị: 1-3 bài/batch để tránh CAPTCHA</li>
              <li>Mỗi batch sẽ mở 1 tab Chrome riêng biệt</li>
            </ul>
          </div>

          <div className="flex justify-end space-x-3">
            <Button
              variant="ghost"
              onClick={() => setShowCreateQueueModal(false)}
            >
              Hủy
            </Button>

            <Button
              variant="primary"
              onClick={handleCreateQueue}
              disabled={queueForm.total_songs === 0 || queueForm.total_songs > getAvailablePrompts()}
            >
              Tạo Queue
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
```

#### Afternoon (4 hours)
**Task: Create Quick Song Creator Component**

```typescript
// src/components/features/QuickCreator.tsx
import React, { useState } from 'react';
import { useCurrentAccount } from '@/stores/accountStore';
import { useUIActions } from '@/stores/uiStore';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { electronAPI } from '@/types/electron';

interface QuickCreateData {
  title: string;
  lyrics: string;
  style: string;
  persona_name?: string;
  advanced_options: {
    weirdness: number;
    creativity: number;
    clarity: number;
    model: 'v4' | 'v3.5' | 'v3';
    vocal_gender: 'auto' | 'male' | 'female';
    lyrics_mode: 'auto' | 'manual';
    style_influence: number;
  };
}

export const QuickCreator: React.FC = () => {
  const currentAccount = useCurrentAccount();
  const { addNotification } = useUIActions();

  const [formData, setFormData] = useState<QuickCreateData>({
    title: '',
    lyrics: '',
    style: '',
    advanced_options: {
      weirdness: 0,
      creativity: 50,
      clarity: 80,
      model: 'v4',
      vocal_gender: 'auto',
      lyrics_mode: 'auto',
      style_influence: 50
    }
  });

  const [isCreating, setIsCreating] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = async () => {
    if (!currentAccount) {
      addNotification({
        type: 'warning',
        title: 'Chưa chọn tài khoản',
        message: 'Vui lòng chọn tài khoản trước khi tạo nhạc'
      });
      return;
    }

    if (!formData.title.trim() || !formData.lyrics.trim() || !formData.style.trim()) {
      addNotification({
        type: 'warning',
        title: 'Thiếu thông tin',
        message: 'Vui lòng điền đầy đủ title, lyrics và style'
      });
      return;
    }

    setIsCreating(true);

    try {
      const response = await electronAPI.sendCommand({
        id: `quick-create-${Date.now()}`,
        type: 'SONG_CREATE_SINGLE',
        payload: {
          account_name: currentAccount.name,
          song_data: formData
        },
        timestamp: Date.now()
      });

      if (response.success) {
        addNotification({
          type: 'success',
          title: 'Tạo bài hát thành công',
          message: `Bài hát "${formData.title}" đã được tạo`
        });

        // Reset form
        setFormData({
          title: '',
          lyrics: '',
          style: '',
          advanced_options: {
            weirdness: 0,
            creativity: 50,
            clarity: 80,
            model: 'v4',
            vocal_gender: 'auto',
            lyrics_mode: 'auto',
            style_influence: 50
          }
        });
      } else {
        throw new Error(response.error || 'Không thể tạo bài hát');
      }
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Lỗi',
        message: error instanceof Error ? error.message : 'Không thể tạo bài hát'
      });
    } finally {
      setIsCreating(false);
    }
  };

  if (!currentAccount) {
    return (
      <div className="quick-creator">
        <div className="no-account-message">
          <p>Vui lòng chọn tài khoản để tạo nhạc</p>
        </div>
      </div>
    );
  }

  return (
    <div className="quick-creator">
      <div className="page-header">
        <div className="page-title">
          <h1>Tạo nhạc nhanh</h1>
          <p className="text-gray-400">
            Tạo bài hát đơn lẻ với đầy đủ tùy chọn
          </p>
        </div>
      </div>

      <div className="quick-create-form">
        <div className="form-section">
          <h3>Thông tin cơ bản</h3>

          <Input
            label="Tiêu đề bài hát"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="Nhập tiêu đề bài hát"
            required
          />

          <div className="form-group">
            <label>Lời bài hát</label>
            <textarea
              value={formData.lyrics}
              onChange={(e) => setFormData({ ...formData, lyrics: e.target.value })}
              placeholder="Nhập lời bài hát"
              rows={8}
              className="textarea-input"
              required
            />
          </div>

          <Input
            label="Style/Nhạc"
            value={formData.style}
            onChange={(e) => setFormData({ ...formData, style: e.target.value })}
            placeholder="Ví dụ: Pop, upbeat, 120bpm, electronic"
            required
          />
        </div>

        <div className="form-section">
          <div className="section-header">
            <h3>Tùy chọn nâng cao</h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowAdvanced(!showAdvanced)}
            >
              {showAdvanced ? 'Ẩn' : 'Hiện'}
            </Button>
          </div>

          {showAdvanced && (
            <div className="advanced-options">
              <div className="options-grid">
                <div className="option-group">
                  <label>Weirdness (0-100)</label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={formData.advanced_options.weirdness}
                    onChange={(e) => setFormData({
                      ...formData,
                      advanced_options: {
                        ...formData.advanced_options,
                        weirdness: parseInt(e.target.value)
                      }
                    })}
                  />
                  <span>{formData.advanced_options.weirdness}</span>
                </div>

                <div className="option-group">
                  <label>Creativity (0-100)</label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={formData.advanced_options.creativity}
                    onChange={(e) => setFormData({
                      ...formData,
                      advanced_options: {
                        ...formData.advanced_options,
                        creativity: parseInt(e.target.value)
                      }
                    })}
                  />
                  <span>{formData.advanced_options.creativity}</span>
                </div>

                <div className="option-group">
                  <label>Clarity (0-100)</label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={formData.advanced_options.clarity}
                    onChange={(e) => setFormData({
                      ...formData,
                      advanced_options: {
                        ...formData.advanced_options,
                        clarity: parseInt(e.target.value)
                      }
                    })}
                  />
                  <span>{formData.advanced_options.clarity}</span>
                </div>

                <div className="option-group">
                  <label>Style Influence (0-100)</label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={formData.advanced_options.style_influence}
                    onChange={(e) => setFormData({
                      ...formData,
                      advanced_options: {
                        ...formData.advanced_options,
                        style_influence: parseInt(e.target.value)
                      }
                    })}
                  />
                  <span>{formData.advanced_options.style_influence}</span>
                </div>

                <div className="option-group">
                  <label>Model</label>
                  <select
                    value={formData.advanced_options.model}
                    onChange={(e) => setFormData({
                      ...formData,
                      advanced_options: {
                        ...formData.advanced_options,
                        model: e.target.value as 'v4' | 'v3.5' | 'v3'
                      }
                    })}
                  >
                    <option value="v4">v4 (Mới nhất)</option>
                    <option value="v3.5">v3.5</option>
                    <option value="v3">v3</option>
                  </select>
                </div>

                <div className="option-group">
                  <label>Vocal Gender</label>
                  <select
                    value={formData.advanced_options.vocal_gender}
                    onChange={(e) => setFormData({
                      ...formData,
                      advanced_options: {
                        ...formData.advanced_options,
                        vocal_gender: e.target.value as 'auto' | 'male' | 'female'
                      }
                    })}
                  >
                    <option value="auto">Auto</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                  </select>
                </div>

                <div className="option-group">
                  <label>Lyrics Mode</label>
                  <select
                    value={formData.advanced_options.lyrics_mode}
                    onChange={(e) => setFormData({
                      ...formData,
                      advanced_options: {
                        ...formData.advanced_options,
                        lyrics_mode: e.target.value as 'auto' | 'manual'
                      }
                    })}
                  >
                    <option value="auto">Auto</option>
                    <option value="manual">Manual</option>
                  </select>
                </div>

                <div className="option-group">
                  <label>Persona Name (tùy chọn)</label>
                  <input
                    type="text"
                    value={formData.persona_name || ''}
                    onChange={(e) => setFormData({ ...formData, persona_name: e.target.value })}
                    placeholder="Nhập persona name"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="form-actions">
          <Button
            variant="primary"
            size="lg"
            onClick={handleSubmit}
            loading={isCreating}
            disabled={!currentAccount}
          >
            Tạo bài hát
          </Button>
        </div>

        <div className="form-tips">
          <h4>Mẹo:</h4>
          <ul>
            <li>Để tránh CAPTCHA, hãy giữ Weirdness thấp (0-30)</li>
            <li>Creativity cao hơn sẽ tạo ra nhạc sáng tạo hơn</li>
            <li>Clarity cao hơn giúp lời rõ hơn</li>
            <li>Style ảnh hưởng đến thể loại nhạc</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
```

### Day 3-5: Remaining Features

*(Continue implementing DownloadManager, HistoryView, SettingsView components with full backend integration)*

## Testing Strategy

```typescript
// tests/integration/account-management.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AccountManager } from '@/components/features/AccountManager';
import { useAccountStore } from '@/stores/accountStore';

// Mock electronAPI
vi.mock('@/types/electron', () => ({
  electronAPI: {
    sendCommand: vi.fn(),
    selectDirectory: vi.fn(),
    onBackendReady: vi.fn(),
    onProgressUpdate: vi.fn(),
    onErrorUpdate: vi.fn()
  }
}));

describe('AccountManager Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('loads accounts on mount', async () => {
    render(<AccountManager />);

    await waitFor(() => {
      expect(electronAPI.sendCommand).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'ACCOUNT_LIST'
        })
      );
    });
  });

  it('creates new account successfully', async () => {
    render(<AccountManager />);

    // Open create modal
    fireEvent.click(screen.getByText('Thêm tài khoản'));

    // Fill form
    fireEvent.change(screen.getByLabelText('Tên tài khoản'), {
      target: { value: 'test-account' }
    });
    fireEvent.change(screen.getByLabelText('Email (tùy chọn)'), {
      target: { value: 'test@example.com' }
    });

    // Submit
    fireEvent.click(screen.getByText('Tạo tài khoản'));

    await waitFor(() => {
      expect(electronAPI.sendCommand).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'ACCOUNT_CREATE',
          payload: {
            name: 'test-account',
            email: 'test@example.com'
          }
        })
      );
    });
  });
});
```

## Success Criteria

### Functional Requirements
- ✅ All account management operations work correctly
- ✅ Song creation with queue system functional
- ✅ Real-time progress updates display correctly
- ✅ Download management works with batch operations
- ✅ History views show accurate data

### Performance Requirements
- ✅ UI updates under 100ms for user actions
- ✅ Progress updates in real-time (<500ms delay)
- ✅ Memory usage under 100MB during normal operation
- ✅ No UI freezing during long operations

### User Experience Requirements
- ✅ Intuitive interface matching Python version functionality
- ✅ Error handling with clear user feedback
- ✅ Loading states for all async operations
- ✅ Responsive design for different window sizes

---

*This phase completes the core functionality migration from Python to React, ensuring all existing features work correctly with modern UI patterns and real-time updates.*