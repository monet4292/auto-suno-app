🔄 Detailed Workflow Descriptions
1. Song Creation Workflow
1.1 Single Song Creation (CreateMusicPanel)
User Action: Click "Tạo nhạc" tab
├── UI Displays: Form with fields
│   ├── Title input
│   ├── Lyrics textarea
│   ├── Style input
│   └── Advanced Options (collapsible)
│       ├── Weirdness slider (0-100)
│       ├── Creativity slider (0-100)
│       ├── Clarity slider (0-100)
│       ├── Model dropdown (v4, v3.5, v3)
│       ├── Vocal Gender dropdown (Auto, Male, Female)
│       ├── Lyrics Mode dropdown (Auto, Manual)
│       └── Style Influence slider (0-100)
│
User Action: Fill form and click "Tạo bài hát"
├── Backend Process:
│   ├── 1. Validate input fields
│   │   ├── Check title not empty
│   │   ├── Check lyrics length (50-2000 chars)
│   │   └── Check style not empty
│   │
│   ├── 2. Get selected account from dropdown
│   │   └── Validate account exists
│   │
│   ├── 3. Launch Chrome with account profile
│   │   ├── SessionManager.get_session_token_from_create_page()
│   │   ├── Create Chrome options with profile path
│   │   ├── Apply stealth techniques
│   │   └── Launch browser to suno.com/create
│   │
│   ├── 4. Wait for user login (if needed)
│   │   └── Monitor for session token
│   │
│   ├── 5. Fill song creation form
│   │   ├── Find title input field
│   │   ├── Find lyrics textarea
│   │   ├── Find style input
│   │   └── Set values from user input
│   │
│   ├── 6. Apply advanced options
│   │   ├── Set weirdness value
│   │   ├── Set creativity value
│   │   ├── Set clarity value
│   │   ├── Set model selection
│   │   ├── Set vocal gender
│   │   ├── Set lyrics mode
│   │   └── Set style influence
│   │
│   ├── 7. Human-like delays (3-5 seconds)
│   │   └── Random delay between actions
│   │
│   └── 8. Submit form
│       ├── Find create button
│       ├── Click submit
│       └── Wait for completion
│
└── UI Updates:
    ├── Show progress indicator
    ├── Display success/error message
    └── Update song creation history

1.2 Batch Song Creation (MultipleSongsPanel)
User Action: Click "Tạo nhiều bài" tab
├── UI Displays: Two-column layout
│   ├── Left Column: Settings
│   │   ├── Account selection dropdown
│   │   ├── XML file upload button
│   │   ├── Songs per batch slider (1-10)
│   │   ├── Queue management section
│   │   │   ├── Create queue button
│   │   │   ├── Queue list with checkboxes
│   │   │   └── Execute selected button
│   │   └── Advanced options (same as single)
│   │
│   └── Right Column: Results
│       ├── XML preview table
│       ├── Queue status display
│       └── Progress bars per queue
│
User Action: Upload XML file
├── Backend Process:
│   ├── 1. Parse XML file
│   │   ├── PromptParser.parse_xml_file()
│   │   ├── Extract TITLE, LYRICS, STYLE tags
│   │   ├── Validate XML structure
│   │   └── Create SunoPrompt objects
│   │
│   ├── 2. Display preview
│   │   └── Show parsed prompts in table
│   │
│   └── 3. Validate prompt count
│       └── Check against available prompts
│
User Action: Create queue
├── Backend Process:
│   ├── 1. QueueManager.add_queue_entry()
│   │   ├── Validate account selection
│   │   ├── Validate prompt range
│   │   ├── Create QueueEntry object
│   │   └── Save to queue_state.json
│   │
│   └── 2. Update UI
│       └── Refresh queue list
│
User Action: Execute selected queues
├── Backend Process:
│   ├── 1. BatchSongCreator.create_from_xml_file()
│   │   ├── Load prompts from XML
│   │   ├── Get selected queues
│   │   └── Initialize progress tracking
│   │
│   ├── 2. For each queue:
│   │   ├── Launch Chrome with account profile
│   │   ├── Open multiple tabs (songs_per_batch)
│   │   ├── For each tab:
│   │   │   ├── Navigate to suno.com/create
│   │   │   ├── Fill form with prompt data
│   │   │   ├── Apply advanced options
│   │   │   ├── Human delay (3-5s)
│   │   │   └── Submit form
│   │   │
│   │   ├── Wait for all tabs to complete
│   │   ├── Close tabs
│   │   └── Update queue progress
│   │
│   └── 3. Save results
│       ├── SongCreationHistoryManager.record_results()
│       └── Update queue status
│
└── UI Updates:
    ├── Real-time progress bars
    ├── Status messages per queue
    ├── Success/failure indicators
    └── History table updates

