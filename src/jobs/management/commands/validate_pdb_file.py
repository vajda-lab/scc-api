pdb_file = open("/home/awake/ftplus/src/ftmap/management/commands/6pav.pdb", "r")
lines = pdb_file.readlines()
pdb_file.close()

standard_residues = [
    "ASX",
    "GLX",
    "UNK",
    "ALA",
    "ARG",
    "ASN",
    "ASP",
    "CYS",
    "GLN",
    "GLU",
    "GLY",
    "HIS",
    "ILE",
    "LEU",
    "LYS",
    "MET",
    "PHE",
    "PRO",
    "SER",
    "THR",
    "TRP",
    "TYR",
    "VAL",
]

"""
Each line is 80 columns wide and is terminated by an end-of-line indicator. The first six columns of every line 
contain a "record name". This must be an exact match to one of  the stated record names described in detail below.

    
    COLUMNS        DATA TYPE       CONTENTS                            
--------------------------------------------------------------------------------
 1 -  6        Record name     "ATOM  " or "HETATM"                                            

 7 - 11        Integer         Atom serial number.                   

13 - 16        Atom            Atom name.                            

17             Character       Alternate location indicator.         

18 - 20        Residue name    Residue name.                         

22             Character       Chain identifier.                     

23 - 26        Integer         Residue sequence number.              

27             AChar           Code for insertion of residues.       

31 - 38        Real(8.3)       Orthogonal coordinates for X in Angstroms.                       

39 - 46        Real(8.3)       Orthogonal coordinates for Y in Angstroms.                            

47 - 54        Real(8.3)       Orthogonal coordinates for Z in Angstroms.                            

55 - 60        Real(6.2)       Occupancy.                            

61 - 66        Real(6.2)       Temperature factor (Default = 0.0).                   

73 - 76        LString(4)      Segment identifier, left-justified.   

77 - 78        LString(2)      Element symbol, right-justified.      

79 - 80        LString(2)      Charge on the atom. 

"""

# Check that each line is no more than 80 columns wide and is terminated by an end-of-line indicator.
for line in lines:
    if len(line.strip()) <= 80 and line.endswith("\n"):
        pass
    else:
        print("fail")
    # Check to make sure atoms look like atoms
    if line.startswith("ATOM"):
        if not line[7:12].strip().isdigit():
            print("FAILED Atom serial number. Expecting Integer")
        if not line[17:20].upper() in standard_residues:
            print("FAILED Residue Type. Expecting standard residue")
        if not line[21].isalnum():
            print("FAILED Chain identifier. Expecting Character")
        if not line[23:26].strip().isdigit():
            print("FAILED Residue Sequence Number")
        if not float(line[31:38].strip()):
            print("FAILED Orthogonal coordinates for X in Angstroms")
        if not float(line[39:46].strip()):
            print("FAILED Orthogonal coordinates for Y in Angstroms")
        if not float(line[47:54].strip()):
            print("FAILED Orthogonal coordinates for Z in Angstroms")

    # Check to make sure HETATM look like correct
    if line.startswith("HETATM"):
        if not line[7:12].strip().isdigit():
            print("FAILED Atom serial number. Expecting Integer")
        if not line[17:20].isalnum():
            print("FAILED Residue Type. Expecting alpha numeric value")
        if not line[21].isalnum():
            print("FAILED Chain identifier. Expecting Character")
        if not line[23:26].strip().isdigit():
            print("FAILED Residue Sequence Number")
        if not float(line[31:38].strip()):
            print("FAILED Orthogonal coordinates for X in Angstroms")
        if not float(line[39:46].strip()):
            print("FAILED Orthogonal coordinates for Y in Angstroms")
        if not float(line[47:54].strip()):
            print("FAILED Orthogonal coordinates for Z in Angstroms")
