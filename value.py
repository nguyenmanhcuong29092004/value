# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util

from learningAgents import ValueEstimationAgent
import collections
#lặp giá trị cho hàm 
class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp #lưu trữ bài toán 
        self.discount = discount #chiết khấu
        self.iterations = iterations #số lần lặp
        self.values = util.Counter() # các giá trị mặc định ban đầu là 0, Đối tượng này sẽ được sử dụng để lưu trữ các ước tính giá trị cho từng trạng thái
        self.runValueIteration()# lặp giá trị

    def runValueIteration(self):
        for _ in range(self.iterations):
            new_values = util.Counter()  # Tạo một bộ giá trị tạm thời
            for state in self.mdp.getStates():
                if self.mdp.isTerminal(state):
                    continue
                q_values = [self.computeQValueFromValues(state, action)
                            for action in self.mdp.getPossibleActions(state)]
                new_values[state] = max(q_values)
            self.values = new_values  # Cập nhật giá trị cho các trạng thái


    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        stateProbs = self.mdp.getTransitionStatesAndProbs(state, action)
        q_value = 0
        for next_state, prob in stateProbs:
            reward = self.mdp.getReward(state, action, next_state)
            q_value += prob * (reward + self.discount * self.values[next_state])
        return q_value


    def computeActionFromValues(self, state):
        possible_actions = self.mdp.getPossibleActions(state)
        if not possible_actions:
            return None  # Trạng thái kết thúc hoặc không có hành động nào
        q_values = [(self.computeQValueFromValues(state, action), action)
                    for action in possible_actions]
        return max(q_values, key=lambda x: x[0])[1]  # Trả về hành động với giá trị Q lớn nhất


    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)


class PrioritizedSweepingValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta #Ngưỡng dừng (stopping threshold) mặc định là 1e-5, được sử dụng để kiểm tra sự hội tụ của giá trị tối ưu. Khi chênh lệch giữa giá trị tối ưu sau mỗi lần lặp nhỏ hơn theta, quá trình giá trị lặp sẽ kết thúc.
        ValueIterationAgent.__init__(self, mdp, discount, iterations)
 

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        for _ in range(self.iterations):
            # Tạo một danh sách ưu tiên (priority queue) để lưu trữ các trạng thái và độ lỗi giá trị
            priority_queue = util.PriorityQueue()

            # Khởi tạo một từ điển để theo dõi các trạng thái tiền nhiệm (predecessors) cho mỗi trạng thái
            predecessors = {}

            # Khởi tạo giá trị cho tất cả trạng thái ban đầu (ví dụ: 0)
            for state in self.mdp.getStates():
                self.values[state] = 0

            # Duyệt qua mỗi trạng thái để tính độ lỗi giá trị và thêm vào danh sách ưu tiên
            for state in self.mdp.getStates():
                if not self.mdp.isTerminal(state):
                    # Tính độ lỗi giá trị cho trạng thái hiện tại
                    value_error = abs(self.values[state] - self.computeQValueFromValues(state, self.computeActionFromValues(state)))

                    # Thêm trạng thái và độ lỗi giá trị tương ứng vào danh sách ưu tiên
                    priority_queue.update(state, -value_error)  # Sử dụng giá trị độ lỗi âm để ưu tiên trạng thái có độ lỗi lớn hơn

                    # Khởi tạo các trạng thái tiền nhiệm cho mỗi trạng thái
                    predecessors[state] = set()

            # Bắt đầu quá trình giá trị lặp
            while not priority_queue.isEmpty():
                # Lấy trạng thái có độ ưu tiên cao nhất (độ lỗi giá trị lớn nhất)
                current_state = priority_queue.pop()

                if not self.mdp.isTerminal(current_state):
                    # Cập nhật giá trị của trạng thái hiện tại dựa trên hành động tốt nhất
                    best_action = self.computeActionFromValues(current_state)
                    self.values[current_state] = self.computeQValueFromValues(current_state, best_action)

                    # Cập nhật giá trị cho các trạng thái tiền nhiệm
                    for predecessor_state, _, _ in self.mdp.getTransitionStatesAndProbs(current_state, best_action):
                        predecessors[predecessor_state].add(current_state)

                # Cập nhật độ lỗi giá trị cho các trạng thái tiền nhiệm và thêm chúng vào danh sách ưu tiên nếu cần
                for predecessor_state in predecessors[current_state]:
                    value_error = abs(self.values[predecessor_state] - self.computeQValueFromValues(predecessor_state, self.computeActionFromValues(predecessor_state)))
                    if value_error > self.theta:
                        priority_queue.update(predecessor_state, -value_error)
