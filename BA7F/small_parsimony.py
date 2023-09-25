import numpy as np
import math as m 

class Node:
    def __init__(self, label):
        self.label = label
        self.direction = []
        self.reverse_direction = []
        self.tag = None
        self.penalty_vector = []
        self.count = None
        self.leaf_verify = 0
        self.sequence = []
        self.reverse_vector = []
        self.edge_to_parent= 0
        self.penalty_general= [] 

    def add_child(self, child):
        self.direction.append(child)

    def add_reverse(self, in_parent):
        self.reverse_direction.append(in_parent)

    def add_string(self, string):
        for char in string:
            self.sequence.append(char)
      
def tree_relations(text):
    relations = text.strip().split('\n')
    node_dict = {}
    label_count = 0

    for relation in relations:
        parent, child = relation.split("->")

        if parent not in node_dict:
            node_dict[parent] = Node(parent)

        if child.isnumeric():
            node_dict[parent].add_child(child)
            node_dict[child].add_reverse(parent)
        else:
            new_node_label = str(label_count)  
            node_dict[new_node_label] = Node(new_node_label)
            node_dict[new_node_label].add_string(child)
            node_dict[parent].add_child(new_node_label)
            node_dict[new_node_label].add_reverse(parent)
            node_dict[new_node_label].leaf_verify = 1 
            label_count += 1
        
    return node_dict

def initial_score(first_character): 
    leaf_vector = np.inf * np.array([1, 1, 1, 1])
    if first_character == 'A': 
        leaf_vector[0] = 0 
    elif first_character == 'C':
        leaf_vector[1] = 0 
    elif first_character == 'G': 
        leaf_vector[2] = 0
    elif first_character == 'T': 
        leaf_vector[3] = 0 
    return leaf_vector

def score_vector(left, right, penalty_matrix):
    score_left = np.tile(left, (4, 1)) + penalty_matrix
    score_right = np.tile(right, (4, 1)) + penalty_matrix
    min_score_left = np.min(score_left, axis=1)
    min_score_right = np.min(score_right, axis=1) 
    sum_scores = min_score_left + min_score_right
    return sum_scores, score_left, score_right

def assign_letter(vector):
    min_positions = list(np.where(vector == vector.min())[0])

    if min_positions[0] == 0:
        return 'A' 
    elif min_positions[0] == 1:
        return 'C'
    elif min_positions[0] == 2:
        return 'G'
    elif min_positions[0] == 3:
        return 'T'
    
def get_small_par_row(sequence_parent): 
    last_string = sequence_parent[-1]
    if last_string == 'A':
        return 0
    elif last_string  == 'C': 
        return 1
    elif last_string == 'G': 
        return 2
    elif last_string == 'T':
        return 3

def HammingDistance(text1, text2):
    if len(text1) != len(text2): 
        print('Error. String should have the same length')
    n=len(text1)
    count=0
    for i in range(0,n): 
        l1=text1[i]
        l2=text2[i]
        if l1 != l2: 
            count += 1 
    return count

def small_parsimony(node_dict, n_leaves): 
    h_tree= m.log(n_leaves) / m.log(2) + 1 
    total_nodes = int(2**(h_tree) - 1) 
    total_string = len(node_dict['0'].sequence)
    penalty_matrix = np.array([[0, 1, 1, 1],
                               [1, 0, 1, 1],
                               [1, 1, 0, 1],
                               [1, 1, 1, 0]])
    for i in range(0, total_string): # sequence position

        for ii in range(0, n_leaves): 
            str_label = str(ii)
            leave_character = node_dict[str_label].sequence[i]
            node_dict[str_label].penalty_vector = initial_score(leave_character)

        for iii in range(n_leaves, total_nodes): 
            str_label_2 = str(iii)
            children = node_dict[str_label_2].direction 
            node_dict[str_label_2].penalty_vector,  node_dict[str(children[0])].penalty_general, node_dict[str(children[1])].penalty_general = score_vector(
                node_dict[str(children[0])].penalty_vector,
                node_dict[str(children[1])].penalty_vector,
                penalty_matrix)

        # Backtrack 
        node_dict[str(total_nodes-1)].reverse_vector = node_dict[str(total_nodes - 1)].penalty_vector
        label_root=assign_letter(node_dict[str(total_nodes-1)].reverse_vector)
        node_dict[str(total_nodes-1)].add_string(label_root)

        for node_back in range(total_nodes-1, int(n_leaves + n_leaves/2)-1, -1):
            row_in_p_matrix = get_small_par_row(node_dict[str(node_back)].sequence)
            children = node_dict[str(node_back)].direction
            left_label = assign_letter(node_dict[children[0]].penalty_general[row_in_p_matrix, :])
            rigth_label= assign_letter(node_dict[children[1]].penalty_general[row_in_p_matrix, :])
            node_dict[children[0]].add_string(left_label)
            node_dict[children[1]].add_string(rigth_label)
# Start hamming distance 
    total_distance=0 
    for node_number in range(0, total_nodes-1): 
        parent_label = node_dict[str(node_number)].reverse_direction[0]
        distance= HammingDistance(node_dict[str(node_number)].sequence, node_dict[parent_label].sequence)
        node_dict[str(node_number)].edge_to_parent = distance
        total_distance += distance
    return total_distance

def print_node_info(node_dict):
    for node_label, node in node_dict.items():
        children = node.direction
        parent_label = node.reverse_direction[0] if node.reverse_direction else None

        if children:
            child1_label, child2_label = children
            child1_node = node_dict[child1_label]
            child2_node = node_dict[child2_label]
            child1_sequence = "".join(child1_node.sequence)
            child2_sequence = "".join(child2_node.sequence)
            node_sequence = "".join(node.sequence)
            print(f"{child1_sequence}->{node_sequence}:{child1_node.edge_to_parent}")
            print(f"{child2_sequence}->{node_sequence}:{child2_node.edge_to_parent}")

        if parent_label:
            parent_node = node_dict[parent_label]
            parent_sequence = "".join(parent_node.sequence)
            node_sequence = "".join(node.sequence)
            print(f"{parent_sequence}->{node_sequence}:{node.edge_to_parent}")

