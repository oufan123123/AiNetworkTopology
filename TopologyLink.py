'''
定义一个拓扑连接结构，包括一个主链路，多个副链路，还有若干下挂点；
因为它本身已经定义了链路结构，所以我们需要做的是先区分链路中的主副链路和下挂，然后才能继续进行优化
链路：包含主副节点和下挂点，对应一个NE编号
主链路：在这个链路中，两头为G/H节点，中间是全H或者全J节点，两头组合可以是G/G,G/H,H/H
副链路：附属于主链路，两头为G/H/J，但是两头不能同时是G或者同时是H节点，就是两头的组合可以是G/H,G/J,H/J,J/J
下挂点：附属于一个点，我觉得一般是H/J

链路解析实现思路：
前提，已经构好图G，然后得到了一个链路的所有点集合S
实现算法
（1）主链路：先找到所有的G/G,G/H,H/H对，然后找到所有点对之间的路径，去除重叠路径比如有路径A->B->C->D,则路径B->C就会被删除，确定的所有点对之间的所有可能路径就是所有的主链路，也是所有的链路
（2）副链路：对于一个主链路，首先对所有点排序，然后按照第一个点找第二个点到最后一个点的所有路径，同样去除重叠路径，第二个点找第三个点到最后一个点。。。。依次找到所有副链路，保证不重复计算副链路
（3）剩余的点都下挂
'''


# 定义一个链路
class TopologyLink:
    # 初始化函数中，节点A是起始点，中间节点列表由A连接，节点B是终点
    def __init__(self, node_A, mid_node_list, node_B, topology_link_id):
        self.topology_link_id = topology_link_id
        self.main_link = MainLink(node_A, mid_node_list, node_B)
        self.deputy_link_list = []
        self.gen_node_topology_id()

        # 增加一个下挂点的存储字典
        self.hanging_node_list = []
        self.max_A_node = self.main_link.mid_node_list[0]

        # 当前链路的流量值之和
        self.total_flow = 0.0
        # 得到u值
        self.u = 0.0



    # 为每个主链路点附上链路的编号，表示其已经附属于某个链路，不能作为副链路的中间节点了
    def gen_node_topology_id(self):
        self.main_link.gen_node_topology_id(self.topology_link_id)

    # 加入一个副链路到结果集合中
    def add_deputy_link(self, deputy_link):
        if deputy_link is None:
            return
        self.deputy_link_list.append(deputy_link)
        deputy_link.gen_node_topology_id(self.topology_link_id)

    # 根据新的id更新所有点的链路编号
    def update_topology_id(self, new_topology_link_id):
        self.topology_link_id = new_topology_link_id
        # 更新主链路的id
        self.gen_node_topology_id()
        # 更新副链路的id
        for deputy_link in self.deputy_link_list:
            deputy_link.gen_node_topology_id(self.topology_link_id)
        # 更新下挂点的id
        for hanging_node in self.hanging_node_list:
            hanging_node.node_A.topology_id = self.topology_link_id
            hanging_node.node_B.topology_id = self.topology_link_id

    # 得到链路的节点数目
    def get_topology_node_num(self):
        node_number = 0
        node_number += len(self.main_link.get_path())
        for deputy_link in self.deputy_link_list:
            node_number += len(deputy_link.mid_node_list)
        node_number += len(self.hanging_node_list)
        return node_number

    def get_total_flow(self, day):
        # 得到所有链路其他节点的流量值总和
        total_flow = 0.0
        for main_node in self.main_link.mid_node_list:
            total_flow += main_node.judge_A[day]
        for deputy_link in self.deputy_link_list:
            for deputy_node in deputy_link.mid_node_list:
                total_flow += deputy_node.judge_A[day]
        for couple in self.hanging_node_list:
            if couple.node_A.is_have_hanging_node == True:
                total_flow += couple.node_B.judge_A[day]
            else:
                total_flow += couple.node_A.judge_A[day]
        return total_flow

    # 得到其某天的利用率分数
    def get_use_rate(self, day):
        day = day - 21
        # 最大节点容载量A值,乘以1000
        max_A = self.main_link.mid_node_list[0].A
        # 得到所有链路其他节点的流量值总和
        total_flow = 0.0
        for main_node in self.main_link.mid_node_list:
            total_flow += main_node.judge_A[day]
            print(main_node.judge_A[day])
            if main_node.A > max_A:
                max_A = main_node.A
                self.max_A_node = main_node
        for deputy_link in self.deputy_link_list:
            for deputy_node in deputy_link.mid_node_list:
                total_flow += deputy_node.judge_A[day]
                print(deputy_node.judge_A[day])
        for couple in self.hanging_node_list:
            if couple.node_A.is_have_hanging_node == True:
                total_flow += couple.node_B.judge_A[day]
                print(couple.node_B.judge_A[day])
            else:
                total_flow += couple.node_A.judge_A[day]
                print(couple.node_A.judge_A[day])
        print("max_A"+str(max_A))
        max_A = max_A * 1000
        flow = total_flow / max_A
        print("topology_id:"+str(self.topology_link_id)+"use_rate:"+str(flow))
        return flow















