'''
专用于对链路进行优化，输入已经构好的图和链路，然后按照一定的规则进行拓扑优化
判断节点的流量是否超载：
（1）网元节点当天的流量均值与最大值之间的某个值，我为这个值设定一个系数，可以自由设置，然后得到一个用于判断的流量值；
（2）判断网元节点的这个值和所在链路的左右两边的容载量，进行对比之后，如果高于某个边的容载量，则判定其超载，否则不超载
如果节点超载:
（1）找到这个节点周围的其他链路，看有没有临近点所在链路的A值大于这个值，然后这个链路的边要满足节点的距离需要，主链路的需要，副链路的需要
（2）满足需要则加入这个新的点到链路，拆除原来的边，增加新的边
暂时未考虑节点不超载，反而链路的容载量过剩的情况
'''

import math
from DistanceCaculate import get_distance_hav

# 初始化一份链路优化方法,这是对一天的优化
def topology_optimation(NE_edge_dict, high_use_rate_topology_list,low_use_rate_topology_list, day):
    # 先遍历所有的高流量链路上的节点，找到需要优化的节点
    print("len(high):"+str(len(high_use_rate_topology_list)))
    print("len(low):" + str(len(low_use_rate_topology_list)))
    for topology_link in high_use_rate_topology_list:
        # 优化主链路
        optimate_main_link(topology_link, low_use_rate_topology_list, NE_edge_dict, day)
        # 优化副链路
        optimate_deputy_link(topology_link, low_use_rate_topology_list, NE_edge_dict, day)
        # 优化下挂点
        optimate_hanging_node(topology_link, low_use_rate_topology_list, NE_edge_dict, day)


# 先优化主链路
def optimate_main_link(topology_link, low_use_rate_topology_list, NE_edge_dict, day):
    main_link = topology_link.main_link
    # 不考虑优化两端的节点，只考虑中间节点
    # 先去设置中间节点的判断值
    mid_node_list = main_link.mid_node_list
    for i in range(len(mid_node_list)-1, -1, -1):
        # 判断是否可以被删除，放到其他节点
        if check_main_is_overload(topology_link, i, NE_edge_dict, day):
            print("check_is_overload")
            # 遍历其他的链路,寻找合适的链路,然后优化在新链路的那部分，即拆除原有的连接，插入新的链接
            # ！！！！！先不考虑此链路的其他副链路，后续可以增加
            is_delete = search_topology_link(low_use_rate_topology_list, mid_node_list[i], NE_edge_dict, day)
            # 接着优化在旧链路的那部分，拆除原有的点，将原有点的邻居链接起来
            if is_delete:
                main_link.remove_node(i)


# 再优化副链路
def optimate_deputy_link(topology_link, low_use_rate_topology_list, NE_edge_dict, day):
    deputy_link_list = topology_link.deputy_link_list
    # 不考虑优化两端的节点，只考虑中间节点
    for deputy_link in deputy_link_list:
        # 先去设置中间节点的判断值
        mid_node_list = deputy_link.mid_node_list
        for i in range(len(mid_node_list) - 1, -1, -1):
            # 判断是否可以被删除，放到其他节点
            if check_deputy_is_overload(topology_link, deputy_link, i, NE_edge_dict, day):
                print("check_deputy_is_overload")
                # 遍历其他的链路,寻找合适的链路,然后优化在新链路的那部分，即拆除原有的连接，插入新的链接
                # ！！！！！先不考虑此链路的其他副链路，后续可以增加
                is_delete = search_topology_link(low_use_rate_topology_list, mid_node_list[i], NE_edge_dict,
                                             day)
                # 接着优化在旧链路的那部分，拆除原有的点，将原有点的邻居链接起来
                if is_delete:
                    deputy_link.remove_node(i)

