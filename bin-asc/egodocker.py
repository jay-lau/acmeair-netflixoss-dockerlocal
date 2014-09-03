#!/usr/bin/python

import sys
import getopt
import os
import logging
import subprocess
import signal
import time

log = None
DOCKERID_FILE_PREFIX="/tmp/.egodocker."

def set_log(loglevel, logfile):
    global log 
    log = logging.getLogger('ego-docker')
    if loglevel == "debug":
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.WARNING) 
    if logfile is not None:
        syslog = logging.FileHandler(logfile)
    else:
        syslog = logging.StreamHandler()
    syslog.setLevel(logging.DEBUG)
    syslog_format = logging.Formatter("%(asctime)s %(name)s[%(process)d] %(levelname)s : %(message)s")
    syslog.setFormatter(syslog_format)
    log.addHandler(syslog)
    return

def read_dockerid(cidfile):
    dockerid = None
    log.debug('read_dockerid: cidfile = %s' % cidfile)
    if cidfile is not None:
        try:
	    f = open(cidfile, "r")
            dockerid = f.read().strip()
            log.debug('read_dockerid: dockerid = %s ' % dockerid)
            f.close()
        except IOError:
            log.error('read_dockerid: failed to read docker id from file %s' % cidfile)
        except:
            log.error('read_dockerid: unexpected error %s' % sys.exc_info()[0])
    return dockerid

def cleanup_docker(dockerid):
    if dockerid is not None:
        log.info('cleanup_docker: stop container %s' % dockerid)
        subprocess.check_call(['docker', 'stop', '-t=2', dockerid])
        log.info('cleanup_docker: remove container %s' % dockerid)
#        subprocess.check_call(['docker', 'rm', '-f', dockerid])
        dockerid = None
    return

def cleanup_cidfile(cidfile):
    if  cidfile is not None:
        log.info('cleanup_cidfile: Cleaning up ego docker id file %s' % cidfile)
        subprocess.check_call(['rm', '-f', cidfile])
        cidfile = None
    return


def usage():
    print "Usage: egodocker.py command [arguments]\n"
    print "   commands:"
    print "       run [--debug] [--logfile logfile] [docker options] imagename [command]"
    print "             supported [docker options]:"
    print "              -c, --cpu-shares=0         CPU shares (relative weight)"
    print "              --dns=[]                   Set custom dns servers"
    print "              --dns-search=[]            Set custom dns search domains"
    print "              --entrypoint=\"\"            Overwrite the default entrypoint of the image"
    print "              --expose=[]                Expose a port from the container without publishing it to your host"
    print "              -h, --hostname=\"\"          Container host name"
    print "              -i                         Keep stdin open even if not attached"
    print "              --link=[]                  Add link to another container (name:alias)"
    print "              -m, --memory=\"\"            Memory limit (format: <number><optional unit>, where unit = b, k, m or g)"
    print "              --name=\"\"                  Assign a name to the container"
    print "              --net=\"\"                   Set the Network mode for the container"
    print "                                            'bridge': creates a new network stack for the container on the docker bridge"
    print "                                            'none': no networking for this container"
    print "                                            'container:<name|id>': reuses another container network stack"
    print "                                            'host': use the host network stack inside the contaner"
    print "              -p, --publish=[]           Publish a container's port to the host"
    print "                                            format: ip:hostPort:containerPort | ip::containerPort | hostPort:containerPort"
    print "                                            (use 'docker port' to see the actual mapping)"
    print "              -P, --publish-all=false    Publish all exposed ports to the host interfaces"
    print "              --privileged=false         Give extended privileges to this container"
    print "              -t                         Allocate a pseudo-tty"
    print "              -u, --user=\"\"              Username or UID"
    print "              -v, --volume=[]            Bind mount a volume (e.g. from the host: -v /host:/container, from docker: -v /container)"
    print "              --volumes-from=[]          Mount volumes from the specified container(s)"
    print "              -w, --workdir=\"\"           Working directory inside the container"
    print ""
    print "       stop [--debug] [--logfile logfile] "
    print "       help\n"
    return

def get_cidfile(cid):
    return DOCKERID_FILE_PREFIX + cid


