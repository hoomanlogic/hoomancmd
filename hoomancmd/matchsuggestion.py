### score matched, proximity, missing, or nomatch to find the best fit command ###
# todo: Improve suggestion engine
# >> plns
# Did you mean 'logs'? : 97 : journal:90

# used by all versions
proximity_mapping = {
    'q': ['a', 's', 'w', '2', '1', '`'],
    'w': ['q', 'a', 's', 'd', 'e', '3', '2', '1'],
    'e': ['w', 's', 'd', 'f', 'r', '4', '3', '2'],
    'r': ['e', 'd', 'f', 'g', 't', '5', '4', '3'],
    't': ['r', 'f', 'g', 'h', 'y', '6', '5', '4'],
    'y': ['t', 'g', 'h', 'j', 'u', '7', '6', '5'],
    'u': ['y', 'h', 'j', 'k', 'i', '8', '7', '6'],
    'i': ['u', 'j', 'k', 'l', 'o', '9', '8', '7'],
    'o': ['i', 'k', 'l', ';', 'p', '0', '9', '8'],
    'p': ['o', 'l', ';', '\'', '[', '-', '0', '9'],
    '[': ['p', ';', '\'', ']', '=', '-', '0'],
    ']': ['[', '\'', '\\', '='],

    'a': ['z', 'x', 's',           'w', 'q'],
    's': ['a', 'z', 'x', 'c', 'd', 'e', 'w', 'q'],
    'd': ['s', 'x', 'c', 'v', 'f', 'r', 'e', 'w'],
    'f': ['d', 'c', 'v', 'b', 'g', 't', 'r', 'e'],
    'g': ['f', 'v', 'b', 'n', 'h', 'y', 't', 'r'],
    'h': ['g', 'b', 'n', 'm', 'j', 'u', 'y', 't'],
    'j': ['h', 'n', 'm', ',', 'k', 'i', 'u', 'y'],
    'k': ['j', 'm', ',', '.', 'l', 'o', 'i', 'u'],
    'l': ['k', ',', '.', '/', ';', 'p', 'o', 'i'],
    ';': ['l', '.', '/', '\'', '[', 'p'],
    '\'': [';', '/', ']', '[', 'p'],

    'z': [     'x', 's', 'a'],
    'x': ['z', 'c', 'd', 's', 'a'],
    'c': ['x', 'v', 'f', 'd', 's'],
    'v': ['c', 'b', 'g', 'f', 'd'],
    'b': ['v', 'n', 'h', 'g', 'f'],
    'n': ['b', 'm', 'j', 'h', 'g'],
    'm': ['n', ',', 'k', 'j', 'h'],

    '1': ['q', 'w', '2', '`'],
    '2': ['1', 'q', 'w', 'e', '3'],
    '3': ['2', 'w', 'e', 'r', '4'],
    '4': ['3', 'e', 'r', 't', '5'],
    '5': ['4', 'r', 't', 'y', '6'],
    '6': ['5', 't', 'y', 'u', '7'],
    '7': ['6', 'y', 'u', 'i', '8'],
    '8': ['7', 'u', 'i', 'o', '9'],
    '9': ['8', 'i', 'o', 'p', '0'],
    '0': ['9', 'o', 'p', '[', '-'],
    '-': ['0', 'p', '[', ']', '='],
    '+': ['-', '[', ']', '\\']
}

# version 1 variables
max_extra = 1  # input has extra characters
max_missing = -1  # input has less characters


class MatchStats(object):
    def __init__(self, item, disparity):
        self.match = 0
        self.proximity = 0
        self.disparity = disparity
        self.item = item
        self.too_disparate = False
        self.missing = 0

    def increment_match(self):
        self.match += 1

    def increment_proximity(self):
        self.proximity += 1

    def increment_proximity(self):
        self.proximity += 1

    def increment_missing(self):
        self.missing += 1

    def compare(self, other_instance):
        if other_instance is None:
            return self

        if self.proximity > other_instance.proximity:
            return other_instance
        elif self.proximity < other_instance.proximity:
            return self
        else:
            if self.match > other_instance.match:
                return self
            elif self.match < other_instance.match:
                return other_instance
            else:
                if self.disparity > other_instance.disparity:
                    return other_instance
                else:
                    return self


