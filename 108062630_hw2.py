from sys import argv
import itertools

FP = []



class Header_table_raw():
    def __init__(self, item, frequency):
        self.item = item
        self.frequency = frequency
        

        
class Node():
    def __init__(self, item):
        self.item = item
        self.value = 1
        self.children = []
        self.parent = None
        
        
    def add_child(self,child):
        self.children.append(child)
        
    def have_child(self,search_item):
        ans = False
        next_node = None
        
        for c in self.children:
            if c.item == search_item:
                ans = True
                next_node = c
                break
                
        return ans,next_node
    
    def add_value(self):
        self.value = self.value + 1
        
    def add_parent(self,parent_node):
        self.parent = parent_node
        



def make_header(min_support,db):
    
    #header table dictionary
    ht_dic = {}                                
    
    for tx in db:
        for item in tx:
            if item in ht_dic:
                ht_dic[item] = ht_dic[item]+1
            else:
                ht_dic[item] = 1
                
    
    ht=[]
    for key in ht_dic:
        
        if ht_dic[key] >= min_support:
            a=Header_table_raw(key,ht_dic[key])
            ht.append(a)
            
    
    
    ht.sort(key = lambda x: x.frequency,reverse=True)
    
    return ht
        
        
        
        
        
def scan_db_again(ht,db):
    
    order_item=[a.item for a in ht]
    
    for i, s in enumerate (db):
        temp = []
        
        for j in order_item:
            if (j in s):
                temp.append(j)
        
        db[i] = temp
        
        
    db_temp = [x for x in db if x != []]
                
    db = db_temp

    return db
               
    
    
def generate_tree(db,ht):
    
    root = Node("root")

    node_map ={}

    for s in ht:
        node_map[s.item]=[]
    
    for items in db:
        current_node = root
        
        for item in items:
            exist_child, child_node = current_node.have_child(item)
            if exist_child:
                current_node = child_node
                current_node.add_value()
            else:
                new_child = Node(item)
                node_map[item].append (new_child)
                new_child.add_parent(current_node)
                current_node.add_child(new_child)
                current_node = new_child
 

    #tree_travese(root)

    return root, node_map

            
            
def mining_tree(root,min_support, node_map, suffix, ht, accumulate_suffix=[] ):  

    
    global FP
    
    frequent_map = {}
    condition_base = []
    item_frequent_map = {}
    #get condition base amd frequent
    
    for node in node_map[suffix]:
        
        path = trace_back(node)
        
        for i in range (node.value):
            condition_base.append(path)
        
        for item in path:
            if item in item_frequent_map:
                item_frequent_map[item] = item_frequent_map[item] + node.value
            
            else:
                item_frequent_map[item] = node.value


    if all(x == condition_base[0] for x in condition_base):
        if len(condition_base) > 0:
            for i in range(1, len(condition_base[0]) + 1):  
                for subset in itertools.combinations(condition_base[0], i):
                    subset_list = [x for x in subset]
                    mass_list = subset_list + [suffix] + accumulate_suffix 
                    sorted_list = sorted(mass_list)
                    FP.append([sorted_list,len(condition_base)])       

    else:
        
        delete_list = []

        for key in item_frequent_map:

            if item_frequent_map[key] < min_support:

                delete_list.append(key)

        for delete_item in delete_list:
            item_frequent_map.pop(delete_item)

            for s in condition_base :
                if delete_item in s:
                    s.remove(delete_item)
                    
                    
        for key in item_frequent_map :
                mass_list = [key] + [suffix] + accumulate_suffix 
                sorted_list = sorted(mass_list)
                FP.append([sorted_list,item_frequent_map[key]])
        
        
        
        sub_ht = make_header(min_support,condition_base)
        
        sub_tree_root , sub_node_map = generate_tree(condition_base, sub_ht )

        for new_suffix_row in reversed (sub_ht):
            mining_tree(sub_tree_root, min_support, sub_node_map, new_suffix_row.item, sub_ht, [suffix] + accumulate_suffix)

    
            
            
def trace_back(node):
    
    path = []
    current_node = node.parent
    while(current_node.item != "root"):
        path.insert(0,current_node.item)
        current_node = current_node.parent

    return path
        


            
def main(min_support,input_file,output_file):
    
    global FP

    fi = open(input_file,'r')
    fo = open(output_file,'w+')
    support = float(min_support)   
    support = float(min_support)   
   
    db =[]
    tx = fi.readline().strip('\n')
    while(tx):
        db.append(tx)
        tx=fi.readline().strip('\n')

    min_support = len(db)*support
    
    for i, s in enumerate (db):
        db[i] = [int(x) for x in s.split(',')]
    

    ht = make_header(min_support,db)
    
    for i in ht:
        FP.append([[i.item],i.frequency])
    
    db = scan_db_again(ht,db)
    
    
    tree_root , node_map = generate_tree(db,ht)
    
    for ht_row in reversed(ht):
        mining_tree(tree_root, min_support, node_map, ht_row.item, ht ,[] )
        
    FP.sort()
    FP.sort(key = lambda x:len(x[0]))
    
    for s in FP:
        FP_key = ','.join(map(str,s[0]))
        number = format(round(s[1]/len(db),4), '.4f')
        line =FP_key+':'+number
        fo.writelines([line + '\n'])
        
        
    fi.close()
    fo.close()

        
if __name__ == "__main__":  
   main(argv[1],argv[2], argv[3])