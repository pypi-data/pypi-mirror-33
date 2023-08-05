import os, sys, string, time

def HandleCommandLine(cls, command, customInstallOptions = "", customOptionHandler = None):
    """Utility function allowing services to process the command line.
    Allows standard commands such as 'start', 'stop', 'debug', 'install' etc.
    Install supports 'standard' command line options prefixed with '--', such as
    --username, --password, etc.  In addition,
    the function allows custom command line options to be handled by the calling function.
    """
    err = 0

    
    serviceName = cls._svc_name_
    serviceDisplayName = cls._svc_display_name_
    serviceClassString = "aservice"

    # Pull apart the command line
    import getopt
    opts = []
    args = []
    
    userName = None
    password = None
    startup = None
    delayedstart = None
    interactive = None
    waitSecs = 0
    for opt, val in opts:
        if opt=='--username':
            userName = val
        elif opt=='--password':
            password = val
        elif opt=='--wait':
            try:
                waitSecs = int(val)
            except ValueError:
                print("--wait must specify an integer number of seconds.")
                

    arg=command
    knownArg = 0
    # First we process all arguments which pass additional args on
    if arg=="start":
        knownArg = 1
        print("Starting service %s" % (serviceName))
        try:
            print("start")
        except Exception as ex:
            print("Error starting service:", ex)
            

    elif arg=="restart":
        print("restart")
        knownArg = 1
        print("Restarting service %s" % (serviceName))
        
    
    #if not knownArg and len(args)!=1:
    #    usage() # the rest of the cmds don't take addn args

    if arg=="install":
        print("Installing service %s" % (serviceName,))
        # Note that we install the service before calling the custom option
        # handler, so if the custom handler fails, we have an installed service (from NT's POV)
        # but is unlikely to work, as the Python code controlling it failed.  Therefore
        # we remove the service if the first bit works, but the second doesnt!
        
    if arg == "update":
        print("Changing service configuration")
        
    elif arg=="remove":
        knownArg = 1
        print("Removing service %s" % (serviceName))
        
    elif arg=="stop":
        knownArg = 1
        print("Stopping service %s" % (serviceName))
        
    if not knownArg:
        err = -1
        print("Unknown command - '%s'" % arg)
        #usage()
    return err



def handle_command(commands, app_name, app_id, script_path): 
    service_command = None
    print("yy")
    if commands:

        print("x", commands)
        service_commands = commands
        service_commands += ["dummy"]
        HandleCommandLine(aservice, commands[0])

