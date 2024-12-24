#!/bin/python
#
# written by iskolbin@gmail.com, 2024

import sys, io
    
if len(sys.argv) < 4:
    print('Usage:\n  python lammps2xyz.py <INPUT_WORLD_FILE> <PARAMS> <OUTPUT_FILE>\nwhere PARAMS either .params file or comma-separated list of atoms\nExample:\n  python lammps2xyz.py o2.world o2.params o2.xyz\n  lammps2xyz.py o2.world N,C,O,C,C,N,H,H,H o2.xyz')
    quit(1)
else:
    in_world = sys.argv[1]
    in_params = sys.argv[2]
    out = sys.argv[3]

IDX_TO_TYPE = []

if len(in_params.split(',')) > 1:
    IDX_TO_TYPE = in_params.split(',')
else:
    with open(in_params, 'r') as in_params_file:
        state = 'read_atoms_types_count'
        skip_lines = 0
        for line in in_params_file:
            if skip_lines > 0: skip_lines -= 1
            elif state == 'read_atoms_types_count':
                if line.strip().endswith('atom types'):
                    atoms_types_count = int(line.split(' ')[0])
                    state = 'find_atoms_position'
            elif state == 'find_atoms_position' and line.startswith('PairIJ Coeffs'):
                skip_lines = 1
                state = 'read_atom_types'
            elif state == 'read_atom_types':
                ss = line.split(' ')
                if len(IDX_TO_TYPE) >= atoms_types_count or len(ss) < 8: break
                if int(ss[0]) == len(IDX_TO_TYPE)+1: IDX_TO_TYPE.append(ss[6])
        assert(len(IDX_TO_TYPE) == atoms_types_count)

with open(in_world, 'r') as in_world_file, open(out, 'w+') as out_file:
    state = 'read_atoms_count'
    skip_lines = 0
    for line in in_world_file:
        if skip_lines > 0:
            skip_lines -= 1    
        elif state == 'read_atoms_count':
            if line.strip().endswith('atoms'):
                atoms_count = int(line.split(' ')[0])
                out_file.write(('%d\n\n') % (atoms_count))
                state = 'find_atoms_position'
        elif state == 'find_atoms_position' and line.strip() == "Atoms # full":
            state = 'read_atoms'
            skip_lines = 1
        elif state == 'read_atoms':
            ss = line.split(' ')
            if len(ss) < 2: break
            out_file.write(('%s %f %f %f\n') % (IDX_TO_TYPE[int(ss[2]) - 1], float(ss[4]), float(ss[5]), float(ss[6])))
