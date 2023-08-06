from random_executor import RandomExecutor
from pddlsim.simulator import Simulator
import random
import copy


class AvoidReturn(RandomExecutor):

    def __init__(self):
        super(AvoidReturn, self).__init__(True)

    def initialize(self, services):
        super(AvoidReturn, self).initialize(services)
        self.previous_state = None
        self.last_different_state = None

    def next_action(self):
        '''
        save previous state after choosing next action
        '''
        next_action = super(AvoidReturn, self).next_action()
        current_state = self.services.perception.get_state()
        if current_state != self.previous_state:
            self.last_different_state = self.previous_state
        self.previous_state = current_state
        return next_action

    def is_next_state_same_as_previous(self, option):
        next_state = self.services.perception.get_state()
        self.services.parser.apply_action_to_state(option, next_state, False)
        return next_state != (self.last_different_state if self.previous_state == self.services.perception.get_state() else self.previous_state)

    def remove_return_actions(self, options):
        if self.previous_state:
            return filter(self.is_next_state_same_as_previous, options)
        return options

    def pick_from_many(self, options):
        options = self.remove_return_actions(options)
        return random.choice(options)