# 优化下挂点
def optimate_hanging_node(topology_link, low_use_rate_topology_list, NE_edge_dict, day):
    hanging_node_list = topology_link.hanging_node_list
    for i in range(len(hanging_node_list) - 1, -1, -1):
        if not hanging_node_list[i].node_A.is_have_hanging_node:
            is_delete = search_topology_link(low_use_rate_topology_list, hanging_node_list[i].node_A, NE_edge_dict,
                                             day)
            if is_delete:
                hanging_node_list.pop(i)
        elif not hanging_node_list[i].node_B.is_have_hanging_node:
            is_delete = search_topology_link(low_use_rate_topology_list, hanging_node_list[i].node_B, NE_edge_dict,
                                             day)
            if is_delete:
                hanging_node_list.pop(i)

'''

# 优化下挂点
def optimate_hanging_node(topology_link_dict, topology_link_id, NE_edge_dict):
    hanging_node_list = topology_link_dict[topology_link_id].hanging_node_list
    for couple in hanging_node_list[::-1]:
        if not couple.node_A.is_have_hanging_node:
            is_delete = search_topology_link(topology_link_dict, topology_link_id, couple.node_A, NE_edge_dict, "hanging_node")
            if is_delete:
                hanging_node_list.remove(couple)
        elif not couple.node_B.is_have_hanging_node:
            is_delete = search_topology_link(topology_link_dict, topology_link_id, couple.node_B, NE_edge_dict, "hanging_node")
            if is_delete:
                hanging_node_list.remove(couple)
'''


# 计算两个点之间的距离
def get_two_node_distance(node_A, node_B):
    if node_A.longitude == 0.0 or node_A.lantitude == 0.0 or node_B.longitude == 0.0 or node_B.lantitude == 0.0:
        return 1000
    if node_A.lantitude == node_B.lantitude and node_A.longitude == node_B.longitude:
        return 0
    distance = get_distance_hav(node_A.lantitude, node_A.longitude, node_B.lantitude, node_B.longitude)
    return distance



# 检查这个高流量点是否可删
def check_main_is_overload(topology_link, i, NE_edge_dict, day):
    day = day - 21
    link = topology_link.main_link
    # 得到在path中的位置
    path_node_list = link.get_path()
    node = link.mid_node_list[i]
    position_of_path = i + 1
    # print("path_node_list:"+str(len(path_node_list)))
    # print("NE_list:" + str(len(link.NE_list)))
    # print("position_of_path:"+str(position_of_path))
    # print("i+1:" + str(i+1))

    # 如果这个点的两个边已经动过了，则不要再动移动
    '''
    if node.NodeID == 2101902:
        for path_node in path_node_list:
            print(str(path_node.NodeID))
        for ne_edge in link.NE_list:
            print(str(ne_edge.node_A.NodeID) +":"+str(ne_edge.node_B.NodeID))
        print(str(link.NE_list[i].node_A.NodeID)+":"+str(link.NE_list[i].node_B.NodeID))
        print(str(link.NE_list[i + 1].node_A.NodeID)+":"+str(link.NE_list[i + 1].node_B.NodeID))
    '''
    result = 0
    # 可以删除的基本条件为，不属于最大A的那个点，依然不满足处于那个u值区间
    max_u = topology_link.u * 1.2
    # print("max_u:"+str(max_u))
    may_use_rate = (topology_link.get_total_flow(day) - path_node_list[position_of_path].judge_A[day]) / (topology_link.max_A_node.A * 1000)
    # print("topology_id:"+str(topology_link.topology_link_id)+"may_use_rate:"+str(may_use_rate))
    '''
    if path_node_list[position_of_path] != topology_link.max_A_node:
        result += 1
    else:
        return False
    if may_use_rate > max_u:
        result += 1
    else:
        return False
    '''
    distance_A_B = get_two_node_distance(path_node_list[position_of_path - 1], path_node_list[position_of_path + 1])
    print("main_yes-1")
    if not node.is_have_hanging_node:
        result += 1
    else:
        return False
    if not node.is_deputy_head:
        result += 1
    else:
        return False
    print("main_yes0")
    if not node.isOptimated:
        result += 1
    else:
        return False
    print("main_yes1")
    if link.NE_list[i].A != -1 and link.NE_list[i + 1].A != -1:
        result += 1
    else:
        return False
    print("main_yes2")
    # 还有一个条件，删除这个点以后，链路还有至少一个中间节点
    if len(path_node_list) >= 4:
        result += 1
    else:
        return False
    print("main_yes3")
    if get_NE_from_couple_dict(NE_edge_dict, path_node_list[position_of_path - 1], path_node_list[position_of_path + 1]) != -1:
        return True
    elif distance_A_B < 495:
        return True
    return False

