import json
import xml.etree.ElementTree as xml
import re
import hashlib
from sierralocal.hivdb import HIVdb
import csv
from pathlib import Path
import sys, os

class JSONWriter():
    def __init__(self):
        self.names = {'3TC':'LMV'}

        self.HIVDB_XML_PATH = HIVdb().xml_filename
        if os.path.isfile(self.HIVDB_XML_PATH):
            print("Found HIVdb file {}".format(str(self.HIVDB_XML_PATH)))
        else:
            print("HIVDB file missing.")
            sys.exit(0)

        # Set up algorithm data
        self.algorithm = HIVdb(self.HIVDB_XML_PATH)
        self.root = xml.parse(self.HIVDB_XML_PATH).getroot()
        self.version = self.root.find('ALGVERSION').text
        self.version_date = self.root.find('ALGDATE').text
        self.definitions = self.algorithm.parse_definitions(self.algorithm.root)
        self.levels = self.definitions['level']
        self.globalrange = self.definitions['globalrange']
        self.database = self.algorithm.parse_drugs(self.algorithm.root)
        self.comments = self.algorithm.parse_comments(self.algorithm.root)

        # Load comments files stored locally
        with open(Path('.')/'sierralocal'/'data'/'apobec.tsv','r') as csvfile:
            self.ApobecDRMs = list(csv.reader(csvfile, delimiter='\t'))
        with open(Path('.')/'sierralocal'/'data'/'INSTI-comments.csv','r') as INSTI_file:
            self.INSTI_comments = dict(csv.reader(INSTI_file,delimiter='\t'))
        with open(Path('.')/'sierralocal'/'data'/'PI-comments.csv','r') as PI_file:
            self.PI_comments = dict(csv.reader(PI_file,delimiter='\t'))
        with open(Path('.')/'sierralocal'/'data'/'RT-comments.csv','r') as RT_file:
            self.RT_comments = dict(csv.reader(RT_file,delimiter='\t'))


    def formatValidationResults(self, validated):
        validationResults = []
        for v in validated:
            validationResults.append({'level' : v[0], 'message' : v[1]})
        return validationResults

    def formatDrugResistance(self, scores,genes):
        drugResistance = {}
        drugResistance['version'] = {}
        drugResistance['version']['text'] = self.version
        drugResistance['version']['publishDate'] = self.version_date
        drugResistance['gene'] = {'name' : genes[0]}
        drugScores = []
        # TODO: find a way to restrict drug classes, e.g. only NRTI/NNRTI for RT gene sequence...
        for gene in genes:
            for drugclass in self.definitions['gene'][gene]:
                classlist = self.definitions['drugclass'][drugclass]
                for drug in classlist:
                    # Only record data if the score is non-zero
                    #if float(scores[drug][0]) == 0.0:
                    #    continue
                    drugScore = {}

                    #Infer resistance level text from the score and globalrange
                    resistancelevel = -1
                    for key in self.globalrange:
                        maximum = float(self.globalrange[key]['max'])
                        minimum = float(self.globalrange[key]['min'])
                        if minimum <= scores[drug][0] <= maximum:
                            resistancelevel = str(key)
                            break
                    resistance_text = self.levels[resistancelevel]

                    drugScore['drugClass'] = {'name':drugclass} #e.g. NRTI
                    drugScore['drug'] = {}
                    if drug in self.names:
                        drugScore['drug']['name'] = self.names[drug]
                    else:
                        drugScore['drug']['name'] = drug.replace('/r','')
                    drugScore['drug']['displayAbbr'] = drug
                    drugScore['score'] = float(scores[drug][0]) # score for this paritcular drug
                    # create partial score, for each mutation, datastructure
                    drugScore['partialScores'] = []
                    for index,pscore in enumerate(scores[drug][1]):
                        pscore = float(pscore)
                        if not pscore == 0.0:
                            pscoredict = {}
                            pscoredict['mutations'] = []
                            for combination in scores[drug][2][index]:
                                # find the mutation classification "type" based on the gene
                                type_ = drugclass
                                pos = re.findall(u'([0-9]+)',combination)[0]
                                muts = re.findall(u'(?<=[0-9])([A-Za-z])+',combination)[0]
                                #print(pos, muts)
                                if gene == 'IN':
                                    for key in self.INSTI_comments:
                                        if pos in key and muts in key:
                                            type_ = self.INSTI_comments[key]
                                            break
                                elif gene == 'PR':
                                    for key in self.PI_comments:
                                        if pos in key and muts in key:
                                            type_ = self.PI_comments[key]
                                            break
                                elif gene == 'RT':
                                    for key in self.RT_comments:
                                        if pos in key and muts in key:
                                            type_ = self.RT_comments[key]
                                            break
                                mut = {}
                                mut['text'] = combination.replace('d', 'Deletion')
                                mut['primaryType'] = type_
                                mut['comments'] = [{
                                    'type' : type_,
                                    'text' : self.findComment(gene, combination, self.comments, self.definitions['comment'])
                                }]
                                pscoredict['mutations'].append(mut)                    
                            pscoredict['score'] = pscore
                            drugScore['partialScores'].append(pscoredict)
                    drugScore['text'] = list(resistance_text)[0] #resistance level
                    drugScores.append(drugScore)
        drugResistance['drugScores'] = drugScores
        return [drugResistance]

    def formatAlignedGeneSequences(self, ordered_mutation_list, genes, firstlastNA):
        dic = {}
        dic['firstAA'] = int((firstlastNA[0]+2)/3)
        dic['lastAA'] = int(firstlastNA[1]/3)
        dic['gene'] = {'name' : genes[0]}
        dic['mutations'] = []
        for mutation in ordered_mutation_list:
            mutdict = {}
            mutdict['consensus'] = mutation[2]
            mutdict['position'] = int(mutation[0])
            mutdict['AAs'] = mutation[1]
            mutdict['isInsertion'] = mutation[1] == '_'
            mutdict['isDeletion'] = mutation[1] == '-'
            mutdict['isApobecDRM'] = self.isApobecDRM(genes[0], mutation[2], mutation[0], mutation[1])
            dic['mutations'].append(mutdict)
        return [dic]

    def formatInputSequence(self, name):
        out = {
            'header' : name
        }
        return out

    def write_to_json(self, filename, names, scores, genes, ordered_mutation_list, sequence_lengths, file_firstlastNA, file_trims):
        '''
        The main function to write passed result to a JSON file
        :param filename: the filename to write the JSON to
        :param names: list of sequence headers
        :param scores: list of sequence scores
        :param genes: list of genes in pol
        :param ordered_mutation_list: ordered list of mutations in the query sequence relative to reference
        '''
        out = []
        for index, score in enumerate(scores):
            data = {}
            data['inputSequence'] = self.formatInputSequence(names[index])
            data['subtypeText'] = None
            validation = self.validateSequence(genes[index], sequence_lengths[index], file_trims[index])
            data['validationResults'] = self.formatValidationResults(validation)
            if not 'CRITICAL' in validation:
                data['alignedGeneSequences'] = self.formatAlignedGeneSequences(ordered_mutation_list[index], genes[index], file_firstlastNA[index])
                data['drugResistance'] = self.formatDrugResistance(score, genes[index])
            else:
                data['alignedGeneSequences'] = []
                data['drugResistance'] = []
            out.append(data)

        with open(filename,'w+') as outfile:
            json.dump(out, outfile, indent=2)
            print("Writing JSON to file {}".format(filename))

    def validateSequence(self, genes, length, seq_trim):
        validation_results = []

        # Length validation
        if ('RT' in genes and length < 200) or ('PR' in genes and length < 80) or ('IN' in genes and length < 200):
            validation_results.append(('WARNING', "The {} sequence contains just {} codons, which is not sufficient for a comprehensive interpretation.".format(genes[0], int(length))))
        elif ('RT' in genes and length < 150) or ('PR' in genes and length < 60) or ('IN' in genes and length < 100):
            validation_results.append('SEVERE WARNING', "The {} sequence contains just {} codons, which is not sufficient for a comprehensive interpretation.".format(genes[0], int(length)))
        # Gene validation
        if len(genes) == 0:
            validation_results.append(('CRITICAL', 'oops?'))

        if seq_trim[0] > 0:
            validation_results.append(('WARNING', "The {} sequence had {} amino acid{} trimmed from its 5\u2032-end due to poor quality.".format(genes[0], seq_trim[0], "s" if seq_trim[0] > 1 else "")))
        if seq_trim[1] > 0:
            validation_results.append(('WARNING', "The {} sequence had {} amino acid{} trimmed from its 3\u2032-end due to poor quality.".format(genes[0], seq_trim[1], "s" if seq_trim[1] > 1 else "")))

        return validation_results

    def findComment(self, gene, mutation, comments, details):
        trunc_mut = re.findall(r'\d+\D',mutation)[0] #163K
        pos = re.findall(u'([0-9]+)',trunc_mut)[0]
        muts = re.findall(u'(?<=[0-9])([A-Za-z])+',trunc_mut)[0]
        for g, mutationdict in comments.items():
            for item in mutationdict.keys():
                if pos in item and muts in item:
                    full_mut = mutationdict[item]
                    if full_mut in details and g == gene:
                        return details[full_mut]['1']

    def isApobecDRM(self, gene, consensus, position, AA):
        ls = [row[0:3] for row in self.ApobecDRMs[1:]]
        if [gene, consensus, str(position)] in ls:
            i = ls.index([gene, consensus, str(position)])
            for aa in AA:
                if aa in self.ApobecDRMs[1:][i][3]:
                    return True
        return False

if __name__ == "__main__":
    writer = JSONWriter()
    assert (writer.isApobecDRM("IN", "G", 163, "TRAG")) == True