import pandas as pd
import os
from Graph import Graph
from Graph import Node
from Graph import Couple
import sys
from TopologyLink import TopologyLink
import random
import csv
from TopologyOptimation import topology_optimation
from TopologyOptimation import get_two_node_distance

def main():
    # 拓扑连接的文件路径
    pathOfCollection = '.\\data\\test.csv'

    # 第一步，读取赛题数据，创建网络拓扑

    # 第二步，预测每个城市的未来10天网络拓扑

    # 第三步，优化网络结构
# 得到过高过低两个链路列表
def get_two_topology_list(topology_link_dict, day):
    average_flow_rate = 0.0
    high_use_rate_topology_list = []
    low_use_rate_topology_list = []
    for topology_link in topology_link_dict.values():
        average_flow_rate += topology_link.get_use_rate(day)
    average_flow_rate = average_flow_rate / len(topology_link_dict)

    max_rate = average_flow_rate * 1.3
    min_rate = average_flow_rate * 0.7
    for topology_link in topology_link_dict.values():
        if topology_link.get_use_rate(day) < min_rate:
            low_use_rate_topology_list.append(topology_link)
        elif topology_link.get_use_rate(day) > max_rate:
            high_use_rate_topology_list.append(topology_link)
        topology_link.u = average_flow_rate
    print("u:" + str(average_flow_rate))
    print("high_num:"+str(len(high_use_rate_topology_list)))
    print("low_num:" + str(len(low_use_rate_topology_list)))
    test_sort(low_use_rate_topology_list, day)
    return high_use_rate_topology_list, low_use_rate_topology_list


# 设置所有节点的judgeA值,同时在这里设置参数
def set_node_list_judge_A(node_list, day):
    day = day - 21
    param = 0.0
    for node in node_list:
        set_node_judge_A(node, param, day)


# 输入一个节点，输出一个节点的判断A值,param取值范围0~1
def set_node_judge_A(node, param, day):
    # 平均值
    day_flow_average = 0.5
    # 最大值
    day_flow_max = node.day_flow_list[day][0]
    for hour_flow in node.day_flow_list[day]:
        day_flow_average += hour_flow
        if day_flow_max < hour_flow:
            day_flow_max = hour_flow
    day_flow_average = day_flow_average / 24.0
    # 得到这一天的小时级别的判断流量
    node.judge_A[day] = day_flow_average + (day_flow_max - day_flow_average) * param

def get_NE_from_couple_dict(NE_edge_dict, node_A, node_B):
    for key in NE_edge_dict.keys():
        if NE_edge_dict[key].is_couple(node_A, node_B):
            return key
    return -1

