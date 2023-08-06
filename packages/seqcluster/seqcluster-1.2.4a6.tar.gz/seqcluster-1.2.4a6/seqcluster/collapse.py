import os
from libs.fastq import collapse, splitext_plus, write_output
import logging


logger = logging.getLogger('seqbuster')


def collapse_fastq(args):
    """collapse fasq files after adapter trimming
    """
    try:
        umi_fn = args.fastq
        if _is_umi(args.fastq):
            umis = collapse(args.fastq)
            umi_fn = os.path.join(args.out, splitext_plus(os.path.basename(args.fastq))[0] + "_umi_trimmed.fastq")
            write_output(umi_fn, umis, args.minimum)
        seqs = collapse(umi_fn)
        out_file = splitext_plus(os.path.basename(args.fastq))[0] + "_trimmed.fastq"
    except IOError as e:
        logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
        raise "Can not read file"
    out_file = os.path.join(args.out, out_file)
    write_output(out_file, seqs, args.minimum)

def _is_umi(fn):
    with open(fn) as inh:
        if inh.next().find("UMI_") > -1:
            return True
    return False