# 检查这个高流量点是否可删
def check_deputy_is_overload(topology_link, deputy_link, i, NE_edge_dict, day):
    day = day - 21
    # 得到在path中的位置
    path_node_list = deputy_link.get_path()
    node = deputy_link.mid_node_list[i]
    position_of_path = i + 1
    distance_A_B = get_two_node_distance(path_node_list[position_of_path - 1], path_node_list[position_of_path + 1])
    # print("path_node_list:"+str(len(path_node_list)))
    # print("NE_list:" + str(len(link.NE_list)))
    # print("position_of_path:"+str(position_of_path))
    # print("i+1:" + str(i+1))

    # 如果这个点的两个边已经动过了，则不要再动移动
    '''
    if node.NodeID == 2101902:
        for path_node in path_node_list:
            print(str(path_node.NodeID))
        for ne_edge in link.NE_list:
            print(str(ne_edge.node_A.NodeID) +":"+str(ne_edge.node_B.NodeID))
        print(str(link.NE_list[i].node_A.NodeID)+":"+str(link.NE_list[i].node_B.NodeID))
        print(str(link.NE_list[i + 1].node_A.NodeID)+":"+str(link.NE_list[i + 1].node_B.NodeID))
    '''
    result = 0
    # 可以删除的基本条件为，不属于最大A的那个点，依然不满足处于那个u值区间
    # max_u = topology_link.u * 1.2
    # print("max_u:"+str(max_u))
    # may_use_rate = (topology_link.get_total_flow(day) - path_node_list[position_of_path].judge_A[day]) / (topology_link.max_A_node.A * 1000)
    # print("topology_id:"+str(topology_link.topology_link_id)+"may_use_rate:"+str(may_use_rate))
    '''
    if may_use_rate > max_u:
        result += 1
    else:
        return False
    '''
    print("deputy_yes0")
    if not node.is_have_hanging_node:
        result += 1
    else:
        return False
    print("deputy_yes1")
    if not node.isOptimated:
        result += 1
    else:
        return False
    print("deputy_yes2")
    '''
    if deputy_link.NE_list[i].A != -1 and deputy_link.NE_list[i + 1].A != -1:
        result += 1
    else:
        return False
    '''
    # 还有一个条件，删除这个点以后，链路还有至少一个中间节点
    if len(path_node_list) >= 4:
        result += 1
    else:
        return False
    print("deputy_yes3")
    if get_NE_from_couple_dict(NE_edge_dict, path_node_list[position_of_path - 1], path_node_list[position_of_path + 1]) != -1:
        return True
    elif distance_A_B < 499:
        return True
    return False

def search_topology_dict(topology_link_list, node, NE_edge_dict):
    for topology_link in topology_link_list:
        # 得到链路的节点个数
        link_node_number = topology_link.get_topology_node_num()

        # 找主链路
        main_link_NE_list = topology_link.main_link.NE_list
        # 主链路两个端点的A值进行获取
        main_link_node_A_A = topology_link.main_link.node_A.A
        main_link_node_B_A = topology_link.main_link.node_B.A
        for i in range(0, len(main_link_NE_list)):
            main_link_NE = main_link_NE_list[i]
            # 判断这个点是否可以加入这个主链路
            # print("why")
            if check_hanging_node(topology_link, NE_edge_dict, main_link_NE, node, main_link_node_A_A, main_link_node_B_A,
                          link_node_number):
                # 插入到主链路中去
                print("插入主链路" + str(node.NodeID) + "插入到点：" + str(main_link_NE.node_A.NodeID) + "和点：" + str(
                    main_link_NE.node_B.NodeID) + "之间")
                topology_link.main_link.insert_node(node, i)
                return True
    return False

