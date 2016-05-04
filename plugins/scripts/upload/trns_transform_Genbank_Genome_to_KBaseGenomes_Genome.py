#!/usr/bin/env python

# standard library imports
import sys
import os
import logging
import subprocess

# 3rd party imports
# None

# KBase imports
import biokbase.Transform.script_utils as script_utils


def transform(shock_service_url=None, workspace_service_url=None,
              workspace_name=None, object_name=None, contigset_object_name=None,
              input_directory=None, working_directory=None, 
              level=logging.INFO, logger=None):
    """
    Transforms Genbank file to KBaseGenomes.Genome and KBaseGenomes.ContigSet objects.
    
    Args:
        shock_service_url: If you have shock references you need to make.
        workspace_service_url: KBase Workspace URL
        workspace_name: Name of the workspace to save the data to
        object_name: Name of the genome object to save
        contigset_object_name: Name of the ContigSet object that is created with this Genome
        input_directory: A directory of either a genbank file or a directory of partial genome files to merge
        working_directory: A directory where you can do work
    
    Returns:
        Workspace objects saved to the user's workspace.
    
    Authors:
        Shinjae Yoo, Marcin Joachimiak, Matt Henderson
    """

    if logger is None:
        logger = script_utils.stdoutlogger(__file__, logging.INFO)

    logger.info("Starting transformation of Genbank to KBaseGenomes.Genome")

    # TODO get the classpath definition out into the config instead
    KB_TOP = os.environ["KB_TOP"]

    classpath = ["{}/lib/jars/kbase/transform/kbase_transform_deps.jar".format(KB_TOP),
                 "{}/lib/jars/kbase/genomes/kbase-genomes-20140411.jar".format(KB_TOP),
                 "{}/lib/jars/kbase/common/kbase-common-0.0.6.jar".format(KB_TOP),
                 "{}/lib/jars/jackson/jackson-annotations-2.2.3.jar".format(KB_TOP),
                 "{}/lib/jars/jackson/jackson-core-2.2.3.jar".format(KB_TOP),
                 "{}/lib/jars/jackson/jackson-databind-2.2.3.jar".format(KB_TOP),
                 "{}/lib/jars/kbase/auth/kbase-auth-1398468950-3552bb2.jar".format(KB_TOP),
                 "{}/lib/jars/kbase/workspace/WorkspaceClient-0.2.0.jar".format(KB_TOP)]

    for p in classpath:
        try:
            assert os.path.exists(p)
        except AssertionError, e:
            raise IOError("Unable to find classpath library {}".format(p))

    argslist = ["--shock_url {0}".format(shock_service_url),
                "--workspace_service_url {0}".format(workspace_service_url),
                "--workspace_name {0}".format(workspace_name),
                "--object_name {0}".format(object_name),
                "--working_directory {0}".format(working_directory),
                "--input_directory {0}".format(input_directory)]

    if contigset_object_name is not None:
        argslist.append("--contigset_object_name {0}".format(contigset_object_name))

    arguments = ["java",
                 "-classpath", ":".join(classpath),
                 "us.kbase.genbank.ConvertGBK",
                 " ".join(argslist)]

    # TODO get this working without shell=True, possibly more at work here than just environment variables
    tool_process = subprocess.Popen(" ".join(arguments), shell=True)
    tool_process.wait()

    exit_status = tool_process.returncode
    sys.stderr.write("Tool execution returned exit status {}".format(exit_status))

    if exit_status != 0:
        raise Exception("Transformation from Genbank.Genome to KBaseGenomes.Genome failed on {0}".format(input_directory))

    logger.info("Transformation from Genbank.Genome to KBaseGenomes.Genome completed.")


if __name__ == "__main__":
    script_details = script_utils.parse_docs(transform.__doc__)

    parser = script_utils.ArgumentParser(prog=__file__, 
                                     description=script_details["Description"],
                                     epilog=script_details["Authors"])
    parser.add_argument("--shock_service_url", 
                        help=script_details["Args"]["shock_service_url"], 
                        action="store", 
                        type=str, 
                        nargs="?", 
                        required=True)
    parser.add_argument("--workspace_service_url", 
                        help=script_details["Args"]["workspace_service_url"], 
                        action="store", 
                        type=str, 
                        nargs="?", 
                        required=True)
    parser.add_argument("--workspace_name", 
                        help=script_details["Args"]["workspace_name"], 
                        action="store", 
                        type=str, 
                        nargs="?", 
                        required=True)
    parser.add_argument("--object_name", 
                        help=script_details["Args"]["object_name"], 
                        action="store", 
                        type=str, 
                        nargs="?", 
                        required=True)
    parser.add_argument("--contigset_object_name", 
                        help=script_details["Args"]["contigset_object_name"], 
                        action="store", 
                        type=str, 
                        nargs="?", 
                        required=False)
    parser.add_argument("--input_directory", 
                        help=script_details["Args"]["input_directory"], 
                        action="store", 
                        type=str, 
                        nargs="?", 
                        required=True)
    parser.add_argument("--working_directory", 
                        help=script_details["Args"]["working_directory"], 
                        action="store", 
                        type=str, 
                        nargs="?", 
                        required=True)
    
    args, unknown = parser.parse_known_args()
    returncode = 0
        
    try:
        transform(shock_service_url=args.shock_service_url,
                  workspace_service_url=args.workspace_service_url,
                  workspace_name=args.workspace_name,
                  object_name=args.object_name,
                  contigset_object_name=args.contigset_object_name,
                  input_directory=args.input_directory,
                  working_directory=args.working_directory)
    except Exception, e:
        logger = script_utils.stderrlogger(__file__, logging.INFO)
        logger.exception(e)
        returncode = 1
    
    sys.stdout.flush()
    sys.stderr.flush()
    os.close(sys.stdout.fileno())
    os.close(sys.stderr.fileno())
    sys.exit(returncode)
    