# Main function
if __name__ == '__main__':
    tree = """
128->CGCCTGAACTATGAATAGACCTGGGACAATGAGTCAGAGGAAATCTATCATTGAGAGATCCCGCGTCGCCTCTGTCCCGAAGGGCCCCAGCTTACAGCCCGTGATGAGGAAGTAGTCACTTGTTAGCATGATCTTGTCGAGTTACTAGCAAGGCTATCCTC
128->CCATCTCGTTCTGCCTACCGTCCCCTATAGTGAGGCCCGGGCTCCAGGCCGGACCCATGATGCGCGCTCGACAATACAACGCCTATCACGAACAGTAGACCTTAAAGCTTTAGTGAGTGTTCGCGGTGGGTTAAGGAAGGATTTTGCGCTAGATGGAGCTT
129->GGCCCGCTTATCCGTAACGGATCAAAGGATTCCCTATGATACCTCAGAGACTCACGTGATTGGAAAGTATTCCCAGCTTTGGTTTTTTGCCCTGATTGATAAGGCACCAGCTGTAGGCCAGATTCACACCGCCAAAAACGTTTTACTGCCGTACAAATTGA
129->GTACATGCGCCACCTTGCGCACGCAATGAGTTACAGAGGCATCCGGCTGAGCTCTTACTTTCGGGTTGACAAACGAGAATGCAACGCAGCCAGTGCCGAAATTGCCCAGCCTCGTCATAAGCGGATTAAGAGAGAGTCCTCGTAGGTGGGAGACGGGCGTG
130->GATGGATGGCGAAACGGTTGTGCTCTCTGTAACTACCGCGTCTCAATCCTAATCCAAGGATCACCGTCGTGAGGCTCTTACGTCCAAGTCCAGCGACCCTTTATTAACCCTCGGCAGCCTGAAAACGTCGCGCGTTTGGCCGTCCGGAAGATGAACCGATC
130->GGCCATTTTAATATTGGCTCGGCCCTGGGTGCCCCTCAGCTAACCGTTTTCGACCGTCAAGGTGGGCCCGGCCACGGGAATGGAGCAGGGGTGTGCGGCTTGCCTAATCAGTACATGGGGTTACTAACCGGTTATGGGTACTCTGAAATACTTAGTGGACG
131->GGTGGACTTTTACGCGTCGGGTAGGCGGCATAATGCTGGAATGCTTGAGGGCAACCGTGACGGGGAGTAACGAATACCTCAACAGACCTGAACGTCCATGCATCGAGCTACTGGAAGAGAACTACGGCGACTCCCAAGGCCACGTCACAGTACGGCCATCT
131->TCGTAACTCACAGCCTAGATACACGACTCTCCCATAAAAGTGGGGCAGGATCCTTAATCATCGTATCCGCGAGCTGATCTACCACGTCTCATGAGGCTAGAGCACTAAAGGATAGATAGGTTTCTTGTCCTGAAGGTATTCAAGACCATCGCTTAACAAAA
132->GCCCCGATTTAGGATGGGCCGTGTCTTGTTAAGATAACTATTATGATGTACAAATTATGCCCACCTATCCAGGGGCCCTAGAAATAGTCGTCTGGCATACATCCCAATGTGCGCACGCATTCAAACCGCTGCTGCCCCATGGGACATTGAAACTTTGACGC
132->TCCTGTAGCATTGTGTTGTACTACTATTGTGGGCCCAGCTGACCTGGGCGGAGATGGCGGGGATGACCCAGACCATCCAGCGGGTCTCGGAATAAATATCCGATATGGAAGACAGATTTATATCTCCATATGGATTAATCGCCGTAAAATCTGCACCCTTA
133->AGCTTTTACCGTTTTTCGTGATATCATGCCAGACTGACAGCCAATCTCGCCAGGTGGACGGTGATATAGCCGTGTGTCTGAGACCTGGTTAGAACGCATCATCACCGCAACCCATCCAATACAAAGGACCACGAGCTGTAATAGGTCAACGTTAATCACCG
133->TTGAACAGCGGTCAGACCGATTTTATACGGTTTGGAGAGACATTTCGTTTTAGATACGACGGCCTAGGGGCGCATTCATACCTTATCAAAGCCTGCGAGATATAGGATAAGGCAATCACCCGGTACTAGTGTCGCGGAGTCCGCGGTGTCAACACAAATTA
134->CTTTACAGTAGTGCGAAATCATGTCAGATATACGGCTTCACAAGTCTAAGACAGAACAACCGATACGCATTAAAGTGCATGGTAGGTTCTATGTGTCTCATCATGGCACATCAATAAGACATTTTATCACAGAGCTTCGAATAGTGGATTACGATGTCGCG
134->GCCATTCCAAAGGGGACGCTCAAGCGGGCTCCGGGCCACGATTCCTTACATTCGCTCTAGAAGGTCTTCGAAAGACCGCACTCATGGGCCCCGAGAACGCAGGGGATAACTCAGCTTAAATCCAGGATGCCTTTATTCAACAGGTAGTGGAACTACAGTTA
135->GTCAACAATTTAGCAGTTAAGCCATGTGCACGCGTGGTTGTGACCGACAACACCAATGGGATCCTTCCGGTCGAACAGCCAGTCGTTCTATTACTCTCGATCCGGGATGGAAATACTGTTTTATAGGAGGACTTCCATCAATCGATATGCCACGGAACTAC
135->ACTGTTCACCGACTTCGAGATCCCGACCTTCGACTTGGAGTGGATGTCCCGCTACTAGTAGTTCTTTCTCCGCATTCATTGGAAGCTCTACAGTTTACGGACACCTTCCCGATGTATTTATGCTATTAATATTTGACTTTGGCTGCGCATGTTGTTATGCA
136->ACCGGATACATCTGTAATTGAGTTACCAGGGTGGTCCAGGCTTGATATTCTCGGTTTTTCGGCTCACTCCCGCCACCTAACCTGCATCCTGAAGTATCCCGACGTGATTCCAATCACCAGCTTACGATGAAGTGGGTATAATACTGCCGTGAACCCGTCGA
136->AACAAGTTGCAAGATCGATATGGCGCGGTTCTAGTCCAAAAGCGACTATTAGGAAGACTCTTTAGGTCGCGCCTTAGCCTCGCGCGCTTGTCCGCACGTGAACTATAATTGGGGGTGGGGCTCATATATGTGAGCTCTCTGGCTCTATATTAGCGGTGATC
137->GCTTTCGTTCTGATGGGGATTTAGTATCGAGGTGGGCACTCTGCAACACATCGACAGAACATGCGACACCAGCCACCTTAACGAACATCTTAGGCCCGTAGGCCGACGGCGACCTTGTCTTTCCGATAGGCGAGCGCAAGAACCCGGACAGCCTATTACTT
137->GTTATTCGCCTGAGTCCGGAGGTCGGTTTTTGGAGTTAGTCGCCCCGGCTTTATGTAGTGGAATCCTCCGAGCGTGATGTCCTAGCTATGCCGAGCTTAACCAAGTAGGGGACTAATGGTAAGAAAAAAGCATGCGTAACCCCCTAGCCCTAAGAAACTGG
138->GCGTTGAGGCAGTGGGAGGCTACAGCGATAGTTGAAGCATTGATGATGAGTGGAGGCTGTTGTCCCTGTATCCTGCACGCGCAGACCTCTCTTCCTGGACTCACCTCGCTACCTAGCGAAACATGTAAGGCAAAGACCATTTAGCTCACTAGTAGCGAGGA
138->CGAAAAAGTCGGCAGAAAAGAGAGCTCAGTCCGGGTATTCAGAGCTGCCGGGGCACTGGCGGTATAATAATTAGACTGTTATACTCTTTAAGGTCACCCAGTTGTGGAATAGACTATTTGTAACAAAGAGACTATCCGATCTCAGCACCACCTTCGCTGCA
139->CACTGATATGATTAGATGTTGATTACAGTAGGAGGACGTACCAACTCGACTACAACGCGATCGCCTCTCCCACACACATCCGCTTTGGTGCTTTGCTGCCGGAGGTGGAACTTCGCGATAGACCTTTTTCTTCGTCCTCGCCAAACTCATCTAACGTGAAA
139->TTGAGGGATCCCAACATGTCTCTGCTCAGGATACGAAGGCGGCAATCTTGCGAGCAGGTCAGCGCGGCGTGTGCCTATTTAGCTCGATAGAAACGCAGTTCTTAGATTAGAGCTGCGATCAGCGCCGTGCCTTGTCCATGGAAGTAATCGGTCCAAATACG
140->GATGGTGACACAGCGCCTTTACCCAAGACTTGGAATTGACACGCTTGATGTTTTAGAGCGAACTATGTTGGTACCCACGGCGCGGGCGACGCCAGGACACCAGGCCGGTAGGAACACCGGTGTGGAGCTTTAGTAAGTATTCACTACAGATAACAGACCGG
140->CTGGCTAGATAAGCATGATATCGAAAGATGTCGAACTGTTAATATACTCCGTCGTTAAAGACTCCACGCAGAGATTGTGGGCGAGAGCGTTCAGACGAGGCGACTGCTCTCAGGCATTCCGTTGATTTGCTCTTTGGAGTCAGGTGTAGCGATCTCGTTAT
141->TCATGGAGGGTGGACCGCACTCAATATTTGCTCCCGTACGCCTGTACTATTGTAGCTCCTGTGGGTAGGGCAGCCGTTCACACGCTTCGGACTGGTCGGCCAGAAGGTCGTGGAATATACGCGCTGTCCTAAGTGGGCCGTGTAGGATTGAGGTACCTTGG
141->AAGCGGTGAAGCCTTCTAACGCGCAGATACCCACTGAATACACGAACTGACAACCTGAGTAGCGGGATTAGTGTCTCATGTGACAGCGAATTCAGACGACGGAACTCTCGAGGGGATGCTGCCCGCATGATTCGCTACACGCCAATTAACCCGGGCGACGT
142->ACTAGCCCTCACCTGAACTATTTCTACTCGCCAGAGGGGTACGTCCACATGATCTGCGAGACTGGGAGGCGACCCATAACGGGGTTTAATGAATGCACAGCATGCGTGTGATAGGTCATGCATGAGTGGCATCCCGGGCTTGCATTCTTTAACTTCTGTTT
142->CTACGTGTCAACTAAAGCCACCATAGGGGGAGCTACAGTAAGGAGAACACCTTTCTAGACTGTTATGCCCGCGCACGTGAGCTGACAGCTCGCGGCGACGGTGATTTCCGAACAACTGGTCGTATGTACTGACCCCATCCGTTACTAGGGGGATCTTGATG
143->CCACTACCTGAATGCCATGAACTTGACAACACTATCCTACTCCACGGAATCGAGATGTACTACGCTAAATATACAGTGACGCCCCTATCGGCAGTGTGTGAACATACATACTCATCTGCAGTAGGCGATCGCAACCCAGCTGTCCCATCGAGGTTGATCAG
143->CACTAACAACAGGTGTCTCATGGCAGTCAGAGGCAGAGTTTGAATGTCACCGGAGTGAGTACCTTACAGATAGTCGCGCGTGCCAGGGAACATAATTGGAACATTGTTCGTAGCCGTGGCGTCTCACCGTGATCGACAGCTAAATTACTGGATGCATTGTG
144->CTAGTCACACTAGGGTTCTTATTCAATGTAAGCACGGTTGGAAGTGCGTCTCCACGCATCCGTGCGACGCACAAATGGTGATGGGCGAGGAGGTACACACATCGGTCTCCCAACTGGCCCACCTACCCTCGTCGGTATGATGATATAGAACTCGTGTTTAG
144->CTGGTTAACCACGTTCAAGGAAGACGGGGGTAACGAAGTACCAGTGATTCAACCTATGGTATTGCGTCCAGCGCACGGTCTGGCTAGAAACACAGTCTTTCGCGCGGCATTCGTCCGCCTGTCGGGGATGTAACTATAGTTTCTTAGTCCTGGTGTACCGC
145->GGTCTTGTACTAGAAGTCGGGGGCCTGCCTTTACGTTTGCCAGTTTCAACCCCCCCGTTTTAACCAGAACTCACGAGTCTGAAGTGTGAGCGTAGTCTAATATATGGCCTGGTGTTGAATCTACGTATTCTGACAGTGAAGCGTGGGTATTTGATCGGAGC
145->ATCAAGGCACGTATTTTTCACGGCTCATGGATACCGATGAGAGTCCCCTCATGCATGTTCCAGGTTCCGAAGGACTGGCCAGGTCTTCGCGAAGAAGTTCGTTCGCGCCGACACCGACATGACCAATTACCAAGTCGCTACGCAACAGGTCCTCGTGTACT
146->CTCGATCTGGTTGAAGTAGCTATCCGGGCGTGCTTTTCCCTCGTTCCACTACGCGAGGGTCTTCCGTCGGGGCCGTGTGCAGTCATGACGCTTTCCCGCGTTGCCCGCCACGCTCGAGTACCTCAGAGAGTGTTCCGTTAAATTTTACATCGACGAGACCA
146->GGGCAGAGATAGGAACGAAAGAAACTATCACCGGTGGCCCTAGCATTGTGGACGGCCCGTATGTACGTCGAAATTTATAAAAAGACCAAGGGCTTCATGGAGGTGCATATGAAAAGCGCATGGCCAAGGCATATGTGCATGCTACACTAGCGTCACAGCTG
147->TTAGTTCCGCACGTGTGTCCCGAACCGCCTAGTAGGTGTGGGTTACACTTCAATACAACTGAGACTACTGTGTGATCCCAATAAGCGACTATGCCTTTGGGCTTCAGACGGAGATTTCAATGCCAGGCACACCTCATGTACCCGTCGGTTCCGTGCAGTAG
147->GGCAGCCCCTTGAGCGAGCGAGTGGGATAGCGAAAATTTGACATGCTGGAGAACCATTTGATCTCTTTGGAGCTCCTGCATATTCATACGATTAACATATGACTTCGATACGTGTCAGGCACGTCCCTTCGCCCAGGTTTAAGATCGGCACGCACGCCCCG
148->CATTTACGCGGTCTCCGGAAATGAGGGCCTAGACGCTTTTCTTACTGTAAAGGTACGCCCAATTCCAAGATTCTGACGGCGGATTGTCCCAACCGTCGTAATGTTGTCACCCTCCGCGTGATTCCGACCCTCTGGGCAAGAAATCGAGTACAGGTAATTTG
148->ATACGTTGAGTCGTTGTAGAACTAATTTTTGGCCATGAGATACGTATAAACATTCACATGCGAATACATTTTTGGAGACCAGACCTGAGGCCACATTTGCGGCAATCCGTCGGGTACCTACGTAGGGGTTACAAGTGTGCTTTGTCGCGCGTTGAATACGT
149->CAAAGACAGTCGTCCGGTGATGTGTGGGCCTCGCTCCACACCTGGATTGATTGTAGCCCTATGGAAAAATTGACATTCGGGCAGCTCATAGACCGGACTTAATTAGGCGCCCGAAGTCAGCAAAAACCGTGATACTAGATTGGGTCTGCAGGACGACCTCA
149->GGTGGTGACGTACGCTGGGCGCAAGCTGTATGCAAAGGTTCGAATTGATGAGCTCGTGGTGTACCTTGGCCATTCGCCCCACACCTGGATACCTGGTCTGAAGCTGAGTCTGACGTAGAATTGGACCATGACTCGACGACAAACGAATTCCTTAGGCATTG
150->CTGGACAGACACAATCGCGATCAAGGTGCGGTAACCGCCACCGGCGGACGCTATTTCTGATCCACCGTTGCGGTGCGCTGACAGCGCGCGTCTCCTGGCGAGGGCGGAGCGTTATCAGTTAACGATTCGCTGAAACTGGAGGGAACTTTACTTAATAGCAC
150->TCCCCCAAAAGAAACCGGTAATACCGCTAAATGACTCACGGGAACATAGTCAATTAGACTCCCATGGGCTAGTAGCCGCGCCGAAAACTAGTCCGCCCAGGACCACAGGTACGGAGTGTGTTATGCCACAGAAAGCGTTCCAGTCGGTTAAGTGATAGGCA
151->GTATACGTTGTAGTTAGCCAGAGCAACATACGTATCCCATCCTTCCGCTTAGAGCTATCTCTGTATCGCTCCGCTAAACAATCTAGCAGACATCGTTAGGGCATTCCCTTTCAGTGATCGGGTCAACCTTTAGTCACGTCCGATACATTGAGTCGACCAGG
151->CAGACACCTTCATTATGATTATGGCCAAGAGTGACCGAGGCCTGGCCAATCTTAACGGAGACCGTGAACGGTTATGCGGTCAGCCGACGTTGCGATGTTTTTAACATATATGTGGATGTAATATCTCTTCAGTACCGGCACCTCCGTCCGCAAACCAGTGT
152->GTTTGTAGCTCCTTCAAGCCCCAGGACGCCGGGCTGGAAACCCAGGGAGGGTCTGATAATACTCCAGTTAAAAAATGCGTTCGACATAAGTAAGCGCGCAGCGACAGCTTTCCTTAACACGGTGAGAGCTACTAGAACATGCAGAACGTAAAGAGTTTTAG
152->TAGAAGCAGACCTCCACGCCAGATCGGTTTCTACAGTTTTCTAACTTCAGTAATCACTAGGTCCTGTCCTTCAAGTGAGGTCTTGTCACGCTACGGTCATAAGCCTCCATCACTGTTCTGACTCATACCCGAAAATAGACTAGTCATCCCCGTCCGGCGTG
153->GTCTCAACGCATTCCCAATGCCTCTCGCCACCCGAGGCTAGTGTACGGTTAGTCACCGTTTGGCTCTGTGTAAGCGCTAATCCTGCAGGCAGGGTTACATGTGTTGTAGGACACCTGATAGTAGTGCCTTCTCGTCTAGCGTACTGATATATAACCGCCGA
153->ACAGCAAGCTTCCCGAAGACAACAAAAGGGCCTCATTGGCCCGCGTCGGGCCGTGCGGGCTTTCGAAAACTCAGAACCCTACCATGGAATCTGGGAGAACCTATTATCAGGCTGTTGGAACAAATCGTCAAACACATCTTTCACGCTGGAACGGAGTCGTA
154->GGCCAAGTATTGGTTTTGCTCGGCCGACAAGTCGTAGACCAATTGACAGTCCTCATTGATTATTTGTGTCAATTGGATTCTGTAAGACAAGACGCTCGGTAGCGACTTATCCAAAGTGTCCTCAATATTGCAAGGGAGCGTCTGAATTTCACCTCATAGGC
154->GTCTACACCGATTCGGATGCCGTAGGCCAGTCCACTTTACATAGAGCTGGGTTTACTTAGCGCCCAGAGAATCTCCGCAGCCCACGCGGGCCCTGGTGCATCTGGTTGCTTATGCATTGTTCAAAGTCCGATTCACCATCACAAAGGTCAATAACAGTGAC
155->CTTCGCTCTACATTGAACCGGATTTGGACCCACTCAGGCGCCTTCGTGGAGATCGATCGCAGGGGGGGATCTAAGACAGTGAGTACCCAGGAGCCGACCAAGGGTACCTGGGAAGCGTATTGCCGGTCCCTCGGTTACTTGCGATACCTCGTTGTAGATTG
155->CTCTAGCGGAGATTTTTCAAGCTCATGAAGTCGTTACACGAGGACGTTTCGCTGGATTTAGTTGCTTAGGTCACTCCCTCCAATCCTGATCGAGTTAGAAGGAGGACACGAAGGGTAGGTTTTGCTGGGCCCTACAACCCGTTGGTTGCCCAGGAAATTGC
156->GCCGTATGTTCAGAACCCCGGCCGTACTAATACGCGTCAGCTGGTGTACGGACCCGTGGAGTCCTACGGTTGTAGTTCGGAGGGTGCTAGGTAAAAAGGCGAACCAGTGAAAGTTGCACATACGATCGGATTAAATCCGGCGTGAAGAAATAATAAAAGGA
156->AACTCGGCAGCGTAAGTGGGAGGAAAGTGGCTGCCCGTGTCATACAGGGTAGCCCGACGGCCGCATACAATTAGCAGTCTAGTGTACAGATGATGGTATTCACAGTTCCTGCTACACCCAATATGAGACTGGCTGCAGTACGGGGCAGCTAGCATGTGTGA
157->ATTTAGTCTGTCACTCAAAAGATGGAAGTCGTGGTCGGTACGAGGGGACGTCTACGCGCAGAGGCACACCCCACGAAGTCGTGTAAGGTGAGTCGCCGAGTTAGCGCACTGAGCAGTACCAGCGTGGTGCGGCCCCGGAGGCAGTCGGGTGCGCTAACCTG
157->GAAAGTGAGGCCGCGATGTGAGTCCGGAGGAAGGACTCTGGAATGCTATCGTGCTCTGTCCGTTTGATCGTGCTGCTGAGATCCACCAGTATAAGGCCATCAACGAGCTTCGTACCATTTTTGGCGGGAGGACAGCCTCTTTTTAACACAAATACCTGTTG
158->GGGCAGAGCACCCCTTCATCAAGAAGAGTTGGGGGGTTTTATTAATGAAAGCACGCACACAGTAGCCTGCTCAATGATGGGTCGCCGGTCTGTGTAGACGCAACCACGTAGGGGCCAAACCCGCTTATCTAGGCCTGTTGTTTCTTGGGAACGAGTGTAAT
158->ATAGTTTGGAGGGAGGTCTCAGAGTATCCCTAACTGCTCAAGTCGCCCTCCCACGATGGTAGCTTTGACGCAGTGACAAGTCAGCTATCCACAAGATTACTTCTTTTCGCAGCATACTTCATAATAGGGGGATGTTTCCATTCTCGAGGCTAATGATTCTA
159->GTGACGAGCCCCTGCCATACGTATGCCGGCCAATTGATCACACGGTTCTTATAACACAAGGGATGCGTCAGCTGTGTTTAAGAGTCATCTGCGTCATCTAAGGGTCGATAGAAGGTGTATGTAGATCGAGGGGCCAGATGTCAGAGCGACGTTGTCAGAGG
159->GAGAGTTACAGGCAAATCCTCAGACTGTGTCGTTCCATGCGCCTACTTAGCGGGTGCCTACCGCAGGCTTTAACAGGTCAAGAGTTAATAAGAAGGCGCAGCCCGGGCGCAGGTGTTCATACTCCCTTCCGGGAATATTGCAGCTCCGGCCCAAATGATGC
160->CCCTGTCTGCACTGCAAATTGCAATTCGATCGGTGCGAGGGTAATTAGGACAAAGTCTTGCTGCCGGCCGGCAGACGCCATGCACATCTCCTTTCCGAAAAATACAGAACGTGATGGCGTACTATCAACATGCTGCACAACGAATGCTAGGGTGCAAGATC
160->GGCACCTGCATTTAAGGTTCCCTATGAATGGATAAGACGCATAGTTGCATGTATCGCCATTGTACACCGGCCGTTTACTGACCCCATCTATTTGAACACGGCGGGCTCCTGCGGAGTCTACGGACGCGCGGGCCCGACGAGCCGTCATATAATTTGGGCCA
161->GCGCCAAGCCAAGCCTGGGAGCTCACGGTAATGGGCTCAGCGCACCTAACTGCTAGGCGGCGCACGAATGTTAATCGGGAGGCCAGTTGACGATGTAGTGCCATGTGTCTCCAAGGGACGATATCTATCCTACTGTCGGTAACTGCATACGAGGACAGGCC
161->CCCTGATATCTACGTTTACTTTGGTGGCAAGGCTTTTACTCTCCTATGGAATATTTGATATTTCGTCTTAGAGACTTGTCGGGCTTCAGTTGCGCTTTAATCGGCGGCAATTTCTATTCTGGGATTGGTACCGGATATGAATAATATCGCTCAGAGTCACA
162->CACAATCAGAAGTAATCTTGAGACAGTTCGGTGCTCCCTTAGCAGAGTCTTTTCCGGACCTTTACCCACTATAAATCCATCTGCCGGCTAGATTCTAGATGCCGAACCGCAGCCGAGCGAAGATATTAGTAACGTACTGGGTTGAGAATATTGCGGCACCG
162->AGAACCACCTTACGATTGCTGATTGCTGACCGACCTCGGTTCCAACTTAAATGTAGGAGACTGTCCCCCTTAAGCGTAGCAGGTGAAGAGATAAGTAGAGAAACGTGTTGGATTACTTGTGGTAAAACATAGGATAGCCCATTTCATTGGGTTCAGATTAA
163->CCACCTTTCGCTAGTAGTATGCAAATCTGGAGGCACACAACTGTTGTAGCGAACTGTATAACTGACAGACCTTTCCTGCCACACGAAGTTATTACATCCAGAAACACCGGGGCTCAGGCGTCGAGAGACAACAACCCTGCACCCTTGCAGCATAGATTTCG
163->TAGGGGCCTAGGGGGTTATAAGCCTCGACGAGGGCGGTGAAGAATGGAACCATAGTGCCCAGAGGCCCGAGAAAACTAACAAATAGTCCAGTGGTGGACACTCCCAAATGGGATACGGCCCGCCGTAGTAGATTAAGGGATCGACGCAAATCGCGCGATTA
164->AACCCCGATAAATCAAGTCACGAGTGCCAACCGTAGGCCCCACGGCCCGAGGTGCGCATAAACATTAAAAGTCACGCCGCTGCTTGGGCTCAGCGTGAGGTCCCGTAAACGTACACCTGATCGCACTAGTTGCTAGGTATACCTATTGATACCCAAAGCAC
164->TCGAGCTTACTGTTCCTCTACTATCCGCCAGTGCCCTGGGAACCTCCGGTCGCATGTTGGATACGAGTATGGCTACCTATTTGCAATACTTCGACGTTTCCTCATGCTCATGACCCGTCTTTAAGGCTAACGCTTTCGTTAGCGAGAAGCCGAAGAATTAC
165->ATCGATCAATTAACCTGATCTACCGCTCCATGATGACACATGTCAAGTACTCGGAGGCATGGTTTCTGGAGGCTGAGGGAGGCCGGTCGAGAGGTTTTTACGCGACACTCACTGGTATGGCTGCGTTCAGCAACACGTAGGGCGGCAGGCTCCTTGAAACT
165->GCCCGCAATGTACCTCACCGCAACAGATATCGTTGTTTGAAGCGTGCTCCCTGCAAGGAGGCTCTCTAGTCTACCAAACGAGCCCCAAGTCCGAGAGCGTCTCGAGAGCGATGTTGACTAATTACCTGTTAGCGCCTGTTGGTATAAAGCCTCGTACTGCC
166->TACCGGGTGCCGCGCGCTACTGCTGAATATAAAACATGGACCCTGTGTCTCTCGGTGAGCTCTGCTGCATTTGGATGTGCATTTACAGGCTGTAACCGGAGAAGTCATACGTCTGTGAAGGAAGCCAGGTGGTCGCAGCCAATTCAAACGTATACATGGGT
166->CTAATAAGGGGGTTCCTTAACGTGCTGCTCCGGGCCCTGCATATAGGAGTGGGGGAGGGATGTACTTCGTAGATCATGATCCGCGCTGGGGTCACAGACATCCTTCATTGAAATCTCCAATTTACTTGGTCAAAAATATACACGATAGAATTCGGCAAATG
167->TTCATGTTACGGCTAGCCCGCAATGCAGTAGTGTAGGCATTTCGGCTATAGCGCCGGCTGGCTGCAAAGGTGCTGCATGGGCCGGAAGTTTGTTGACAAGCAGCTTTTAAAAGCGAGCAATCGGGTTCGAAGACTCCCCTCGGATCTCTAGACTCTCACCC
167->GATGTGTCCCAGGATATTTGACCTGGCAAGCAGATATTATACATATCTCAACTCTGCGATCGTCGAAATGCACCCGGACAAGCTCCAACCCGGGCTTCCACCAATACCTGGCTCCTTCCTTTCCGGTAGCACATTCAGTGATAGTGAATCCCGCTGAAGTC
168->ATATACACTTCTGCTGTATTAAGCGTGGGCGATCCATGGGCGGACGTGCTCTCTCGGATAATGCGCAGGGCACTCGCTAGCGACTAACAGGTGGGTCCCGAGTTGTTACCTACCCAGCAGCATTTTCGACGAGTGGCGGCTGCAGGGATATGGCAATTAAG
168->GTGTAGGAACTGGAAGCAAAGAGGATACACGTGACTTATTGGGTTACGTAAACACCAAAACGCGGAAAGCTACTGAATAGGTTTCGCATAGTCTTATACTAGCTACGCGCTAGGGAGAGTACTCCGTGGGGCCAATCCAACGTTGCCTGGACTTACTTAAG
169->TTATTAAATCACGCTTTGCGGTTCTAGACACCGAATCGGTCCGCACTCAGGGGTGGAGACGGGTCGCCGCTGCTAGGGCTGGCGGATAACCGGAATCGAAAATTTATTCTGGAACCCCCGTCGTAGTCGCGCCATGGAGATCTGCCGATATCTCGCGAGTC
169->TTATCTCTGGAGATAGTATCGCTCGGTTATTGGGGCCGTTTCTCATGTTCTGTAAGCTCACACATGTGACGTTGGTAGCTCGCGCAAGCCGGCACGCGAGATGACGGGTTCACGGCTCTCTTGTATCTACAACGATCATCCCCGCTGGCGCTCATCCGCGA
170->CCTTCACAGTAATTGCGGGTACACCCGTCCCCCCGCAGGCGTAGGTATTGTGTGCCCCGAGTGGTCGAGTGACAAGCGTAACCCGCTGAATGAGAGTAACACTTCTCTGTTCCAGGCGTGACCCCACAGGTTGGGGAGGGTTATATTGACCGTCACGAAAC
170->GATGGTAAATTCATGGGAACGTAAGCCTGCGGGATCCCCACGAGTTGGCAAAGCCAACGTGGCTTATGGATGGAGTCCCGGCGTCTGTCGGGTCCCCGAGGTTGAGAGCGTACAACCGATGAAGGGGATAACTTATTTAGATTTCCACAGAAGAATTCTTG
171->CATTGGGCGCCTATACTATGTGCCGTCGTGTGCCTTCTACTACTGGCCCACGAAAGGTTTGACCGGATTCGTGTCGTGTAACGTCTCTCAGTCAACCCGATACAAGGGATCCATGACCTTGATTTTTTTTGGTTCTACATTGGCGGGACCCGACACTTTGC
171->CAGAGAGAAGTGTATTCTTTGGAACGCGTGGCTTCAGTACGCCGTTGCAGTGAGCAGCAACACTGCCGGGCATTCTTATGGGTGGTTGTCTAGTCGTCCAAGTTGGTACAAATCGTTTTTTAAGCGTAACTCGGATCTAGGCTCGCGAGAGGCGGACCCAT
172->CCGGATACGTCCTGACCAGAAACTAACTGTCATACGTGTCGGCCAGATGCACCACACGAGGCGAGCCACCGGCTTGACTGCTCATAGCGGTCACTTACAAGACCGTTAGGTTCGGGCCTCAACCGATTGCCCGGTCTCTTATATCTACGTCAAGATTTCTC
172->ATACAGGGCTCCGTGGTACAGATTCCCCTAGGCCCAAACGGACATGCCTATGCAAGAGGGTCTGCACAACAGGTCACAGGCTTTCAACCGTACCACGTAGTATCTTGTTTGTCTAGGTGCTTGGTATAACTACATTGCAACGTCCCCATTGTCGAATAGTT
173->TGCTCCCGGTTTGCACGTACCCTTGAGACATCTGGAAATTAGAACCCTCCGTAACCACGGAGTATGAATTCCTTCTGCCTCCACGCGTATCACCATCGTTCAGCGCAACCTGTCGAGAAACCCGCACGATGACAGAGACGGGAGATATAGCACCGGTTGCC
173->TTACTAATGAGTTCTTACAGAGTTGCCTATCCCGATGGTACTTGAACCAGCTGTTCTCTGCCGACGGCCATTCTGTAGGTTTCATGCACAGTACAAATCGGCGTCCTCGAATCTAACGGATCGTAAATCCGAAACCAGCTGAGACAGTATGTATATCCGCT
174->TTACCCTTTTACCCCGAGTCCATGTTCGGTGTCGATTCCCACAGGTCGTAAGGAACAACCACGAACGTTATCGGACAGATTCATATACTACGGTCTGCGCCCACGGGTGCTGCGTTTATTTACCAGTTTCCCCCCTGTAAGAAATCCGGCATGGAGCATGA
174->CAAAGCGCCACGCAGGGCGAGAACTTGTGGGTACACTCTGTTTTTCGTGAATCACACTAAGTGCTTGTGCTAGACCGAAAGGCAACGCGCTATCGAAAGTATTGTCTAGTCTTTTTCAGGCTTTGCTCGGAAATTTAGCACTCCGGGGGATATCTAATCCA
175->CGACCTACAATCAGTATTAGCATACTAAGTTCTACCTGCGGATGTGTCGGGGCGACACGTGTGATACTACTCGCTCACCTCATGTATGGACACAGCCGGTCAAGGGTGGAATGGTTACGGACCATCAGCTTAGCGCAAGCTACAGGACGAGTTTCGGTGAG
175->ACAAGAGGACACCTAGCATATGGACGATACGGGAGGTCAATCGTATATTAGGGACTAACGTACATACAGAACCGGGTAGCTGCACGTTTCAGCTATGGAACGCTTGTTGTTTGAATTCGGTCCCGAGCAAACCATAAAGGCGTCATCAGCGAGGAAGGTGA
176->ATGCGTAGTTTTCAGATACTGCTGCCAGCAGTTTAGTCGCAGATGTCGGTCCCGGTGTTAACGACCGTCACAATTCGTCGTTTTGTGATGATAACGATGCCTACCATCGCAACTCATTTTTGTCCGCGGTATTTTTTTCAAAAAAGTTTGGATATCGGTAG
176->TACCAGGTCTATTAGCCTCGATCAGTAGTAATGAACTCGTCACTAGGTTCAACTCATTATCTTCGAAGCGAGCTTCTAAGTACAGTAGACCATGTCCCTGGGATCTACGCCAAGACTTGTAACAGGAACTTATACGCTGACAGACAATAGAAAAATGAGTG
177->TATCGTACTGGTACCACAACGTTCTCGTAGACAAAATGACGATGAAAGACTCAGCTTCTTTCGAAATTGGGCGTCGATGTCGTCTATAATGTCCCTCGAATTCTAATCAAAAGATCTTAGTAGCATGTACCCACGAGTTGTAATGTTTCAGATTCCGCCTC
177->CGTAGCTGTCCACTGGCAACGGACCGGCACACATGCGTTGTTACTGGACGTGGGGTGTGGATCCTTGCTTGCTGCACCCAAATGCCGGAAATTGGCCGAGAGTTTCCGGGTTATATCTTTCTAACCCTCTCTGGCATCATCTTATTAAACCCTGCTGGATG
178->ATTTCGCACCCTTTCGATTCAATCCAATTTATCCTCGAGCATTTCACGCCCTCTAGATTGTTGCTTGCCAGAATCGGACGCACATCAATGCAGTAAGGGGTTAACCGGATAGCACGTTGGAAGCTCGGAAGCGAGGTTTTCGTGAAGCAAGCATGTGACCA
178->TATGGTGAACTTTTGGGGACTTGGGCGTCACGCCGTTCACGCAAGTCTATATCAGACGCGTAAAGTCGTCGCATGGCTGCGAGACAATTAGCACTAAATGATTATTACATAGAGTGTAATGATCCAGCCACGCAGAATGAACGCCTGTCTCGTTGGGACTT
179->CTGGAGTGAAGGGGCTCCCCTCTCCCTTCGCCGTCCCAGTGGACAGGTCAAGACTCCGAAACGGGGTTGACTAACCAAAAAAGGATAGCCCAGAATACTTACTGTATAAACGACCTCTATATGCAAGAGACGGTAGCTTCCACTGTGTGAGAACATCTGGA
179->GCAATCAAACATTGGCCACGGAGATATCATATCGTTCGTTGTGTACCGGATCGATGGGATGACTTGAAGGGAATTAGTAAGTCTCTAATGTGGAGCAAATCCATCCCTTGTTGCCTCCGGCCGGACCCGTAATATAGCAGTCCCTAATGGGATGTAATCGA
180->GGTATGGGTTTATATGTAAGTATTAAGGGTTATAAAGACTCAAGGACGTACGCAACTTTGCCTCTTTTATTTGGGAAGTACTAGACAGTACAATTCTAGGAAATTTGGCCGAAATAATCACTCCGCGCACTGCATAATCGCTTAGGACTAGGGTTTACCAC
180->TTACTTCATAGGGGGCCCTGCAACGAGCATTAATGATCCTATTCAAATGGCCTGCATGCTTGAACCACCAGATGTCAACCTTGGGCGCCTTTTGCAGCTAACTATGTATTAGAAACAGAGTTTAGTAGGCAATCAACCTTGCAAGATGGCAAGAACTGCCA
181->TTCGCCGTCTCACGTTTCATTATTCAGGAGGGCGCAAGTCATAGGGCCCTTTTGCATTATGTTGGTCCTACCATGGTGTGCGTGTGAGTTACGGTGTTTTAAACGAAGGTGTACAACACAGGGTACCAGACCGTCTCGCTACCATAGAACATTGAAAAGCG
181->CTCCATTCCGATCCCGGTCCACGCCTACCCAACAGGAGGGCTTTAATTGGCTGTGCCAGTGCACAACTCGACCCAGCCGGCCAGCGAGATTACTTGAGCTTGTTGCGAATACTTCGATAGATTGTTATGCTTGCCTCATAGTACATGAGTAAGTGGTCATC
182->AAGTATCTGATGCTCAAACCAGTGCACCGACTCCCTCTATGGAAACCTCTTATACGTATCTAAAGGGACTGCCGATTCTAATACACCAACCGTGTGATTAAACTGCCAGTCAGTGTAACAATTTCCTGCTTCTCACCTTTGACCGTCTGCAACTGACGATT
182->TCCCAAATGTGTGGACGATTAGGGTGTACTGGACCTAATACATGAGATCACGCAGAGTATCATTAGCGGTGATGTGCTGTCGCTAGCTAGTAAAAAGGCTCATAGTAGCAGTCTGCTTAGAATACATGGTTACGGTGTCTCGCGGTCAAAGAGGTGTGCGA
183->ATGCACGTTTCTGGTATCCTACTTCTATTATAGGACCCTTTCGATCCCGTAAGCTCTTTTGCACTAGAAGCCACTTGGCCTAGAGGGTTACGCCTGTCAAGCGAGCCTTAGAAGGATTAATGTTCACGAAGGGGCGATGAAATCCTGGCTCTTGACGCTAA
183->GCTGCGACACCGAGTTTAGCCTGTAATAGATTGCGTAGGTTGCGGACTGCAAGAGTTAGAAAACAAAAGCACACCTAATCTACCGTTAGTATAGACTTCTGGAAGCGGACCGTCTTAAAGAATAGCCACAGGGACAGTCATCGATCTAACAAGGGGAAGCC
184->CTTCTGTCACGTCTCTATTATCTGCCAGCGCCCCCTGCACCCATGCCAGGCATAAAAAACGGCATAGTCACTCCACCAGTGCCATCAGCGTGCATCTAACGTGAGGATTGTTGGGTCCGGCGTAGGGACGTGCCGAAGGTCTACTAAATCCTTCCTCATAC
184->GCATGAGAGGGTTGTATCCGAAGACGATATTATACATGTTATGATGGCTAAACGCCTGTAGCAAGGACCGTTCAAGAATAGATGGAGACAATCGCATTGGCGTGAGTCACTTCGCTTTGGCGCGAGCGGTTGTAGGTTCTCTGATGAACGAATGGAATGTG
185->GAGTCTTATTTACGCACTGGAGCTCCGTACTTCGCACGCCCTAAAGGCTCTGCTCGCGTACACACCCAAAATTTAATTACCACCCTAGCAGAGAAGGGAAGGTTGTTGCTTTATGCCGAACTGCATTTTCGGTTTCCTTAATTCTCCTACTCTATGGTACG
185->ATCGATGTACGGGTAGCCCTTCGGATGGCCTGTGGGGCGCCAAACCTATAGCGATAAATCATGATCAGGTTCGACGACCCGAACAAAGGGTGATCGCTCCAGGTCACCCCTCCCACCTCTTCTCAATACGCGGCCAACCATTTTATAGACTATATGTCTGA
186->ATGTAAAGGCAATGTACTGCGTTCTAGCCAATAACTGATGAGATTATATCGGCTTAGCGTTACGTTAGCCCGCTCCTCCTCTCCAAATTTGAGTTGGGAGTGTAAACCCAAAGGCAGATCCTTTGTGATGATGAGTGACAGGAGGAGGATCCGTGTGTGCT
186->AACCAGTTTGGGAGCGCCATTTAAGCTAAAGTAAGCGAAGAGTTCCGGACTAAAACGGATCCTTGTGATGCTGGACAATAGAATTCAACAGTGCCTTAATGCGGAAGGAGAAGCACGCACGTGAGAATGTCAATTAATCCAACAAGCGGCATACGCTGCCC
187->AGTTTGTCGCCGACTGAGGGTCACATTCGGACAATCACCCAACGGAGTGAAGCTGGTGGCATGCCATGGATACAACCCCTTTTGGGACCACTGGAAGAAAAGAGGGTTTCCCATTCCTGTTGCATCTGCAAATTGTGAATGGAATGCGTATTGAGTATCGT
187->AGCTAACATATCTTTATCTTCTTTAACAGGTAGTTTACATGTGGGAATTAGTCAAGCTTGTTATTTCTTGATCTCGAGGTTGGACGAGGTCGCTATGCTGCGGCACTATGCATAAATAACGTTCACAGCAATAACGAACCGAGGCGCAAGTTGCGAGGCTT
188->AGGATTGTGAATGTGTTACTGCCATGTGAACCGCTGGTGTGGCACGCATGGCGAAGAACTGGAGGGGAGTATCATATTGTTGCATACGTAATGGGTAATTGACGAAGTCCTGCGTAAGACGCTCGAGGAAGCACTCCTCAATTCACTGAACATAGCCCGGC
188->GCGATAGGAGATTCGCGTAACAGCCTGGTGATGCGATCTACCCTGGTGTGCAGAGTTGCGTCTTGACCTTATCATGCGTCCTTCATGCTTCAGGAGGCACCTATTCGCCCGAACGGTTACATGCTGAAAGTGCATGCCAGGGCCAGGATCCGAATGTAATG
189->TCTACGAAAGCGTAGGAGGGTTCCTCCCTGGACGTGAAACGGATAACCGGTGGGGTACAGCCACCCTATAGGCTGCACACCGTCGGGTGGTCCGGTGCATATGCCGGCGCCGATCCTTCCCAGCGCAGTACGCAGGTAGGGTGGAAGCGCGACCCCTATGA
189->TATCACACAGAATACTTCTGCTACTCGTCAGTGGTCTGGATCGCCTAGTTTTACTGACGCGAGTTTGCTAGTGGACTTTGACGCACCCGTAGGTTTAGGGTGCACATCCTGCTTTCCTCACACTACCCGGAGAATTATAGCAGTCGCGCAATGAAGCATGC
190->ACCAGGAGATACAGTCGTTCAGCTTGGTCGGACAATTCTACATATTGCAATCTAACGGCTTGGTCCATAATGTTATGCAGCAGGGAGGTGTCTGTGAAGTGGTATAACCGCCGACATCGTAAAGCACTGTACAAAACAGTTTTGTTATCGACGTCTCGTGC
190->TTTCTTAAGGCTCCCTGGCGCCTCATCATACGAACCTGTACTAGGGCAGCCGTGCGCCCCGTCCAGCAGTTATTCGGGGGACTGGGCTTGGACAGCTCAATATCGCGCATCAACCTGGGAGCCAAGATTTGTTGCTGGTACATGTGAACCCTGGTAATGGG
191->CGGACTGACCAGCATGCTAAGAAGTAACATTGTCTCATCGTGCCTACGTCCGGTGAAGCAATCGTTGCCGAGCGTGAAAGCATCTTGATTAACGATCTAGATTCATACCATACGAGCTTGAATCGAAATATGAATGGTACTATCACAAAACTCTCCCACTG
191->CCCGGCACATCCTTACTTAAAGGGGGTGACCAGCTTCCGTGACGTGGACGATGGGCGGCAAAGGTATTTAGGTGACGTTACGTAATTGTATCTATGCCGGCCCACTAACATATCAAAGACAAGAAGGCTTCGATTCGCGAGCTCTTTCCCCGAAAGAAAAA
192->172
192->135
193->146
193->183
194->141
194->181
195->158
195->167
196->185
196->191
197->152
197->186
198->178
198->160
199->187
199->169
200->153
200->144
201->140
201->142
202->139
202->131
203->147
203->156
204->137
204->174
205->143
205->170
206->179
206->155
207->157
207->136
208->176
208->159
209->154
209->190
210->150
210->138
211->171
211->145
212->188
212->133
213->189
213->173
214->177
214->149
215->184
215->130
216->132
216->164
217->165
217->163
218->134
218->162
219->128
219->182
220->180
220->161
221->168
221->151
222->148
222->129
223->175
223->166
224->214
224->215
225->192
225->196
226->221
226->201
227->216
227->220
228->217
228->204
229->222
229->193
230->199
230->203
231->200
231->194
232->211
232->205
233->207
233->208
234->197
234->223
235->206
235->213
236->219
236->195
237->210
237->198
238->202
238->212
239->209
239->218
240->227
240->225
241->233
241->230
242->224
242->237
243->231
243->228
244->236
244->239
245->232
245->235
246->238
246->226
247->234
247->229
248->241
248->244
249->246
249->242
250->245
250->247
251->243
251->240
252->249
252->250
253->251
253->248
254->253
254->252
"""



    # Create the dictionary
    node_dict = tree_relations(tree)
    n_leaves = 128  # Number of leaves in the tree
    result = small_parsimony(node_dict, n_leaves)
    print(result)
    print_node_info(node_dict)
   