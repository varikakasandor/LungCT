#!/usr/bin/env python

import os
import numpy as np
import sys
from mpi4py import MPI
import zipfile

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
n_ranks = comm.Get_size()

def print0(*args, **kwargs):
    if rank == 0:
        print(*args, **kwargs)


def getUnzippedCases(path_to_zips, path_to_unzipped_dirs):

    zips = np.sort([z for z in os.listdir(path_to_zips) if z.endswith('.zip')])

    unzipped_cases = []
    non_zips = []
    num_zipf = len(zips)
    for zipf_idx, zipf in enumerate(zips):

        print0(f'\rChecking for unzipped cases: {int((zipf_idx + 1) / num_zipf * 100)} %', end='')

        case_id = zipf.split('.')[0]

        folders_in_zip = []
        try:
            zip_data = zipfile.ZipFile(os.path.join(path_to_zips, zipf))
        except:
            non_zips.append(case_id)
            continue
        zip_info = zip_data.infolist()
        for zip_elem_info in zip_info:
            if zip_elem_info.is_dir():
                folders_in_zip.append(zip_elem_info.filename.strip('/'))
        folders_in_zip = np.sort(folders_in_zip).astype(np.str)

        if not os.path.exists(os.path.join(path_to_unzipped_dirs, case_id)):
            unzipped_cases.append(case_id)
        else:
            folders_unzipped = []
            for acq in os.listdir(os.path.join(path_to_unzipped_dirs, case_id)):
                if os.path.isdir(os.path.join(path_to_unzipped_dirs, case_id, acq)):
                    folders_unzipped.append(acq)
                elif acq.endswith('.npz') and os.path.exists(os.path.join(path_to_unzipped_dirs, case_id, f'{acq.split(".")[0]}.json')):
                    folders_unzipped.append(acq.split(".")[0])
            folders_unzipped = np.sort(folders_unzipped).astype(np.str)
            txt_exists = os.path.exists(os.path.join(path_to_unzipped_dirs, case_id, f'{case_id}.txt'))

            if np.any(folders_unzipped != folders_in_zip) or not txt_exists:
                unzipped_cases.append(case_id)
    print0()

    return unzipped_cases, non_zips

def checkZips(path_to_zips, case_ids):
    
    # Check if each zip has a txt
    zips = np.sort([z for z in os.listdir(path_to_zips) if z.endswith('.zip') if z.split('.')[0] in case_ids])
    txts = np.sort([t for t in os.listdir(path_to_zips) if t.endswith('.txt') if t.split('.')[0] in case_ids])

    zips_set = set([z.split('.')[0] for z in zips])
    txts_set = set([t.split('.')[0] for t in txts])
    txts_missing = np.sort(list(set.difference(zips_set, txts_set)))
    zips_missing = np.sort(list(set.difference(txts_set, zips_set)))
    if len(txts_missing) > 0 or len(zips_missing) > 0:
        print0(f'There are zips/txts missing:')
        if len(txts_missing) > 0:
            print0(f'  - missing txts:')
            for mtxt in txts_missing:
                print0(f'    - {mtxt}')
        if len(zips_missing) > 0:
            print0(f'  - missing zips:')
            for mzip in zips_missing:
                print0(f'    - {mzip}')
        if_cont = '' == input(f'\n\n Do you want to ignore these cases and proceed? If yes, press enter.')
        cases_to_ignore = np.sort(list(set.union(set(zips_missing), set(txts_missing))))
    else:
        if_cont = True
        cases_to_ignore = np.array([])

    return if_cont, cases_to_ignore


def unzip(path_to_zips, path_to_unzipped_dirs, case_ids=None):

    # Collect case ids
    if not case_ids:
        case_ids = getUnzippedCases(path_to_zips, path_to_unzipped_dirs)
    num_case_ids = len(case_ids)

    # Check if each zip has a txt
    if rank == 0:
        zips_ok, cases_to_ignore = checkZips(path_to_zips, case_ids)
    else:
        zips_ok = None
        cases_to_ignore = None
    zips_ok = comm.bcast(zips_ok, root=0)
    cases_to_ignore = comm.bcast(cases_to_ignore, root=0)

    if not zips_ok:
        sys.exit()

    # Split case ids and use mpi
    nums = [0]
    for i in range(n_ranks):
        nums.append((num_case_ids + (n_ranks - (i + 1))) // n_ranks)
    nums = np.cumsum(nums)
    case_ids_mpi = case_ids[nums[rank] : nums[rank + 1]]
    num_case_ids = len(case_ids_mpi)
    
    # Unzip zip files into case directory and copy txt to there
    for case_id in case_ids_mpi:

        if case_id not in cases_to_ignore:

            if os.path.exists(os.path.join(path_to_unzipped_dirs, case_id)):
                os.system(f'rm -r {os.path.join(path_to_unzipped_dirs, case_id)}/*')
            os.makedirs(os.path.join(path_to_unzipped_dirs, case_id), exist_ok=True)

            file_path = os.path.join(path_to_zips, case_id)
            os.system(f'unzip {file_path}.zip -d {os.path.join(path_to_unzipped_dirs, case_id)}')
            os.system(f'cp {file_path}.txt {os.path.join(path_to_unzipped_dirs, case_id)}')


if __name__ == '__main__':
    print("STARTED")
    # Define paths
    path_to_zips = '/mnt/idms/PROJECTS/Lung/Tudo-Ulyssys'
    path_to_unzipped_dirs = '/mnt/idms/PROJECTS/Lung/Tudo-Ulyssys-Unzipped'

    # Check for unzipped and/or corrupt cases and print
    unzipped_cases, non_zips = getUnzippedCases(path_to_zips, path_to_unzipped_dirs)
    if len(unzipped_cases) > 0:
        unzipped_cases_table = []
        i = 0
        while i + 1 <= len(unzipped_cases):
            unzipped_cases_table_row = []
            for _ in range(25):
                if i < len(unzipped_cases):
                    unzipped_cases_table_row.append(unzipped_cases[i])
                i += 1
            unzipped_cases_table.append(', '.join(unzipped_cases_table_row))
        print0("The following cases aren't unzipped yet:")
        for unzipped_cases_row in unzipped_cases_table:
            print0(f'   {unzipped_cases_row}')
    else:
        print0('No cases found to unzip!')

    if len(non_zips) > 0:
        print0("The following cases aren't zip files:")
        for nonzip_case in non_zips:
            print0(f'   {nonzip_case}')
    
    # Ask if still want to continue (bad zips will be ignored)
    if  len(unzipped_cases) > 0:
        if rank == 0:
            print()
            if len(non_zips) > 0:
                if_cont_in = input('Do you want to ignore bad zips and continue? If yes, press enter.')
            else:
                if_cont_in = input('Do you want to continue? If yes, press enter.')
            print('\n')
        else:
            if_cont_in = None
        if_cont_in = comm.bcast(if_cont_in, root=0)
        
        # Unzip
        if if_cont_in == '':
            unzip(path_to_zips, path_to_unzipped_dirs, case_ids=unzipped_cases)