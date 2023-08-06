"""
OMXWare Protein Entity Class
"""


class Protein:
    """Protein Class"""

    def __init__(self, connecthdr, protein):
        """Constructor"""

        if not ("PROTEIN_UID_KEY" in protein):
            raise Exception("The PROTEIN_UID_KEY is missing in the given Protein object.")

        self._jobj = protein

        self._proteinUidKey = protein['PROTEIN_UID_KEY']
        self._proteinName = protein['PROTEIN_FULLNAME']

        self._connecthdr = connecthdr

    def __str__(self):
        return "{ 'type': 'protein', 'uid': '" + self.get_uid() + "', 'name': '" + self.get_name() + "'}"

    def get_name(self):
        return str(self._proteinName)

    def get_uid(self):
        return str(self._proteinUidKey)