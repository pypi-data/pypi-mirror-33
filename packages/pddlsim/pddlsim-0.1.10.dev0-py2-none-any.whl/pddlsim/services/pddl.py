class PDDL():

    """
    Contains the paths to the domain and problem pddl files used
    """

    def __init__(self, domain_path, problem_path):
        self.domain_path = domain_path
        self.problem_path = problem_path

    @staticmethod
    def create_with_simplified_problem_if_necessary(parser, problem_generator):
        problem_path = parser.problem_path
        if parser.uses_custom_features:
            problem_path = problem_generator.generate_problem(parser.goals[0])
        return PDDL(parser.domain_path, problem_path)