# 定义一个主链路，附属于一个链路结构
class MainLink:
    def __init__(self, node_A, mid_node_list, node_B):
        self.node_A = node_A
        self.node_B = node_B
        self.mid_node_list = mid_node_list
        self.hashcode_1,self.hashcode_2 = self.gen_hashcode()

        # 增加一个结构体，存储NE值和NE的A,和边链接的关系对照为:node_list[i]---node_list[i + 1] 对照 NE[i]
        self.NE_list = []

    # 增加一个结构体，存储NE值和NE的A,和边链接的关系对照为:node_list[i]---node_list[i + 1] 对照 NE[i]
    def init_NE_list(self, NE_A_dict, NE_edge_dict):
        node_list = self.get_path()
        for i in range(0, len(node_list) - 1):
            NE_id = get_NE_from_couple_dict(NE_edge_dict, node_list[i], node_list[i + 1])
            self.NE_list.append(NEEdge(NE_id, NE_A_dict[NE_id], node_list[i], node_list[i + 1]))




    # 返回将A点加入头，B点加入尾的列表
    def get_path(self):
        node_list = self.mid_node_list[:]
        node_list.insert(0, self.node_A)
        node_list.append(self.node_B)
        return node_list


    # 生成链路的HASH值
    def gen_hashcode(self):
        node_list = self.mid_node_list[:]
        node_list.insert(0, self.node_A)
        node_list.append(self.node_B)
        hashcode_1 = ""
        hashcode_2 = ""
        # 正序遍历列表为一个hash值

        for node in node_list:
            hashcode_1 = hashcode_1 + "-"+str(node.NodeID)+node.type

        # 逆序遍历列表为一个hash值
        for node in reversed(node_list):
            hashcode_2 = hashcode_2 + "-"+str(node.NodeID)+node.type

        return hashcode_1,hashcode_2

    # 为每个主链路点附上链路的编号，表示其已经附属于某个链路，不能作为副链路的中间节点了
    def gen_node_topology_id(self, topology_id):
        self.node_A.topology_id = 1
        self.node_B.topology_id = 1
        for node in self.mid_node_list:
            node.topology_id = topology_id

    # 插入一个节点到主链路,同时更新NE和邻居关系
    def insert_node(self, node, position):
        # 插入到中间节点
        self.mid_node_list.insert(position, node)
        # 在path中的下标
        position_of_path = position + 1

        path_of_nodes = self.get_path()
        node.isOptimated = True
        node.topology_id = self.node_A.topology_id
        # 更新与两个端点的邻居关系
        # print("node:"+str(node.NodeID)+"new position is right:"+str(path_of_nodes[position_of_path].NodeID)+"position:"+str(position_of_path))

        node_before = path_of_nodes[position_of_path - 1]
        node_after = path_of_nodes[position_of_path + 1]
        # print("node_before:" +str(node_before.NodeID))
        # print("node_after:" + str(node_after.NodeID))
        node_before.neighbor_dict.pop(node_after.NodeID)
        node_after.neighbor_dict.pop(node_before.NodeID)
        node_before.neighbor_dict[node.NodeID] = node
        node_after.neighbor_dict[node.NodeID] = node
        node.neighbor_dict[node_before.NodeID] = node_before
        node.neighbor_dict[node_after.NodeID] = node_after

        # 更新NE——list
        pop_NE = self.NE_list.pop(position)
        self.NE_list.insert(position, NEEdge(-1, -1, node, node_before))
        self.NE_list.insert(position + 1, NEEdge(-1, -1, node, node_after))

    # 删除一个中间节点
    def remove_node(self, position_of_mid_node_list):
        remove_node = self.mid_node_list[position_of_mid_node_list]
        remove_node.isOptimated = True
        # 先更改它与两边节点的邻居关系
        path_of_nodes = self.get_path()
        # 得到其在path中的位置
        position_of_path = position_of_mid_node_list + 1
        print("before:"+str(path_of_nodes[position_of_path -1].NodeID))
        print("after:" + str(path_of_nodes[position_of_path + 1].NodeID))
        self.mid_node_list.pop(position_of_mid_node_list)
        '''
        # print("mid_node:"+str(remove_node.NodeID)+":path_node:"+str(path_of_nodes[position_of_path].NodeID))
        node_before = path_of_nodes[position_of_path - 1]
        node_after = path_of_nodes[position_of_path + 1]
        node_before.neighbor_dict.pop(remove_node.NodeID)
        node_after.neighbor_dict.pop(remove_node.NodeID)
        remove_node.neighbor_dict.pop(node_before.NodeID)
        remove_node.neighbor_dict.pop(node_after.NodeID)
        node_before.neighbor_dict[node_after.NodeID] = node_after
        node_after.neighbor_dict[node_before.NodeID] = node_before

        

        # 更新NE_list
        self.NE_list.pop(position_of_path - 1)
        self.NE_list.pop(position_of_path - 1)
        self.NE_list.insert(position_of_path - 1, NEEdge(-1, -1, node_before, node_after))
        '''

