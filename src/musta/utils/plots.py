import gzip
import json

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.colors import LogNorm
from datetime import datetime, timedelta

colors = {
    'musta': 'tab:red',
    'lofreq': 'tab:blue',
    'mutect': 'tab:green',
    'strelka': 'tab:orange',
    'muse': 'tab:purple',
    'varscan': 'tab:pink',
    'vardict': 'tab:brown',
    'vep': 'lightblue',
    'funcotator': 'lightcoral', 
}


def plot_summary_for_each_sample_and_variant_tool(df, plot, out_file):
    fig, axs = plt.subplots(figsize=(15, 12))

    axs.set_title(plot.get('title'))
    for key, grp in df.groupby(plot.get('groupby')):
        axs.errorbar(grp[plot.get('x')], grp[plot.get('y')],
                     fmt='o', linestyle='-', label=key,
                     color=colors.get(key, 'gray'))

    axs.set_xlabel(plot.get('labelx'))
    axs.set_ylabel(plot.get('labely'))
    axs.legend()
    axs.grid(axis='y', linestyle='--', alpha=0.7)
    axs.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.savefig(out_file, bbox_inches='tight')

    axs.set_yscale('log')
    plt.tight_layout()
    plt.savefig(out_file.replace('.png', '.logscale.png'), bbox_inches='tight')


def plot_mean_pass_variants(df, plot, out_plot, out_csv):

    fig, axs = plt.subplots(figsize=(15, 12))

    mean_snvs_per_caller = df.groupby(plot.get('groupby'))[plot.get('field')].mean()
    mean_snvs_per_caller_sorted = mean_snvs_per_caller.sort_values(ascending=False)
    axs.set_title(plot.get('title'))
    bars = axs.barh(mean_snvs_per_caller_sorted.index, mean_snvs_per_caller_sorted,
                    color=[colors.get(key, 'black') for key in mean_snvs_per_caller_sorted.index])

    axs.set_xlabel(plot.get('labelx'))
    axs.set_ylabel(plot.get('labely'))
    axs.grid(axis='x', linestyle='--', alpha=0.7)

    max_width = axs.get_xlim()[1] * 0.5

    for bar in bars:
        width = bar.get_width()
        if width < max_width:
            axs.text(width + 5,
                     bar.get_y() + bar.get_height() / 2, f'{width:.0f}',
                     fontsize=12, va='center',color='black', ha='left')
        else:
            axs.text(max_width,
                     bar.get_y() + bar.get_height() / 2, f'{width:.0f}',
                     fontsize=12, va='center', color='white', ha='center')

    plt.tight_layout()
    plt.savefig(out_plot, bbox_inches='tight')

    axs.set_xscale('log')
    plt.tight_layout()
    plt.savefig(out_plot.replace('.png', '.logscale.png'),
                bbox_inches='tight')

    mean_pass_variants = mean_snvs_per_caller_sorted.reset_index()
    mean_pass_variants.columns = [plot.get('labelx'), plot.get('labely')]
    mean_pass_variants.to_csv(out_csv, index=False, sep='\t')


def plot_runtime_for_each_sample_and_variant_tool(df, plot, out_file):
    fig, axs = plt.subplots(figsize=(15, 12))

    _df = df[df[plot.get('groupby')] != 'musta']

    axs.set_title(plot.get('title'))
    for key, grp in _df.groupby(plot.get('groupby')):
        axs.errorbar(grp[plot.get('x')], grp[plot.get('y')] / 60,
                     fmt='o', linestyle='-', label=key,
                     color=colors.get(key, 'gray'))

    axs.set_xlabel(plot.get('labelx'))
    axs.set_ylabel(plot.get('labely'))
    axs.legend()
    axs.grid(axis='y', linestyle='--', alpha=0.7)
    axs.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.savefig(out_file, bbox_inches='tight')

    axs.set_yscale('log')
    plt.tight_layout()
    plt.savefig(out_file.replace('.png', '.logscale.png'),
                bbox_inches='tight')


def plot_mean_runtime(df, plot, out_plot, out_csv):
    fig, axs = plt.subplots(figsize=(15, 12))

    _df = df[df[plot.get('groupby')] != 'musta']
    mean_runtime_per_caller = _df.groupby(plot.get('groupby'))[plot.get('field')].mean() / 60
    mean_runtime_per_caller_sorted = mean_runtime_per_caller.sort_values(ascending=False)
    axs.set_title(plot.get('title'))
    bars = axs.barh(mean_runtime_per_caller_sorted.index, 
            mean_runtime_per_caller_sorted, 
            color=[colors.get(key, 'black') for key in mean_runtime_per_caller_sorted.index])
    axs.set_xlabel(plot.get('labelx'))
    axs.set_ylabel(plot.get('labely'))
    axs.grid(axis='x', linestyle='--', alpha=0.7)

    max_width = axs.get_xlim()[1] * 0.5
    for bar in bars:
        width = bar.get_width()
        if width < max_width:
            axs.text(width, bar.get_y() + bar.get_height()/2, f'{width:.0f}',
                     fontsize=12, va='center', color='black', ha='left', )
        else:
            axs.text(max_width, bar.get_y() + bar.get_height()/2, f'{width:.0f}',
                     fontsize=12, va='center', color='white', ha='center', )

    # plt.tight_layout()
    plt.savefig(out_plot)

    axs.set_xscale('log')
    plt.savefig(out_plot.replace('.png', '.logscale.png'))

    mean_runtime = mean_runtime_per_caller_sorted.reset_index()
    mean_runtime.columns = [plot.get('labelx'), plot.get('labely')]
    mean_runtime.to_csv(out_csv, index=False, sep='\t')


def plot_common_variants_heatmap(df, plot, out_json, out_plot, out_cont_csv, out_mean_csv):

    fig, axs = plt.subplots(figsize=(15, 12))

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

    mask = np.triu(np.ones_like(mean_data, dtype=bool))
    axs = sns.heatmap(mean_data, annot=True, fmt='.0f',
                      cmap=plot.get('cmap'), mask=mask, ax=axs)

    axs.set_title(plot.get('cmap'))
    axs.set_xlabel(plot.get('label'))
    axs.set_ylabel(plot.get('label'))

    plt.tight_layout()
    plt.savefig(out_plot, bbox_inches='tight')
    
    axs = sns.heatmap(mean_data, annot=True, fmt='.0f',
                      cmap=plot.get('cmap'), mask=mask, 
                      ax=axs, norm=LogNorm())

    axs.set_title(plot.get('cmap'))
    axs.set_xlabel(plot.get('label'))
    axs.set_ylabel(plot.get('label'))

    plt.tight_layout()
    plt.savefig(out_plot.replace('.png', '.logscale.png'),
                bbox_inches='tight')


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
