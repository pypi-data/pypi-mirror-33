import mpathic as mpa


# Load dataset and model dataframes
dataset_df = mpa.io.load_dataset(mpa.__path__[0]+'/data/sortseq/full-0/data.txt')
model_df = mpa.io.load_model(mpa.__path__[0]+'/data/sortseq/full-0/crp_model.txt')

# mut profile example
profile_mut = mpa.ProfileMut(dataset_df = dataset_df)
print(profile_mut.mut_df.head())

# freq profile example
profile_freq = mpa.ProfileFreq(dataset_df = dataset_df)
print(profile_freq.freq_df.head())

# info profile example
profile_info = mpa.ProfileInfo(dataset_df = dataset_df)
print(profile_info.info_df.head())