from .constants import CONFIG
from .job import Job
import subprocess

class TORQUE(Job):

    config = CONFIG['torque']

    
    def __init__(self, script, script_type = None, name = None, 
                 nodes = None, ppn = None, walltime = None, 
                 node_type = None, account = None ):

        super().__init__( self, script, script_type )

        self.command = ''
        self.dependents = []
        self.nodes = nodes
        self.ppn = ppn

    def set_config( self, **kwargs ):
        
        allowed_keys = ['nodes', 'ppn', 'walltime', 'script', 'account', 
            'node_type' ]

        self.__dict__.update( (k,v) for k, v in kwargs.iteritems() if k in allowed_keys )
    
    def depends( self, id, type ):
        if type not in config['supported_dep']:
            raise ValueError('type not supported.')

        self.dependents.append( [id, type] )

    def submit( self, dry_run ):
         
        dep = defaultdict(list)
        # Create the command line arguments
        args = []
        # append executable name
        if self._sched_override:
            args.append( self._sched_type )
        else:
            args.append( config['exe'] )

        # Add PBS dependencies
        for dep in self.dependents:
            args.append( config['depends'].format( dep[0] + config['delimit'] + dep[1] ) )

        # Add node requirements
        if self.nodes:
            args.append( config['resource'] )
            args.append( 'nodes={}'.format( self.nodes ) )
        if self.ppn:
            args.append( config['resource'] )
            args.append( 'ppn={}'.format( self.ppn ) + 
                '{}'.format(config['delimit'] + self.node_type) if self.node_type
                else '' )
        if self.walltime:
            args.append( config['resource'] )
            args.append( self.walltime )
        if self.account:
            args.append( config['account'] )
            args.append( self.account )
        

        args.append( self.script )

        # We cd to the location of the PBS script because PBS will print out
        # log files in its current working directory. Just keep them all in
        # one place.
        os.chdir( os.path.dirname( self.script ) )

        if dry_run:
            print('\nDry run submission.')

        print( ' '.join(args) )
        
        if not dry_run:
            subproc = subprocess.Popen( args, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
            retcode = subproc.wait()

            # Retrieve the scheduler ID
            stderrFile = subproc.stderr
            sub_stderr = stderrFile.read()
            stdoutFile = subproc.stdout
            sub_stdout = stdoutFile.read()

            if stdout:
                stdout.write( sub_stdout )
            if stderr:
                stderr.write( sub_stderr )
            if retcode != 0:
                print( sub_stderr )
                print( sub_stdout )
                raise RuntimeError('Process exited with retcode {}'.format(retcode))

            self._sched_id = sub_stdout.strip().decode('UTF-8')
        else:
            # Use internal identifier instead of scheduler-supplied ID
            self._sched_id = self._id
 
