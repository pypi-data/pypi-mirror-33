from duck.steps.parametrize import prepare_system
from duck.utils.get_from_fragalysis import get_from_prot_code
from duck.utils.cal_ints import find_interaction
from duck.steps.prepare import prep_lig
from duck.steps.chunk import chunk_with_pymol,do_tleap
from duck.steps.equlibrate import do_equlibrate
from duck.steps.normal_md import perform_md
from duck.steps.steered_md import run_steered_md
import yaml, sys

def run_simulation(prot_code, prot_int, cutoff, init_velocity, num_smd_cycles):
    # A couple of file names
    chunk_protein = "protein_out.pdb"
    chunk_prot_protein = "protein_out_prot.pdb"
    # Now it does the magic
    results  = get_from_prot_code(prot_code)
    prot_file = results[0]
    mol_file = results[1]
    # Chunk
    chunk_with_pymol(mol_file, prot_file, chunk_protein, cutoff)
    # Protontate
    do_tleap(chunk_protein,chunk_prot_protein)
    results = prep_lig(mol_file,prot_code)
    mol2_file = results[0]
    results = prepare_system(mol2_file,chunk_prot_protein)
    complex = results[0]
    # Now find the interaction and save to a file
    results = find_interaction(prot_int,prot_file)
    startdist = results[2]
    # Now do the equlibration
    results = do_equlibrate()
    for i in range(num_smd_cycles):
        if i==0:
            md_start = results[0]
        else:
            md_start = "md_"+str(i-1)+".chk"
        perform_md(md_start,"md_"+str(i)+".chk","md_"+str(i)+".csv","md_"+str(i)+".pdb",md_len=0.5)
        # Now find the interaction and save to a file
        run_steered_md(300,"md_"+str(i)+".chk","smd_"+str(i)+"_300.csv","smd_"+str(i)+"_300.dat",
                       "smd_"+str(i)+"_300.pdb","smd_"+str(i)+"_300.dcd",startdist,init_velocity=init_velocity)
        run_steered_md(325,"md_"+str(i)+".chk","smd_"+str(i)+"_325.csv","smd_"+str(i)+"_325.dat",
                       "smd_"+str(i)+"_325.pdb","smd_"+str(i)+"_325.dcd",startdist,init_velocity=init_velocity)


def main():
    # Define these in a YAML
    out_data = yaml.load(open(sys.argv[1]))
    prot_code = out_data["prot_code"]
    prot_int = out_data["prot_int"]
    # Cutoff for the sphere
    cutoff = out_data["cutoff"]
    md_len = out_data["md_len"]
    init_velocity = out_data["init_velocity"]
    num_smd_cycles = out_data["num_smd_cycles"]
    run_simulation(prot_code, prot_int, cutoff, init_velocity, num_smd_cycles)

if __name__ == "__main__":
    main()
