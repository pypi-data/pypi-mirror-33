# typing Modules
import typing as typ

# External Modules

# Internal Modules
from catalog.jobs.jobs        import Job
from catalog.jobs.versions    import current_version
from catalog.datalog.db_utils import Query
# from catalog.misc.sql_utils   import STRJOB_EXACT_,STRJOB_GRAPH_,job,JOB
################################################################################
class RepeatChecker(object):
    """
    Interface for checking repeat jobs
    Preserve this object throughout submitting jobs in one session
    to avoid constantly scraping fireworks database
    """

    def __init__(self
                ,granularity : str = 'exact'
                ) -> None:

        assert granularity in ['graph','exact'], 'Invalid option for "granularity"'
        self.granularity=granularity
        self._scrape_incomplete_jobs()

    def add_incomplete_job(self
                          ,job : Job
                          ) -> None:
        """
        Add a newly created job to the list for repeat-checking
        """
        self.incomplete_jobs.append(job.to_string(self.granularity))

    def check_repeat(self
                    ,job : Job
                    ) -> bool:
        """
        Returns True if job is a repeat
        """
        #HACK FOR GETTING AROUND BROKEN CHECKER
        return False

        job_str = job.to_string(self.granularity)
        return (  self._repeat_incomplete(job_str)
               or self._repeat_complete(job_str))

    def _repeat_incomplete(self
                          ,job_str : str
                          ) -> bool:
        """
        Check current list of incomplete jobs for a repeat
        """
        return job_str in self.incomplete_jobs

    def _repeat_complete(self
                        ,job_str : str
                        ) -> bool:
        """Check CataLog database for a particular job"""
        constraint = STRJOB_EXACT_ if self.granularity=='exact' else STRJOB_GRAPH_
        constraints = [constraint(job_str)] # type: ignore
        return Query(constraints=constraints,table=job
                       ,db_path=self.db_path).any_query(JOB)

    def _scrape_incomplete_jobs(self) -> None:
        """
        Initialize incomplete job list from FireWorks database
        """
        from catalog.fw.incomplete import incompleteFWIDS,lpad
        incomplete_fwids = incompleteFWIDS()
        params = [lpad.get_fw_dict_by_id(i)['spec']['params'] for i in incomplete_fwids]
        self.incomplete_jobs = [current_version.process_dict(p).to_string(self.granularity) for p in params] # type: typ.List[str]
