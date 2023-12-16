import gzip
import json

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from datetime import datetime, timedelta


def plot_summary_for_each_sample_and_variant_tool(df, plot, out_file):
    sns.set(style=plot.get('style'))

    plt.figure(figsize=(20, 14))

    sns.barplot(
        x=plot.get('x'),
        y=plot.get('y'),
        hue=plot.get('hue'),
        data=df,
        palette=plot.get('palette'),
        errorbar=None,
        saturation=0.8,
        capsize=0.2,
        width=0.95,
    )

    plt.title(plot.get('title'))
    plt.xlabel(plot.get('xlabel'))
    plt.ylabel(plot.get('ylabel'))
    plt.yscale('log')
    plt.legend(title=plot.get('legend'), loc='upper right')
    plt.xticks(rotation=45, ha='right')

    plt.savefig(out_file, bbox_inches='tight')


def plot_mean_pass_variants(df, plot, out_plot, out_csv):
    # Mean Pass Variants
    mean_pass_variants = df.groupby(plot.get('groupby'))[plot.get('field')].mean()
    plt.figure(figsize=(10, 6))
    mean_pass_variants.plot(kind='bar', color=plot.get('color'))
    plt.title(plot.get('title'))
    plt.xlabel(plot.get('labelx'))
    plt.ylabel(plot.get('labely'))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(out_plot, bbox_inches='tight')
    mean_pass_variants.columns = [plot.get('labelx'), plot.get('labely')]
    mean_pass_variants.to_csv(out_csv, index=False, sep='\t')


def plot_runtime_for_each_sample_and_variant_tool(df, plot, out_file):
    plt.figure(figsize=(20, 14))
    sns.barplot(
        x=plot.get('x'),
        y=plot.get('y'),
        hue=plot.get('hue'),
        data=df,
        palette=plot.get('palette'),
        errorbar=None,
        saturation=0.8,
        capsize=0.2,
        width=0.95,
    )

    plt.title(plot.get('title'))
    plt.xlabel(plot.get('labelx'))
    plt.ylabel(plot.get('labely'))
    plt.legend(title=plot.get('legend'), loc='upper right')
    plt.xticks(rotation=45, ha='right')
    plt.yscale('log')
    plt.savefig(out_file, bbox_inches='tight')


def plot_mean_runtime(df, plot, out_plot, out_csv):
    mean_runtime = df.groupby(plot.get('groupby'))[plot.get('field')].mean()
    plt.figure(figsize=(10, 6))
    mean_runtime.plot(kind='bar', color=plot.get('color'))
    plt.title(plot.get('title'))
    plt.xlabel(plot.get('labelx'))
    plt.ylabel(plot.get('labely'))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(out_plot, bbox_inches='tight')
    mean_runtime.columns = [plot.get('labelx'), plot.get('labely')]
    mean_runtime.to_csv(out_csv, index=False, sep='\t')


def plot_common_variants_heatmap(df, plot, out_json, out_plot, out_cont_csv, out_mean_csv):
    with open(out_json, 'w') as json_file:
        json.dump(df, json_file, default=list, indent=2)

    common_variants_counts = {}
    for sample, tools_data in df.items():
        common_variants_counts[sample] = {}
        for tool, variants_set in tools_data.items():
            for other_tool, other_variants_set in tools_data.items():
                if tool != other_tool:
                    common_variants = variants_set.intersection(other_variants_set)
                    common_variants_counts[sample][(tool, other_tool)] = len(common_variants)

    common_variants_df = pd.DataFrame(common_variants_counts).fillna(0)
    common_variants_df.to_csv(out_cont_csv, index=True, sep='\t')
    data = pd.read_csv(out_cont_csv, index_col=[0, 1], sep='\t')

    variant_callers = data.index.levels[1]

    mean_data = pd.DataFrame(index=variant_callers, columns=variant_callers)

    for caller1 in variant_callers:
        for caller2 in variant_callers:
            if caller1 != caller2:
                common_variants = data.loc[(caller1, caller2)]
                mean_value = common_variants.mean().mean()
                mean_data.loc[caller1, caller2] = mean_value

    mean_data = mean_data.astype(float)
    mean_data.to_csv(out_mean_csv, index=True, sep='\t')

    plt.figure(figsize=(10, 8))
    sns.heatmap(
        mean_data,
        annot=True,
        cmap=plot.get('cmap'),
        fmt=".0f",
        linewidths=.5,
        robust=True,
    )
    plt.title(plot.get('title'))
    plt.savefig(out_plot)


def count_variants(vcf_file):
    variants = set()
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
                    variants.add(variant_id)
                num_variants += 1

    return num_variants, num_pass_variants, variants


def sum_duration_for_sample(json_path, sample):
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)

    total_duration = 0.0

    for file_path, file_data in data.get('files', {}).items():
        if sample in file_path:
            total_duration += file_data.get('duration', 1.0)

    d = (datetime(1, 1, 1) + timedelta(seconds=total_duration))
    total_duration_formatted = "%d:%d:%d:%d" % (d.day - 1, d.hour, d.minute, d.second)
    return total_duration_formatted, total_duration
