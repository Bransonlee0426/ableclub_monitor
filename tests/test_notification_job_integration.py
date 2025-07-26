import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from scheduler.job_manager import (
    execute_notification_job,
    trigger_notification_job,
    _call_notification_processor,
    _execute_notification_with_retry
)
from app.jobs.notification_job import process_and_notify_users


class TestNotificationJobIntegration:
    """
    Test suite for notification job integration with APScheduler
    """
    
    @pytest.mark.asyncio
    async def test_execute_notification_job_success(self):
        """
        Test successful execution of notification job
        """
        with patch('scheduler.job_manager.get_db') as mock_get_db, \
             patch('scheduler.job_manager.crud_job_execution_history') as mock_crud, \
             patch('scheduler.job_manager._call_notification_processor') as mock_processor:
            
            # Setup mocks
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            mock_crud.cleanup_old_records.return_value = 0
            mock_crud.is_job_paused.return_value = False
            mock_crud.get_consecutive_failures.return_value = 0
            mock_crud.create.return_value = MagicMock()
            mock_crud.update.return_value = MagicMock()
            
            # Mock successful processor execution
            mock_processor.return_value = {
                "users_processed": 5,
                "notifications_sent": 3,
                "status": "completed"
            }
            
            # Execute the job
            await execute_notification_job()
            
            # Verify interactions
            mock_crud.cleanup_old_records.assert_called_once()
            mock_crud.is_job_paused.assert_called_once_with(mock_db, job_name="notification_processor")
            mock_crud.get_consecutive_failures.assert_called_once_with(mock_db, job_name="notification_processor")
            mock_processor.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_notification_job_paused(self):
        """
        Test notification job execution when job is paused
        """
        with patch('scheduler.job_manager.get_db') as mock_get_db, \
             patch('scheduler.job_manager.crud_job_execution_history') as mock_crud:
            
            # Setup mocks
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            mock_crud.cleanup_old_records.return_value = 0
            mock_crud.is_job_paused.return_value = True  # Job is paused
            
            # Execute the job
            await execute_notification_job()
            
            # Verify that processing was skipped
            mock_crud.cleanup_old_records.assert_called_once()
            mock_crud.is_job_paused.assert_called_once_with(mock_db, job_name="notification_processor")
            # Should not proceed to consecutive failures check
            mock_crud.get_consecutive_failures.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_call_notification_processor_success(self):
        """
        Test successful call to notification processor
        """
        with patch('scheduler.job_manager.process_and_notify_users') as mock_process:
            
            # Execute the processor call
            result = await _call_notification_processor()
            
            # Verify the call and result structure
            mock_process.assert_called_once()
            assert result["status"] == "completed"
            assert "users_processed" in result
            assert "notifications_sent" in result
            assert "execution_time" in result
    
    @pytest.mark.asyncio
    async def test_call_notification_processor_exception(self):
        """
        Test notification processor call with exception
        """
        with patch('scheduler.job_manager.process_and_notify_users') as mock_process:
            
            # Setup mock to raise exception
            mock_process.side_effect = Exception("Test notification error")
            
            # Execute and expect exception
            with pytest.raises(Exception) as exc_info:
                await _call_notification_processor()
            
            assert "Test notification error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_trigger_notification_job(self):
        """
        Test manual trigger of notification job
        """
        with patch('scheduler.job_manager.execute_notification_job') as mock_execute:
            
            # Trigger the job
            result = await trigger_notification_job()
            
            # Verify execution
            mock_execute.assert_called_once()
            assert result["message"] == "Notification job execution triggered"
    
    @pytest.mark.asyncio
    async def test_execute_notification_with_retry_success_first_attempt(self):
        """
        Test notification execution with retry - success on first attempt
        """
        with patch('scheduler.job_manager.get_db') as mock_get_db, \
             patch('scheduler.job_manager.crud_job_execution_history') as mock_crud, \
             patch('scheduler.job_manager._call_notification_processor') as mock_processor:
            
            # Setup mocks
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            mock_execution_record = MagicMock()
            
            # Mock successful processor execution
            mock_processor.return_value = {
                "users_processed": 2,
                "notifications_sent": 1,
                "status": "completed"
            }
            
            # Execute with retry
            await _execute_notification_with_retry(mock_db, mock_execution_record)
            
            # Verify single successful call
            mock_processor.assert_called_once()
            mock_crud.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_notification_with_retry_final_failure(self):
        """
        Test notification execution with retry - final failure after max retries
        """
        with patch('scheduler.job_manager.get_db') as mock_get_db, \
             patch('scheduler.job_manager.crud_job_execution_history') as mock_crud, \
             patch('scheduler.job_manager._call_notification_processor') as mock_processor, \
             patch('scheduler.job_manager._send_notification_failure_notification') as mock_notify, \
             patch('scheduler.job_manager.settings') as mock_settings, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            
            # Setup mocks
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            mock_execution_record = MagicMock()
            mock_settings.JOB_RETRY_MAX = 2  # Set max retries to 2
            
            # Mock processor to always fail
            mock_processor.side_effect = Exception("Persistent notification error")
            
            # Execute with retry
            await _execute_notification_with_retry(mock_db, mock_execution_record)
            
            # Verify retries and final failure handling
            assert mock_processor.call_count == 3  # Initial + 2 retries
            mock_crud.update.assert_called_once()  # Final failure update
            mock_notify.assert_called_once()  # Failure notification sent
            assert mock_sleep.call_count == 2  # Wait between retries
    
    def test_process_and_notify_users_mock_execution(self):
        """
        Test the core notification processing function with mocked dependencies
        """
        with patch('app.jobs.notification_job._get_all_user_settings') as mock_users, \
             patch('app.jobs.notification_job._get_unprocessed_events') as mock_events, \
             patch('app.jobs.notification_job._send_email_notifications') as mock_send, \
             patch('app.jobs.notification_job._update_processed_events') as mock_update:
            
            # Setup mock data
            mock_users.return_value = [
                {
                    "email_address": "test@example.com",
                    "keywords": ["Python", "AI"],
                    "is_active": True
                }
            ]
            
            mock_events.return_value = [
                {
                    "id": 1,
                    "title": "Python Programming Workshop",
                },
                {
                    "id": 2,
                    "title": "AI and Machine Learning Seminar",
                }
            ]
            
            # Execute the function
            process_and_notify_users()
            
            # Verify all steps were called
            mock_users.assert_called_once()
            mock_events.assert_called_once()
            mock_send.assert_called_once()
            mock_update.assert_called_once()
    
    def test_process_and_notify_users_no_users(self):
        """
        Test notification processing with no user settings
        """
        with patch('app.jobs.notification_job._get_all_user_settings') as mock_users, \
             patch('app.jobs.notification_job._get_unprocessed_events') as mock_events:
            
            # Setup empty user settings
            mock_users.return_value = []
            
            # Execute the function
            process_and_notify_users()
            
            # Verify early return when no users
            mock_users.assert_called_once()
            mock_events.assert_not_called()  # Should not fetch events if no users
    
    def test_process_and_notify_users_no_events(self):
        """
        Test notification processing with no unprocessed events
        """
        with patch('app.jobs.notification_job._get_all_user_settings') as mock_users, \
             patch('app.jobs.notification_job._get_unprocessed_events') as mock_events, \
             patch('app.jobs.notification_job._send_email_notifications') as mock_send:
            
            # Setup mock data
            mock_users.return_value = [{"email_address": "test@example.com", "is_active": True}]
            mock_events.return_value = []  # No events
            
            # Execute the function
            process_and_notify_users()
            
            # Verify early return when no events
            mock_users.assert_called_once()
            mock_events.assert_called_once()
            mock_send.assert_not_called()  # Should not send notifications if no events
    
    @pytest.mark.asyncio
    async def test_notification_job_consecutive_failures_pause(self):
        """
        Test notification job pausing after consecutive failures
        """
        with patch('scheduler.job_manager.get_db') as mock_get_db, \
             patch('scheduler.job_manager.crud_job_execution_history') as mock_crud, \
             patch('scheduler.job_manager._pause_notification_job_due_to_failures') as mock_pause, \
             patch('scheduler.job_manager.settings') as mock_settings:
            
            # Setup mocks
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            mock_crud.cleanup_old_records.return_value = 0
            mock_crud.is_job_paused.return_value = False
            mock_crud.get_consecutive_failures.return_value = 3  # Max failures reached
            mock_settings.JOB_RETRY_MAX = 3
            
            # Execute the job
            await execute_notification_job()
            
            # Verify that job was paused due to failures
            mock_pause.assert_called_once_with(mock_db, 3)


