"""
OMXWare Gene Entity Class
"""


class Gene:
    """Gene Class"""

    def __init__(self, connecthdr, gene):
        """Constructor"""

        if not ("GENE_UID_KEY" in gene):
            raise Exception("The GENE_UID_KEY is missing in the given Gene object.")

        self._jobj = gene

        self._geneUidKey = gene['GENE_UID_KEY']
        self._geneName = gene['GENE_FULLNAME']

        self._connecthdr = connecthdr

    def __str__(self):
        return "{'type': 'gene', 'uid': '" + self.get_uid() + "', 'name': '" + self.get_name() + "'}"

    def get_name(self):
        return str(self._geneName)

    def get_uid(self):
        return str(self._geneUidKey)