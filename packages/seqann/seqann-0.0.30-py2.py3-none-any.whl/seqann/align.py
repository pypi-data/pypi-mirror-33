# -*- coding: utf-8 -*-

#
#    seqann Sequence Annotation
#    Copyright (c) 2017 Be The Match operated by National Marrow Donor Program. All Rights Reserved.
#
#    This library is free software; you can redistribute it and/or modify it
#    under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation; either version 3 of the License, or (at
#    your option) any later version.
#
#    This library is distributed in the hope that it will be useful, but WITHOUT
#    ANY WARRANTY; with out even the implied warranty of MERCHANTABILITY or
#    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
#    License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this library;  if not, write to the Free Software Foundation,
#    Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA.
#
#    > http://www.fsf.org/licensing/licenses/lgpl.html
#    > http://www.opensource.org/licenses/lgpl-license.php
#

from __future__ import absolute_import

import os
import re
import sys

from Bio.Alphabet import SingleLetterAlphabet
from Bio.SeqRecord import SeqRecord
from subprocess import Popen
from subprocess import PIPE
from subprocess import STDOUT

from Bio import SeqIO
from Bio.Seq import Seq
from Bio import AlignIO
from Bio.Alphabet import IUPAC
from Bio.SeqFeature import SeqFeature
from Bio.SeqFeature import FeatureLocation
from Bio.SeqFeature import ExactPosition
from Bio.Align.Applications import ClustalOmegaCommandline

from seqann.util import cleanup
from seqann.util import randomid
from seqann.util import get_seqfeat
from seqann.seq_search import getblocks
from seqann.models.annotation import Annotation
import logging

flatten = lambda l: [item for sublist in l for item in sublist]


def align_seqs(found_seqs, sequence, locus, start_pos, refdata, missing, verbose=False, verbosity=0):
    """
    Aligns sequences with clustalw

    :param locus: string containing HLA locus.
    :param sequence: string containing sequence data.

    :return: GFEobject.
    """
    logger = logging.getLogger("Logger." + __name__)
    seqs = [found_seqs, sequence]

    if verbose and verbosity > 0:
        logger.info("found_seqs length = " + str(len(found_seqs)))
        logger.info("sequence length = " + str(len(sequence)))

    seqs = []
    seqs.append(found_seqs)
    seqs.append(sequence)

    align = []
    if len(sequence) > 7000:
        if verbose:
            logger.info("Sequence too large to use pipe")
        randid = randomid()
        input_fasta = str(randid) + ".fasta"
        output_clu = str(randid) + ".clu"
        SeqIO.write(seqs, input_fasta, "fasta")
        clustalomega_cline = ClustalOmegaCommandline(infile=input_fasta,
                                                     outfile=output_clu,
                                                     outfmt='clu', wrap=20000,
                                                     verbose=True, auto=True)
        stdout, stderr = clustalomega_cline()
        aligns = AlignIO.read(output_clu, "clustal")
        for aln in aligns:
            align.append(str(aln.seq))

        # Delete files
        cleanup(randid)
    else:
        indata = flatten([[">" + str(s.id), str(s.seq)]
                          for s in seqs])
        child = Popen(['clustalo',
                       '--outfmt', 'clu',
                       '--wrap=50000',
                       '--auto', '-i', '-'],
                      stdout=PIPE,
                      stderr=STDOUT,
                      stdin=PIPE)

        stdout = child.communicate(input=str.encode("\n".join(indata)))
        child.wait()

        lines = bytes.decode(stdout[0]).split("\n")
        for line in lines:
            if re.search("\w", line) and not re.search("CLUSTAL", line):
                alignment = re.findall(r"[\S']+", line)
                if len(alignment) == 2:
                    align.append(list(alignment[1]))
        child.terminate()

    # Print out what blocks haven't been annotated
    if verbose and len(align) > 0:
        logger.info("* ClustalOmega alignment succeeded *")

    insers, dels = 0, 0
    all_features = []
    if len(align)-2 == 0:
        infeats = get_seqfeat(seqs[0])
        diffs = count_diffs(align, infeats, sequence, verbose, verbosity)
        if isinstance(diffs, Annotation):
            return diffs, 0, 0
        else:
            insers, dels = diffs[0], diffs[1]
        f = find_features(infeats, align[0])
        all_features.append(f)
    else:
        for i in range(0, len(align)-2):
            infeats = get_seqfeat(seqs[i])
            f = find_features(infeats, align[i])
            all_features.append(f)

    if verbose:
        logger.info("Number of features found = " + str(len(all_features)))

    if len(all_features) > 0:
        annotation = resolve_feats(all_features,
                                   align[len(align)-1],
                                   start_pos,
                                   refdata,
                                   locus,
                                   missing,
                                   verbose,
                                   verbosity)
        return annotation, insers, dels
    else:
        return Annotation(complete_annotation=False), 0, 0


