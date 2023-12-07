import os
import pandas as pd

from .plots import (count_variants, sum_duration_for_sample,
                    plot_summary_for_each_sample_and_variant_tool,
                    plot_mean_pass_variants,
                    plot_runtime_for_each_sample_and_variant_tool,
                    plot_mean_runtime,
                    plot_common_variants_heatmap)


def generate_detection_summary(main_directory, vcf_directory, out_files, plots):
    summary = []
    pass_variants_data = {}

    for filename in os.listdir(vcf_directory):
        if filename.endswith('.vcf.gz'):
            _ = filename.split('.')
            if 'snvs' in _:
                sample = _[0]
                tool = _[2] if 'somatic' in _ else 'CONSENSUS'
                if sample not in pass_variants_data:
                    pass_variants_data[sample] = {tool: set()}
                else:
                    if tool not in pass_variants_data[sample]:
                        pass_variants_data[sample][tool] = set()

                vcf_file = os.path.join(vcf_directory, filename)
                num_variants, num_pass_variants, variants = count_variants(vcf_file)
                pass_variants_data[sample][tool] = variants
                runtime_tool = tool if 'CONSENSUS' not in tool else 'somaticseq'
                runtime_file = os.path.join(main_directory, runtime_tool, 'stats.txt')
                runtime, seconds = sum_duration_for_sample(runtime_file, sample)
                summary.append([sample, tool, num_variants, num_pass_variants, runtime, seconds])

    df = pd.DataFrame(summary, columns=['SAMPLE', 'VARIANT CALLER', 'TOTAL VARIANT COUNT', 'PASS VARIANT COUNT',
                                        'RUNTIME (DAYS:HOURS:MINUTES:SECONDS)', 'RUNTIME (seconds)'])
    df_summary = df.sort_values(by=['SAMPLE', 'VARIANT CALLER'])
    df_summary.to_csv(out_files.get('summary_for_each_sample_and_variant_caller'), index=False, sep='\t')

    plot_summary_for_each_sample_and_variant_tool(df_summary,
                                                  plot=plots.get('plot_summary_for_each_sample_and_variant_caller'),
                                                  out_file=out_files.get(
                                                      'somatic_variants_for_sample_and_variant_caller'))
    plot_mean_pass_variants(df_summary,
                            plot=plots.get('plot_mean_pass_variants'),
                            out_plot=out_files.get('mean_pass_variants_plot'),
                            out_csv=out_files.get('mean_pass_variants'))

    plot_runtime_for_each_sample_and_variant_tool(df_summary,
                                                  plot=plots.get('plot_runtime_for_each_sample_and_variant_caller'),
                                                  out_file=out_files.get('runtime_for_sample_and_variant_caller'))

    plot_mean_runtime(df_summary,
                      plot=plots.get('plot_mean_runtime_variant_callers'),
                      out_plot=out_files.get('mean_runtime_plot'),
                      out_csv=out_files.get('mean_runtime'))

    plot_common_variants_heatmap(pass_variants_data,
                                 plot=plots.get('plot_common_variants_heatmap'),
                                 out_json=out_files.get('pass_variants_data'),
                                 out_cont_csv=out_files.get('common_variants_counts'),
                                 out_mean_csv=out_files.get('common_variants_mean'),
                                 out_plot=out_files.get('common_pass_variants_heatmap')
                                 )


