import os
import gzip
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from datetime import datetime, timedelta


def run_detection_statistics(main_directory, vcf_directory, out_files):
    def count_pass_variants(vcf_file):
        _variants = set()
        num_variants = 0
        num_pass_variants = 0
        with gzip.open(vcf_file, 'rt') as vcf:
            for line in vcf:
                if not line.startswith('#'):
                    fields = line.strip().split('\t')
                    info = fields[6]
                    if 'PASS' in info:
                        num_pass_variants += 1
                        variant_id = "{}-{}-{}-{}".format(fields[0], fields[1], fields[3], fields[4])
                        _variants.add(variant_id)
                    num_variants += 1

        return num_variants, num_pass_variants, _variants

    def sum_duration_for_sample(json_path, sample):
        with open(json_path, 'r') as json_file:
            data = json.load(json_file)

        total_duration = 0.0

        for file_path, file_data in data.get('files', {}).items():
            if sample in file_path:
                total_duration += file_data.get('duration', 1.0)

        d = (datetime(1, 1, 1) + timedelta(seconds=total_duration))
        total_duration_formatted = "%d:%d:%d:%d" % (d.day-1, d.hour, d.minute, d.second)
        return total_duration_formatted, total_duration

    # plot Somatic Variants for Each Sample and Variant Caller
    def plot_stats_for_each_sample_and_variant_caller(df):
        sns.set(style="whitegrid")

        plt.figure(figsize=(20, 14))

        sns.barplot(
            x='SAMPLE',
            y='PASS VARIANT COUNT',
            hue='VARIANT CALLER',
            data=df,
            palette='Set2',
            errorbar=None,
            saturation=0.8,
            capsize=0.2,
            width=0.95,
        )

        plt.title('Somatic Variants for each Sample and Variant Caller')
        plt.xlabel('Samples')
        plt.ylabel('Somatic Variants')
        plt.yscale('log')
        plt.legend(title='Variant Caller', loc='upper right')
        plt.xticks(rotation=45, ha='right')

        plt.savefig(out_files.get('somatic_variants_for_sample_and_variant_caller'), bbox_inches='tight')

    def plot_mean_pass_variants(df):
        # Mean Pass Variants
        mean_pass_variants = df.groupby('VARIANT CALLER')['PASS VARIANT COUNT'].mean()

        plt.figure(figsize=(10, 6))
        mean_pass_variants.plot(kind='bar', color='skyblue')
        plt.title('Average Pass Variants for each Variant Caller')
        plt.xlabel('Variant Caller')
        plt.ylabel('Average count PASS')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(out_files.get('mean_pass_variants_plot'), bbox_inches='tight')
        mean_pass_variants.to_csv(out_files.get('mean_pass_variants'), index=False, sep='\t')

    # Plot Runtime for each Sample and Variant Caller
    def plot_runtime_for_each_sample_and_variant_caller(df):

        plt.figure(figsize=(20, 14))
        sns.barplot(
            x='SAMPLE',
            y='RUNTIME (seconds)',
            hue='VARIANT CALLER',
            data=df,
            palette='Set2',
            errorbar=None,
            saturation=0.8,
            capsize=0.2,
            width=0.95,
        )

        plt.title('Runtime for Each Sample and Variant Caller')
        plt.xlabel('Samples')
        plt.ylabel('Runtime (seconds)')
        plt.legend(title='Variant Caller', loc='upper right')
        plt.xticks(rotation=45, ha='right')
        plt.yscale('log')
        plt.savefig(out_files.get('runtime_for_sample_and_variant_caller'), bbox_inches='tight')

    # Plot Mean Runtime for each
    def plot_mean_runtime(df):
        mean_runtime = df.groupby('VARIANT CALLER')['RUNTIME (seconds)'].mean()

        plt.figure(figsize=(10, 6))
        mean_runtime.plot(kind='bar', color='lightcoral')
        plt.title('Average Runtime for each Variant Caller')
        plt.xlabel('Variant Caller')
        plt.ylabel('Media del Runtime (seconds)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        plt.savefig(out_files.get('mean_runtime_plot'), bbox_inches='tight')
        mean_runtime.to_csv(out_files.get('mean_runtime'), index=False, sep='\t')

    # Common Variants

    def plot_common_variants_heatmap(df):
        with open(out_files.get('pass_variants_data'), 'w') as json_file:
            json.dump(df, json_file, default=list, indent=2)

        common_variants_counts = {}
        for sample, tools_data in pass_variants_data.items():
            common_variants_counts[sample] = {}
            for tool, variants_set in tools_data.items():
                for other_tool, other_variants_set in tools_data.items():
                    if tool != other_tool:
                        common_variants = variants_set.intersection(other_variants_set)
                        common_variants_counts[sample][(tool, other_tool)] = len(common_variants)

        common_variants_df = pd.DataFrame(common_variants_counts).fillna(0)
        common_variants_df.to_csv(out_files.get('common_variants_counts'), index=True, sep='\t')
        data = pd.read_csv(out_files.get('common_variants_counts'), index_col=[0, 1], sep='\t')

        variant_callers = data.index.levels[1]

        mean_data = pd.DataFrame(index=variant_callers, columns=variant_callers)

        for caller1 in variant_callers:
            for caller2 in variant_callers:
                if caller1 != caller2:
                    common_variants = data.loc[(caller1, caller2)]
                    mean_value = common_variants.mean().mean()
                    mean_data.loc[caller1, caller2] = mean_value

        mean_data = mean_data.astype(float)
        mean_data.to_csv(out_files.get('common_variants_mean'), index=True, sep='\t')

        plt.figure(figsize=(10, 8))
        sns.heatmap(
            mean_data,
            annot=True,
            cmap='crest',
            fmt=".0f",
            linewidths=.5,
            robust=True,
        )
        plt.title('Average of Common Variants among Variant Callers')
        plt.savefig(out_files.get('common_pass_variants_heatmap'))

    stats = []
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
                num_variants, num_pass_variants, variants = count_pass_variants(vcf_file)
                pass_variants_data[sample][tool] = variants
                runtime_tool = tool if 'CONSENSUS' not in tool else 'somaticseq'
                runtime_file = os.path.join(main_directory, runtime_tool, 'stats.txt')
                runtime, seconds = sum_duration_for_sample(runtime_file, sample)
                stats.append([sample, tool, num_variants, num_pass_variants, runtime, seconds])

    df = pd.DataFrame(stats, columns=['SAMPLE', 'VARIANT CALLER', 'TOTAL VARIANT COUNT', 'PASS VARIANT COUNT', 'RUNTIME (DAYS:HOURS:MINUTES:SECONDS)', 'RUNTIME (seconds)'])
    df_stats = df.sort_values(by=['SAMPLE', 'VARIANT CALLER'])
    df_stats.to_csv(out_files.get('stats_for_each_sample_and_variant_caller'), index=False, sep='\t')

    plot_stats_for_each_sample_and_variant_caller(df_stats)
    plot_mean_pass_variants(df_stats)
    plot_runtime_for_each_sample_and_variant_caller(df_stats)
    plot_mean_runtime(df_stats)
    plot_common_variants_heatmap(pass_variants_data)