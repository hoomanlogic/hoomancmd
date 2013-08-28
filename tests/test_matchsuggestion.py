
def test_matchsuggestion(self, line):
    args = self.split_args(line)
    import hoomancmd.hoomancmd.matchsuggestion as suggest
    bestmatch = suggest.getbestmatch_v3(args[0], args[1:], set_max_sequential_disparity=2)
    self.print_line(bestmatch.matchterm, bestmatch.get_score(), bestmatch.runner_up_matchterm, bestmatch.runner_up_score)