# 输出csv文件
def write_result(NE_edge_dict, topology_link_dict, day):
    # 解析所有的链路边到NE编号,输出到文件
        csvFile = open('.\\8-10-2\\Graph_topology_B_202003{}.csv'.format(str(day)), 'w+', newline='')
        writer = csv.writer(csvFile)
        writer.writerow(('Circle_ID', 'NodeID_A', 'NodeID_Z', 'NE', 'Link_class'))
        topology_link_list = list(topology_link_dict.values())

        new_topology_link_id = 1
        new_NE_id = 1
        for topology_link in topology_link_list:
            # 先更新编号，想按照+1的序列增加链路编号
            topology_link.update_topology_id(new_topology_link_id)

            # 查找链路中所有边对应的NE编号，然后按照格式输出到文件
            # 先找到主链路
            main_link_path = topology_link.main_link.get_path()
            for i in range(0, len(main_link_path) - 1):
                # 得到这个couple对应的NE编号

                NE_id = get_NE_from_couple_dict(NE_edge_dict, main_link_path[i], main_link_path[i + 1])
                if NE_id == -1:
                    if get_two_node_distance(main_link_path[i], main_link_path[i + 1]) > 450:
                        print("distance:" + str(get_two_node_distance(main_link_path[i], main_link_path[i + 1])))
                    if main_link_path[i].A >= main_link_path[i + 1].A:
                        writer.writerow((str(new_topology_link_id), str(main_link_path[i].NodeID),
                                         str(main_link_path[i + 1].NodeID), str(new_NE_id), '1'))
                    else:
                        writer.writerow((str(new_topology_link_id), str(main_link_path[i + 1].NodeID),
                                         str(main_link_path[i].NodeID), str(new_NE_id), '1'))
                    new_NE_id += 1
                else:
                    if main_link_path[i].A >= main_link_path[i + 1].A:
                        # print(str(new_topology_link_id)+ str(main_link_path[i].NodeID)+ str(main_link_path[i + 1].NodeID)+ str(NE_id)+'1')
                        writer.writerow((str(new_topology_link_id), str(main_link_path[i].NodeID), str(main_link_path[i + 1].NodeID), str(NE_id), '1'))
                    else:
                        writer.writerow((str(new_topology_link_id), str(main_link_path[i + 1].NodeID), str(main_link_path[i].NodeID), str(NE_id), '1'))

            # 再找副链路
            deputy_link_list = topology_link.deputy_link_list
            for deputy_link in deputy_link_list:
                deputy_link_path = deputy_link.get_path()
                for i in range(0, len(deputy_link_path) - 1):
                    # 得到这个couple对应的NE编号

                    NE_id = get_NE_from_couple_dict(NE_edge_dict, deputy_link_path[i], deputy_link_path[i + 1])
                    if NE_id == -1:
                        if get_two_node_distance(deputy_link_path[i], deputy_link_path[i + 1]) > 450:
                            print("distance:" + str(get_two_node_distance(deputy_link_path[i], deputy_link_path[i + 1])))
                        if deputy_link_path[i].A >= deputy_link_path[i + 1].A:
                            writer.writerow((str(new_topology_link_id), str(deputy_link_path[i].NodeID),
                                             str(deputy_link_path[i + 1].NodeID), str(new_NE_id), '2'))
                        else:
                            writer.writerow((str(new_topology_link_id), str(deputy_link_path[i + 1].NodeID),
                                             str(deputy_link_path[i].NodeID), str(new_NE_id), '2'))
                        new_NE_id += 1
                    else:
                        if deputy_link_path[i].A >= deputy_link_path[i + 1].A:
                            writer.writerow((str(new_topology_link_id), str(deputy_link_path[i].NodeID), str(deputy_link_path[i + 1].NodeID), str(NE_id), '2'))
                        else:
                            writer.writerow((str(new_topology_link_id), str(deputy_link_path[i + 1].NodeID),str(deputy_link_path[i].NodeID), str(NE_id), '2'))

            # 最后找下挂点
            hanging_node_list = topology_link.hanging_node_list
            for hanging_node in hanging_node_list:
                NE_id = get_NE_from_couple_dict(NE_edge_dict, hanging_node.node_A, hanging_node.node_B)
                if NE_id == -1:
                    writer.writerow((str(new_topology_link_id), str(hanging_node.node_A.NodeID), str(hanging_node.node_B.NodeID), str(new_NE_id), '3'))
                    new_NE_id += 1
                else:
                    writer.writerow((str(new_topology_link_id), str(hanging_node.node_A.NodeID), str(hanging_node.node_B.NodeID), str(NE_id), '3'))
            new_topology_link_id += 1

        csvFile.close()

# 读取预测的未来的节点的值
def insert_data_to_node(graph, pathOfFutureData):
    # 解析文件
    # 读取csv文件,转为二维数组
    for x in range(21, 31):
        path = pathOfFutureData+"{}.csv".format(str(x))
        city = pd.read_csv(path)
        collectionList = city.values.tolist()
        for i in range(len(collectionList)):
            node = graph.find_node_by_id(collectionList[i][0])
            day_flow = []
            # 读取每天的流量
            for j in range(6, 30):
                day_flow.append(collectionList[i][j])
            node.day_flow_list.append(day_flow)