def find_features(feats, sequ):
    feats_a = list(feats.keys())

    j = 0
    s = 0
    en = 0
    start = 0
    for i in range(0, len(sequ)):
        if j <= len(feats_a)-1:
            if i > int(feats[feats_a[j]].location.end):
                j += 1
            if(sequ[i] == '-'):
                if i == 0:
                    start += 1
                    en += 1
                    s = 1
                else:
                    start += 1
                    en += 1
                    if s == 0:
                        feats[feats_a[j]] = SeqFeature(FeatureLocation(ExactPosition(feats[feats_a[j]].location.start), ExactPosition(int(feats[feats_a[j]].location.end + 1)), strand=1), type=feats[feats_a[j]].type)
                        if j != len(feats_a):
                            for l in range(j+1, len(feats_a)):
                                feats[feats_a[l]] = SeqFeature(FeatureLocation(ExactPosition(feats[feats_a[l]].location.start+1), ExactPosition(int(feats[feats_a[l]].location.end + 1)), strand=1), type=feats[feats_a[l]].type)
                      
            else:
                if s == 1:
                    st = feats[feats_a[j]].location.start + start
                    end = feats[feats_a[j]].location.end + en
                    feats[feats_a[j]] = SeqFeature(FeatureLocation(ExactPosition(st), ExactPosition(end), strand=1), type=feats[feats_a[j]].type)
                    if j != len(feats_a):
                        for l in range(j+1, len(feats_a)):
                            feats[feats_a[l]] = SeqFeature(FeatureLocation(ExactPosition(feats[feats_a[l]].location.start+st+1), ExactPosition(int(feats[feats_a[l]].location.end + end)), strand=1), type=feats[feats_a[l]].type)

                    s = 0
    return feats


