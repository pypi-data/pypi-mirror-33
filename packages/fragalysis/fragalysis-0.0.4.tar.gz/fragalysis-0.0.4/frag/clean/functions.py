def align_structure(structure_one, other_structures, align_residues):
    """
    Need to be able to robustly align two structures (normally > 10 to a reference structure).
    Maybe wrap Biojava (or even NGL) for this - not sure.
    :return:
    """
    pass


def extract_ligand(protein, ligand_res_id, ligand_smiles):
    """
    Need to be able to robustly extract a ligand from a structure.
    RDKit + some PDB weirdness should work here.
    :return:
    """
    pass


def find_interactions(protein, ligand):
    """
    Need to be able to robustly extract a ligand from a structure.
    This is about defining the SMARTS patterns / angles / distances to define interactions.
    :return:
    """
    pass


# TODO - I need corner cases - like tons of them from pharma - and what they expect to see. Then we run into pipeline and test.
# TODO - Aim is to have this clean and distributed by September.
