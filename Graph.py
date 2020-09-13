'''
定义一个城市的拓扑连接无向图结构；
图的数据结构为无向邻接图，通过一个点的ID和点的映射的字典实现；
'''

from TopologyLink import TopologyLink
from TopologyLink import DeputyLink
from TopologyOptimation import get_two_node_distance
from TopologyOptimation import search_topology_dict
import sys
import random


# 定义图结构
class Graph:
    # 图初始化一个点的字典
    def __init__(self):
        # G节点字典
        self.G_node_dict = dict()
        # H节点字典
        self.H_node_dict = dict()
        # J节点字典
        self.J_node_dict = dict()

    # 根据ID找点
    def find_node_by_id(self, node_id):
        if node_id in self.G_node_dict:
            return self.G_node_dict[node_id]
        elif node_id in self.H_node_dict:
            return self.H_node_dict[node_id]
        elif node_id in self.J_node_dict:
            return self.J_node_dict[node_id]


    # 往图中加点
    def insert_node(self, node):
        if node is None or node.NodeID is None:
            return False
        elif node.type == 'G':
            self.G_node_dict[node.NodeID] = node
        elif node.type == 'H':
            self.H_node_dict[node.NodeID] = node
        elif node.type == 'J':
            self.J_node_dict[node.NodeID] = node

    # 往图中加边
    def add_edge(self, node_A, node_B):
        # 先判断两个点不存在则不能加边
        if node_A is None or node_B is None:
            return False
        # 两点存在则加入图
        else:
            # 两个点连接起来,注意是添加的图的字典中的点，保证点的唯一性
            node_A.neighbor_dict[node_B.NodeID] = node_B
            node_B.neighbor_dict[node_A.NodeID] = node_A

    def add_neighbor(self):
        H_node_list = list(self.H_node_dict.values())
        J_node_list = list(self.J_node_dict.values())
        for i in range(0, len(H_node_list)):
            for j in range(i+1, len(H_node_list)):
                if get_two_node_distance(H_node_list[i], H_node_list[j]) < 498 and len(H_node_list[i].neighbor_dict) < 4 and len(H_node_list[j].neighbor_dict) < 3:
                    H_node_list[i].neighbor_dict[H_node_list[j].NodeID] = H_node_list[j]
                    H_node_list[j].neighbor_dict[H_node_list[i].NodeID] = H_node_list[i]
            for j in range(0, len(J_node_list)):
                if get_two_node_distance(H_node_list[i], J_node_list[j]) < 498 and len(H_node_list[i].neighbor_dict) < 4 and len(J_node_list[j].neighbor_dict) < 3:
                    H_node_list[i].neighbor_dict[J_node_list[j].NodeID] = J_node_list[j]
                    J_node_list[j].neighbor_dict[H_node_list[i].NodeID] = H_node_list[i]

        for i in range(0, len(J_node_list)):
            for j in range(i + 1, len(J_node_list)):
                if get_two_node_distance(J_node_list[i], J_node_list[j]) < 498 and len(J_node_list[i].neighbor_dict) < 4 and len(J_node_list[j].neighbor_dict) < 3:
                    J_node_list[i].neighbor_dict[J_node_list[j].NodeID] = J_node_list[j]
                    J_node_list[j].neighbor_dict[J_node_list[i].NodeID] = J_node_list[i]
    # 生成所有的链路，包括一个链路的一条主链路，一条副链路
    def gen_all_topology_link(self, NE_A_dict, NE_edge_dict, day):
        # 先找到所有的对
        couple_list = self.find_couple_list()

        topology_link_dict = dict()
        # 找到所有对的路径,符合条件就是主链路，所以直接生成主链路集合--链路集合，确定所有的链路
        topology_link_id = self.find_topology_link_dict(couple_list, topology_link_dict, 0)

        # 得到一个新的couple，即A与B点对换
        #reversed_couple_list = self.get_reversed_couple_list(couple_list)

        # 再来寻找一次主链路，因为第一步只找了以A点为起点的所有链路，而没有找B点为起点的链路
        # topology_link_id = self.find_topology_link_dict(reversed_couple_list, topology_link_dict, topology_link_id)

        print(len(topology_link_dict))

        # 根据生成的主链路，找到一个主链路下所有的副链路
        self.find_deputy_link(topology_link_dict)

        topology_link_list = list(topology_link_dict.values())
        # 初始化链路的NE
        for topology_link in topology_link_list:
            topology_link.main_link.init_NE_list(NE_A_dict, NE_edge_dict)
            deputy_link_list = topology_link.deputy_link_list
            for deputy_link in deputy_link_list:
                deputy_link.init_NE_list(NE_A_dict, NE_edge_dict)

        # 遍历所有的剩余节点，一遍遍的遍历，直到所有的节点加到下挂点
        self.find_hanging_node(topology_link_dict, NE_edge_dict, day)

        return topology_link_dict

    '''
    这块用于找到所有主链路
    
    !!!!! 放宽条件1：首尾的A值可以不等
    !!!!! 放宽条件2：G-H-G中间节点的A值可以不等
    '''


    # 找到所有的G/H节点对，前提是A值相同,

    def find_couple_list(self):
        couple_list = []

        # 先把字典转列表
        G_node_list = list(self.G_node_dict.values())
        H_node_list = list(self.H_node_dict.values())

        # 找到所有的G的对
        for i in range(0, len(G_node_list)):
            node_A = G_node_list[i]
            for j in range(i+1, len(G_node_list)):
                node_B = G_node_list[j]
                # 两个点A值相同则加入到列表
                couple = Couple(node_A, node_B)
                couple_list.append(couple)

        # 找到所有的H的对
        for i in range(0, len(H_node_list)):
            node_A = H_node_list[i]
            for j in range(i+1, len(H_node_list)):
                node_B = H_node_list[j]
                # 两个点A值相同则加入到列表
                couple = Couple(node_A, node_B)
                couple_list.append(couple)
        # 找到所有的G/H对
        for i in range(0, len(G_node_list)):
            node_A = G_node_list[i]
            for j in range(0, len(H_node_list)):
                node_B = H_node_list[j]
                # 两个点A值相同则加入到列表
                couple = Couple(node_A, node_B)
                couple_list.append(couple)

        for coup in couple_list:
            # print(str(coup.node_A.NodeID)+":"+str(coup.node_A.A))
            # print(str(coup.node_B.NodeID) + ":" + str(coup.node_B.A))
            # print(".............")
            pass
        return couple_list

    # 找到所有点对之间的路径，然后判断是否符合主链路的要求,符合的就生成一个主链路
    def find_topology_link_dict(self, couple_list, topology_link_dict, topology_link_id):
        # 链路字典集合
        for couple in couple_list:
            # 存储所有链路集合
            couple_link_list = []
            # 起始点为A，终点为B
            stack_list = []
            # 找到A点的所有邻居,转为list
            node_A_neighbors = list(couple.node_A.neighbor_dict.values())
            # 处理起始点，起始点设置为已访问，防止回环到起始点
            couple.node_A.isVisited = True
            # print("start dfs head:"+str(couple.node_A.NodeID))
            # 搜索每个邻居能到达的可能链路集合
            # print("node_Anumber:" + str(len(node_A_neighbors)))
            for node_A_neighbor in node_A_neighbors:

                # 将端点的第一个邻居设置为已访问，加入到栈

                # 中间节点不能是G节点
                if node_A_neighbor.type == 'G':
                    continue
                # 判断是否小于首尾节点
                if node_A_neighbor.A > couple.node_A.A or node_A_neighbor.A > couple.node_B.A:
                    continue
                node_A_neighbor.isVisited = True
                stack_list.append(node_A_neighbor)
                # print("main link dfs continue go:" + str(node_A_neighbor.NodeID))
                # DFS递归深搜
                self.dfs_main_link(stack_list, couple_link_list, couple.node_B, node_A_neighbor.A, node_A_neighbor.type, couple.node_A)
            # 恢复未访问状态
            couple.node_A.isVisited = False
            # 将所有找到的主链路进行长度排序，长的在前，保证J点只属于一条链路,所以还需要删除一些短的链路
            self.sort_couple_link_list(couple_link_list)


            # 转为主链路结构
            for couple_link in couple_link_list:
                # 得到一个链路
                # 链路至少有三个点，即两个端点，一个中间节点
                if len(couple_link) == 0:
                    continue

                # 进行主链路的筛选
                if self.check_main_link(couple_link):
                    topology_link = TopologyLink(couple.node_A, couple_link, couple.node_B, topology_link_id)
                    if self.delete_copy_main_link(topology_link, topology_link_dict):
                        topology_link_dict[topology_link_id] = topology_link
                        topology_link_id += 1
                        # print("find1")


        return topology_link_id

    # 对找到的所有主链路排序
    def sort_couple_link_list(self, couple_link_list):
        if len(couple_link_list) == 0 or len(couple_link_list) == 1:
            return
        # 长度排序
        for i in range(0, len(couple_link_list) - 1):
            for j in range(0, len(couple_link_list) - i - 1):
                if len(couple_link_list[j]) < len(couple_link_list[j + 1]):
                    temp = couple_link_list[j]
                    couple_link_list[j] = couple_link_list[j + 1]
                    couple_link_list[j + 1] = temp



    # 对换couple中的AB点
    def get_reversed_couple_list(self, couple_list):
        copy_couple_list = couple_list[:]
        for couple in copy_couple_list:
            temp = couple.node_A
            couple.node_A = couple.node_B
            couple.node_B = temp
        return copy_couple_list

    # 判断条件为，如果是H节点，则直接作为主链路，J节点则需要是所有点都暂时没有归属
    def check_main_link(self, couple_link):
        for node in couple_link:
            if node.type == 'J' and node.topology_id != -1:
                return False
        return True

    # 删除一些重复的主链路
    def delete_copy_main_link(self, topology_link, topology_link_dict):
        hashcode_1_from_node = topology_link.main_link.hashcode_1
        hashcode_2_from_node = topology_link.main_link.hashcode_2
        result = True
        keys = list(topology_link_dict.keys())
        for key in keys:
            # 结果集合中主链路的hash值
            hashcode_1_from_dict = topology_link_dict[key].main_link.hashcode_1
            hashcode_2_from_dict = topology_link_dict[key].main_link.hashcode_2

            # 这个新链路附属于某个链路，不加入结果集合
            if hashcode_1_from_node in hashcode_1_from_dict or hashcode_1_from_node in hashcode_2_from_dict:
                return False

            # 如果这个新链路包含某个结果集合的链路，则需要移除被包含链路，然后继续搜索，看有没有链路附属于这个新链路，然后继续删除
            if hashcode_1_from_dict in hashcode_1_from_node or hashcode_1_from_dict in hashcode_2_from_node:
                topology_link_dict.pop(key)
        return result


    # 找到所有主链路，DFS深度搜索所有可能的链路,value_A表示后面所有的A值必须与这个A值一致
    # 注意这里的value_A,如果中间节点都是J，则value_A是作为相等的中间值
    def dfs_main_link(self, stack_list, couple_link_list, end_node, value_A, type, node_A):
        # 判断是否是终点
        if stack_list[-1].NodeID == end_node.NodeID:
            # 将终点弹出,设置为未访问节点，后复制列表到结果中
            node_B = stack_list.pop()
            node_B.isVisited = False
            # print("main link stop dfs end:" + str(node_B.NodeID))
            stack_copy_list = stack_list[:]
            couple_link_list.append(stack_copy_list)


        # 看是否是符合条件的点，是否是已经访问过的点
        else:
            # 主链路长度不能超过30
            if len(stack_list) == 29:
                # 没有找到对应邻居或者遍历结束,将此点退栈,同时恢复其未访问状态
                node = stack_list.pop()
                # print("main link dfs continue back:" + str(node.NodeID))
                node.isVisited = False
                return

            node_neighbors = list(stack_list[-1].neighbor_dict.values())
            for node_neighbor in node_neighbors:
                # print(str(node_neighbor.NodeID)+":"+node_neighbor.type+":"+str(node_neighbor.A))
                # 要保证下一个点未访问过，且A值要与所有中间点的值一致,或者找到了
                if node_neighbor.NodeID == end_node.NodeID:
                    node_neighbor.isVisited = True
                    stack_list.append(node_neighbor)
                    # print("main link dfs continue go:" + str(node_neighbor.NodeID))
                    # DFS递归深搜
                    self.dfs_main_link(stack_list, couple_link_list, end_node, value_A, type, node_A)
                elif node_neighbor.type == type and node_neighbor.type == 'J' and node_neighbor.A == value_A and not node_neighbor.isVisited:
                    node_neighbor.isVisited = True
                    stack_list.append(node_neighbor)
                    # print("main link dfs continue go:" + str(node_neighbor.NodeID))
                    # DFS递归深搜
                    self.dfs_main_link(stack_list, couple_link_list, end_node, value_A, type, node_A)
                elif node_neighbor.type == type and node_neighbor.type == 'H' and node_neighbor.A <= end_node.A and node_neighbor.A <= node_A.A and not node_neighbor.isVisited:
                    node_neighbor.isVisited = True
                    stack_list.append(node_neighbor)
                    # print("main link dfs continue go:" + str(node_neighbor.NodeID))
                    # DFS递归深搜
                    self.dfs_main_link(stack_list, couple_link_list, end_node, value_A, type, node_A)

            # 没有找到对应邻居或者遍历结束,将此点退栈,同时恢复其未访问状态
            node = stack_list.pop()
            # print("main link dfs continue back:" + str(node.NodeID))
            node.isVisited = False



    '''
    这块用于找到所有副链路
    '''

    # 找到所有副链路
    def find_deputy_link(self, topology_link_dict):
        new_list = list(topology_link_dict.values())
        copy_new_list = new_list[:]
        for topology_link in copy_new_list:
            # 得到这个主链路从一个端点到另一个端点的列表，然后开始遍历
            main_link_node_list = topology_link.main_link.mid_node_list[:]
            main_link_node_list.insert(0, topology_link.main_link.node_A)
            main_link_node_list.append(topology_link.main_link.node_B)
            # 遍历这个列表
            for i in range(0, len(main_link_node_list)-1):
                # 开始端点
                start_node = main_link_node_list[i]
                # print("deputy link start DFS head:"+str(start_node.NodeID))
                # 可能的结束端点
                stop_node_list = main_link_node_list[i+1:]

                # 所有可能的副链路
                deputy_link_list = []
                # 存储已访问节点
                stack_list = []
                start_node_neighbors = list(start_node.neighbor_dict.values())
                start_node.isVisited = True
                for start_node_neighbor in start_node_neighbors:

                    # 排除G/H节点，因为副链路中间节点只能是J，同时排除已经属于其他链路的节点,也排除A值比起始点高的点
                    if not start_node_neighbor.type == 'J' or start_node_neighbor.topology_id != -1 or start_node_neighbor.A > start_node.A:
                        continue
                    # 设置为已访问节点，并且存入栈中
                    # print("deputy link DFS continue:" + str(start_node_neighbor.NodeID))
                    start_node_neighbor.isVisited = True
                    stack_list.append(start_node_neighbor)
                    depth = 0
                    self.dfs_deputy_link(stack_list, deputy_link_list, stop_node_list, start_node, start_node_neighbor.A, depth)
                # 找到所有的副链路之后转为相应的结构，并进行筛选，筛选的要求就是被包含的链路要删除
                start_node.isVisited = False
                for deputy_link_nodes in deputy_link_list:

                    # 首先排除小于三个点的链路
                    if len(deputy_link_nodes) < 2:
                        continue
                    # 得到一个备选的副链路
                    stop_node = deputy_link_nodes.pop()
                    deputy_link = DeputyLink(start_node, deputy_link_nodes, stop_node)
                    if (len(deputy_link.mid_node_list) + topology_link.get_topology_node_num()) > 30:
                        continue
                    # !!!!!!!!!!!!!!!!!注意未考虑包含关系比如A-B-C-D和A-C-D，这两个都属于这个链路就行了，不一定要区分是第几个副链路，因为最后我们提交的时候只是说明属于副链路与否
                    topology_link.add_deputy_link(deputy_link)

    # 找到所有副链路，DFS深度搜索所有可能的副链路
    def dfs_deputy_link(self, stack_list, deputy_link_list, stop_node_list, start_node, mid_node_highest_A, depth):
        # print("deep---------"+str(depth))

        # 先判断是否是终点
        if stack_list[-1] in stop_node_list:
            # 不是可用的副链路，则直接删除跳过
            if not self.is_deputy_link(start_node, stack_list[-1], mid_node_highest_A):
                stop_node = stack_list.pop()
                stop_node.isVisited = False
                return
            else:
                stack_copy_list = stack_list[:]
                deputy_link_list.append(stack_copy_list)
                stop_node = stack_list.pop()
                stop_node.isVisited = False
                # print("deputy link stop dfs end:" + str(stop_node.NodeID))
        # 看是否是符合条件的点，是否是已经访问过的点
        else:
            node_neighbors = list(stack_list[-1].neighbor_dict.values())
            for node_neighbor in node_neighbors:
                # print(str(node_neighbor.NodeID) + ":" + node_neighbor.type + ":" + str(node_neighbor.A))
                # 要保证下一个点未访问过，且A值小于等于开始点，J类型，不属于任何一个链路，或者找到了终点
                if not node_neighbor.isVisited and node_neighbor.A <= start_node.A and node_neighbor.type == 'J' and node_neighbor.topology_id == -1:
                    node_neighbor.isVisited = True
                    stack_list.append(node_neighbor)
                    # print("deputy link dfs continue go:" + str(node_neighbor.NodeID))
                    if node_neighbor.A > mid_node_highest_A:
                        mid_node_highest_A = node_neighbor.A
                    # DFS递归深搜
                    depth += 1
                    self.dfs_deputy_link(stack_list, deputy_link_list, stop_node_list, start_node, mid_node_highest_A, depth)
                elif node_neighbor in stop_node_list:
                    node_neighbor.isVisited = True
                    stack_list.append(node_neighbor)
                    # print("start node_id:"+str(start_node.NodeID))
                    # print("node_id:"+str(node_neighbor.NodeID))
                    depth += 1
                    self.dfs_deputy_link(stack_list, deputy_link_list, stop_node_list, start_node, mid_node_highest_A, depth)

            # 没有找到对应邻居或者遍历结束,将此点退栈,同时恢复其未访问状态
            node = stack_list.pop()
            # print("deputy link dfs continue back:" + str(node.NodeID))
            node.isVisited = False
            depth -= 1

    # 分析起始点和终点类型是否符合副链路定义，以及中间节点的A值是否满足小于等于两端的A值
    def is_deputy_link(self, start_node, stop_node, mid_node_highest_A):

        # 先看A值是否满足
        if mid_node_highest_A > start_node.A or mid_node_highest_A > stop_node.A:
            return False
        # 再看类型
        if start_node.type == 'J' or stop_node.type == 'J':
            return True
        return False


    '''
    找到所有的下挂点
    '''

    def test_sort(self, link_list, day):
        # 长度排序
        for i in range(0, len(link_list) - 1):
            for j in range(0, len(link_list) - i - 1):
                if link_list[j].get_use_rate(day) > link_list[j + 1].get_use_rate(day):
                    temp = link_list[j]
                    link_list[j] = link_list[j + 1]
                    link_list[j + 1] = temp
        return link_list

    # 所有的剩余点找到附属点
    def find_hanging_node(self, topology_link_dict, NE_edge_dict, day):

        # 下挂点插入主链路
        number = 0
        topology_link_list = self.test_sort(list(topology_link_dict.values()), day)
        for node in list(self.J_node_dict.values()):
            if node.topology_id != -1:
                continue
            # print("yeh")

            is_insert = search_topology_dict(topology_link_list, node, NE_edge_dict)
            if is_insert:
                number += 1
        print("hanging_number:"+str(number))



        hanging_node_list = []
        for topology_link in topology_link_list:
            main_link = topology_link.main_link
            deputy_link_list = topology_link.deputy_link_list

            # 先遍历主链路,加入下挂
            for node in main_link.get_path():
                node_neighbor_dict = node.neighbor_dict
                for node_neighbor in list(node_neighbor_dict.values()):
                    if node_neighbor.topology_id == -1 and node_neighbor.A <= node.A:
                        # print(main_link.hashcode_1+"链路增加下挂点："+str(node.NodeID)+"->"+str(node_neighbor.NodeID))
                        node_neighbor.topology_id = topology_link.topology_link_id
                        node.is_have_hanging_node = True
                        topology_link.hanging_node_list.append(Couple(node, node_neighbor))

            # 遍历副链路，增加下挂
            for deputy_link in deputy_link_list:
                for node in deputy_link.get_path():
                    node_neighbor_dict = node.neighbor_dict
                    for node_neighbor in list(node_neighbor_dict.values()):
                        if node_neighbor.topology_id == -1 and node_neighbor.A <= node.A:
                            # print(deputy_link.hashcode + "链路增加下挂点：" + str(node.NodeID) + "->" + str(node_neighbor.NodeID))
                            node_neighbor.topology_id = topology_link.topology_link_id
                            node.is_have_hanging_node = True
                            topology_link.hanging_node_list.append(Couple(node, node_neighbor))
        # 下挂深度不超过2，所以可以再找一次
        for node in list(self.J_node_dict.values()):
            if node.topology_id != -1:
                continue
            for node_neighbor in list(node.neighbor_dict.values()):
                if node_neighbor.topology_id != -1 and node_neighbor.A >= node.A:
                    node.topology_id = node_neighbor.topology_id
                    node_neighbor.is_have_hanging_node = True
                    topology_link_dict[node.topology_id].hanging_node_list.append(Couple(node_neighbor, node))
        # a城市需要再找一轮下挂点
        for node in list(self.J_node_dict.values()):
            if node.topology_id != -1:
                continue
            for node_neighbor in list(node.neighbor_dict.values()):
                if node_neighbor.topology_id != -1 and node_neighbor.A >= node.A:
                    node.topology_id = node_neighbor.topology_id
                    node_neighbor.is_have_hanging_node = True
                    topology_link_dict[node.topology_id].hanging_node_list.append(Couple(node_neighbor, node))



























