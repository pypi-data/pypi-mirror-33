import os
from glob import glob

config = CONFIG_TEMPLATE
ROOT_OUT_DIR = ROOT_OUT_DIR_TEMPLATE
NGS_PLOT_EXE = NGS_PLOT_EXE_TEMPLATE
GTF = GTF_TEMPLATE
FASTQ_DIR = FASTQ_DIR_TEMPLATE
REPORT_STEP = REPORT_STEP_TEMPLATE
PROTOCOL = PROTOCOL_TEMPLATE
ADAPTOR = ADAPTOR_TEMPLATE
MARS_SEQ, RNA_SEQ = 'MARS-seq', 'RNA-seq'

if 'job_name' in config:
    JOB_NAME = '_' + config['job_name']
else:
    JOB_NAME = ''
    run_num = 1
    DIR_REPORT_NAME = 'report_output' + JOB_NAME
    while os.path.isdir(os.path.join(ROOT_OUT_DIR, REPORT_STEP, DIR_REPORT_NAME)):
        run_num += 1
        JOB_NAME = '_' + str(run_num)
        DIR_REPORT_NAME = 'report_output' + JOB_NAME

DIR_REPORT_NAME = 'report_output' + JOB_NAME
if PROTOCOL == MARS_SEQ:
    DIR_REPORT_UMI_COUNTS_NAME = 'report_umi_counts_output' + JOB_NAME
LOG_DIR_NAME = 'logs' + JOB_NAME
SAMPLE_DESC_CSV = 'sample_desc' + JOB_NAME + '.csv'
COMPARISONS_CSV = 'comparisons' + JOB_NAME + '.csv'

CREATURE = os.path.basename(GTF).split('.')[0]
NGSPLOT_GENOME = 'hg19'
INTERMINE_WEB_QUERY = 'http:\/\/www.humanmine.org\/humanmine'
INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
MINE_CREATURE = 'H. sapiens'
ANNOTAT_TYPE = 'RefSeq'
GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
RUN_NGSPLOT = False

if CREATURE == 'hg38':
    RUN_NGSPLOT = True
    NGSPLOT_GENOME = 'hg19'
    INTERMINE_WEB_QUERY = 'http:\/\/www.humanmine.org\/humanmine'
    INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
    MINE_CREATURE = 'H. sapiens'
    ANNOTAT_TYPE = 'RefSeq'
    GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
elif CREATURE == 'hg38-gencode':
    RUN_NGSPLOT = True
    NGSPLOT_GENOME = 'hg19'
    INTERMINE_WEB_QUERY = 'http:\/\/www.humanmine.org\/humanmine'
    INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
    MINE_CREATURE = 'H. sapiens'
    ANNOTAT_TYPE = 'Gencode'
    GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
elif CREATURE == 'hg19':
    RUN_NGSPLOT = True
    NGSPLOT_GENOME = 'hg19'
    INTERMINE_WEB_QUERY = 'http:\/\/www.humanmine.org\/humanmine'
    INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
    MINE_CREATURE = 'H. sapiens'
    ANNOTAT_TYPE = 'RefSeq'
    GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
elif CREATURE == 'hg19-genecode':
    RUN_NGSPLOT = True
    NGSPLOT_GENOME = 'hg19'
    INTERMINE_WEB_QUERY = 'http:\/\/www.humanmine.org\/humanmine'
    INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
    MINE_CREATURE = 'H. sapiens'
    ANNOTAT_TYPE = 'Genecode'
    GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
elif CREATURE == 'mm10':
    RUN_NGSPLOT = True
    NGSPLOT_GENOME = 'mm10'
    INTERMINE_WEB_QUERY = 'http:\/\/www.mousemine.org\/mousemine'
    INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
    MINE_CREATURE = 'M. musculus'
    ANNOTAT_TYPE = 'RefSeq'
    GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
elif CREATURE == 'mm10-gencode':
    RUN_NGSPLOT = True
    NGSPLOT_GENOME = 'mm10'
    INTERMINE_WEB_QUERY = 'http:\/\/www.mousemine.org\/mousemine'
    INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
    MINE_CREATURE = 'M. musculus'
    ANNOTAT_TYPE = 'Gencode'
    GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
elif CREATURE == 'mm10hg19':
    RUN_NGSPLOT = False
    NGSPLOT_GENOME = ''
    INTERMINE_WEB_QUERY = 'http:\/\/www.mousemine.org\/mousemine'
    INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
    MINE_CREATURE = 'M. musculus'
    ANNOTAT_TYPE = 'RefSeq'
    GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
