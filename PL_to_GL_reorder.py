#!/bin/env python3
import argparse
from Bio.bgzf import BgzfWriter
import gzip
import sys

def main():

    args = parse_args()
    with gzip.open(args.out, 'wt') as fd_out:
        for i_vcf, vcf in enumerate(args.vcf):
            with gzip.open(vcf, 'rt') as fd_vcf:
                ## loop metadata lines and header line
                for line in fd_vcf:
                    ## end of metadata lines
                    if line[0:2] != '##':
                        ## print header line
                        print(line, end='', file=fd_out)
                        ## break loop at the header line
                        break
                    if i_vcf == 0:
                        ## print metadata line
                        if 'ID=GT' in line:
                            # Add GL info to header
                            print('##FORMAT=<ID=GL,Number=G,Type=Integer,Description="Genotype likelihood: -(PL)/10">\n', end='', file=fd_out)
                            
                        print(line, end='', file=fd_out)
                ## loop records
                index = 0
                for line in fd_vcf:
                    if index % 10000 == 0:
                        flush_print('Processed '+str(index)+' SNPs\n')
                        
                    index += 1
                    split_line = line.rstrip().split('\t')
                    field = split_line[8].split(':')
                    ## index PL
                    i_PL = split_line[8].split(':').index('PL')
                    field.append('GL')
                    GT = field.pop(0)
                    field.sort()
                    field.insert(0, GT)
                    split_line[8] = ':'.join(field)
                    ## index GL
                    i_GL = split_line[8].split(':').index('GL')
                    s = '\t'.join(split_line[:9])
                    print(s, sep='\t', file=fd_out, end='')
                    for i_GT in range(9, len(split_line)):
                        info = split_line[i_GT].split(':')
                        if info[0] == './.':
                            info = ['./.','0,0','0']
                            s_GL = '.,.,.'
                        else:
                            s_PL = split_line[i_GT].split(':')[i_PL]
                            if s_PL == '.':
                                s_GL = '.,.,.'
                            else:
                                s_GL = ','.join(
                                        str(-float(PL)/10) for PL in s_PL.split(',')
                                    )
                            if s_GL==".":
                                print(line)
                                exit()
                        info.insert(i_GL, s_GL)
                        print('\t' +
                            ':'.join(info), sep='\t', end='',
                            file=fd_out)
                    print(end='\n', file=fd_out)
                flush_print('Total SNPs: '+str(index))
    return

def flush_print(message):
    print(message)
    system.stdout.flush()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vcf', nargs = '+')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()

    return args

if __name__ == '__main__':
    main()