2. Download Workflow
2.1 Download Initiation (DownloadPanel)
User Action: Click "Download" tab
├── UI Displays: Download configuration
│   ├── Account selection dropdown
│   ├── Source selection:
│   │   ├── Radio button: "/me" (personal library)
│   │   └── Radio button: "Profile" (specific user)
│   ├── Profile input (if Profile selected)
│   ├── Batch size input (1-50)
│   ├── Output directory selector
│   └── Download button
│
User Action: Select account and source
├── Backend Process:
│   ├── 1. Validate account selection
│   │   └── Check account exists in AccountManager
│   │
│   ├── 2. Get session token
│   │   ├── SessionManager.get_session_token_from_create_page()
│   │   ├── Launch Chrome with account profile
│   │   ├── Navigate to suno.com
│   │   └── Extract __session cookie
│   │
│   └── 3. Update API client
│       └── SunoApiClient.update_session_token()
│
User Action: Click "Download" button
├── Backend Process:
│   ├── 1. DownloadManager.batch_download_paginated()
│   │   ├── Initialize progress tracking
│   │   ├── Load download history
│   │   └── Start pagination loop
│   │
│   ├── 2. For each page:
│   │   ├── SunoApiClient.fetch_clips_page()
│   │   │   ├── Make API request with session token
│   │   │   ├── Parse response JSON
│   │   │   ├── Extract SongClip objects
│   │   │   └── Check for more pages
│   │   │
│   │   ├── For each clip:
│   │   │   ├── Check if already downloaded
│   │   │   │   └── DownloadHistory.is_downloaded()
│   │   │   │
│   │   │   ├── If not downloaded:
│   │   │   │   ├── FileDownloader.download_mp3_file()
│   │   │   │   │   ├── Download audio file
│   │   │   │   ├── Download image file
│   │   │   │   └── Show progress
│   │   │   │
│   │   │   ├── MetadataHandler.embed_id3_tags()
│   │   │   │   ├── Add title, artist, album
│   │   │   │   ├── Embed artwork
│   │   │   │   └── Add custom metadata
│   │   │   │
│   │   │   └── DownloadHistory.add_download()
│   │   │       └── Record download with timestamp
│   │   │
│   │   └── Update progress callback
│   │       └── UI progress bar update
│   │
│   └── 3. Save history
│       └── DownloadManager.save_histories()
│
└── UI Updates:
    ├── Overall progress bar
    ├── Current file download status
    ├── Success/failure count
    └── Download history table

3. Account Management Workflow
3.1 Account Creation (AccountPanel)
User Action: Click "Tài khoản" tab
├── UI Displays: Account management interface
│   ├── Add account button
│   ├── Refresh button
│   └── Account list with cards
│       └── For each account:
│           ├── Account name
│           ├── Email
│           ├── Status (active/inactive)
│           ├── Last used timestamp
│           ├── Get session token button
│           ├── Rename button
│           └── Delete button
│
User Action: Click "Thêm tài khoản" button
├── UI Shows: Add account dialog
│   ├── Name input field
│   ├── Email input field
│   ├── Save button
│   └── Cancel button
│
User Action: Fill form and click "Save"
├── Backend Process:
│   ├── 1. AccountManager.add_account()
│   │   ├── Validate name not empty
│   │   ├── Validate email format
│   │   ├── Check for duplicate names
│   │   └── Create Account object
│   │
│   ├── 2. Create Chrome profile
│   │   ├── SessionManager.create_profile_directory()
│   │   ├── Create profile folder structure
│   │   └── Initialize Chrome profile
│   │
│   ├── 3. Save account data
│   │   └── AccountManager.save_accounts()
│   │       └── Write to suno_accounts.json
│   │
│   └── 4. Update UI
│       └── Refresh account list
│
User Action: Click "Get session token" button
├── Backend Process:
│   ├── 1. SessionManager.get_session_token_from_create_page()
│   │   ├── Launch Chrome with account profile
│   │   ├── Navigate to suno.com/create
│   │   ├── Wait for user login
│   │   └── Extract session token
│   │
│   └── 2. Update account
│       └── AccountManager.update_last_used()
│
└── UI Updates:
    ├── Show success/error message
    ├── Update account status
    └── Refresh account list

4. History Management Workflow
4.1 Download History (HistoryPanel)
User Action: Click "Lịch sử Download" tab
├── UI Displays: Download history interface
│   ├── Account selection dropdown
│   ├── Statistics cards:
│   │   ├── Total songs downloaded
│   │   ├── Total size downloaded
│   │   └── Last download timestamp
│   ├── History table with columns:
│   │   ├── Song title
│   │   ├── Account name
│   │   ├── Download date
│   │   ├── File size
│   │   └── Actions (play, delete)
│   └── Clear history button
│
User Action: Select account from dropdown
├── Backend Process:
│   ├── 1. DownloadManager.get_history()
│   │   └── Load history for selected account
│   │
│   └── 2. Calculate statistics
│       ├── Count total downloads
│       ├── Sum file sizes
│       └── Find last download date
│
└── UI Updates:
    ├── Update statistics cards
    └── Populate history table

