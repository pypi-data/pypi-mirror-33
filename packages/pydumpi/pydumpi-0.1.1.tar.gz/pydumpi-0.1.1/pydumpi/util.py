from pathlib import Path
from os import listdir


def read_meta_file(file_name):
    with open(file_name) as meta_file:
        return dict([line.strip().split("=") for line in meta_file])


def trace_files_from_dir(directory):
    # find meta info
    file_names = listdir(directory)
    meta_file = [f for f in file_names if "meta" in f]

    if not meta_file:
        raise ValueError("Could not find a meta file in given directory.")

    meta_info = read_meta_file(Path(directory) / meta_file[0])
    
    # filter out any non-binary files
    prefix = meta_info["fileprefix"]
    traces = [f for f in file_names if f.startswith(prefix) and f.endswith(".bin")]

    # abort if there are files missing
    num_procs = int(meta_info["numprocs"])
    if len(traces) != num_procs:
        raise ValueError("Some binary traces are missing.")

    # sort by proc id and prepend directory
    traces = sorted(traces, key=lambda t: int(t[len(prefix)+1:len(t)-len(".bin")]))
    return [Path(directory) / trace for trace in traces]
