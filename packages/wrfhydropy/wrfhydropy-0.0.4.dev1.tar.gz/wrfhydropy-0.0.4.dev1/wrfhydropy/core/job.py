import pathlib
import numpy as np
import f90nml
import datetime
import shutil
import subprocess
import shlex
import warnings
import pickle
import os
import copy

from .ioutils import _check_file_exist_colon

class Job(object):
    """A Job represents run-time specific information for a given WRF-Hydro run. A Simulation
    consists of one or more jobs. For example, adding multiple Jobs can be used to split a
    Simulation into multiple runs to limit the wall-clock duration of each individual run."""
    def __init__(
            self,
            job_id: str,
            model_start_time: np.datetime64 = None,
            model_end_time: np.datetime64 = None,
            exe_cmd: str = None,
            entry_cmd: str = None,
            exit_cmd: str = None):
        """Instatiate a Job object.
        Args:
            job_id: A string identify the job
            model_start_time: The model start time to use for the WRF-Hydro model run.
            model_end_time: The model end time to use for the WRF-Hydro model run
            exe_cmd: The system-specific command to execute WRF-Hydro, for example 'mpirun -np
            36./wrf_hydro.exe'
            entry_cmd: A command to run prior to executing WRF-Hydro, such as loading modules or
            libraries.
            exit_cmd: A command to run after completion of the job.
        """

        # Attributes set at instantiation through arguments
        self._exe_cmd = exe_cmd
        """str: The job-specfific command to be executed. If None command is taken from machine 
        class"""

        self._entry_cmd = entry_cmd
        """str: A command line command to execute before the exe_cmd"""

        self._exit_cmd = exit_cmd
        """str: A command line command to execute after the exe_cmd"""

        self.job_id = job_id
        """str: The job id."""

        self.model_start_time = model_start_time
        """np.datetime64: The model time at the start of the execution."""

        self.model_end_time = model_end_time
        """np.datetime64: The model time at the end of the execution."""

        # Attributes set by class methods
        self.hrldas_times = {'noahlsm_offline':
                                 {'kday':None,
                                  'khour':None,
                                  'start_year':None,
                                  'start_month':None,
                                  'start_day': None,
                                  'start_hour':None,
                                  'start_min':None,
                                  'restart_filename_requested': None}
                             }
        """dict: the HRLDAS namelist used for this job."""

        self.hydro_times = {'hydro_nlist':
                                {'restart_file':None},
                            'nudging_nlist':
                                {'nudginglastobsfile':None}
                            }
        """dict: the hydro namelist used for this job."""

        self.exit_status = None
        """int: The exit status of the model job parsed from WRF-Hydro diag files"""

        # Attributes set by Scheduler class if job is used in scheduler
        self._job_start_time = None
        """str?: The time at the start of the execution."""

        self._job_end_time = None
        """str?: The time at the end of the execution."""

        self._job_submission_time = None
        """str?: The time the job object was created."""

    def add_hydro_namelist(self, namelist: dict):
        """Add a hydro_namelist dictionary to the job object
        Args:
            namelist: The namelist dictionary to add
        """
        self.hydro_namelist = namelist
        if self.model_start_time is None or self.model_end_time is None:
            warnings.warn('model start or end time was not specified in job, start end times will \
            be used from supplied namelist')
            self.model_start_time, self.model_end_time = self._solve_model_start_end_times()

        self._set_hydro_times()
        self.hydro_namelist['hydro_nlist'].update(self.hydro_times['hydro_nlist'])
        self.hydro_namelist['nudging_nlist'].update(self.hydro_times['nudging_nlist'])


    def add_hrldas_namelist(self, namelist: dict):
        """Add a hrldas_namelist dictionary to the job object
        Args:
            namelist: The namelist dictionary to add
        """
        self.hrldas_namelist = namelist
        if self.model_start_time is None or self.model_end_time is None:
            warnings.warn('model start or end time was not specified in job, start end times will \
            be used from supplied namelist')
            self.model_start_time, self.model_end_time = self._solve_model_start_end_times()
        self._set_hrldas_times()
        self.hrldas_namelist['noahlsm_offline'].update(self.hrldas_times['noahlsm_offline'])

    def clone(self, N) -> list:
        """Clone a job object N-times using deepcopy.
        Args:
            N: The number of time to clone the Job
        Returns:
            A list of Job objects
        """
        clones = []
        for ii in range(N):
            clones.append(copy.deepcopy(self))
        return(clones)

    def _run(self):
        """Private method to run a job"""

        # Create curent dir path to use for all operations. Needed so that everything can be run
        # relative to the simulation directory

        current_dir = pathlib.Path(os.curdir)

        # Print some basic info about the run
        print('\nRunning job ' + self.job_id + ': ')
        print('    Wall start time: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print('    Model start time: ' + self.model_start_time.strftime('%Y-%m-%d %H:%M'))
        print('    Model end time: ' + self.model_end_time.strftime('%Y-%m-%d %H:%M'))

        # Check for restart files both as specified and in the run dir..
        # Alias the mutables for some brevity
        hydro_nlst = self.hydro_namelist['hydro_nlist']
        hydro_nlst['restart_file'] = _check_file_exist_colon(current_dir, hydro_nlst[
            'restart_file'])
        nudging_nlst = self.hydro_namelist['nudging_nlist']
        if nudging_nlst:
            nudging_nlst['nudginglastobsfile'] = \
                _check_file_exist_colon(current_dir, nudging_nlst['nudginglastobsfile'])

        # Copy namelists from job_dir to current_dir
        hydro_namelist_path = self.job_dir.joinpath('hydro.namelist')
        hrldas_namelist_path = self.job_dir.joinpath('namelist.hrldas')
        shutil.copy(str(hydro_namelist_path),str(current_dir))
        shutil.copy(str(hrldas_namelist_path),str(current_dir))

        # These dont have the sched_job_id that the scheduled job output files have.
        self.stderr_file = current_dir / ("{0}.stderr".format(self.job_id))
        self.stdout_file = current_dir / ("{0}.stdout".format(self.job_id))

        # Fromulate bash command string
        cmd_string = '/bin/bash -c "'
        if self._entry_cmd is not None:
            cmd_string += self._entry_cmd + ';'

        cmd_string += self._exe_cmd + ';'

        if self._exit_cmd is not None:
            cmd_string += self._exit_cmd

        cmd_string += '"'

        # Set start time of job execution
        self.job_start_time = str(datetime.datetime.now())

        self._proc_log = subprocess.run(shlex.split(cmd_string),
                                        cwd=str(current_dir),
                                        stderr = self.stderr_file.open(mode='w'),
                                        stdout = self.stdout_file.open(mode='w'))

        self.job_end_time = str(datetime.datetime.now())

        # String match diag files for successfull run
        self.exit_status = 1
        with current_dir.joinpath('diag_hydro.00000').open() as f:
            diag_file = f.read()
            if 'The model finished successfully.......' in diag_file:
                self.exit_status = 0

        # cleanup job-specific run files
        diag_files = current_dir.glob('*diag*')
        for file in diag_files:
            shutil.move(str(file), str(self.job_dir))

        shutil.move(str(self.stdout_file),str(self.job_dir))
        shutil.move(str(self.stderr_file),str(self.job_dir))
        current_dir.joinpath('hydro.namelist').unlink()
        current_dir.joinpath('namelist.hrldas').unlink()

    def _write_namelists(self):
        """Private method to write namelist dicts to FORTRAN namelist files"""
        f90nml.write(self.hydro_namelist, str(self.job_dir.joinpath('hydro.namelist')))
        f90nml.write(self.hrldas_namelist, str(self.job_dir.joinpath('namelist.hrldas')))

    def _set_hrldas_times(self):
        """Private method to set model run times in the hrldas namelist"""
        # Duration
        self.hrldas_times['noahlsm_offline']['kday'] = None
        self.hrldas_times['noahlsm_offline']['khour'] = None
        duration = self.model_end_time - self.model_start_time
        if duration.seconds == 0:
            self.hrldas_times['noahlsm_offline']['kday'] = int(duration.days)
            self.hrldas_times['noahlsm_offline'].pop('khour')
        else:
            self.hrldas_times['noahlsm_offline']['khour'] = int(duration.days * 60 + duration.seconds / 3600)
            self.hrldas_times['noahlsm_offline'].pop('kday')

        # Start
        self.hrldas_times['noahlsm_offline']['start_year'] = int(self.model_start_time.year)
        self.hrldas_times['noahlsm_offline']['start_month'] = int(self.model_start_time.month)
        self.hrldas_times['noahlsm_offline']['start_day'] = int(self.model_start_time.day)
        self.hrldas_times['noahlsm_offline']['start_hour'] = int(self.model_start_time.hour)
        self.hrldas_times['noahlsm_offline']['start_min'] = int(self.model_start_time.minute)

        lsm_restart_dirname = '.'  # os.path.dirname(noah_nlst['restart_filename_requested'])

        # Format - 2011082600 - no minutes
        lsm_restart_basename = 'RESTART.' + \
                               self.model_start_time.strftime('%Y%m%d%H') + '_DOMAIN1'

        lsm_restart_file = lsm_restart_dirname + '/' + lsm_restart_basename

        self.hrldas_times['noahlsm_offline']['restart_filename_requested'] = lsm_restart_file

    def _set_hydro_times(self):
        """Private method to set model run times in the hydro namelist"""

        hydro_restart_dirname = '.'  # os.path.dirname(hydro_nlst['restart_file'])
        # Format - 2011-08-26_00_00 - minutes
        hydro_restart_basename = 'HYDRO_RST.' + \
                                 self.model_start_time.strftime('%Y-%m-%d_%H:%M') + '_DOMAIN1'

        # Format - 2011-08-26_00_00 - seconds
        nudging_restart_basename = 'nudgingLastObs.' + \
                                 self.model_start_time.strftime('%Y-%m-%d_%H:%M:%S') + '.nc'

        # Use convenience function to return name of file with or without colons in name
        # This is needed because the model outputs restarts with colons, and our distributed
        # domains do not have restarts with colons so that they can be easily shared across file
        # systems
        hydro_restart_file = _check_file_exist_colon(os.getcwd(),hydro_restart_basename)
        nudging_restart_file = _check_file_exist_colon(os.getcwd(),nudging_restart_basename)

        self.hydro_times['hydro_nlist']['restart_file'] = hydro_restart_file
        self.hydro_times['nudging_nlist']['nudginglastobsfile'] = nudging_restart_file

    def _make_job_dir(self):
        """Private method to make the job directory"""
        if self.job_dir.is_dir():
            raise IsADirectoryError(str(self.job_dir) + 'already exists')
        else:
            self.job_dir.mkdir()

    def _write_run_script(self):
        """Private method to write a python script to run the job. This is used primarily for
        compatibility with job schedulers on HPC systems"""

        self._pickle()

        pystr = ""
        pystr += "# import modules\n"
        pystr += "import wrfhydropy\n"
        pystr += "import pickle\n"
        pystr += "import argparse\n"
        pystr += "import os\n"
        pystr += "import pathlib\n"

        pystr += "# Get path of this script to set working directory\n"
        pystr += "sim_dir = pathlib.Path(__file__)\n"
        pystr += "os.chdir(sim_dir.parent)\n"

        pystr += "parser = argparse.ArgumentParser()\n"
        pystr += "parser.add_argument('--job_id',\n"
        pystr += "                    help='The numeric part of the scheduler job ID.')\n"
        pystr += "args = parser.parse_args()\n"
        pystr += "\n"

        pystr += "#load job object\n"
        pystr += "job_dir = '.job_' + args.job_id + '/WrfHydroJob.pkl'\n"
        pystr += "job = pickle.load(open(job_dir,mode='rb'))\n"
        pystr += "#Run the job\n"
        pystr += "job._run()\n"
        pystr += "job._pickle()\n"

        pystr_file = 'run_job.py'
        with open(pystr_file,mode='w') as f:
            f.write(pystr)

    def _solve_model_start_end_times(self):
        """Private method ot get the model start and end times from the namelist"""
        noah_namelist = self.hrldas_namelist['noahlsm_offline']
        # model_start_time
        start_noah_keys = {'year': 'start_year', 'month': 'start_month',
                           'day': 'start_day', 'hour': 'start_hour', 'minute': 'start_min'}
        start_noah_times = {kk: noah_namelist[vv] for (kk, vv) in start_noah_keys.items()}
        model_start_time = datetime.datetime(**start_noah_times)

        # model_end_time
        if 'khour' in noah_namelist.keys():
            duration = {'hours': noah_namelist['khour']}
        elif 'kday' in noah_namelist.keys():
            duration = {'days': noah_namelist['kday']}
        else:
            raise ValueError("Neither KDAY nor KHOUR in namelist.hrldas.")
        model_end_time = model_start_time + datetime.timedelta(**duration)

        return model_start_time, model_end_time

    def _pickle(self):
        with self.job_dir.joinpath('WrfHydroJob.pkl').open(mode='wb') as f:
            pickle.dump(self, f, 2)

    @property
    def job_dir(self):
        """Path: Path to the run directory"""
        job_dir_name = '.job_' + self.job_id
        return pathlib.Path(job_dir_name)