def resolve_feats(feat_list, seqin,  start, refdata, locus, missing, verbose=False, verbosity=0):
    """
    Resolves features from alignments

    :param feat_list: string containing HLA locus.
    :param seqin: string containing sequence data.

    :return: Annotation.
    """
    logger = logging.getLogger("Logger." + __name__)
    seq = SeqRecord(seq=Seq("".join(seqin), SingleLetterAlphabet()))
    seq_covered = len(seq.seq)
    coordinates = dict(map(lambda x: [x, 1],
                       [i for i in range(0, len(seq.seq)+1)]))

    mapping = dict(map(lambda x: [x, 1],
                       [i for i in range(0, len(seq.seq)+1)]))

    if len(feat_list) > 1:
        if verbose:
            logger.error("resolve_feats error")
        return Annotation(complete_annotation=False)
    else:
        features = {}
        full_annotation = {}
        features = feat_list[0]
        for feat in features:
            if feat in missing:
                f = features[feat]
                seqrec = f.extract(seq)
                seq_covered -= len(seqrec.seq)
                if re.search("-", str(seqrec.seq)):
                    newseq = re.sub(r'-', '', str(seqrec.seq))
                    seqrec.seq = Seq(newseq, IUPAC.unambiguous_dna)

                if seqrec.seq:
                    sp = f.location.start + start
                    ep = f.location.end + start
                    featn = SeqFeature(FeatureLocation(ExactPosition(sp),
                                                       ExactPosition(ep),
                                                       strand=1), type=f.type)

                    features.update({feat: featn})
                    full_annotation.update({feat: seqrec})
                    for i in range(f.location.start, f.location.end):
                        if i in coordinates:
                            del coordinates[i]
                        mapping[i] = feat

        blocks = getblocks(coordinates)

        rmapping = {k+start: mapping[k] for k in mapping.keys()}

        # Print out what blocks haven't been annotated
        if verbose and verbosity > 2:
            logger.info("Blocks not mapped:")
            for b in blocks:
                logger.info(",".join([str(i) for i in b]))

        # Print out what features are missing
        if verbose and verbosity > 0 and len(full_annotation.keys()) > 1:
            logger.info("Features resolved:")
            for f in full_annotation:
                logger.info(f)

        if not full_annotation or len(full_annotation) == 0:
            if verbose:
                logger.info("Failed to align missing features")
            return Annotation(complete_annotation=False)
        else:
            return Annotation(annotation=full_annotation,
                              method="clustalo",
                              features=features,
                              mapping=rmapping,
                              blocks=blocks)


def count_diffs(align, feats, inseq, verbose=False, verbosity=0):
    """
    Aligns sequences with clustalw

    :param locus: string containing HLA locus.
    :param sequence: string containing sequence data.
    """

    nfeats = len(feats.keys())
    mm = 0
    insr = 0
    dels = 0
    gaps = 0
    match = 0
    lastb = ''
    l = len(align[0]) if len(align[0]) > len(align[1]) else len(align[1])

    for i in range(0, l):
        if align[0][i] == "-" or align[1][i] == "-":
            if align[0][i] == "-":
                insr += 1
                if lastb != '-':
                    gaps += 1
                lastb = "-"
            if align[1][i] == "-":
                dels += 1
                if lastb != '-':
                    gaps += 1
                lastb = "-"
        else:
            lastb = ''
            if align[0][i] != align[1][i]:
                mm += 1
            else:
                match += 1

    gper = gaps / nfeats
    delper = dels / l
    iper = insr / l
    mmper = mm / l
    mper = match / l
    mper2 = match / len(inseq)

    logger = logging.getLogger("Logger." + __name__)

    if verbose and verbosity > 0:
        logger.info("Features algined = " + ",".join(list(feats.keys())))
        logger.info('{:<22}{:<6d}'.format("Number of feats: ", nfeats))
        logger.info('{:<22}{:<6d}{:<1.2f}'.format("Number of gaps: ", gaps, gper))
        logger.info('{:<22}{:<6d}{:<1.2f}'.format("Number of deletions: ", dels, delper))
        logger.info('{:<22}{:<6d}{:<1.2f}'.format("Number of insertions: ", insr, iper))
        logger.info('{:<22}{:<6d}{:<1.2f}'.format("Number of mismatches: ", mm, mmper))
        logger.info('{:<22}{:<6d}{:<1.2f}'.format("Number of matches: ", match, mper))
        logger.info('{:<22}{:<6d}{:<1.2f}'.format("Number of matches: ", match, mper2))
    indel = iper + delper

    if match == 455:
        return Annotation(complete_annotation=False)

    if len(inseq) > 8000 and mmper < .10 and mper2 > .80:
        if verbose:
            logger.info("Alignment coverage high enough to complete annotation")
        return insr, dels
    else:
        # TODO:
        # These numbers need to be fine t
        if (indel > 0.5 or mmper > 0.05 or gper > .50) and mper2 < .9:
            if verbose:
                logger.info("Alignment coverage NOT high enough to return annotation")
            return Annotation(complete_annotation=False)
        else:
            if verbose:
                logger.info("Alignment coverage high enough to complete annotation")
            return insr, dels




