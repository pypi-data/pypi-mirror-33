import mpathic as mpa

# Load dataset and model dataframes
dataset_df = mpa.io.load_dataset(mpa.__path__[0]+'/data/sortseq/full-0/data.txt')
model_df = mpa.io.load_model(mpa.__path__[0]+'/data/sortseq/full-0/crp_model.txt')

# learn models example
learned_model = mpa.LearnModel(df=dataset_df)
print(learned_model.output_df.head())

# evaluate models example
eval_model = mpa.EvaluateModel(dataset_df = dataset_df, model_df = model_df)
print(eval_model.out_df.head())

# scan models example
# get contigs, provided with mpathic
fastafile = mpa.__path__[0]+"/data/sortseq/full-0/genome_ecoli_1000lines.fa"
contig_list = mpa.io.load_contigs_from_fasta(fastafile, model_df)

scanned_model = mpa.ScanModel(model_df = model_df, contig_list = contig_list)
print(scanned_model.sitelist_df.head())

# predictive info example
#predictive_info = mpa.PredictiveInfo(data_df = dataset_df, model_df = model_df,start=52)