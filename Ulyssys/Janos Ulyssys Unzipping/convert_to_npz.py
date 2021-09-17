#!/usr/bin/env python

import sys
import os
import json
import pydicom as dcm
import numpy as np
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
n_ranks = comm.Get_size()

def print0(*args):
    if rank == 0:
        print(*args)

def getUnconvertedCases(path_to_cases, path_to_zips_overview):

    with open(path_to_zips_overview) as jsonf:
        zips_overview = json.load(jsonf)

    case_ids = np.sort(os.listdir(path_to_cases))

    unconverted_cases = []
    for case_id in case_ids:
        for acquisition_id in zips_overview['stats'][case_id]['num_files'].keys():
            path_npz = os.path.join(path_to_cases, case_id, f'{acquisition_id}.npz')
            if not os.path.exists(path_npz):
                if case_id not in unconverted_cases:
                    unconverted_cases.append(case_id)

    return unconverted_cases


def convert(path_to_cases, case_ids=None):
    
    print0(f'Looking for cases in: {path_to_cases}')

    if not case_ids and not isinstance(case_ids, list):
        case_ids = np.sort(os.listdir(path_to_cases))
    num_case_ids = len(case_ids)

    if num_case_ids > 0:


        # Split case ids and use mpi
        nums = [0]
        for i in range(n_ranks):
            nums.append((num_case_ids + (n_ranks - (i + 1))) // n_ranks)
        nums = np.cumsum(nums)
        case_ids_mpi = case_ids[nums[rank] : nums[rank + 1]]
        num_case_ids = len(case_ids_mpi)

        for case_id_idx, case_id in enumerate(case_ids_mpi):

            acquisition_ids = np.sort([d for d in os.listdir(os.path.join(path_to_cases, case_id)) if os.path.isdir(os.path.join(path_to_cases, case_id, d))])
            num_acquisition_ids = len(acquisition_ids)
            for acquisition_id_idx, acquisition_id in enumerate(acquisition_ids):
                print(f'Case: {case_id} ({case_id_idx + 1}/{num_case_ids}), acquisition: {acquisition_id} ({acquisition_id_idx + 1}/{num_acquisition_ids}): reading...')

                ct_scans = []
                
                slice_ids = np.sort([i for i in os.listdir(os.path.join(path_to_cases, case_id, acquisition_id)) if i.endswith('.dcm')])
                num_slice_ids = len(slice_ids)
                for slice_id_idx, slice_id in enumerate(slice_ids):

                    meta_data = dcm.dcmread((os.path.join(path_to_cases, case_id, acquisition_id, slice_id)))
                    if slice_id_idx == 0:
                        meta_data_json = meta_data.to_json_dict()
                        del meta_data_json['7FE00010'] # drop pixel data
                        with open(os.path.join(path_to_cases, case_id, f'{acquisition_id}.json'), 'w') as jsonf:
                            json.dump(meta_data_json, jsonf, indent=4)
                    raw_slice_data = dcm.read_file((os.path.join(path_to_cases, case_id, acquisition_id, slice_id)))
                    ct_scans.append(tuple((meta_data[0x0020, 0x0013].value, raw_slice_data.pixel_array)))
                
                ct_scan_shape = tuple((
                    len(ct_scans),
                    *ct_scans[0][1].shape
                ))

                ct_scan_array = np.zeros(ct_scan_shape)

                print(f'Case: {case_id} ({case_id_idx + 1}/{num_case_ids}), acquisition: {acquisition_id} ({acquisition_id_idx + 1}/{num_acquisition_ids}): populating array...')
                for ct_scan_idx, ct_scan in enumerate(ct_scans):
                    ct_scan_array[ct_scan[0] - 1] = ct_scan[1]
                ct_scan_array_shape_range = np.arange(len(ct_scan_array.shape))
                ct_scan_array = np.transpose(ct_scan_array, [*ct_scan_array_shape_range[1:], ct_scan_array_shape_range[0]])

                print(f'Case: {case_id} ({case_id_idx + 1}/{num_case_ids}), acquisition: {acquisition_id} ({acquisition_id_idx + 1}/{num_acquisition_ids}): saving...')
                np.savez_compressed(
                    os.path.join(path_to_cases, case_id, f'{acquisition_id}.npz'),
                    **{acquisition_id: ct_scan_array}
                )

                os.system(f'rm -r {os.path.join(path_to_cases, case_id, acquisition_id)}')

    else:
        print0("Didn't find anything to convert!")

if __name__ == '__main__':

    # path_to_cases = '/srv/data/lung/SZTAKI/superres/unzipped'
    # path_to_zips_overview = '/srv/data/lung/SZTAKI/superres/stats/zip_overview.json'
    path_to_cases = '/mnt/idms/PROJECTS/Lung/Tudo-Ulyssys-Unzipped'
    path_to_zips_overview = '/mnt/idms/home/andor/zips_overview.json'

    unconverted_cases = getUnconvertedCases(path_to_cases, path_to_zips_overview)
    unconverted_cases_table = []
    i = 0
    while i + 1 <= len(unconverted_cases):
        unconverted_cases_table_row = []
        for _ in range(25):
            if i < len(unconverted_cases):
                unconverted_cases_table_row.append(unconverted_cases[i])
            i += 1
        unconverted_cases_table.append(', '.join(unconverted_cases_table_row))
    print0("The following cases aren't converted yet:")
    for unconverted_cases_row in unconverted_cases_table:
        print0(f'   {unconverted_cases_row}')

    # Ask if still want to continue (bad zips will be ignored)
    if rank == 0:
        if_cont_in = input('\nDo you want to continue? If yes, press enter.')
        print('\n')
    else:
        if_cont_in = None
    if_cont_in = comm.bcast(if_cont_in, root=0)
    
    # Convert
    if if_cont_in == '':
        convert(path_to_cases, case_ids=unconverted_cases)
