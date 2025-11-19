# Component Mapping: CustomTkinter to React

## Overview

Document detailing the mapping from CustomTkinter components to React + TypeScript equivalents, ensuring 100% feature parity during migration.

## Tab Structure Mapping

### 1. Account Panel (`src/ui/account_panel.py` → `AccountPanel.tsx`)

#### CustomTkinter Components → React Equivalents

| CustomTkinter Component | React Equivalent | Props/Configuration | Notes |
|------------------------|-----------------|-------------------|-------|
| `ctk.CTkFrame` | `div` with Tailwind classes | `className="bg-gray-800 rounded-lg p-4"` | Main container |
| `ctk.CTkButton` | `Button` component | `{ variant, size, disabled, onClick }` | Consistent styling |
| `ctk.CTkEntry` | `Input` component | `{ value, onChange, placeholder, disabled }` | Form validation |
| `ctk.CTkLabel` | `Typography` component | `{ variant, children }` | Text display |
| `ctk.CTkScrollableFrame` | `div` with `overflow-y-auto` | Custom scrollbar styling | Account list scrollable |
| `ctk.CTkCheckBox` | Checkbox component | `{ checked, onChange, label }` | Queue selection |
| `ctk.CTkOptionMenu` | Select component | `{ value, onChange, options }` | Dropdown selections |

#### Functionality Mapping

```typescript
// CustomTkinter: Add Account Button
add_btn = ctk.CTkButton(
    self,
    text="➕ Thêm tài khoản",
    command=self.add_account_clicked,
    width=150
)

// React Equivalent
<Button
  onClick={handleCreateAccount}
  className="flex items-center gap-2"
  disabled={isLoading}
>
  <PlusIcon className="h-5 w-5" />
  Add Account
</Button>
```

### 2. Multiple Songs Panel (`src/ui/multiple_songs_panel.py` → `MultipleSongsPanel.tsx`)

#### Complex Component Mapping

| CustomTkinter | React | Implementation Details |
|---------------|-------|------------------------|
| XML Upload Frame | FileUpload component | Drag & drop support, progress indicator |
| Queue List | VirtualList component | Efficient rendering for large queues |
| Progress Bars | ProgressBar component | Animated, real-time updates |
| 2-Column Layout | Grid layout | Responsive CSS Grid |
| Advanced Options | CollapsiblePanel | Animated accordion |

```typescript
// CustomTkinter XML Upload
xml_frame = ctk.CTkFrame(self)
xml_label = ctk.CTkLabel(xml_frame, text="Chọn file XML:")
xml_file_entry = ctk.CTkEntry(xml_frame)
browse_btn = ctk.CTkButton(xml_frame, text="📁 Browse", command=self.browse_xml_file)

// React Equivalent
<FileUpload
  accept=".xml"
  onFileSelect={handleXMLUpload}
  isLoading={isLoading}
  disabled={isProcessing}
>
  <div className="border-2 border-dashed border-gray-600 rounded-lg p-6 text-center">
    <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
    <p className="mt-2 text-sm text-gray-400">
      {isLoading ? 'Loading...' : 'Drop XML file here or click to browse'}
    </p>
  </div>
</FileUpload>
```

### 3. Download Panel (`src/ui/download_panel.py` → `DownloadPanel.tsx`)

#### State Management Mapping

```python
# CustomTkinter State
class DownloadPanel(ctk.CTkFrame):
    def __init__(self, parent, download_manager, session_manager):
        self.download_manager = download_manager
        self.session_manager = session_manager
        self.is_downloading = False
        self.progress_var = ctk.IntVar(value=0)
```

```typescript
// React Zustand Store
interface DownloadStore {
  // State
  isDownloading: boolean;
  progress: number;
  selectedAccount: string | null;
  downloadSettings: DownloadSettings;

  // Actions
  startDownload: (settings: DownloadSettings) => Promise<void>;
  stopDownload: () => void;
  updateProgress: (progress: number) => void;
  selectAccount: (account: string) => void;
}

export const useDownloadStore = create<DownloadStore>((set, get) => ({
  isDownloading: false,
  progress: 0,
  selectedAccount: null,
  downloadSettings: {
    limit: 10,
    outputDir: '',
    withThumbnails: true,
    appendUuid: false,
    useCreatePage: false
  },

  startDownload: async (settings) => {
    set({ isDownloading: true, progress: 0, downloadSettings: settings });
    try {
      await window.electronAPI.download.start(settings);
    } catch (error) {
      set({ isDownloading: false });
      throw error;
    }
  },

  updateProgress: (progress) => set({ progress }),
  // ... other actions
}));
```

