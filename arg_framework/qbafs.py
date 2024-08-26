from bafs import BAF


class QBAF(BAF):

    def __init__(self, explanandum: str, arguments: list[str], tau, semantics, eval_range, attacks: list[tuple] = None, supports: list[tuple] = None):
        super().__init__(explanandum, arguments, attacks, supports)
        # tau is a function from the set of argument nodes to a chosen evaluation range
        # which assigns a base score the arguments
        self._tau = tau
        # a gradual semantics function which calculates a dialectical strength for arguments
        # parameters should be the QBAF and argument number
        self._semantics = semantics
        # function that determines the positive (1), negative (-1) and neutral (0) divisions of the evaluation range
        self._eval_range = eval_range

    def update_tau(self, new_tau):
        self._tau = new_tau

    def update_semantics(self, new_semantics):
        self._semantics = new_semantics

    def update_eval_range(self, new_eval_range):
        self._eval_range = new_eval_range

    def tau(self, a: int):
        return self._tau(self.get_argument(a))

    def evaluate_argument(self, a):
        return self._semantics(self, a)

    def get_stance(self, return_score = False):
        score = self.evaluate_argument(0)
        stance = self._eval_range(score)
        if return_score:
            return stance, score
        return stance