class BetterMatchStats(object):
    # version 2 & 3 variables
    max_sequential_disparity = 2

    def __init__(self, matchterm):
        self.match = 0
        self.proximity = 0
        self.disparity = 0
        self.sequential_disparity = 0
        self.matchterm = matchterm
        self.too_disparate = False
        self.runner_up_score = 0
        self.runner_up_matchterm = ''

    def increment_match(self):
        self.match += 1
        self._reset_sequential_disparity()

    def increment_proximity(self):
        self.proximity += 1
        self._reset_sequential_disparity()

    def increment_disparity(self):
        self.disparity += 1
        self._increment_sequential_disparity()
        if self.disparity > len(self.matchterm):
            self.too_disparate = True

    def _increment_sequential_disparity(self):
        self.sequential_disparity += 1
        if self.sequential_disparity > BetterMatchStats.max_sequential_disparity:
            self.too_disparate = True

    def _reset_sequential_disparity(self):
        self.sequential_disparity = 0

    def get_score(self):
        if self.disparity == 0 and self.proximity == 0:
            return 100
        else:
            return 100 - ((self.disparity * 2) + self.proximity)

    def compare(self, other_instance):
        if other_instance is None or other_instance.too_disparate:
            return self

        if self.too_disparate:
            other_instance.runner_up_score = self.get_score()
            other_instance.runner_up_matchterm = self.matchterm
            return other_instance

        if self.disparity > other_instance.disparity:
            other_instance.runner_up_score = self.get_score()
            other_instance.runner_up_matchterm = self.matchterm
            return other_instance
        elif self.disparity < other_instance.disparity:
            return self

        if self.match > other_instance.match:
            return self
        elif self.match < other_instance.match:
            other_instance.runner_up_score = self.get_score()
            other_instance.runner_up_matchterm = self.matchterm
            return other_instance

        if self.proximity > other_instance.proximity:
            other_instance.runner_up_score = self.get_score()
            other_instance.runner_up_matchterm = self.matchterm
            return other_instance
        else:
            return self

    def copy_attributes(self, other_instance):
        self.match = other_instance.match
        self.proximity = other_instance.proximity
        self.disparity = other_instance.disparity
        self.sequential_disparity = other_instance.sequential_disparity
        self.too_disparate = other_instance.too_disparate

    @classmethod
    def copy(cls, obj):
        instance = BetterMatchStats(obj.matchterm)
        instance.match = obj.match
        instance.proximity = obj.proximity
        instance.disparity = obj.disparity
        instance.sequential_disparity = obj.sequential_disparity
        instance.too_disparate = obj.too_disparate
        return instance


def is_in_proximity(char1, char2):
    if char2 in proximity_mapping[char1]:
        return True
    else:
        return False


# version 1
def getbestmatch_v1(input_, list_):
    input_ = input_.lower()
    matchstats_best = None
    for item in list_:
        item = item.lower()
        disparity = len(input_) - len(item)
        # ensure disparity isn't too great
        if disparity < max_missing or disparity > max_extra:
            continue

        inner = input_
        outer = item
        if disparity < 0:
            inner = input_
            outer = item
        elif disparity > 0:
            inner = item
            outer = input_

        # now we put the smaller as the inner to move around
        # so we use the absolute val of disparity to
        # put the smaller through the scenarios

        for i in range(0, abs(disparity) + 1):
            outer_subset = outer[i:]
            matchstats = MatchStats(item, abs(disparity))

            # loop through characters and compare them
            for j, inner_char in enumerate(inner):
                if inner_char == outer_subset[j]:
                    matchstats.increment_match()
                    continue
                elif is_in_proximity(inner_char, outer_subset[j]):
                    matchstats.increment_proximity()
                    continue
                else:
                    matchstats.too_disparate = True
                    break

            if not matchstats.too_disparate:
                matchstats_best = matchstats.compare(matchstats_best)

    if matchstats_best is None:
        return None
    else:
        return matchstats_best.item