# 定义一个副链路，附属于一个链路
class DeputyLink:
        def __init__(self, node_A, mid_node_list, node_B):
            self.node_A = node_A
            # 只用一个hashcode就行，因为如果主链路有序，根据主链路的顺序找的链路应该也是有序的
            self.node_B = node_B
            self.mid_node_list = mid_node_list
            self.hashcode = self.gen_hashcode()

            # 增加一个结构体，存储NE值和NE的A,和边链接的关系对照为:node_list[i]---node_list[i + 1] 对照 NE[i]
            self.NE_list = []


        # 增加一个结构体，存储NE值和NE的A,和边链接的关系对照为:node_list[i]---node_list[i + 1] 对照 NE[i]
        def init_NE_list(self, NE_A_dict, NE_edge_dict):
            node_list = self.get_path()
            for i in range(0, len(node_list) - 1):
                NE_id = get_NE_from_couple_dict(NE_edge_dict, node_list[i], node_list[i + 1])
                self.NE_list.append(NEEdge(NE_id, NE_A_dict[NE_id], node_list[i], node_list[i + 1]))

        # 返回将A点加入头，B点加入尾的列表
        def get_path(self):
            node_list = self.mid_node_list[:]
            node_list.insert(0, self.node_A)
            node_list.append(self.node_B)
            return node_list

        def gen_hashcode(self):
            node_list = self.mid_node_list[:]
            node_list.insert(0, self.node_A)
            node_list.append(self.node_B)
            hashcode = ""
            for node in node_list:
                hashcode = hashcode + "-" + str(node.NodeID)
            return hashcode

        # 为每个副链路点附上链路的编号，表示其已经附属于某个链路，不能作为副链路的中间节点了
        def gen_node_topology_id(self, topology_id):
            self.node_A.is_deputy_head = True
            self.node_B.is_deputy_head = True
            for node in self.mid_node_list:
                node.topology_id = topology_id

        # 插入一个节点到链路,同时更新NE和邻居关系
        def insert_node(self, node, position):
            # 插入到中间节点
            self.mid_node_list.insert(position, node)
            # 在path中的下标
            position_of_path = position + 1
            node.isOptimated = True
            path_of_nodes = self.get_path()

            # 更新与两个端点的邻居关系
            node_before = path_of_nodes[position_of_path - 1]
            node_after = path_of_nodes[position_of_path + 1]
            node_before.neighbor_dict.pop(node_after.NodeID)
            node_after.neighbor_dict.pop(node_before.NodeID)
            node_before.neighbor_dict[node.NodeID] = node
            node_after.neighbor_dict[node.NodeID] = node
            node.neighbor_dict[node_before.NodeID] = node_before
            node.neighbor_dict[node_after.NodeID] = node_after

            # 更新NE——list
            self.NE_list.pop(position)
            self.NE_list.insert(position, NEEdge(-1, -1, node, node_before))
            self.NE_list.insert(position + 1, NEEdge(-1, -1, node, node_after))

        # 删除一个中间节点
        def remove_node(self, position_of_mid_node_list):
            remove_node = self.mid_node_list[position_of_mid_node_list]
            remove_node.isOptimated = True
            # 先更改它与两边节点的邻居关系
            path_of_nodes = self.get_path()
            # 得到其在path中的位置
            position_of_path = position_of_mid_node_list + 1
            # print("mid_node:"+str(remove_node.NodeID)+":path_node:"+str(path_of_nodes[position_of_path].NodeID))
            node_before = path_of_nodes[position_of_path - 1]
            node_after = path_of_nodes[position_of_path + 1]
            node_before.neighbor_dict.pop(remove_node.NodeID)
            node_after.neighbor_dict.pop(remove_node.NodeID)
            remove_node.neighbor_dict.pop(node_before.NodeID)
            remove_node.neighbor_dict.pop(node_after.NodeID)
            node_before.neighbor_dict[node_after.NodeID] = node_after
            node_after.neighbor_dict[node_before.NodeID] = node_before

            self.mid_node_list.pop(position_of_mid_node_list)

            # 更新NE_list
            self.NE_list.pop(position_of_path - 1)
            self.NE_list.pop(position_of_path - 1)
            self.NE_list.insert(position_of_path - 1, NEEdge(-1, -1, node_before, node_after))

class NEEdge:
    def __init__(self, NE_id, A, node_A, node_B):
        self.NE_id = NE_id
        self.A = A
        self.node_A = node_A
        self.node_B = node_B


def get_NE_from_couple_dict(NE_edge_dict, node_A, node_B):
    for key in NE_edge_dict.keys():
        if NE_edge_dict[key].is_couple(node_A, node_B):
            return key
    return None



















