from django_cron import CronJobBase, Schedule
from freightmonster.management.commands.delete_old_loads_drafts import DeleteLoadDraftCommand


class DeleteOldLoadDraftsJob(CronJobBase):
    RUN_AT_TIMES = ['00:00']  # Run at midnight every day

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'freightmonster.delete_old_load_drafts_job'

    @staticmethod
    def do():
        DeleteLoadDraftCommand().handle()