# version 2
def getbestmatch_v2(input_, list_):
    # case insenitive matching
    input_ = input_.lower()

    # stores best match so far
    current_matchstats_best = None

    # iterate through all the possible matchterms
    # to find the best match
    for matchterm in list_:

        # case insenitive matching
        matchterm = matchterm.lower()

        # ensure disparity isn't too great from the get go
        # by comparing overall length, if it is too disparate
        # then move on to the next matchterm
        # if abs(len(input_) - len(matchterm)) > max_sequential_disparity:
        #     continue

        # create object to hold the match stats
        matchstats = BetterMatchStats(matchterm)

        # run the input_ and matchterm through
        # scenarios find a potential match
        matchup_v2(input_, matchterm, matchstats)

        # done with while because we hit the end of an index
        # now let's calculate the leftover disparity
        max_char_len = 0
        if len(input_) > len(matchterm):
            max_char_len = len(input_)
        else:
            max_char_len = len(matchterm)
        for i in (range(0, abs(max_char_len - (matchstats.match + matchstats.proximity + matchstats.disparity)))):
            matchstats.increment_disparity()

        # compare the matchstats after matchup with the current best matchstats
        # and set the better of the two to the best match so far
        # -- may the best match win...
        current_matchstats_best = matchstats.compare(current_matchstats_best)

    return current_matchstats_best.matchterm


def matchup_v2(input_, matchterm, matchstats, depth=0):
    input_index = 0
    matchterm_index = 0
    while matchterm_index <  len(matchterm) and input_index < len(input_):
        if input_[input_index] == matchterm[matchterm_index]:
            matchstats.increment_match()
            input_index = input_index + 1
            matchterm_index = matchterm_index + 1
            continue
        elif is_in_proximity(input_[input_index], matchterm[matchterm_index]):
            matchstats.increment_proximity()
            input_index = input_index + 1
            matchterm_index = matchterm_index + 1
        else:
            # increment disparity and check if we are too disparate
            matchstats.increment_disparity()
            if matchstats.too_disparate:
                return

            # here we need to branch and try both the possibility that input_ has
            # missing or extra chars, then compare the two branches to pick the
            # best matchup

            # input_ may have bad chars, similar to the proximity solution,
            # but treats it as a disparity
            bad_char_scenario = None
            if input_index + 1 <= len(input_) and matchterm_index + 1 <= len(matchterm):
                bad_char_scenario = BetterMatchStats.copy(matchstats)
                matchup_v2(input_[input_index + 1:], matchterm[matchterm_index + 1:], bad_char_scenario, depth=depth+1)

            # input_ may have missing chars
            missing_char_scenario = None
            if matchterm_index + 1 <= len(matchterm):
                missing_char_scenario = BetterMatchStats.copy(matchstats)
                matchup_v2(input_[input_index:], matchterm[matchterm_index + 1:], missing_char_scenario, depth=depth+1)

            # input_ may have extra chars
            extra_char_scenario = None
            if input_index + 1 <= len(input_):
                extra_char_scenario = BetterMatchStats.copy(matchstats)
                matchup_v2(input_[input_index + 1:], matchterm[matchterm_index:], extra_char_scenario, depth=depth+1)

            # if both the input_ and matchterm have reached the end of their input_
            # then return
            if input_index + 1 >= len(input_) and matchterm_index + 1 >= len(matchterm):
                return

            # grab either one that is not None and compare to the other
            # one, which may be None, but one of these scenarios is
            # guaranteed to not be None by this point
            best_scenario = None
            if missing_char_scenario is not None:
                best_scenario = missing_char_scenario.compare(extra_char_scenario)
            else:
                best_scenario = extra_char_scenario.compare(missing_char_scenario)

            # compare the winner of missing vs extra with the bad chars scenario
            best_scenario = best_scenario.compare(bad_char_scenario)

            # copy the attributes from the best scenario
            # because simply setting the object makes the
            # root caller lose the changes
            matchstats.copy_attributes(best_scenario)
            return

            # investigate this
            # >> veweerython
            # Did you mean "deleteprop"?