elif CREATURE == 'mm10hg19-gencode':
    RUN_NGSPLOT = False
    NGSPLOT_GENOME = ''
    INTERMINE_WEB_QUERY = 'http:\/\/www.mousemine.org\/mousemine'
    INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
    MINE_CREATURE = 'M. musculus'
    ANNOTAT_TYPE = 'Gencode'
    GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
elif CREATURE == 'mm10hg38':
    RUN_NGSPLOT = False
    NGSPLOT_GENOME = ''
    INTERMINE_WEB_QUERY = 'http:\/\/www.mousemine.org\/mousemine'
    INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
    MINE_CREATURE = 'M. musculus'
    ANNOTAT_TYPE = 'RefSeq'
    GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
elif CREATURE == 'mm10hg38-gencode':
    RUN_NGSPLOT = False
    NGSPLOT_GENOME = ''
    INTERMINE_WEB_QUERY = 'http:\/\/www.mousemine.org\/mousemine'
    INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
    MINE_CREATURE = 'M. musculus'
    ANNOTAT_TYPE = 'Gencode'
    GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
elif CREATURE == 'tair10' or CREATURE == 'tair11-araport':
    RUN_NGSPLOT = False
    NGSPLOT_GENOME = ''
    INTERMINE_WEB_QUERY = 'https:\/\/apps.araport.org\/thalemine'
    INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
    MINE_CREATURE = 'A. thaliana'
    ANNOTAT_TYPE = 'Araport'
    GENE_DB_URL = "https:\/\/www.arabidopsis.org\/servlets\/Search?type=general\&search_action=detail\&method=1\&show_obsolete=F\&sub_type=gene\&SEARCH_EXACT=4\&SEARCH_CONTAINS=1\&name="
elif CREATURE == 'sl3':
    RUN_NGSPLOT = False
    NGSPLOT_GENOME = ''
    INTERMINE_WEB_QUERY = 'https:\/\/phytozome.jgi.doe.gov\/phytomine'
    INTERMINE_WEB_BASE = 'https:\/\/phytozome.jgi.doe.gov'
    MINE_CREATURE = 'S. lycopersicum'
    ANNOTAT_TYPE = 'Sol genomics'
    GENE_DB_URL = "https:\/\/phytozome.jgi.doe.gov\/phytomine\/keywordSearchResults.do?searchSubmit=GO\&searchTerm="
elif CREATURE == 'emihu1':
    RUN_NGSPLOT = False
    NGSPLOT_GENOME = ''
    INTERMINE_WEB_QUERY = ''
    INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
    MINE_CREATURE = ''
    ANNOTAT_TYPE = 'emiliania_huxleyi'
    GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
elif CREATURE == 'danRer10':
    RUN_NGSPLOT = True
    NGSPLOT_GENOME = 'Zv9'
    INTERMINE_WEB_QUERY = 'http:\/\/www.zebrafishmine.org'
    INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
    MINE_CREATURE = 'D. rerio'
    ANNOTAT_TYPE = 'RefSeq'
    GENE_DB_URL = "http:\/\/www.zebrafishmine.org\/keywordSearchResults.do?searchSubmit=GO\&searchTerm="
elif CREATURE == 'barley_cv_morex-HighConfidence' or CREATURE == 'barley_cv_morex-LowConfidence':
    RUN_NGSPLOT = False
    NGSPLOT_GENOME = ''
    INTERMINE_WEB_QUERY = 'https:\/\/phytozome.jgi.doe.gov\/phytomine'
    INTERMINE_WEB_BASE = 'https:\/\/phytozome.jgi.doe.gov'
    MINE_CREATURE = 'H. vulgare early-release'
    ANNOTAT_TYPE = 'doi:10.5447\/IPK\/2016\/38'
    GENE_DB_URL = "https:\/\/phytozome.jgi.doe.gov\/phytomine\/keywordSearchResults.do?searchSubmit=GO\&searchTerm="
elif CREATURE == 'barley_cv_morex-LowConfidence':
    RUN_NGSPLOT = False
    NGSPLOT_GENOME = ''
    INTERMINE_WEB_QUERY = 'https:\/\/phytozome.jgi.doe.gov\/phytomine'
    INTERMINE_WEB_BASE = 'https:\/\/phytozome.jgi.doe.gov'
    MINE_CREATURE = 'H. vulgare early-release'
    ANNOTAT_TYPE = 'doi:10.5447\/IPK\/2016\/46'
    GENE_DB_URL = "https:\/\/phytozome.jgi.doe.gov\/phytomine\/keywordSearchResults.do?searchSubmit=GO\&searchTerm="