def test():
    pathOfCity = '.\\data\\Data_attributes_B_20200301.csv'
    pathOfCollection  = '.\\data\\Data_topology_B.csv'
    pathOfFutureData = ".\\future_data\\Data_attributes_B_202003"

    # 每天优化
    for day in range(21, 31):

        # 解析文件
        # 读取csv文件,转为二维数组
        city = pd.read_csv(pathOfCity)
        collectionList = city.values.tolist()

        all_node_dict = dict()

        # 对图上的点进行插入
        graph = Graph()
        for i in range(len(collectionList)):
            node_A = Node(collectionList[i][0], collectionList[i][1], collectionList[i][2], collectionList[i][3],
                          collectionList[i][4], collectionList[i][5])
            if collectionList[i][0] in graph.G_node_dict:
                node_A = graph.G_node_dict[collectionList[i][0]]
            elif collectionList[i][0] in graph.H_node_dict:
                node_A = graph.H_node_dict[collectionList[i][0]]
            elif collectionList[i][0] in graph.J_node_dict:
                node_A = graph.J_node_dict[collectionList[i][0]]
            graph.insert_node(node_A)
            all_node_dict[collectionList[i][0]] = 0

        # 读取未来10天的数据,将数据插入到节点
        insert_data_to_node(graph, pathOfFutureData)

        # 读取csv文件,转为二维数组
        collection = pd.read_csv(pathOfCollection)
        collectionList = collection.values.tolist()

        # 存储一个边编号---两个点对应的字典
        NE_edge_dict = dict()
        # 存储一个边编号---A值对应的字典
        NE_A_dict = dict()

        # 对图上的边进行插入
        for i in range(len(collectionList)):
            node_A = graph.find_node_by_id(collectionList[i][0])
            node_B = graph.find_node_by_id(collectionList[i][4])
            couple = Couple(node_A, node_B)
            NE_edge_dict[collectionList[i][9]] = couple
            NE_A_dict[collectionList[i][9]] = collectionList[i][8]
            if node_A.type == 'G':
                # print(str(node_A.NodeID)+":"+str(node_A.longitude)+":"+str(node_A.lantitude)+":"+node_A.type+":"+str(node_A.A)+":"+str(node_A.D))
                pass
            graph.add_edge(node_A, node_B)
        # 为图的所有小于500m的点加为邻居
        print("1")
        # graph.add_neighbor()
        print("2")
        '''
        J_node_dict = graph.J_node_dict
        for J_node in J_node_dict.values():
            if J_node.NodeID == 38584530:
                for key in J_node.neighbor_dict.keys():
                    print(str(key))
        '''
        print(len(graph.G_node_dict))
        print(len(graph.H_node_dict))
        print(len(graph.J_node_dict))
        print("文件阅读完毕。。。")

        set_node_list_judge_A(list(graph.G_node_dict.values()), day)
        set_node_list_judge_A(list(graph.H_node_dict.values()), day)
        set_node_list_judge_A(list(graph.J_node_dict.values()), day)

        # 生成所有的链路
        topology_link_dict = graph.gen_all_topology_link(NE_A_dict, NE_edge_dict, day)
        print(len(topology_link_dict))
        print("带有主链路的链路解析完毕。。。")


        topology_link_list = list(topology_link_dict.values())

        # 打印每条链路的利用率
        csvFile = open('.\\use_rate\\rate.csv', 'w+', newline='')
        writer = csv.writer(csvFile)
        writer.writerow(('Circle_ID', 'rate', 'main_link_number', 'all_number', 'max_A'))


        print("开始优化链路。。。")

        # 先把所有点设置好juedgeA

        # 得到u值，然后根据利用率排序,将不满足要求的链路放到两个列表中，一个是利用率过高，一个是利用率过低，过高的点
        # 会把点放到过低的链路进行优化
        high_use_rate_topology_list,low_use_rate_topology_list = get_two_topology_list(topology_link_dict, day)
        # 优化链路
        topology_optimation(NE_edge_dict, high_use_rate_topology_list,low_use_rate_topology_list, day)

        print("停止优化链路。。。")

        # 看是不是所有点都到了某个链路上面
        G_node_num = 0
        H_node_num = 0
        J_node_num = 0
        for node in graph.G_node_dict.values():
            if node.topology_id == -1:
                G_node_num += 1
        for node in graph.H_node_dict.values():
            if node.topology_id == -1:
                H_node_num += 1
        for node in graph.J_node_dict.values():
            if node.topology_id == -1:
                print("剩余节点：" + str(node.NodeID) + node.type + str(node.A))
                for node_neighbor in list(node.neighbor_dict.values()):
                    print("node_neighbor:" + str(node_neighbor.NodeID)+": 是否在链路中"+str(node_neighbor.topology_id)+node_neighbor.type+ str(node_neighbor.A))
                J_node_num += 1
        print("G剩余点："+str(G_node_num))
        print("H剩余点：" + str(H_node_num))
        print("J剩余点：" + str(J_node_num))


        write_result(NE_edge_dict, topology_link_dict, day)
        # print_topology_NE(NE_edge_dict, NE_A_dict, topology_link_dict)






        # 展示一个链路
        # topology_link_list[0].show_main_link()

        topology_link_list = list(topology_link_dict.values())


        for topology_link in topology_link_list:
            node_number = 0
            node_number += len(topology_link.main_link.get_path())
            main_path = topology_link.main_link.get_path()
            for node in main_path:
                if node.NodeID in all_node_dict:
                    all_node_dict[node.NodeID] = 1
            deputy_link_list = topology_link.deputy_link_list
            for deputy_link in deputy_link_list:
                for node in deputy_link.mid_node_list:
                    if node.NodeID in all_node_dict:
                        all_node_dict[node.NodeID] = 1
            for couple in topology_link.hanging_node_list:
                if couple.node_A.NodeID in all_node_dict:
                    all_node_dict[couple.node_A.NodeID] = 1
                if couple.node_B.NodeID in all_node_dict:
                    all_node_dict[couple.node_B.NodeID] = 1
        # 看优化后是否有点不在链路上
        for key in all_node_dict.keys():
            if all_node_dict[key] == 0:
                print("优化后有点不在链路上：" + str(key))
        for key in all_node_dict.keys():
            all_node_dict[key] = 0


def test_sort(link_list, day):
    # 长度排序
    for i in range(0, len(link_list) - 1):
        for j in range(0, len(link_list) - i - 1):
            if link_list[j].get_use_rate(day) < link_list[j + 1].get_use_rate(day):
                temp = link_list[j]
                link_list[j] = link_list[j + 1]
                link_list[j + 1] = temp

if __name__ == '__main__':
    # main()
    test()
    #test_sort()