# 搜寻所有的链路字典，找到符合条件的链路，然后进行优化
def search_topology_link(low_use_rate_topology_list, node, NE_edge_dict, day):
    for topology_link in low_use_rate_topology_list:
        # 得到链路的节点个数
        link_node_number = topology_link.get_topology_node_num()

        # 找主链路
        main_link_NE_list = topology_link.main_link.NE_list
        # 主链路两个端点的A值进行获取
        main_link_node_A_A = topology_link.main_link.node_A.A
        main_link_node_B_A = topology_link.main_link.node_B.A
        for i in range(0, len(main_link_NE_list)):
            main_link_NE = main_link_NE_list[i]
            # 判断这个点是否可以加入这个主链路
            if check_main(topology_link, NE_edge_dict, main_link_NE, node, main_link_node_A_A, main_link_node_B_A, link_node_number, day):
                # 插入到主链路中去
                print("插入主链路"+str(node.NodeID)+"插入到点："+str(main_link_NE.node_A.NodeID)+"和点："+str(main_link_NE.node_B.NodeID)+"之间")
                if node.type == 'J':
                    print("J_insert:"+str(node.NodeID))
                topology_link.main_link.insert_node(node, i)
                return True
    return False







# 取绝对值
def get_abs(number):
    if number >= 0:
        number = number
    else:
        number = -number
    return number

# 判断这个点是否可以加入这个主链路
def check_main(topology_link, NE_edge_dict, main_link_NE, node, node_A_A, node_B_A, main_link_node_number, day):
    day = day - 21
    '''
    条件有：点juedgeA值小于等于这个边的A值；点与这个边的两端距离要小于等于500；符合主链路的要求，即如果有一个点是J点，则加入点保证是J点,A值必须一致
    然后就是如果两个点是G/H，则这个点不能是J点，A值必须小于等于两端的A值,最后必须满足的一个条件就是在增加这个点之后如果链路的节点数目大于30则不能增加
    '''
    # 可以增加的基本条件为，容载量不大于最大A的那个点，依然不满足处于那个u值区间
    min_u = topology_link.u * 0.8
    may_use_rate = (topology_link.get_total_flow(day) + node.judge_A[day]) / (
                topology_link.max_A_node.A * 1000)
    # print("check_main min_u:" + str(min_u))
    # print("check_main topology_id:" + str(topology_link.topology_link_id) + "may_use_rate:" + str(may_use_rate))
    # 得到这个边的两个端点
    node_A = main_link_NE.node_A
    node_B = main_link_NE.node_B
    # 计算与这两个点的距离
    distance_of_A = get_two_node_distance(node, node_A)
    distance_of_B = get_two_node_distance(node, node_B)

    couple_A = get_NE_from_couple_dict(NE_edge_dict, node, node_A)
    couple_B = get_NE_from_couple_dict(NE_edge_dict, node, node_B)
    result = 0
    '''
    if node.A < topology_link.max_A_node.A:
        result += 1
    else:
        return False
    
    if may_use_rate < min_u:
        result += 1
    else:
        return False
    '''
    # 如果是新边，则不要加
    if couple_A != -1:
        result += 1
    elif distance_of_A <= 499:
        result += 1
    else:
        return False
    if couple_B != -1:
        result += 1
    elif distance_of_B <= 499:
        result += 1
    else:
        return False
    print("yes3")
    if node_A.type != 'J' and node_B.type != 'J':
        if node.type == 'H' and node.A <= node_A_A and node.A <= node_B_A:
            result += 1
        else:
            return False
    print("yes4:"+node_A.type + node_B.type)
    if node_A.type == 'J' or node_B.type == 'J':
        if node.type == 'J':
            if node_A.type == 'J' and node_A.A == node.A:
                result += 1
            elif node_B.type == 'J' and node_B.A == node.A:
                result += 1
            else:
                return False
        else:
            return False
    print("yes4:" + node_A.type + node_B.type)
    if main_link_node_number < 30:
        result += 1
    else:
        return False
    print("yes5")

    if result == 4:
        return True
    else:
        return False