elif CREATURE == 'rn6' or CREATURE == 'rn6-HornsteinLab':
    RUN_NGSPLOT = False
    NGSPLOT_GENOME = ''
    INTERMINE_WEB_QUERY = 'http:\/\/ratmine.mcw.edu\/ratmine'
    INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
    MINE_CREATURE = 'R. norvegicus'
    ANNOTAT_TYPE = 'RefSeq'
    GENE_DB_URL = "http:\/\/ratmine.mcw.edu\/ratmine\/keywordSearchResults.do?searchSubmit=GO\&searchTerm="
elif CREATURE == 'toy':
    RUN_NGSPLOT = False
    NGSPLOT_GENOME = 'hg19'
    INTERMINE_WEB_QUERY = 'http:\/\/www.humanmine.org\/humanmine'
    INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
    MINE_CREATURE = 'H. sapiens'
    ANNOTAT_TYPE = 'Gencode'
    GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="


if not NGS_PLOT_EXE: #empty string ''
    RUN_NGSPLOT = False
    NGSPLOT_GENOME = ''

if 'factors_file' in config.keys() and ('samples' in config.keys() or 'factors' in config.keys()):
    raise Exception(
        'Invalid config.yaml file: You use with \'factors_file\' and \'sample\' or \'factors\' togther in config file, you can use only with factors_file alone or sample and factors')

SAMPLES = []
SAMPLES_DESEQ = []
FACTORS = []
BATCHES = []
COMBINE_INPUT_FILES = False

try:
    SAMPLES_DESEQ_FILE = config['factors_file']
    with open(SAMPLES_DESEQ_FILE) as ff:
        for line in ff:
            line = line.rstrip()
            try:
                sample, factor, batch = line.split('\t')
                BATCHES.append(batch)
            except ValueError:
                sample, factor = line.split('\t')
                if not BATCHES:
                    BATCHES.append('no-deseq')
            SAMPLES_DESEQ.append(sample)
            FACTORS.append(factor.strip())
except KeyError:  # No factors_file in config
    try:
        FACTORS += config['factors']
        BATCHES += config['batches']
        SAMPLES_DESEQ = config['samples_deseq']
    except KeyError:
        FACTORS.append('no-deseq')
        BATCHES.append('no-deseq')
        SAMPLES_DESEQ.append('no-deseq')

try:
    SAMPLES += config['samples']
except KeyError:
    for sample_path in glob(os.path.join(FASTQ_DIR, '*')):
        if os.path.isfile(sample_path):
            continue
        sample_name = os.path.basename(sample_path)
        if sample_name == 'Undetermined':
            continue
        splitted_files_r1 = glob(os.path.join(sample_path, '*_R1_0*.fastq')) + glob(
            os.path.join(sample_path, '*_R1_0*.fastq.gz'))
        splitted_files_r2 = + glob(os.path.join(sample_path, '*_R2_0*.fastq')) + glob(
            os.path.join(sample_path, '*_R2_0*.fastq.gz'))
        if len(splitted_files_r1) > 1  or len(splitted_files_r2) > 1:
            COMBINE_INPUT_FILES = True
            SAMPLES.append(sample_name)
        elif glob(os.path.join(sample_path, '*_R1*.fastq')) + glob(
            os.path.join(sample_path, '*_R1*.fastq.gz')) + glob(
            os.path.join(sample_path, '*_R2*.fastq')) + glob(
            os.path.join(sample_path, '*_R2*.fastq.gz')):
            SAMPLES.append(sample_name)
        else:
            raise IOError('Missing input file in foler %s' % sample_path)
    if not len(SAMPLES):
        raise IOError('No input fastq files in %s' % FASTQ_DIR)

# reorder SAMPLES according to SAMPLES_DESEQ
TEMP_SAMPLES = []
for i in SAMPLES_DESEQ:
    if i != 'no-deseq':
        TEMP_SAMPLES.append(i)
        SAMPLES.remove(i)
TEMP_SAMPLES.extend(SAMPLES)
SAMPLES = TEMP_SAMPLES

SAMPLES_LIST = ' '.join(SAMPLES)
SAMPLES_DESEQ_LIST = ' '.join(SAMPLES_DESEQ)
FACTORS_LIST = ' '.join(FACTORS)
BATCHES_LIST = ' '.join(BATCHES)

FACTOR_OBJ = ''
unique_factor = sorted(list(set(FACTORS)))
try:
    FACTOR_OBJ = unique_factor[0] + '_or_' + unique_factor[1]
except IndexError:
    FACTOR_OBJ = ''