class TestNotificationJobConfiguration:
    """
    Test configuration aspects of notification job integration
    """
    
    def test_notification_job_interval_setting(self):
        """
        Test that notification job interval setting is available
        """
        from core.config import settings
        
        # Verify the setting exists and has expected default
        assert hasattr(settings, 'NOTIFICATION_JOB_INTERVAL_HOURS')
        assert settings.NOTIFICATION_JOB_INTERVAL_HOURS == 1
    
    def test_scheduler_job_registration(self):
        """
        Test that notification job is properly registered in scheduler
        This is an integration test that verifies scheduler configuration
        """
        from scheduler.job_scheduler import SchedulerManager
        from unittest.mock import patch
        
        # Create scheduler instance
        scheduler_manager = SchedulerManager()
        
        # Mock the actual job functions to avoid execution
        with patch('scheduler.job_manager.execute_corporate_events_job'), \
             patch('scheduler.job_manager.execute_notification_job'):
            
            # This would normally start the scheduler, but we're just testing configuration
            # In a real test environment, you might want to use a test scheduler
            assert scheduler_manager.scheduler is not None
            assert scheduler_manager.scheduler.timezone.zone == 'Asia/Taipei'


# Integration test utilities
class TestNotificationJobTestUtils:
    """
    Utility functions for testing notification job integration
    """
    
    @staticmethod
    def create_mock_user_setting(email: str = "test@example.com", keywords: list = None, is_active: bool = True):
        """
        Create mock user notification setting for testing
        """
        if keywords is None:
            keywords = ["test", "keyword"]
        
        return {
            "email_address": email,
            "keywords": keywords,
            "is_active": is_active
        }
    
    @staticmethod
    def create_mock_event(event_id: int = 1, title: str = "Test Event"):
        """
        Create mock event for testing
        """
        return {
            "id": event_id,
            "title": title
        }