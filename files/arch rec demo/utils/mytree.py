import anytree
from anytree import Node


class FileTreeFolderNode:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.subfolder_name2node = {}
        self.files = set()
        
        self.is_module = None
        self.submodule_info = None
        self.module_name = None
        self.module_summary = None
        
    
    def get_full_path(self):
        if self.parent == None:
            return self.name
        else:
            n = self.parent.get_full_path() + '/' + self.name
            return n.strip('/')
    
    def get_sorted_files(self):
        return sorted([f for f in self.files], key=lambda x:x.name)
    
    def get_file(self, name):
        for f in self.files:
            if f.name == name:
                return f
        return None
    
    def get_all_sub_files(self):
        all_files = []
        for f in self.files:
            all_files.append(f)
        for subfolder in self.subfolder_name2node.values():
            all_files.extend(subfolder.get_all_sub_files())
        return all_files
    
    def add_child(self, name, is_file=False):
        if is_file:
            node = FileTreeFileNode(name, self)
            self.files.add(node)
        else:
            node = FileTreeFolderNode(name, self)
            self.subfolder_name2node[name] = node

    def remove_folder(self, name):
        n = self.subfolder_name2node[name]
        del self.subfolder_name2node[name]
        return n

class FileTreeFileNode:
    def __init__(self, name, folder):
        self.name = name
        self.folder = folder
        self.summary = None
        
    def get_full_path(self):
        return (self.folder.get_full_path() + '/' + self.name).strip('/')
            
class FileTree:
    def __init__(self, paths):
        root = FileTreeFolderNode('')
        for p in paths:
            path_parts = p.split('/')
            curr_node = root
            for part in path_parts[:-1]:
                if part not in curr_node.subfolder_name2node:
                    curr_node.add_child(part, is_file=False)
                curr_node = curr_node.subfolder_name2node[part]
            curr_node.add_child(path_parts[-1], is_file=True)
        self.root = root        
        self.submodule2parent_folder = {}
    
    def dfs(self):
        # yield all folder nodes - LRD
        def _dfs(node):
            for subfolder in node.subfolder_name2node.values():
                yield from _dfs(subfolder)
            yield node
        yield from _dfs(self.root)
    
    def dfs_preorder(self):
        # yield all folder nodes - DLR
        def _dfs(node):
            yield node
            for subfolder in node.subfolder_name2node.values():
                yield from _dfs(subfolder)
        yield from _dfs(self.root)
           
    def get_folder(self, path):
        path_parts = path.split('/')
        curr_node = self.root
        for part in path_parts:
            if part not in curr_node.subfolder_name2node:
                return None
            curr_node = curr_node.subfolder_name2node[part]
        return curr_node

class ModuleNode(Node):
    def __init__(self, name, parent=None, children=None, **kwargs):
        super().__init__(name, parent, children, **kwargs)
        # self.is_module = True
        self.summary = kwargs.get('summary', None)
        self.files = kwargs.get('files', [])
        
    def add_file(self, file_node):
        self.files.append(file_node)
        
    def get_partition(self):
        result = []
        for module in anytree.PreOrderIter(self):
            if module.files:
                result.append(module.files)
        return result

    def get_result(self):
        partition = self.get_partition()
        result = {}
        for i, files in enumerate(partition):
            for f in files:
                result[f.get_full_path()] = i
        return result

    def get_lv1_partition(self):
        result = []
        for module in self.children:
            result.append(module.get_all_sub_files())
        return result
    
    def get_lv1_result(self):
        partition = self.get_lv1_partition()
        result = {}
        for i, files in enumerate(partition):
            for f in files:
                result[f.get_full_path()] = i
        return result
    
    
    def get_full_path(self):
        if self.parent == None:
            # if self.name == 'root':
            #     return '/'
            return '/'+self.name
        else:
            n = self.parent.get_full_path() + '/' + self.name
            return '/'+n.strip('/')
    
    def get_sorted_files(self):
        return sorted([f for f in self.files], key=lambda x:(x.name+x.get_full_path()))
    
    def get_filenames(self):
        return [f.get_full_path() for f in self.get_sorted_files()]
    
    def get_all_sub_files(self):
        all_files = []
        all_files.extend(self.files)
        for submodule in self.children:
            all_files.extend(submodule.get_all_sub_files())
        all_files = sorted(all_files, key=lambda x:x.get_full_path())
        return all_files
    
    def get_all_sub_filenames(self):
        all_files = self.get_all_sub_files()
        return sorted([f.get_full_path() for f in all_files])
    
    def get_parent_at_depth(self, depth):
        if self.depth < depth:
            raise
        if self.depth == depth:
            return self
        if self.depth > depth:
            return self.parent.get_parent_at_depth(depth)
    
    def hierachical_cluster(self, nx_graph):
        
        file2total_in = {}
        file2total_out = {}
        for src, dst, data in nx_graph.edges(data=True):
            # file2total_out[src] = file2total_out.get(src, 0) + data['total']
            # file2total_in[dst] = file2total_in.get(dst, 0) + data['total']
            file2total_out[src] = file2total_out.get(src, 0) + 1
            file2total_in[dst] = file2total_in.get(dst, 0) + 1
        
        nx_graph_ud = nx_graph.to_undirected(as_view=True)
        
        all_leaf_modules = [n for n in self.descendants if n.is_leaf]
        filename2module = {}
        for module in all_leaf_modules:
            for f in module.files:
                filename2module[f.get_full_path()] = module
        module2module2dep_cnt = {
            m1: {m2:0 for m2 in all_leaf_modules} for m1 in all_leaf_modules
        }
        for src, dst, data in nx_graph.edges(data=True):
            src_module = filename2module[src]
            dst_module = filename2module[dst]
            # cnt = data['total']
            cnt = 1/((file2total_out[src]*file2total_in[dst]))
            module2module2dep_cnt[src_module][dst_module] += cnt
            module2module2dep_cnt[dst_module][src_module] += cnt
            pass
        
        module_pair2dep_cnt = {}
        for m1, m2_dep_cnt in module2module2dep_cnt.items():
            for m2, cnt in m2_dep_cnt.items():
                if m1.name >= m2.name:
                    continue
                if cnt > 0:
                    module_pair2dep_cnt[(m1, m2)] = cnt/(len(m1.files)+len(m2.files))
        module_pair2dep_cnt = {k:v for k, v in sorted(module_pair2dep_cnt.items(), key=lambda x:x[1], reverse=True)}
        for module_a, module_b in module_pair2dep_cnt:
            pass
        pass
    
    def get_file_by_name(self, name):
        for f in self.files:
            if f.get_full_path() == name or f.name == name:
                return f
        return None
    
    def to_dict(self, is_first_call=True):
        if is_first_call:
            return {self.name: {c.name:c.to_dict(is_first_call=False) for c in self.children}}
        if self.is_leaf:
            return [f.get_full_path() for f in self.files]
        return {c.name:c.to_dict(is_first_call=False) for c in self.children}
    
class FileNode(Node):
    def __init__(self, name, parent=None, children=None, **kwargs):
        super().__init__(name, parent, children, **kwargs)
        self.is_module = False
        self.summary = kwargs.get('summary', None)
    pass