# 定义点结构
class Node:
    # 通过点的属性初始化一个点
    def __init__(self, NodeID, type, A, longitude, lantitude, D):
        self.NodeID = NodeID
        self.type = type
        self.A = A
        self.longitude = longitude
        self.lantitude = lantitude
        self.D = D
        self.topology_id = -1
        self.is_end_node = False

        # 是否是副链路的端点
        self.is_deputy_head = False

        # 是否有下挂点
        self.is_have_hanging_node = False

        # 存储了所有邻居点集合
        self.neighbor_dict = dict()

        # 是否访问过
        self.isVisited = False

        # 每日数据
        self.day_flow_list = []

        # 是否已经优化过
        self.isOptimated = False

        # 与链路容载量进行判断的数据
        self.judge_A = []
        self.init_judge_A()

    # 初始化判断A值
    def init_judge_A(self):
        for i in range(0, 10):
            self.judge_A.append(-1)

# 两个端点组成的对
class Couple:
    def __init__(self, node_A, node_B):
        self.node_A = node_A
        self.node_B = node_B
    # 判断是否是一个对
    def is_couple(self, node_a, node_b):
        if node_a == self.node_A and node_b == self.node_B:
            return True
        elif node_b == self.node_A and node_a == self.node_B:
            return True
        else:
            return False

    # 第一个是高A值，第二个是低A值的点
    def get_high_low_node(self):
        if self.node_A.A >= self.node_B:
            return self.node_A, self.node_B
        else:
            return self.node_B, self.node_A