4.2 Song Creation History (SongCreationHistoryPanel)
User Action: Click "Lịch sử Tạo bài hát" tab
├── UI Displays: Song creation history interface
│   ├── Account selection dropdown
│   ├── Search input field
│   ├── Filter options:
│   │   ├── Date range picker
│   │   ├── Status filter (success/failed)
│   │   └── Style filter
│   ├── History table with columns:
│   │   ├── Song title
│   │   ├── Account name
│   │   ├── Creation date
│   │   ├── Status
│   │   ├── Error message (if failed)
│   │   └── Actions (retry, view details)
│   └── Export to CSV button
│
User Action: Apply filters or search
├── Backend Process:
│   ├── 1. SongCreationHistoryManager.get_filtered_history()
│   │   ├── Apply account filter
│   │   ├── Apply search filter
│   │   ├── Apply date range filter
│   │   ├── Apply status filter
│   │   └── Apply style filter
│   │
│   └── 2. Update UI
│       └── Populate filtered results
│
User Action: Click "Export to CSV"
├── Backend Process:
│   ├── 1. SongCreationHistoryManager.export_to_csv()
│   │   ├── Generate CSV data
│   │   ├── Include headers
│   │   └── Save to file
│   │
│   └── 2. Show save dialog
│       └── Let user choose file location
│
└── UI Updates:
    ├── Show export success message
    └── Open file location

5. Application Startup Workflow
User Action: Launch application
├── Backend Process:
│   ├── 1. Initialize managers
│   │   ├── AccountManager()
│   │   │   └── Load accounts from JSON
│   │   ├── SessionManager()
│   │   ├── DownloadManager()
│   │   │   └── Load histories from JSON
│   │   ├── QueueManager()
│   │   │   └── Load queue state from JSON
│   │   └── SongCreationHistoryManager()
│   │       └── Load creation history from JSON
│   │
│   ├── 2. Create main window
│   │   ├── Set window properties
│   │   ├── Apply theme
│   │   └── Center on screen
│   │
│   ├── 3. Create UI panels
│   │   ├── AccountPanel
│   │   ├── CreateMusicPanel
│   │   ├── MultipleSongsPanel
│   │   ├── DownloadPanel
│   │   ├── HistoryPanel
│   │   └── SongCreationHistoryPanel
│   │
│   └── 4. Show default tab
│       └── Display AccountPanel
│
└── UI Displays:
    ├── Main window with tab navigation
    ├── Default tab content
    └── Loading indicators if needed

6. Error Handling Workflow
Error Occurs: Any operation fails
├── Backend Process:
│   ├── 1. Catch exception
│   │   ├── Log error details
│   │   ├── Determine error type
│   │   └── Create user-friendly message
│   │
│   ├── 2. Handle specific errors:
│   │   ├── Network errors: Retry mechanism
│   │   ├── Chrome errors: Profile cleanup
│   │   ├── File errors: Check permissions
│   │   └── API errors: Token refresh
│   │
│   └── 3. Update UI
│       └── Show error message
│
└── UI Displays:
    ├── Error dialog with details
    ├── Retry button (if applicable)
    └── Continue button (if non-critical)

7. Data Persistence Workflow
Data Change: Any manager data update
├── Backend Process:
│   ├── 1. Validate data
│   │   └── Check data integrity
│   │
│   ├── 2. Serialize to JSON
│   │   └── Convert objects to JSON
│   │
│   ├── 3. Atomic write
│   │   ├── Write to temporary file
│   │   ├── Validate write success
│   │   └── Rename to target file
│   │
│   └── 4. Handle errors
│       └── Rollback on failure
│
└── File Operations:
    ├── accounts.json (AccountManager)
    ├── download_history.json (DownloadManager)
    ├── queue_state.json (QueueManager)
    └── song_creation_history.json (SongCreationHistoryManager)

📊 Workflow Summary Table
Workflow	Trigger	Key Steps	Output	Error Handling
Single Song Creation	User fills form & clicks create	Validate → Launch Chrome → Fill form → Submit	Show error dialog, retry option	
Batch Song Creation	User uploads XML & executes queues	Parse XML → Create queues → Multi-tab automation	Continue on individual failures	
Download Songs	User selects account & clicks download	Get token → Fetch clips → Download files	Retry failed downloads	
Account Management	User adds/manages accounts	Validate → Create profile → Save data	Profile cleanup on errors	
History Viewing	User selects filters	Load history → Apply filters → Display	Show empty state on no results	
Application Startup	User launches app	Load data → Initialize UI → Show default tab	Graceful degradation on missing data	
These detailed workflows provide a complete picture of how each feature operates from user interaction to backend processing to UI updates. They can be used as a reference for implementing the application in any programming language.