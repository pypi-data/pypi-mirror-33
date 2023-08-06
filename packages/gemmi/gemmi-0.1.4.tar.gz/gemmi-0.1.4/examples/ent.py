#!/usr/bin/env python

import sys
import gemmi

def run(path):
    st = gemmi.read_structure(path)
    for chain in st[0]:
        if st.get_entity_of(chain).entity_type == gemmi.EntityType.Polymer:
            if len(chain) < 8:
                print(st.name, chain.name, chain.auth_name, len(chain),
                      '-'.join(x.name for x in chain),
                      str(st.get_entity_of(chain).polymer_type)[12:])

def main():
    for arg in sys.argv[1:]:
        for path in gemmi.CoorFileWalk(sys.argv[1]):
            run(path)

if __name__ == '__main__':
    main()
