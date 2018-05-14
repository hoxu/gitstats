from dataclasses import dataclass
from typing import Dict, List, Set
from gitstats.data.revision import Revision

@dataclass
class RevisionGraph:
    revisions: Dict[str, Revision]
    master_revs: Set[str]
    linkage: Dict[str, List[str]]

    def add_revision_to_graph(self, revision: Revision, parents: List[str], is_master: bool=False):
        if not revision.hash in self.revisions:
            self.revisions[revision.hash] = revision
        if not revision.hash in self.linkage:
            self.linkage[revision.hash] = parents
        if revision.master_pr or is_master:
            self.master_revs.add(revision.hash)
