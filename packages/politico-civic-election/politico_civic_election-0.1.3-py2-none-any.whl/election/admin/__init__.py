from django.contrib import admin
from election.models import (Candidate, CandidateElection, Election,
                             ElectionCycle, ElectionDay, ElectionType, Race)
from .candidate import CandidateAdmin
from .candidate_election import CandidateElectionAdmin
from .election import ElectionAdmin
from .election_cycle import ElectionCycleAdmin
from .election_day import ElectionDayAdmin
from .election_type import ElectionTypeAdmin
from .race import RaceAdmin


admin.site.register(Race, RaceAdmin)
admin.site.register(Election, ElectionAdmin)
admin.site.register(CandidateElection, CandidateElectionAdmin)
admin.site.register(ElectionDay, ElectionDayAdmin)
admin.site.register(ElectionType, ElectionTypeAdmin)
admin.site.register(ElectionCycle, ElectionCycleAdmin)
admin.site.register(Candidate, CandidateAdmin)