## Event Handling Mapping

### CustomTkinter → React Event Patterns

#### Button Click Events

```python
# CustomTkinter
def create_button_clicked(self):
    # Handle button click
    pass

create_btn = ctk.CTkButton(
    self,
    text="Create",
    command=self.create_button_clicked
)
```

```typescript
// React Equivalent
const handleCreateButton = useCallback(async () => {
  try {
    setIsLoading(true);
    await window.electronAPI.song.createSingle(formData);
    toast.success('Song created successfully');
  } catch (error) {
    toast.error(error.message);
  } finally {
    setIsLoading(false);
  }
}, [formData]);

<Button
  onClick={handleCreateButton}
  disabled={isLoading}
>
  {isLoading ? 'Creating...' : 'Create'}
</Button>
```

#### Form Input Events

```python
# CustomTkinter
def on_entry_change(self, value):
    self.text_value = value

entry = ctk.CTkEntry(
    self,
    command=self.on_entry_change
)
```

```typescript
// React with controlled inputs
const [formData, setFormData] = useState({
  accountName: '',
  email: ''
});

const handleInputChange = useCallback((field: string, value: string) => {
  setFormData(prev => ({ ...prev, [field]: value }));
}, []);

<Input
  value={formData.accountName}
  onChange={(e) => handleInputChange('accountName', e.target.value)}
  placeholder="Enter account name"
/>
```

## Progress Callback Mapping

### CustomTkinter Progress Updates → React State Management

```python
# CustomTkinter Progress
def update_progress_callback(self, current, total, message=""):
    progress = (current / total) * 100
    self.progress_var.set(int(progress))
    self.status_label.configure(text=message)
```

```typescript
// React Progress with Zustand + useEffect
const ProgressTracker = ({ operationId }: { operationId: string }) => {
  const { progress, status } = useProgressStore();
  const [localProgress, setLocalProgress] = useState(0);

  useEffect(() => {
    const handleProgressEvent = (event: ProgressEvent) => {
      if (event.operation_id === operationId) {
        setLocalProgress(event.progress);
        // Update global store if needed
        useProgressStore.getState().updateProgress(event.progress);
      }
    };

    window.electronAPI.onProgressEvent(handleProgressEvent);

    return () => {
      window.electronAPI.removeAllListeners('progress-event');
    };
  }, [operationId]);

  return (
    <div className="w-full">
      <div className="flex justify-between text-sm text-gray-400 mb-2">
        <span>{status}</span>
        <span>{localProgress}%</span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-2">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${localProgress}%` }}
        />
      </div>
    </div>
  );
};
```

## Layout System Migration

### CustomTkinter Grid → CSS Grid/Flexbox

```python
# CustomTkinter Grid Layout
self.grid_columnconfigure(0, weight=1)
self.grid_columnconfigure(1, weight=2)
self.grid_rowconfigure(0, weight=1)

left_frame = ctk.CTkFrame(self)
left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

right_frame = ctk.CTkFrame(self)
right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
```

```typescript
// React CSS Grid
<div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
  {/* Left Panel - 1 column */}
  <div className="lg:col-span-1 space-y-4">
    <div className="bg-gray-800 rounded-lg p-4">
      {/* Account selection */}
    </div>
    <div className="bg-gray-800 rounded-lg p-4">
      {/* Queue configuration */}
    </div>
  </div>

  {/* Right Panel - 2 columns */}
  <div className="lg:col-span-2">
    <div className="bg-gray-800 rounded-lg p-4 h-full">
      {/* Queue list and progress */}
    </div>
  </div>
</div>
```

## Styling Migration

### CustomTkinter Themes → Tailwind CSS Classes

| CustomTkinter Theme | Tailwind Classes | Color Mapping |
|---------------------|------------------|---------------|
| `dark-blue` | `bg-gray-900 text-white` | Main background |
| Frame background | `bg-gray-800` | Card backgrounds |
| Button primary | `bg-blue-600 hover:bg-blue-700` | Primary actions |
| Button secondary | `bg-gray-700 hover:bg-gray-600` | Secondary actions |
| Success state | `text-green-400 bg-green-900/20` | Success indicators |
| Error state | `text-red-400 bg-red-900/20` | Error indicators |
| Warning state | `text-yellow-400 bg-yellow-900/20` | Warning indicators |

```css
/* Custom components with consistent styling */
.btn-primary {
  @apply bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg
         transition-colors duration-200 font-medium disabled:opacity-50
         disabled:cursor-not-allowed;
}

