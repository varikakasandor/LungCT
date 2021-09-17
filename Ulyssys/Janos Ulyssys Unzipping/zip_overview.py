#!/usr/bin/env python

import zipfile
import os
import json
import numpy as np

def overview(path_to_zips, path_results):

    zips = np.sort([z for z in os.listdir(path_to_zips) if z.endswith('.zip')])

    num_zipf = len(zips)
    overview_results = {}
    for zipf_idx, zipf in enumerate(zips):

        print(f'\rChecking for unzipped cases: {int((zipf_idx + 1) / num_zipf * 100)} %', end='')

        case_id = zipf.split('.')[0]

        try:
            zip_data = zipfile.ZipFile(os.path.join(path_to_zips, zipf))
        except:
            overview_results[case_id] = None
            continue
        zip_info = zip_data.infolist()
        zip_dirs = []
        files_corresps = {}
        for zip_elem_info in zip_info:
            if zip_elem_info.is_dir():
                new_zip_dir = zip_elem_info.filename.strip('/')
                zip_dirs.append(new_zip_dir)
                files_corresps[new_zip_dir] = 0
        for zip_elem_info in zip_info:
            if not zip_elem_info.is_dir():
                corresp_found = False
                assert zip_elem_info.filename.endswith('.dcm'), f'File {zip_elem_info.filename} is not dicom file!'
                for zip_dir in zip_dirs:
                    if zip_dir in zip_elem_info.filename:
                        # If there would be a folder in a folder, this should throw an error:
                        assert not corresp_found, f'Correspondence ambigous for element {zip_elem_info.filename}!'
                        files_corresps[zip_dir] += 1
                        corresp_found = True
        overview_results[case_id] = {
            'num_dirs': len(zip_dirs),
            'num_files': files_corresps
        }
    print()

    overview_results_final = {
        'path': path_to_zips,
        'stats': overview_results
    }

    with open(os.path.join(path_results, 'zips_overview.json'), 'w') as jsonf:
        json.dump(overview_results_final, jsonf, indent=4)

def analyzeOverview(path_results):
    with open(os.path.join(path_results, 'zips_overview.json')) as jsonf:
        overview_results_final = json.load(jsonf)
    
    overview_results = overview_results_final['stats']
    
    num_dirs = [dir_info['num_dirs'] for dir_info in overview_results.values() if dir_info]
    num_files = [sum(list(dir_info['num_files'].values())) for dir_info in overview_results.values() if dir_info]
    dir_nums, dir_nums_counts = np.unique(num_dirs, return_counts=True)
    print(f'Zip dirs overview in {overview_results_final["path"]}:')
    print(f'  Found {len(overview_results):,d} zip folders.')
    print(f'    - of which {len(overview_results) - len(num_dirs):,d} are bad zip folders')
    for dn, c in zip(dir_nums, dir_nums_counts):
        print(f'    - of which {c:,d} contain {dn:,d} folders')
    print(f'  Found {sum(num_files):,d} files in total.')
    num_files_detailed = []
    for case_stats in overview_results.values():
        if case_stats:
            num_files_detailed.extend(case_stats['num_files'].values())
    case_stats_hist_counts, case_stats_hist_bins = np.histogram(num_files_detailed)
    for c_idx, c in enumerate(case_stats_hist_counts):
        print(f'  - which belong in {c} cases to acqusitions with {int(round(case_stats_hist_bins[c_idx])):,d}...{int(round(case_stats_hist_bins[c_idx + 1])):,d} files')

def getCorruptZipFolders(path_results):
    with open(os.path.join(path_results, 'zips_overview.json')) as jsonf:
        overview_results_final = json.load(jsonf)
    
    overview_results = overview_results_final['stats']

    bad_zips = [case_id for case_id, stats in overview_results.items() if not stats]

    print('Following zips are bad:')
    for bad_zip in bad_zips:
        print(f'  - {bad_zip}')

if __name__ == '__main__':

    path_to_zips = '/mnt/idms/PROJECTS/Lung/Tudo-Ulyssys'
    path_results = '/mnt/idms/home/andor'

    overview(path_to_zips, path_results)
    analyzeOverview(path_results)
    getCorruptZipFolders(path_results)