# version 3
def getbestmatch_v3(input_, list_, set_max_sequential_disparity=None):
    # case insenitive matching
    input_ = input_.lower()

    # stores best match so far
    current_matchstats_best = None

    if set_max_sequential_disparity is not None:
        BetterMatchStats.max_sequential_disparity = set_max_sequential_disparity

    # iterate through all the possible matchterms
    # to find the best match
    for matchterm in list_:

        # case insenitive matching
        matchterm = matchterm.lower()

        # ensure disparity isn't too great from the get go
        # by comparing overall length, if it is too disparate
        # then move on to the next matchterm
        # if abs(len(input_) - len(matchterm)) > max_sequential_disparity:
        #     continue

        # create object to hold the match stats
        matchstats = BetterMatchStats(matchterm)

        if len(input_) > len(matchterm):
            max_char_len = len(input_)
            inner = matchterm
            outer = input_
        else:
            max_char_len = len(matchterm)
            inner = input_
            outer = matchterm

        # run the input_ and matchterm through
        # scenarios find a potential match
        matchup_v3(inner, outer, matchstats)

        for i in (range(0, abs(max_char_len - (matchstats.match + matchstats.proximity + matchstats.disparity)))):
            matchstats.disparity = matchstats.disparity + 1

        # compare the matchstats after matchup with the current best matchstats
        # and set the better of the two to the best match so far
        # -- may the best match win...
        current_matchstats_best = matchstats.compare(current_matchstats_best)

        # >> testmatch hooman human humous humid
        # humid 90  0

    return current_matchstats_best


def matchup_v3(input_, matchterm, matchstats, depth=0):
    input_index = 0
    matchterm_index = 0
    while matchterm_index <  len(matchterm) and input_index < len(input_):
        if input_[input_index] == matchterm[matchterm_index]:
            matchstats.increment_match()
            input_index = input_index + 1
            matchterm_index = matchterm_index + 1
            continue
        elif is_in_proximity(input_[input_index], matchterm[matchterm_index]):
            matchstats.increment_proximity()
            input_index = input_index + 1
            matchterm_index = matchterm_index + 1
        else:
            # increment disparity and check if we are too disparate
            matchstats.increment_disparity()
            if matchstats.too_disparate:
                return

            # here we need to branch and try both the possibility that input_ has
            # missing or extra chars, then compare the two branches to pick the
            # best matchup

            # input_ may have bad chars, similar to the proximity solution,
            # but treats it as a disparity
            bad_char_scenario = None
            if input_index + 1 <= len(input_) and matchterm_index + 1 <= len(matchterm):
                bad_char_scenario = BetterMatchStats.copy(matchstats)
                matchup_v3(input_[input_index + 1:], matchterm[matchterm_index + 1:], bad_char_scenario, depth=depth+1)

            # input_ may have missing chars
            missing_char_scenario = None
            if matchterm_index + 1 <= len(matchterm):
                missing_char_scenario = BetterMatchStats.copy(matchstats)
                matchup_v3(input_[input_index:], matchterm[matchterm_index + 1:], missing_char_scenario, depth=depth+1)

            # input_ may have extra chars
            extra_char_scenario = None
            if input_index + 1 <= len(input_):
                extra_char_scenario = BetterMatchStats.copy(matchstats)
                matchup_v3(input_[input_index + 1:], matchterm[matchterm_index:], extra_char_scenario, depth=depth+1)

            # if both the input_ and matchterm have reached the end of their input_
            # then return
            if input_index + 1 >= len(input_) and matchterm_index + 1 >= len(matchterm):
                return

            # grab either one that is not None and compare to the other
            # one, which may be None, but one of these scenarios is
            # guaranteed to not be None by this point
            best_scenario = None
            if missing_char_scenario is not None:
                best_scenario = missing_char_scenario.compare(extra_char_scenario)
            else:
                best_scenario = extra_char_scenario.compare(missing_char_scenario)

            # compare the winner of missing vs extra with the bad chars scenario
            best_scenario = best_scenario.compare(bad_char_scenario)

            # copy the attributes from the best scenario
            # because simply setting the object makes the
            # root caller lose the changes
            matchstats.copy_attributes(best_scenario)
            return


