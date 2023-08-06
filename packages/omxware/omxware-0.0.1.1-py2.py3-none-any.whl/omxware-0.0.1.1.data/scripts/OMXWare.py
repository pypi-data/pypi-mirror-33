"""
OMXWare Services Package
"""

from omxware.Config import *
from omxware.Connect import *
from omxware.Gene import Gene
from omxware.Genome import *

import simplejson as json

from omxware.Genus import Genus
from omxware.Protein import Protein


class OMXWare:
    """OMXWare Services Class"""

    @staticmethod
    def connect():
        """Make a connection to OMXWare and save the context for further connections"""

        config = Configuration();
        hosturl = config.getHostURL()

        connecthdr = Connection(hosturl)
        connecthdr.connect()

        return connecthdr

    @staticmethod
    def disconnect(connecthdr):
        """End the connection the OMXWare and destroy the context"""
        connecthdr.disconnect()
        connecthdr = None

# GENUS #
    @staticmethod
    def all_genera():
        """Return all the Genera
        """
        connecthdr = OMXWare.connect()

        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        methodurl = "/genus/all"
        params = {'fromCache': 'true'}
        genusResp = connecthdr.get(methodurl=methodurl, headers=headers, payload=params)
        if genusResp is not None:
            genusRepJ = genusResp.json()
            if len(genusRepJ["result"]) <= 0:
                return None
            else:

                genusJ = genusRepJ["result"]
                genera = []
                for genus in genusJ:
                    genera.append((Genus(connecthdr, genus)))

                return genera
        else:
            return None

 # GENOMES #

    @staticmethod
    def genome(accession_number):
        """Return the meta data about a genome with a given genome accession_number

            Arguments:
              accession_number -- genome accession number
        """

        connecthdr = OMXWare.connect()

        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        genomemethodurl = "/genomes/id:" + str(accession_number)
        params = json.dumps({"fromCache": "true"})

        genomeResp = connecthdr.get(methodurl=genomemethodurl, headers=headers, payload=params)
        if genomeResp is not None:
            genomeRepJ = genomeResp.json()
            if len(genomeRepJ["result"]) <= 0:
                return None
            else:
                genomeJ = genomeRepJ["result"][0]
                return (Genome(connecthdr, genomeJ))
        else:
            return None

    @staticmethod
    def genomes_by_genus(genus_name):
        """Return all the Genomes encoding a Genus - by genus name

            Arguments:
              genus_name -- Genus name
        """
        connecthdr = OMXWare.connect()

        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        methodurl = "/genomes/name:" + str(genus_name)
        params = {'fromCache': 'true'}
        genomeResp = connecthdr.get(methodurl=methodurl, headers=headers, payload=params)
        if genomeResp is not None:
            genomeRepJ = genomeResp.json()
            if len(genomeRepJ["result"]) <= 0:
                return None
            else:

                genomesJ = genomeRepJ["result"]
                genomes = []
                for genome in genomesJ:
                    genomes.append((Genome(connecthdr, genome)))

                return genomes
        else:
            return None

    @staticmethod
    def genes_by_genome(accession_number):
        """Return all the genes encoding a genome - by genome accession_number

            Arguments:
              accession_number -- genome accession number
        """
        connecthdr = OMXWare.connect()

        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        methodurl = "/genomes/id:"+str(accession_number)+"/all/genes"
        params = {'fromCache': 'true'}
        genesResp = connecthdr.get(methodurl=methodurl, headers=headers, payload=params)
        if genesResp is not None:
            genesRespJ = genesResp.json()
            if len(genesRespJ["result"]) <= 0:
                return None
            else:

                genesJ = genesRespJ["result"]
                genes = []
                for gene in genesJ:
                    genes.append((Gene(connecthdr, gene)))

                return genes
        else:
            return None

    @staticmethod
    def resistant_genes_by_genome(accession_number):
        """Return all the resistant genes encoding a genome - by genome accession_number

            Arguments:
              accession_number -- genome accession number
        """
        connecthdr = OMXWare.connect()

        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        methodurl = "/genomes/id:" + str(accession_number) + "/all/genes:resistant"
        params = {'fromCache': 'true'}
        genesResp = connecthdr.get(methodurl=methodurl, headers=headers, payload=params)
        if genesResp is not None:
            genesRespJ = genesResp.json()
            if len(genesRespJ["result"]) <= 0:
                return None
            else:

                genesJ = genesRespJ["result"]
                genes = []
                for gene in genesJ:
                    genes.append((Gene(connecthdr, gene)))

                return genes
        else:
            return None

    @staticmethod
    def genera_with_resistant_genes_by_genome(accession_number):
        """Return all the Genera containing the resistant genes encoding a genome - by genome accession_number

            Arguments:
              accession_number -- genome accession number
        """
        connecthdr = OMXWare.connect()

        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        methodurl = "/genomes/id:" + str(accession_number) + "/all/genes:resistant/genera"
        params = {'fromCache': 'true'}
        generaResp = connecthdr.get(methodurl=methodurl, headers=headers, payload=params)
        if generaResp is not None:
            generaRespJ = generaResp.json()
            if len(generaRespJ["result"]) <= 0:
                return None
            else:

                generaJ = generaRespJ["result"]
                genera = []
                for genus in generaJ:
                    genera.append((Genus(connecthdr, genus)))

                return genera
        else:
            return None

    @staticmethod
    def genomes_with_resistant_genes_by_genome(accession_number):
        """Return all the Genomes containing the resistant genes encoding a genome - by genome accession_number

            Arguments:
              accession_number -- genome accession number
        """
        connecthdr = OMXWare.connect()

        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        methodurl = "/genomes/id:" + str(accession_number) + "/all/genes:resistant/genomes"
        params = {'fromCache': 'true'}
        genomesResp = connecthdr.get(methodurl=methodurl, headers=headers, payload=params)
        if genomesResp is not None:
            genomesRespJ = genomesResp.json()
            if len(genomesRespJ["result"]) <= 0:
                return None
            else:

                genomesJ = genomesRespJ["result"]
                genomes = []
                for genome in genomesJ:
                    genomes.append((Genus(connecthdr, genome)))

                return genomes
        else:
            return None

    @staticmethod
    def proteins_by_genome(accession_number):
        """Return all the proteins encoding a genome - by genome accession_number

            Arguments:
              accession_number -- genome accession number
        """
        connecthdr = OMXWare.connect()

        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        methodurl = "/genomes/id:" + str(accession_number) + "/all/proteins"
        params = {'fromCache': 'true'}
        proteinsResp = connecthdr.get(methodurl=methodurl, headers=headers, payload=params)
        if proteinsResp is not None:
            proteinsRespJ = proteinsResp.json()
            if len(proteinsRespJ["result"]) <= 0:
                return None
            else:

                proteinsJ = proteinsRespJ["result"]
                proteins = []
                for protein in proteinsJ:
                    proteins.append((Protein(connecthdr, protein)))

                return proteins
        else:
            return None

 # GENES #
    @staticmethod
    def gene(GENE_UID_KEY):
        '''
            Gene by GENE_UID_KEY
            :param GENE_UID_KEY:
            :return: Gene
        '''

        connecthdr = OMXWare.connect()

        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        methodurl = "/genes/id:" + str(GENE_UID_KEY)
        params = json.dumps({"fromCache": "true"})

        geneResp = connecthdr.get(methodurl=methodurl, headers=headers, payload=params)
        if geneResp is not None:
            geneRepJ = geneResp.json()
            if len(geneRepJ["result"]) <= 0:
                return None
            else:
                geneJ = geneRepJ["result"][0]
                return (Gene(connecthdr, geneJ))
        else:
            return None

    @staticmethod
    def genes_by_name(GENE_FULLNAME):
        '''
        Genes by name
        :param GENE_FULLNAME:
        :return: List<Gene>
        '''

        connecthdr = OMXWare.connect()

        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        methodurl = "/genes/name:" + str(GENE_FULLNAME)
        params = {'fromCache': 'true'}
        geneResp = connecthdr.get(methodurl=methodurl, headers=headers, payload=params)
        if geneResp is not None:
            geneRepJ = geneResp.json()
            if len(geneRepJ["result"]) <= 0:
                return None
            else:

                genesJ = geneRepJ["result"]
                genes = []
                for gene in genesJ:
                    genes.append((Gene(connecthdr, gene)))

                return genes
        else:
            return None

    @staticmethod
    def resistant_genes():
        '''
        Get all Resistant Genes
        :return: List<Gene>
        '''

        connecthdr = OMXWare.connect()

        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        methodurl = "/genes/all/genes:resistant"
        params = {'fromCache': 'true'}
        geneResp = connecthdr.get(methodurl=methodurl, headers=headers, payload=params)
        if geneResp is not None:
            geneRepJ = geneResp.json()
            if len(geneRepJ["result"]) <= 0:
                return None
            else:

                genesJ = geneRepJ["result"]
                genes = []
                for gene in genesJ:
                    genes.append((Gene(connecthdr, gene)))

                return genes
        else:
            return None

    @staticmethod
    def genera_by_gene_name(GENE_FULLNAME):
        '''
            Get all the Genera containing genes by Gene name
            :param GENE_FULLNAME:
            :return: List<Genus>
        '''

        connecthdr = OMXWare.connect()

        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        methodurl = "/genes/name:" + str(GENE_FULLNAME)+"/all/genera"
        params = {'fromCache': 'true'}
        generaResp = connecthdr.get(methodurl=methodurl, headers=headers, payload=params)
        if generaResp is not None:
            generaRepJ = generaResp.json()
            if len(generaRepJ["result"]) <= 0:
                return None
            else:

                generaJ = generaRepJ["result"]
                genera = []
                for genus in generaJ:
                    genera.append((Genus(connecthdr, genus)))

                return genera
        else:
            return None

    @staticmethod
    def genomes_by_gene_name(GENE_FULLNAME):
        '''
            Get all the Genomes containing genes by Gene name
            :param GENE_FULLNAME:
            :return: List<Genome>
        '''

        connecthdr = OMXWare.connect()

        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        methodurl = "/genes/name:" + str(GENE_FULLNAME) + "/all/genomes"
        params = {'fromCache': 'true'}
        genomesResp = connecthdr.get(methodurl=methodurl, headers=headers, payload=params)
        if genomesResp is not None:
            genomesRepJ = genomesResp.json()
            if len(genomesRepJ["result"]) <= 0:
                return None
            else:

                genomesJ = genomesRepJ["result"]
                genomes = []
                for genome in genomesJ:
                    genomes.append((Genus(connecthdr, genome)))

                return genomes
        else:
            return None

 # PROTEINS #
    @staticmethod
    def protein(PROTEIN_UID_KEY):
        '''
            Protein by PROTEIN_UID_KEY
            :param PROTEIN_UID_KEY:
            :return: Protein
        '''

        connecthdr = OMXWare.connect()

        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        methodurl = "/proteins/id:" + str(PROTEIN_UID_KEY)
        params = json.dumps({"fromCache": "true"})

        proteinResp = connecthdr.get(methodurl=methodurl, headers=headers, payload=params)
        if proteinResp is not None:
            proteinRepJ = proteinResp.json()
            if len(proteinRepJ["result"]) <= 0:
                return None
            else:
                proteinJ = proteinRepJ["result"][0]
                return (Protein(connecthdr, proteinJ))
        else:
            return None

    @staticmethod
    def proteins_by_name(PROTEIN_FULLNAME):
        '''
        Proteins by name
        :param PROTEIN_FULLNAME:
        :return: List<Protein>
        '''

        connecthdr = OMXWare.connect()

        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        methodurl = "/proteins/name:" + str(PROTEIN_FULLNAME)
        params = {'fromCache': 'true'}
        proteinResp = connecthdr.get(methodurl=methodurl, headers=headers, payload=params)
        if proteinResp is not None:
            proteinRepJ = proteinResp.json()
            if len(proteinRepJ["result"]) <= 0:
                return None
            else:

                proteinsJ = proteinRepJ["result"]
                proteins = []
                for protein in proteinsJ:
                    proteins.append((Protein(connecthdr, protein)))

                return proteins
        else:
            return None

    @staticmethod
    def genera_by_protein_name(PROTEIN_FULLNAME):
        '''
            Get all the Genera containing proteins by Protein name
            :param PROTEIN_FULLNAME:
            :return: List<Genus>
        '''

        connecthdr = OMXWare.connect()

        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        methodurl = "/proteins/name:" + str(PROTEIN_FULLNAME)+"/all/genera"
        params = {'fromCache': 'true'}
        generaResp = connecthdr.get(methodurl=methodurl, headers=headers, payload=params)
        if generaResp is not None:
            generaRepJ = generaResp.json()
            if len(generaRepJ["result"]) <= 0:
                return None
            else:

                generaJ = generaRepJ["result"]
                genera = []
                for genus in generaJ:
                    genera.append((Genus(connecthdr, genus)))

                return genera
        else:
            return None

    @staticmethod
    def genomes_by_protein_name(PROTEIN_FULLNAME):
        '''
            Get all the Genomes containing proteins by Protein name
            :param PROTEIN_FULLNAME:
            :return: List<Genome>
        '''

        connecthdr = OMXWare.connect()

        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        methodurl = "/proteins/name:" + str(PROTEIN_FULLNAME) + "/all/genomes"
        params = {'fromCache': 'true'}
        genomesResp = connecthdr.get(methodurl=methodurl, headers=headers, payload=params)
        if genomesResp is not None:
            genomesRepJ = genomesResp.json()
            if len(genomesRepJ["result"]) <= 0:
                return None
            else:

                genomesJ = genomesRepJ["result"]
                genomes = []
                for genome in genomesJ:
                    genomes.append((Genome(connecthdr, genome)))

                return genomes
        else:
            return None

    @staticmethod
    def search(keyword):
        '''

        :param keyword: Search keyword
        :return: Results grouped by entity type
        '''

        connecthdr = OMXWare.connect()

        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        methodurl = "/search/" + str(keyword)
        params = {'fromCache': 'true'}
        searchResp = connecthdr.get(methodurl=methodurl, headers=headers, payload=params)
        if searchResp is not None:
            searchRepJ = searchResp.json()
            if len(searchRepJ["result"]) <= 0:
                return None
            else:
                genesJ = searchRepJ["result"]["GENE"]
                generaJ = searchRepJ["result"]["GENUS"]
                genomesJ = searchRepJ["result"]["GENOME"]
                # proteinsJ = searchRepJ["result"]["PROTEIN"]

                genera = []
                genomes = []
                genes = []
                # proteins = []

                for genus in generaJ:
                    genera.append((Genus(connecthdr, genus)))

                for genome in genomesJ:
                    genomes.append((Genome(connecthdr, genome)))

                for gene in genesJ:
                    genes.append((Gene(connecthdr, gene)))

                # for protein in proteinsJ:
                #     proteins.append((Protein(connecthdr, protein)))

                result = {}
                result['genera'] = genera
                result['genomes'] = genomes
                result['genes'] = genes
                # result['proteins'] = proteins

                return result
        else:
            return None

    @staticmethod
    def sql(sql_query, fromCache=True):
        '''

        :param sql_query: SQL to query OMX DB
        :return: SQL query result as JSON
        '''

        connecthdr = OMXWare.connect()

        headers = {'content-type': 'application/json',
                   'content-language': 'en-US',
                   'accept': 'application/json'}
        methodurl = "/query/db/omxdb"

        # params = json.dumps({'fromCache':str(fromCache)})
        # params = {'fromCache': 'true'}
        
        params = {'fromCache':str(fromCache), 'sql_query': sql_query}
        
        sqlResp = connecthdr.get(methodurl=methodurl, headers=headers, payload=params)
        if sqlResp is not None:
            sqlRepJ = sqlResp.json()
            if len(sqlRepJ["result"]) <= 0:
                return None
            else:
                return sqlRepJ["result"]