def check_hanging_node(topology_link, NE_edge_dict, main_link_NE, node, node_A_A, node_B_A, main_link_node_number):
    node_A = main_link_NE.node_A
    node_B = main_link_NE.node_B
    # 计算与这两个点的距离
    distance_of_A = get_two_node_distance(node, node_A)
    distance_of_B = get_two_node_distance(node, node_B)

    couple_A = get_NE_from_couple_dict(NE_edge_dict, node, node_A)
    couple_B = get_NE_from_couple_dict(NE_edge_dict, node, node_B)
    result = 0
    '''
    if node.A < topology_link.max_A_node.A:
        result += 1
    else:
        return False

    if may_use_rate < min_u:
        result += 1
    else:
        return False
    '''
    # print("yes1")
    if couple_A != -1:
        result += 1
    elif distance_of_A <= 499:
        result += 1
    else:
        return False
    # print("yes2")
    if couple_B != -1:
        result += 1
    elif distance_of_B <= 499:
        result += 1
    else:
        return False
    # print("yes3")
    if node_A.type != 'J' and node_B.type != 'J':
        if node.type == 'H' and node.A <= node_A_A and node.A <= node_B_A:
            result += 1
        else:
            return False
    # print("yes4:" + node_A.type + node_B.type)
    if node_A.type == 'J' or node_B.type == 'J':
        if node.type == 'J':
            if node_A.type == 'J' and node_A.A == node.A:
                result += 1
            elif node_B.type == 'J' and node_B.A == node.A:
                result += 1
            else:
                return False
        else:
            return False
    # print("yes4:" + node_A.type + node_B.type)
    if main_link_node_number < 30:
        result += 1
    else:
        return False
    print("yes5")

    if result == 4:
        return True
    else:
        return False
'''
# 判断这个点是否可以加入这个主链路
def check_deputy(NE_edge_dict, deputy_link_NE, node, deputy_link_node_A_A, deputy_link_node_B_A, link_node_number):
    
    条件有：点juedgeA值小于等于这个边的A值；点与这个边的两端距离要小于等于500；符合副链路的要求，加入点保证是J点,A值必须一致
    最后必须满足的一个条件就是在增加这个点之后如果链路的节点数目大于30则不能增加
    
    # 得到这个边的两个端点
    node_A = deputy_link_NE.node_A
    node_B = deputy_link_NE.node_B
    key_A = get_NE_from_couple_dict(NE_edge_dict, node_A, node)
    key_B = get_NE_from_couple_dict(NE_edge_dict, node_B, node)
    # 计算与这两个点的距离
    distance_of_A = get_two_node_distance(node, node_A)
    distance_of_B = get_two_node_distance(node, node_B)

    result = 0
    # 如果是新边，则不要加
    if deputy_link_NE.A != -1:
        result += 1
    else:
        return False
    if node.A <= deputy_link_NE.A:
        result += 1
    else:
        return False
    # 如果原来两个点之间距离大于1000则肯定不可能
    if key_A != -1:
        result += 1
    elif distance_of_A <= 490:
        result += 1
    else:
        return False
    if key_B != -1:
        result += 1
    elif distance_of_B <= 490:
        result += 1
    else:
        return False
    if node_A.type != 'J' and node_B.type != 'J':
        return False
    if node_A.type == 'J' or node_B.type == 'J':
        if node.type == 'J':
            if node.A <= deputy_link_node_A_A and node.A <= deputy_link_node_B_A:
                result += 1
            else:
                return False
        else:
            return False

    if link_node_number < 29:
        result += 1
    else:
        return False

    if result == 6:
        return True
    else:
        return False
'''






def get_NE_from_couple_dict(NE_edge_dict, node_A, node_B):
    for key in NE_edge_dict.keys():
        if NE_edge_dict[key].is_couple(node_A, node_B):
            return key
    return -1