def stop_docker(argv):
    cid = None
    logfile = None
    loglevel = "warning"  
    try:
        opts, args = getopt.getopt(argv, "", ["cid=", "debug", "logfile="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '--debug':
            loglevel = "debug"
        elif opt == "--cid":
            cid = arg
        elif opt == "--logfile":
            logfile = arg
        else:
            pass

    set_log(loglevel, logfile)
    if cid is None:
        cid = os.getenv("EGO_CONTAINER_ID")
        if cid is None:
            print "Must define ego container id either by setting EGO_CONTAINER_ID environment variable or by using --cid option"
            sys.exit(2)

    cidfile = get_cidfile(cid)
    dockerid = read_dockerid(cidfile)
    if dockerid is not None:
        cleanup_docker(dockerid)
    else:
        pass
    log.debug('stop_docker')
    return  

def run_with_settings(cid, cidfile, dockeroptions=[], args=[], netflag=0, nameflag=0):
    cmd = [ 'run', '--cidfile', cidfile, '--rm']
    #if netflag == 0 :
    #    cmd += ['--net', 'host']
    if nameflag == 0 :
        cmd += ['--name', 'egoid_%s' % cid]
    for k,v in os.environ.items():
        if k == 'PATH':
            continue
        cmd += [ '-e', '%s=%s' % (k,v) ]
    argv = ['docker'] + cmd + dockeroptions + args

    log.debug('run_with_settings: ARGV ' + ' '.join(str(arg) for arg in argv))
    proc = subprocess.Popen(argv)
    proc.wait() 
    log.info ('run_with_setting: Docker exits with code: %d' % proc.returncode)

def run_docker(argv):
    loglevel = "warning"
    cid = None
    logfile = None 
    dockeroptions = []
    netflag = 0
    nameflag = 0
    
    try:
        opts, args = getopt.getopt(argv, "c:h:m:p:Pu:v:w:it",["cid=", "debug", "logfile=", "cpu-shares=", "dns=", "dns-search=", "entrypoint=", "expose=", "hostname=", "link=", "memory=","name=", "net=", "publish=", "publish-all=", "privileged=", "sig-proxy=", "user=", "volume=", "workdir="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '--debug':
            loglevel = "debug"
        elif opt == "--cid":
            cid = arg
        elif opt == "--logfile":
            logfile = arg
        elif opt in ("-c", "--cpu-shares"):
            dockeroptions += ['-c', arg]
        elif opt in ("-h", "--hostname"):
            dockeroptions += ['-h', arg]
        elif opt == "--dns":
            dockeroptions += ['--dns', arg]
        elif opt == "--dns-search":
            dockeroptions += ['--dns-search', arg]
        elif opt == "--entrypoint":
            dockeroptions += ['--entrypoint', arg]
        elif opt == "--expose":
            dockeroptions += ['--expose', arg]
        elif opt == "--link":
            dockeroptions += ['--link', arg]
        elif opt in ("-m", "--memory"):
            dockeroptions += ['-m', arg]
        elif opt == "-i" :
            dockeroptions += ['-i']
        elif opt == "-t" :
            dockeroptions += ['-t']
        elif opt == "--name":
            dockeroptions += ['--name', arg]
            nameflag = 1
        elif opt == "--net":
            dockeroptions += ['--net', arg]
            netflag = 1
        elif opt in ("-p", "--publish"):
            dockeroptions += ['-p', arg]
        elif opt in ("-P", "--publish-all"):
            if opt == "-P":
                dockeroptions += ['-P']
            elif arg == "true": 
                dockeroptions += ['-P']
            else:
                pass
        elif opt == "--privileged" and arg == "true":
            dockeroptions += ['--privileged=true']
        elif opt in ("-u", "--user"):
            dockeroptions += ['-u', arg]
        elif opt in ("-v", "--volume"):
            dockeroptions += ['-v', arg]
        elif opt in ("-w", "--workdir"):
            dockeroptions += ['-w', arg]
        else:
            pass
    set_log(loglevel, logfile)

    if cid is None:
        cid = os.getenv("EGO_CONTAINER_ID")
        if cid is None:
            print "Must define ego container id either by setting EGO_CONTAINER_ID environment variable or by using --cid option"
            sys.exit(2)
        
    cidfile = get_cidfile(cid)
    run_with_settings(cid, cidfile, dockeroptions, args, netflag, nameflag)
    cleanup_cidfile(cidfile)
    time.sleep(2)
    log.debug('run_docker')
    return

def handler(signum, _):
    log.info('Exiting due to signal: '+str(signum))
    exit(-signum)
     
def main(argv):
    signal.signal(signal.SIGINT,  handler)
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGABRT, handler)
    signal.signal(signal.SIGPIPE, handler)
    signal.signal(signal.SIGSEGV, handler)

    if argv[0] == "run":
        run_docker(argv[1:])
    elif argv[0] == "stop":
        stop_docker(argv[1:])
    elif argv[0] == "help":
        usage()
    else:
        print "Unrecognized command option"
        usage()
        sys.exit(2)
    return

if __name__ == "__main__":
    main(sys.argv[1:])