.btn-secondary {
  @apply bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg
         transition-colors duration-200 font-medium border border-gray-600;
}

.input-field {
  @apply bg-gray-700 text-white px-3 py-2 rounded-lg border border-gray-600
         focus:border-blue-500 focus:ring-1 focus:ring-blue-500
         transition-colors duration-200;
}

.panel {
  @apply bg-gray-800 rounded-lg p-6 border border-gray-700;
}
```

## Animation Migration

### CustomTkinter Limited Animations → React CSS Animations

```typescript
// Loading Spinner Component
const LoadingSpinner = ({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8'
  };

  return (
    <div className={`animate-spin ${sizeClasses[size]} border-2 border-gray-600 border-t-blue-500 rounded-full`} />
  );
};

// Fade-in Animation for Components
const FadeIn = ({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) => (
  <div
    className="animate-fade-in"
    style={{ animationDelay: `${delay}ms` }}
  >
    {children}
  </div>
);

// CSS Animations (tailwind.config.js)
module.exports = {
  theme: {
    extend: {
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        }
      }
    }
  }
};
```

## Testing Strategy Mapping

### CustomTkinter Manual Testing → React Automated Testing

```typescript
// Component Unit Tests
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AccountPanel } from '../AccountPanel';
import { useAccountStore } from '../stores/accountStore';

// Mock Electron API
const mockElectronAPI = {
  account: {
    getAll: jest.fn(),
    create: jest.fn(),
    delete: jest.fn(),
    rename: jest.fn(),
    getSession: jest.fn()
  }
};

Object.defineProperty(window, 'electronAPI', {
  value: mockElectronAPI,
  writable: true
});

describe('AccountPanel', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset store state
    useAccountStore.setState({
      accounts: [],
      selectedAccount: null,
      isLoading: false,
      error: null
    });
  });

  it('should display empty state when no accounts exist', async () => {
    mockElectronAPI.account.getAll.mockResolvedValue([]);

    render(<AccountPanel />);

    await waitFor(() => {
      expect(screen.getByText('No accounts found')).toBeInTheDocument();
    });
  });

  it('should create new account successfully', async () => {
    mockElectronAPI.account.getAll.mockResolvedValue([]);
    mockElectronAPI.account.create.mockResolvedValue({ account_created: true });

    render(<AccountPanel />);

    // Click add account button
    fireEvent.click(screen.getByText('Add Account'));

    // Fill form
    fireEvent.change(screen.getByPlaceholderText('e.g., my_main_account'), {
      target: { value: 'test_account' }
    });

    // Submit form
    fireEvent.click(screen.getByText('Create Account'));

    await waitFor(() => {
      expect(mockElectronAPI.account.create).toHaveBeenCalledWith('test_account', undefined);
    });
  });
});
```

## Migration Checklist

### Phase 1: Core Components
- [ ] Button component with all variants
- [ ] Input component with validation
- [ ] Select component for dropdowns
- [ ] Modal component for dialogs
- [ ] ProgressBar component for status
- [ ] Layout components (Header, Sidebar, Content)

### Phase 2: Panel Components
- [ ] AccountPanel with full CRUD operations
- [ ] CreateMusicPanel for single song creation
- [ ] MultipleSongsPanel with queue system
- [ ] DownloadPanel with configuration
- [ ] HistoryPanel for download history
- [ ] SongCreationHistoryPanel

### Phase 3: Advanced Features
- [ ] Real-time progress tracking
- [ ] File upload with drag & drop
- [ ] Toast notifications
- [ ] Error boundaries
- [ ] Keyboard shortcuts
- [ ] Responsive design

### Phase 4: Integration
- [ ] State management integration
- [ ] IPC communication testing
- [ ] Performance optimization
- [ ] Accessibility compliance
- [ ] Cross-browser compatibility

This mapping ensures that every CustomTkinter component and functionality has a direct, equivalent React implementation, maintaining 100% feature parity while improving the user experience and developer productivity.