def generate_classification_summary(main_directory, maf_directory, out_files, plots):
    summary_dict = {}
    summary = []

    for file_name in os.listdir(maf_directory):

        if file_name.endswith('.maf'):

            sample_name = file_name.split('.')[0]
            tool_name = file_name.split('.')[2]

            maf_file = os.path.join(maf_directory, file_name)
            vcf_file = os.path.join(maf_directory, file_name.replace('.maf', '.vcf.gz'))
            runtime_file = os.path.join(main_directory, tool_name, 'stats.txt')

            maf_df = pd.read_csv(maf_file, sep='\t', comment='#', low_memory=False)
            maf_df['VARIANT'] = list(zip(maf_df['Chromosome'], maf_df['Start_Position']))

            vcf_df = pd.read_csv(vcf_file, sep='\t', comment='#', usecols=[0, 1, 6],
                                 names=['CHROM', 'POS', 'FILTER'], encoding='latin1')
            pass_variants = set(
                tuple((row['CHROM'], row['POS'])) for index, row in vcf_df.iterrows() if 'PASS' in row['FILTER'])

            maf_df_pass = maf_df[maf_df['VARIANT'].isin(pass_variants)]

            if sample_name not in summary_dict:
                summary_dict[sample_name] = {}

            summary_dict[sample_name][tool_name] = {
                'Gene_Summary_PASS': maf_df_pass['Hugo_Symbol'].value_counts().reset_index().rename(
                    columns={'index': 'Gene', 'Hugo_Symbol': 'Count'}),
                'Impact_Summary_PASS': maf_df_pass['Variant_Classification'].value_counts().reset_index().rename(
                    columns={'index': 'Impact', 'Variant_Classification': 'Count'}),
                'Gene_Summary_All': maf_df['Hugo_Symbol'].value_counts().reset_index().rename(
                    columns={'index': 'Gene', 'Hugo_Symbol': 'Count'}),
                'Impact_Summary_All': maf_df['Variant_Classification'].value_counts().reset_index().rename(
                    columns={'index': 'Impact', 'Variant_Classification': 'Count'}),
            }

            num_variants = vcf_df.shape[0]
            num_pass_variants = len(pass_variants)
            runtime, seconds = sum_duration_for_sample(runtime_file, sample_name)
            summary.append([sample_name, tool_name, num_variants, num_pass_variants, runtime, seconds])

    df = pd.DataFrame(summary, columns=['SAMPLE', 'VARIANT ANNOTATOR', 'TOTAL VARIANT COUNT', 'PASS VARIANT COUNT',
                                        'RUNTIME (DAYS:HOURS:MINUTES:SECONDS)', 'RUNTIME (seconds)'])
    df_summary = df.sort_values(by=['SAMPLE', 'VARIANT ANNOTATOR'])
    df_summary.to_csv(out_files.get('summary_for_each_sample_and_variant_annotator'), index=False, sep='\t')

    plot_summary_for_each_sample_and_variant_tool(df_summary,
                                                  plot=plots.get('plot_summary_for_each_sample_and_variant_annotator'),
                                                  out_file=out_files.get(
                                                      'somatic_variants_for_sample_and_variant_annotator'))

    plot_runtime_for_each_sample_and_variant_tool(df_summary,
                                                  plot=plots.get('plot_runtime_for_each_sample_and_variant_annotator'),
                                                  out_file=out_files.get('runtime_for_sample_and_variant_annotator'))

    plot_mean_runtime(df_summary,
                      plot=plots.get('plot_mean_runtime_variant_annotators'),
                      out_plot=out_files.get('mean_runtime_plot'),
                      out_csv=out_files.get('mean_runtime'))

    gene_summary_pass = pd.DataFrame()
    impact_summary_pass = pd.DataFrame()
    gene_summary_all = pd.DataFrame()
    impact_summary_all = pd.DataFrame()

    for sample_name, sample_data in summary_dict.items():

        for tool_name, tool_data in sample_data.items():
            gene_summary_pass_df = tool_data['Gene_Summary_PASS'].rename(columns={'Count': 'Gene'})
            impact_summary_pass_df = tool_data['Impact_Summary_PASS'].rename(columns={'Count': 'Impact'})
            gene_summary_all_df = tool_data['Gene_Summary_All'].rename(columns={'Count': 'Gene'})
            impact_summary_all_df = tool_data['Impact_Summary_All'].rename(columns={'Count': 'Impact'})

            gene_summary_pass_df['Sample'] = sample_name
            gene_summary_pass_df['Tool'] = tool_name
            impact_summary_pass_df['Sample'] = sample_name
            impact_summary_pass_df['Tool'] = tool_name
            gene_summary_all_df['Sample'] = sample_name
            gene_summary_all_df['Tool'] = tool_name
            impact_summary_all_df['Sample'] = sample_name
            impact_summary_all_df['Tool'] = tool_name

            gene_summary_pass = pd.concat([gene_summary_pass, gene_summary_pass_df], axis=0, ignore_index=True,
                                          sort=False)
            impact_summary_pass = pd.concat([impact_summary_pass, impact_summary_pass_df], axis=0, ignore_index=True,
                                            sort=False)
            gene_summary_all = pd.concat([gene_summary_all, gene_summary_all_df], axis=0, ignore_index=True, sort=False)
            impact_summary_all = pd.concat([impact_summary_all, impact_summary_all_df], axis=0, ignore_index=True,
                                           sort=False)

    pivot_gene_summary_pass = gene_summary_pass.pivot(index=['Sample', 'Gene'], columns='Tool', values='count')
    pivot_impact_summary_pass = impact_summary_pass.pivot(index=['Sample', 'Impact'], columns='Tool', values='count')
    pivot_gene_summary_all = gene_summary_all.pivot(index=['Sample', 'Gene'], columns='Tool', values='count')
    pivot_impact_summary_all = impact_summary_all.pivot(index=['Sample', 'Impact'], columns='Tool', values='count')

    pivot_gene_summary_pass.sort_values(by=['Sample', pivot_gene_summary_pass.columns[0], "Gene"],
                                        ascending=[True, False, True]).to_csv(out_files.get('gene_summary_pass'),
                                                                              sep='\t')

    pivot_impact_summary_pass.sort_values(by=['Sample', pivot_impact_summary_pass.columns[0], "Impact"],
                                          ascending=[True, False, True]).to_csv(out_files.get('impact_summary_pass'),
                                                                                sep='\t')

    pivot_gene_summary_all.sort_values(by=['Sample', pivot_gene_summary_all.columns[0], "Gene"],
                                       ascending=[True, False, True]).to_csv(out_files.get('gene_summary_all'),
                                                                             sep='\t')

    pivot_impact_summary_all.sort_values(by=['Sample', pivot_impact_summary_all.columns[0], "Impact"],
                                         ascending=[True, False, True]).to_csv(out_files.get('impact_summary_all'),
                                                                               sep='\t')


def generate_interpretation_summary(main_directory):
    pass
