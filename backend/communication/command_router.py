"""
Command Router - Routes incoming commands to appropriate manager methods
"""
import traceback
from typing import Dict, Any, Optional
from .message_handler import MessageHandler
from .types import (
    Command, CommandTypes, ResponseTypes, ErrorCodes
)
from .progress_manager import ProgressManager


class CommandRouter(MessageHandler):
    """Routes commands to appropriate manager methods"""

    def __init__(self):
        super().__init__()
        self.progress_manager = ProgressManager()

        # Managers will be injected
        self.account_manager = None
        self.queue_manager = None
        self.download_manager = None
        self.session_manager = None
        self.batch_song_creator = None
        self.history_manager = None

    def register_managers(self, **managers):
        """Register manager instances"""
        for name, manager in managers.items():
            setattr(self, f"{name}_manager", manager)

    def process_command(self, command_data: dict) -> Optional[Dict[str, Any]]:
        """Process incoming command and return response"""
        command = self.parse_command(command_data)
        if not command:
            return None

        try:
            # Route command to appropriate handler
            handler = self._get_command_handler(command.type)
            if handler:
                return handler(command)
            else:
                return {
                    "id": command.id,
                    "type": ResponseTypes.GET_ACCOUNTS_RESPONSE,  # Default response type
                    "success": False,
                    "error": f"Unknown command type: {command.type}",
                    "error_code": ErrorCodes.UNKNOWN_COMMAND
                }

        except Exception as e:
            error_msg = f"Error processing command {command.type}: {str(e)}"
            traceback.print_exc()  # Log full traceback for debugging

            return {
                "id": command.id,
                "type": ResponseTypes.GET_ACCOUNTS_RESPONSE,  # Default response type
                "success": False,
                "error": error_msg,
                "error_code": ErrorCodes.INTERNAL_ERROR
            }

    def _get_command_handler(self, command_type: str):
        """Get handler method for command type"""
        handlers = {
            CommandTypes.GET_ACCOUNTS: self._handle_get_accounts,
            CommandTypes.CREATE_ACCOUNT: self._handle_create_account,
            CommandTypes.UPDATE_ACCOUNT: self._handle_update_account,
            CommandTypes.RENAME_ACCOUNT: self._handle_rename_account,
            CommandTypes.DELETE_ACCOUNT: self._handle_delete_account,
            CommandTypes.GET_ACCOUNT_PROFILE_PATH: self._handle_get_account_profile_path,

            CommandTypes.GET_QUEUES: self._handle_get_queues,
            CommandTypes.CREATE_QUEUE: self._handle_create_queue,
            CommandTypes.REMOVE_QUEUE: self._handle_remove_queue,
            CommandTypes.UPDATE_QUEUE_PROGRESS: self._handle_update_queue_progress,
            CommandTypes.VALIDATE_PROMPTS: self._handle_validate_prompts,
            CommandTypes.CLEAR_QUEUES: self._handle_clear_queues,

            CommandTypes.LAUNCH_BROWSER: self._handle_launch_browser,
            CommandTypes.GET_SESSION_TOKEN: self._handle_get_session_token,
            CommandTypes.VERIFY_SESSION: self._handle_verify_session,

            CommandTypes.GET_DOWNLOAD_HISTORY: self._handle_get_download_history,
            CommandTypes.FETCH_CLIPS: self._handle_fetch_clips,
            CommandTypes.GET_NEW_CLIPS: self._handle_get_new_clips,
            CommandTypes.DOWNLOAD_CLIP: self._handle_download_clip,
            CommandTypes.BATCH_DOWNLOAD: self._handle_batch_download,
            CommandTypes.CLEAR_DOWNLOAD_HISTORY: self._handle_clear_download_history,

            CommandTypes.CREATE_SONGS_BATCH: self._handle_create_songs_batch,
            CommandTypes.START_QUEUE_EXECUTION: self._handle_start_queue_execution,

            CommandTypes.GET_CREATION_HISTORY: self._handle_get_creation_history,
            CommandTypes.ADD_CREATION_RECORD: self._handle_add_creation_record,
            CommandTypes.EXPORT_HISTORY_TO_CSV: self._handle_export_history_to_csv,
            CommandTypes.SEARCH_HISTORY: self._handle_search_history,
        }

        return handlers.get(command_type)

    # Placeholder handlers - will be implemented with actual manager methods
    def _handle_get_accounts(self, command: Command):
        """Handle GET_ACCOUNTS command"""
        if not self.account_manager:
            return self._create_error_response(
                command.id, "Account manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        accounts = self.account_manager.get_all_accounts()
        return self._create_success_response(
            command.id,
            ResponseTypes.GET_ACCOUNTS_RESPONSE,
            [self._account_to_dict(acc) for acc in accounts]
        )

    def _handle_create_account(self, command: Command):
        """Handle CREATE_ACCOUNT command"""
        if not self.account_manager:
            return self._create_error_response(
                command.id, "Account manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        name = payload.get('name')
        email = payload.get('email', '')

        if not name:
            return self._create_error_response(
                command.id, "Account name is required",
                ErrorCodes.INVALID_PAYLOAD
            )

        success = self.account_manager.add_account(name, email)
        if success:
            account = self.account_manager.get_account(name)
            return self._create_success_response(
                command.id,
                ResponseTypes.CREATE_ACCOUNT_RESPONSE,
                self._account_to_dict(account)
            )
        else:
            return self._create_error_response(
                command.id, "Failed to create account",
                ErrorCodes.ACCOUNT_CREATION_FAILED
            )

    # Add other placeholder handlers...
    def _handle_update_account(self, command: Command):
        """Handle UPDATE_ACCOUNT command"""
        if not self.account_manager:
            return self._create_error_response(
                command.id, "Account manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        name = payload.get('name')
        kwargs = {k: v for k, v in payload.items() if k != 'name'}

        if not name:
            return self._create_error_response(
                command.id, "Account name is required",
                ErrorCodes.INVALID_PAYLOAD
            )

        success = self.account_manager.update_account(name, **kwargs)
        if success:
            account = self.account_manager.get_account(name)
            return self._create_success_response(
                command.id,
                ResponseTypes.UPDATE_ACCOUNT_RESPONSE,
                self._account_to_dict(account)
            )
        else:
            return self._create_error_response(
                command.id, "Account not found",
                ErrorCodes.ACCOUNT_NOT_FOUND
            )

    def _handle_rename_account(self, command: Command):
        """Handle RENAME_ACCOUNT command"""
        if not self.account_manager:
            return self._create_error_response(
                command.id, "Account manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        old_name = payload.get('old_name')
        new_name = payload.get('new_name')

        if not old_name or not new_name:
            return self._create_error_response(
                command.id, "Both old_name and new_name are required",
                ErrorCodes.INVALID_PAYLOAD
            )

        success = self.account_manager.rename_account(old_name, new_name)
        if success:
            return self._create_success_response(
                command.id,
                ResponseTypes.RENAME_ACCOUNT_RESPONSE,
                {"old_name": old_name, "new_name": new_name}
            )
        else:
            return self._create_error_response(
                command.id, "Rename failed",
                ErrorCodes.ACCOUNT_NOT_FOUND
            )

    def _handle_delete_account(self, command: Command):
        """Handle DELETE_ACCOUNT command"""
        if not self.account_manager:
            return self._create_error_response(
                command.id, "Account manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        name = payload.get('name')
        delete_profile = payload.get('delete_profile', False)

        if not name:
            return self._create_error_response(
                command.id, "Account name is required",
                ErrorCodes.INVALID_PAYLOAD
            )

        success = self.account_manager.delete_account(name, delete_profile)
        if success:
            return self._create_success_response(
                command.id,
                ResponseTypes.DELETE_ACCOUNT_RESPONSE,
                {"name": name}
            )
        else:
            return self._create_error_response(
                command.id, "Delete failed",
                ErrorCodes.ACCOUNT_NOT_FOUND
            )

    def _handle_get_account_profile_path(self, command: Command):
        """Handle GET_ACCOUNT_PROFILE_PATH command"""
        if not self.account_manager:
            return self._create_error_response(
                command.id, "Account manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        name = payload.get('name')

        if not name:
            return self._create_error_response(
                command.id, "Account name is required",
                ErrorCodes.INVALID_PAYLOAD
            )

        profile_path = self.account_manager.get_profile_path(name)
        return self._create_success_response(
            command.id,
            ResponseTypes.GET_ACCOUNT_PROFILE_PATH_RESPONSE,
            {"name": name, "profile_path": str(profile_path) if profile_path else None}
        )

    def _handle_get_queues(self, command: Command):
        """Handle GET_QUEUES command"""
        if not self.queue_manager:
            return self._create_error_response(
                command.id, "Queue manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        queues = self.queue_manager.get_all_queues()
        return self._create_success_response(
            command.id,
            ResponseTypes.GET_QUEUES_RESPONSE,
            [self._queue_entry_to_dict(queue) for queue in queues]
        )

    def _handle_create_queue(self, command: Command):
        """Handle CREATE_QUEUE command"""
        if not self.queue_manager:
            return self._create_error_response(
                command.id, "Queue manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        account_name = payload.get('account_name')
        total_songs = payload.get('total_songs')
        songs_per_batch = payload.get('songs_per_batch')
        prompts_data = payload.get('prompts', [])

        if not all([account_name, total_songs, songs_per_batch]):
            return self._create_error_response(
                command.id, "account_name, total_songs, and songs_per_batch are required",
                ErrorCodes.INVALID_PAYLOAD
            )

        # Convert prompts from dict to SunoPrompt objects
        from src.utils.prompt_parser import SunoPrompt
        prompts = []
        for prompt_data in prompts_data:
            prompt = SunoPrompt(
                title=prompt_data.get('title', ''),
                lyrics=prompt_data.get('lyrics', ''),
                style=prompt_data.get('style', '')
            )
            prompts.append(prompt)

        try:
            queue_entry = self.queue_manager.add_queue_entry(
                account_name=account_name,
                total_songs=total_songs,
                songs_per_batch=songs_per_batch,
                prompts=prompts
            )
            return self._create_success_response(
                command.id,
                ResponseTypes.CREATE_QUEUE_RESPONSE,
                self._queue_entry_to_dict(queue_entry)
            )
        except Exception as e:
            return self._create_error_response(
                command.id, f"Queue creation failed: {str(e)}",
                ErrorCodes.INVALID_QUEUE_PARAMETERS
            )

    def _handle_remove_queue(self, command: Command):
        """Handle REMOVE_QUEUE command"""
        if not self.queue_manager:
            return self._create_error_response(
                command.id, "Queue manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        queue_id = payload.get('queue_id')

        if not queue_id:
            return self._create_error_response(
                command.id, "queue_id is required",
                ErrorCodes.INVALID_PAYLOAD
            )

        success = self.queue_manager.remove_queue_entry(queue_id)
        return self._create_success_response(
            command.id,
            ResponseTypes.REMOVE_QUEUE_RESPONSE,
            {"queue_id": queue_id, "success": success}
        )

    def _handle_update_queue_progress(self, command: Command):
        """Handle UPDATE_QUEUE_PROGRESS command"""
        if not self.queue_manager:
            return self._create_error_response(
                command.id, "Queue manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        queue_id = payload.get('queue_id')
        completed_count = payload.get('completed_count')
        status = payload.get('status')

        if not queue_id:
            return self._create_error_response(
                command.id, "queue_id is required",
                ErrorCodes.INVALID_PAYLOAD
            )

        success = self.queue_manager.update_queue_progress(
            queue_id=queue_id,
            completed_count=completed_count,
            status=status
        )
        return self._create_success_response(
            command.id,
            ResponseTypes.UPDATE_QUEUE_PROGRESS_RESPONSE,
            {"queue_id": queue_id, "success": success}
        )

    def _handle_validate_prompts(self, command: Command):
        """Handle VALIDATE_PROMPTS command"""
        if not self.queue_manager:
            return self._create_error_response(
                command.id, "Queue manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        requested_total = payload.get('requested_total', 0)

        is_valid = self.queue_manager.validate_total_prompts(requested_total)
        available_slots = self.queue_manager.available_prompt_slots

        return self._create_success_response(
            command.id,
            ResponseTypes.VALIDATE_PROMPTS_RESPONSE,
            {
                "is_valid": is_valid,
                "requested_total": requested_total,
                "available_slots": available_slots
            }
        )

    def _handle_clear_queues(self, command: Command):
        """Handle CLEAR_QUEUES command"""
        if not self.queue_manager:
            return self._create_error_response(
                command.id, "Queue manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        self.queue_manager.clear()
        return self._create_success_response(
            command.id,
            ResponseTypes.CLEAR_QUEUES_RESPONSE,
            {"message": "All queues cleared"}
        )

    def _handle_launch_browser(self, command: Command):
        """Handle LAUNCH_BROWSER command"""
        if not self.session_manager:
            return self._create_error_response(
                command.id, "Session manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        account_name = payload.get('account_name')
        headless = payload.get('headless', False)

        if not account_name:
            return self._create_error_response(
                command.id, "account_name is required",
                ErrorCodes.INVALID_PAYLOAD
            )

        try:
            driver = self.session_manager.launch_browser(account_name, headless)
            return self._create_success_response(
                command.id,
                ResponseTypes.LAUNCH_BROWSER_RESPONSE,
                {"account_name": account_name, "launched": driver is not None}
            )
        except Exception as e:
            return self._create_error_response(
                command.id, f"Browser launch failed: {str(e)}",
                ErrorCodes.BROWSER_LAUNCH_FAILED
            )

    def _handle_get_session_token(self, command: Command):
        """Handle GET_SESSION_TOKEN command"""
        if not self.session_manager:
            return self._create_error_response(
                command.id, "Session manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        account_name = payload.get('account_name')

        if not account_name:
            return self._create_error_response(
                command.id, "account_name is required",
                ErrorCodes.INVALID_PAYLOAD
            )

        token = self.session_manager.get_session_token(account_name)
        return self._create_success_response(
            command.id,
            ResponseTypes.GET_SESSION_TOKEN_RESPONSE,
            {"account_name": account_name, "token": token}
        )

    def _handle_verify_session(self, command: Command):
        """Handle VERIFY_SESSION command"""
        if not self.session_manager:
            return self._create_error_response(
                command.id, "Session manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        account_name = payload.get('account_name')

        if not account_name:
            return self._create_error_response(
                command.id, "account_name is required",
                ErrorCodes.INVALID_PAYLOAD
            )

        is_valid = self.session_manager.verify_session(account_name)
        return self._create_success_response(
            command.id,
            ResponseTypes.VERIFY_SESSION_RESPONSE,
            {"account_name": account_name, "is_valid": is_valid}
        )

    def _handle_get_download_history(self, command: Command):
        """Handle GET_DOWNLOAD_HISTORY command"""
        if not self.download_manager:
            return self._create_error_response(
                command.id, "Download manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        account_name = payload.get('account_name')

        history = self.download_manager.get_history(account_name)
        return self._create_success_response(
            command.id,
            ResponseTypes.GET_DOWNLOAD_HISTORY_RESPONSE,
            self._download_history_to_dict(history)
        )

    def _handle_fetch_clips(self, command: Command):
        """Handle FETCH_CLIPS command"""
        if not self.download_manager:
            return self._create_error_response(
                command.id, "Download manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        session_token = payload.get('session_token')
        profile_name = payload.get('profile_name')
        use_my_songs = payload.get('use_my_songs', True)
        use_create_page = payload.get('use_create_page', False)

        if not session_token:
            return self._create_error_response(
                command.id, "session_token is required",
                ErrorCodes.INVALID_PAYLOAD
            )

        try:
            clips = self.download_manager.fetch_clips(
                session_token=session_token,
                profile_name=profile_name,
                use_my_songs=use_my_songs,
                use_create_page=use_create_page
            )
            return self._create_success_response(
                command.id,
                ResponseTypes.FETCH_CLIPS_RESPONSE,
                [self._song_clip_to_dict(clip) for clip in clips]
            )
        except Exception as e:
            return self._create_error_response(
                command.id, f"Fetch clips failed: {str(e)}",
                ErrorCodes.INTERNAL_ERROR
            )

    def _handle_get_new_clips(self, command: Command):
        """Handle GET_NEW_CLIPS command"""
        if not self.download_manager:
            return self._create_error_response(
                command.id, "Download manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        account_name = payload.get('account_name')
        all_clips_data = payload.get('all_clips', [])

        # Convert dict clips back to SongClip objects
        all_clips = []
        for clip_data in all_clips_data:
            from src.models import SongClip
            clip = SongClip.from_api_response(clip_data)
            all_clips.append(clip)

        new_clips = self.download_manager.get_new_clips(account_name, all_clips)
        return self._create_success_response(
            command.id,
            ResponseTypes.GET_NEW_CLIPS_RESPONSE,
            [self._song_clip_to_dict(clip) for clip in new_clips]
        )

    def _handle_download_clip(self, command: Command):
        """Handle DOWNLOAD_CLIP command"""
        if not self.download_manager:
            return self._create_error_response(
                command.id, "Download manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        session_token = payload.get('session_token')
        clip_data = payload.get('clip')
        output_dir = payload.get('output_dir')
        with_thumbnail = payload.get('with_thumbnail', True)
        append_uuid = payload.get('append_uuid', True)

        if not all([session_token, clip_data, output_dir]):
            return self._create_error_response(
                command.id, "session_token, clip, and output_dir are required",
                ErrorCodes.INVALID_PAYLOAD
            )

        # Convert dict back to SongClip object
        from src.models import SongClip
        clip = SongClip.from_api_response(clip_data)

        # Create progress callback
        def progress_callback(filename, downloaded, total):
            self.send_progress_event({
                "file_name": filename,
                "downloaded": downloaded,
                "total": total,
                "progress": int((downloaded / total) * 100) if total > 0 else 0
            }, ProgressEventTypes.DOWNLOAD_PROGRESS)

        try:
            success = self.download_manager.download_clip(
                session_token=session_token,
                clip=clip,
                output_dir=output_dir,
                with_thumbnail=with_thumbnail,
                append_uuid=append_uuid,
                progress_callback=progress_callback
            )
            return self._create_success_response(
                command.id,
                ResponseTypes.DOWNLOAD_CLIP_RESPONSE,
                {"success": success, "clip_id": clip.id}
            )
        except Exception as e:
            return self._create_error_response(
                command.id, f"Download failed: {str(e)}",
                ErrorCodes.DOWNLOAD_FAILED
            )

    def _handle_batch_download(self, command: Command):
        """Handle BATCH_DOWNLOAD command"""
        if not self.download_manager:
            return self._create_error_response(
                command.id, "Download manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        account_name = payload.get('account_name')
        session_token = payload.get('session_token')
        clips_data = payload.get('clips', [])
        output_dir = payload.get('output_dir')
        with_thumbnail = payload.get('with_thumbnail', True)
        append_uuid = payload.get('append_uuid', True)
        delay = payload.get('delay', 2.0)

        if not all([account_name, session_token, output_dir]):
            return self._create_error_response(
                command.id, "account_name, session_token, and output_dir are required",
                ErrorCodes.INVALID_PAYLOAD
            )

        # Convert dict clips back to SongClip objects
        from src.models import SongClip
        clips = []
        for clip_data in clips_data:
            clip = SongClip.from_api_response(clip_data)
            clips.append(clip)

        # Create progress callback
        def progress_callback(filename, downloaded, total):
            self.send_progress_event({
                "account_name": account_name,
                "file_name": filename,
                "downloaded": downloaded,
                "total": total,
                "progress": int((downloaded / total) * 100) if total > 0 else 0
            }, ProgressEventTypes.BATCH_DOWNLOAD_PROGRESS)

        try:
            results = self.download_manager.batch_download(
                account_name=account_name,
                session_token=session_token,
                clips=clips,
                output_dir=output_dir,
                with_thumbnail=with_thumbnail,
                append_uuid=append_uuid,
                progress_callback=progress_callback,
                delay=delay
            )
            return self._create_success_response(
                command.id,
                ResponseTypes.BATCH_DOWNLOAD_RESPONSE,
                results
            )
        except Exception as e:
            return self._create_error_response(
                command.id, f"Batch download failed: {str(e)}",
                ErrorCodes.DOWNLOAD_FAILED
            )

    def _handle_clear_download_history(self, command: Command):
        """Handle CLEAR_DOWNLOAD_HISTORY command"""
        if not self.download_manager:
            return self._create_error_response(
                command.id, "Download manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        account_name = payload.get('account_name')

        success = self.download_manager.clear_history(account_name)
        return self._create_success_response(
            command.id,
            ResponseTypes.CLEAR_DOWNLOAD_HISTORY_RESPONSE,
            {"account_name": account_name, "success": success}
        )

    def _handle_create_songs_batch(self, command: Command):
        """Handle CREATE_SONGS_BATCH command"""
        if not self.batch_song_creator:
            return self._create_error_response(
                command.id, "Batch song creator not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        prompts_data = payload.get('prompts', [])
        songs_per_session = payload.get('songs_per_session', 1)
        advanced_options = payload.get('advanced_options', {})
        auto_submit = payload.get('auto_submit', False)
        account_name = payload.get('account_name')

        if not account_name:
            return self._create_error_response(
                command.id, "account_name is required",
                ErrorCodes.INVALID_PAYLOAD
            )

        # Convert prompts from dict to SunoPrompt objects
        from src.utils.prompt_parser import SunoPrompt
        prompts = []
        for prompt_data in prompts_data:
            prompt = SunoPrompt(
                title=prompt_data.get('title', ''),
                lyrics=prompt_data.get('lyrics', ''),
                style=prompt_data.get('style', '')
            )
            prompts.append(prompt)

        # Create progress callback
        operation_id = self.progress_manager.generate_operation_id()
        progress_callback = self.progress_manager.create_progress_callback(
            operation_id, self
        )

        # Create history manager reference
        history_manager = getattr(self, 'history_manager', None)

        try:
            results = self.batch_song_creator.create_songs_batch(
                prompts=prompts,
                songs_per_session=songs_per_session,
                advanced_options=advanced_options,
                auto_submit=auto_submit,
                progress_callback=progress_callback,
                account_name=account_name,
                history_manager=history_manager
            )
            return self._create_success_response(
                command.id,
                ResponseTypes.CREATE_SONGS_BATCH_RESPONSE,
                {"operation_id": operation_id, "results": results}
            )
        except Exception as e:
            return self._create_error_response(
                command.id, f"Batch creation failed: {str(e)}",
                ErrorCodes.BATCH_CREATION_FAILED
            )

    def _handle_start_queue_execution(self, command: Command):
        """Handle START_QUEUE_EXECUTION command"""
        if not self.batch_song_creator or not self.queue_manager:
            return self._create_error_response(
                command.id, "Required managers not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        queue_ids = payload.get('queue_ids', [])

        if not queue_ids:
            return self._create_error_response(
                command.id, "queue_ids is required",
                ErrorCodes.INVALID_PAYLOAD
            )

        # Create progress callback
        operation_id = self.progress_manager.generate_operation_id()
        queue_progress_callback = self.progress_manager.create_queue_progress_callback(
            operation_id, self
        )

        # Start queue execution in background thread
        import threading
        import uuid

        def execute_queues():
            try:
                # This would need to be implemented in BatchSongCreator
                # For now, return a placeholder response
                self.send_progress_event({
                    "operation_id": operation_id,
                    "message": "Queue execution started",
                    "queue_ids": queue_ids,
                    "status": "running"
                }, ProgressEventTypes.QUEUE_PROGRESS)
            except Exception as e:
                self.progress_manager.fail_operation(operation_id, str(e), self)
            finally:
                self.progress_manager.complete_operation(operation_id)

        thread = threading.Thread(target=execute_queues, daemon=True)
        thread.start()

        return self._create_success_response(
            command.id,
            ResponseTypes.START_QUEUE_EXECUTION_RESPONSE,
            {
                "operation_id": operation_id,
                "queue_ids": queue_ids,
                "status": "started"
            }
        )

    def _handle_get_creation_history(self, command: Command):
        """Handle GET_CREATION_HISTORY command"""
        if not self.history_manager:
            return self._create_error_response(
                command.id, "History manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        account_name = payload.get('account_name')

        if account_name:
            records = self.history_manager.get_records_by_account(account_name)
        else:
            records = self.history_manager.get_all_records()

        return self._create_success_response(
            command.id,
            ResponseTypes.GET_CREATION_HISTORY_RESPONSE,
            [self._song_creation_record_to_dict(record) for record in records]
        )

    def _handle_add_creation_record(self, command: Command):
        """Handle ADD_CREATION_RECORD command"""
        if not self.history_manager:
            return self._create_error_response(
                command.id, "History manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        record_data = payload.get('record')

        if not record_data:
            return self._create_error_response(
                command.id, "record is required",
                ErrorCodes.INVALID_PAYLOAD
            )

        # Convert dict back to SongCreationRecord object
        from src.models import SongCreationRecord
        record = SongCreationRecord.from_dict(record_data)

        self.history_manager.add_creation_record(record)
        return self._create_success_response(
            command.id,
            ResponseTypes.ADD_CREATION_RECORD_RESPONSE,
            {"success": True, "record_id": record.song_id}
        )

    def _handle_export_history_to_csv(self, command: Command):
        """Handle EXPORT_HISTORY_TO_CSV command"""
        if not self.history_manager:
            return self._create_error_response(
                command.id, "History manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        output_path = payload.get('output_path')

        if not output_path:
            return self._create_error_response(
                command.id, "output_path is required",
                ErrorCodes.INVALID_PAYLOAD
            )

        try:
            csv_path = self.history_manager.export_to_csv(output_path)
            return self._create_success_response(
                command.id,
                ResponseTypes.EXPORT_HISTORY_TO_CSV_RESPONSE,
                {"csv_path": str(csv_path)}
            )
        except Exception as e:
            return self._create_error_response(
                command.id, f"Export failed: {str(e)}",
                ErrorCodes.INTERNAL_ERROR
            )

    def _handle_search_history(self, command: Command):
        """Handle SEARCH_HISTORY command"""
        if not self.history_manager:
            return self._create_error_response(
                command.id, "History manager not initialized",
                ErrorCodes.INTERNAL_ERROR
            )

        payload = command.payload or {}
        keyword = payload.get('keyword')

        if not keyword:
            return self._create_error_response(
                command.id, "keyword is required",
                ErrorCodes.INVALID_PAYLOAD
            )

        records = self.history_manager.search_records(keyword)
        return self._create_success_response(
            command.id,
            ResponseTypes.SEARCH_HISTORY_RESPONSE,
            [self._song_creation_record_to_dict(record) for record in records]
        )

    # Helper methods
    def _create_success_response(self, command_id: str, response_type: str, data: Any = None):
        """Create success response"""
        return {
            "id": command_id,
            "type": response_type,
            "success": True,
            "data": data
        }

    def _create_error_response(self, command_id: str, error_msg: str, error_code: str):
        """Create error response"""
        return {
            "id": command_id,
            "type": "ERROR_RESPONSE",
            "success": False,
            "error": error_msg,
            "error_code": error_code
        }

    def _account_to_dict(self, account):
        """Convert account object to dictionary"""
        if not account:
            return None
        return {
            "name": account.name,
            "email": account.email,
            "created_at": account.created_at,
            "last_used": account.last_used,
            "status": account.status
        }

    def _queue_entry_to_dict(self, queue_entry):
        """Convert queue entry object to dictionary"""
        if not queue_entry:
            return None
        return {
            "id": queue_entry.id,
            "account_name": queue_entry.account_name,
            "total_songs": queue_entry.total_songs,
            "songs_per_batch": queue_entry.songs_per_batch,
            "prompts_range": list(queue_entry.prompts_range),
            "status": queue_entry.status,
            "created_at": queue_entry.created_at,
            "completed_count": queue_entry.completed_count
        }

    def _song_clip_to_dict(self, song_clip):
        """Convert song clip object to dictionary"""
        if not song_clip:
            return None
        return {
            "id": song_clip.id,
            "title": song_clip.title,
            "audio_url": song_clip.audio_url,
            "image_url": song_clip.image_url,
            "tags": song_clip.tags,
            "created_at": song_clip.created_at,
            "duration": song_clip.duration
        }

    def _download_history_to_dict(self, download_history):
        """Convert download history object to dictionary"""
        if not download_history:
            return None
        return {
            "account_name": download_history.account_name,
            "downloaded_ids": download_history.downloaded_ids,
            "total_downloaded": download_history.total_downloaded,
            "last_download": download_history.last_download,
            "current_page": download_history.current_page,
            "last_profile": download_history.last_profile
        }

    def _song_creation_record_to_dict(self, record):
        """Convert song creation record object to dictionary"""
        if not record:
            return None
        return {
            "song_id": record.song_id,
            "title": record.title,
            "prompt_index": record.prompt_index,
            "account_name": record.account_name,
            "status": record.status,
            "created_at": record.created_at,
            "error_message": record.error_message
        }