os.makedirs(ROOT_OUT_DIR, exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, LOG_DIR_NAME), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, REPORT_STEP), exist_ok=True)
os.makedirs(os.path.join(ROOT_OUT_DIR, REPORT_STEP, DIR_REPORT_NAME), exist_ok=True)
if PROTOCOL == MARS_SEQ:
    os.makedirs(os.path.join(ROOT_OUT_DIR, '1_combined_fastq'), exist_ok=True)
    os.makedirs(os.path.join(ROOT_OUT_DIR, '2_cutadapt'), exist_ok=True)
    os.makedirs(os.path.join(ROOT_OUT_DIR, '3_fastqc'), exist_ok=True)
    os.makedirs(os.path.join(ROOT_OUT_DIR, '4_mapping'), exist_ok=True)
    os.makedirs(os.path.join(ROOT_OUT_DIR, '5_move_umi'), exist_ok=True)
    os.makedirs(os.path.join(ROOT_OUT_DIR, '6_count_reads'), exist_ok=True)
    os.makedirs(os.path.join(ROOT_OUT_DIR, '7_mark_dup'), exist_ok=True)
    os.makedirs(os.path.join(ROOT_OUT_DIR, '8_dedup_counts'), exist_ok=True)
    os.makedirs(os.path.join(ROOT_OUT_DIR, '9_umi_counts'), exist_ok=True)
elif PROTOCOL == RNA_SEQ:
    os.makedirs(os.path.join(ROOT_OUT_DIR, '1_cutadapt'), exist_ok=True)
    os.makedirs(os.path.join(ROOT_OUT_DIR, '2_fastqc'), exist_ok=True)
    os.makedirs(os.path.join(ROOT_OUT_DIR, '3_mapping'), exist_ok=True)

with open(os.path.join(ROOT_OUT_DIR, REPORT_STEP, DIR_REPORT_NAME, 'report.html'), 'w') as r_file:
    r_file.write("<h1>The pipeline running has not ended yet</h1>")


def concatenation_fastq(fastq_dir, fastq_dir_concat):
    chunksize = 100 * 1024 * 1024  # 100 megabytes
    os.makedirs(fastq_dir_concat)
    for read in ['_R1', '_R2']:
        for sample_name in SAMPLES:
            sample_dir = os.path.join(fastq_dir, sample_name)
            sample_dir_concat = os.path.join(fastq_dir_concat, sample_name)
            os.makedirs(sample_dir_concat, exist_ok=True)
            files = sorted(glob(os.path.join(sample_dir, '*' + read + '*')))
            if files:  # Open output file only if input files of the read are exists
                if files[0][-3:] == '.gz':  # All input files are gzipped or all of them uncompressed
                    outfile = os.path.join(sample_dir_concat, sample_name + read + '.fastq.gz')
                else:
                    outfile = os.path.join(sample_dir_concat, sample_name + read + '.fastq')
                with open(outfile, 'wb') as fho:
                    for file in files:
                        with open(file, "rb") as fhi:
                            while True:
                                chunk = fhi.read(chunksize)
                                if chunk:
                                    fho.write(chunk)
                                else:
                                    break


if COMBINE_INPUT_FILES:
    FASTQ_DIR_CONCAT = os.path.join(ROOT_OUT_DIR, '0_concatenating_fastq')
    if not os.path.isdir(FASTQ_DIR_CONCAT):
        concatenation_fastq(FASTQ_DIR, FASTQ_DIR_CONCAT)
    FASTQ_DIR_ANALYSIS = FASTQ_DIR_CONCAT
else:
    FASTQ_DIR_ANALYSIS = FASTQ_DIR

if PROTOCOL == MARS_SEQ:
    def fastq_r1(wildcards):
        sample = wildcards.sample
        return glob(os.path.join(FASTQ_DIR_ANALYSIS, sample, '*R1*'))[0]

    def fastq_r2(wildcards):
        sample = wildcards.sample
        return glob(os.path.join(FASTQ_DIR_ANALYSIS, sample, '*R2*'))[0]

elif PROTOCOL == RNA_SEQ:
    PAIRED_END = True if glob(os.path.join(FASTQ_DIR_ANALYSIS, SAMPLES[0], '*_R2*')) else False
    if PAIRED_END and len(ADAPTOR.split(',')) < 2:
        raise IOError("The number of adapters is not equal to the numbers of the reads")

    def fastq_r1(wildcards):
        sample = wildcards.sample
        return glob(os.path.join(FASTQ_DIR_ANALYSIS, sample, '*R1*'))[0]

    def fastq_r2(wildcards):
        sample = wildcards.sample
        return glob(os.path.join(FASTQ_DIR_ANALYSIS, sample, '*R2*'))[0]

    def get_fastq():
        return [fastq_r1, fastq_r2] if PAIRED_END else [fastq_r1]


    CUTADAPT_TEMPLATE = ROOT_OUT_DIR + '1_cutadapt/{sample}_R1.fastq,' + ROOT_OUT_DIR + '1_cutadapt/{sample}_R2.fastq' if PAIRED_END else ROOT_OUT_DIR + '1_cutadapt/{sample}_R1.fastq'
