# Simulate library example

import mpathic as mpa

# reate a library of random mutants from an initial wildtype sequence and mutation rate
sim_library = mpa.SimulateLibrary(wtseq="TAATGTGAGTTAGCTCACTCAT", mutrate=0.24)
print(sim_library.output_df.head())

# Load dataset and model dataframes
dataset_df = mpa.io.load_dataset(mpa.__path__[0]+'/data/sortseq/full-0/data.txt')
model_df = mpa.io.load_model(mpa.__path__[0]+'/data/sortseq/full-0/crp_model.txt')

# Simulate a Sort-Seq experiment example
sim_sort = mpa.SimulateSort(df=dataset_df,mp=model_df)
print(sim_sort.output_df.head())