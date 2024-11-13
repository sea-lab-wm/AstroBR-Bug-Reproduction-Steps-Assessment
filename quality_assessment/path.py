from collections import deque

class Path:
    def path(self, v, parent, graph):
        q = deque()
        q.append(v)
        node_visited = set()

        while q:
            node = q.popleft()
            for neighbour in graph[node]:
                if neighbour not in node_visited:
                    parent[neighbour] = node
                    q.append(neighbour)
                    node_visited.add(neighbour)

    def get_key_from_value(self, dict, value):
        key = list(filter(lambda x: dict[x]==value, dict))[0]
        return key
    
    def get_value_from_key(self, dict, key):
        return dict[key]

    def get_transition(self, df, u, v, screen_Dict):
        start = self.get_key_from_value(screen_Dict, u)
        end = self.get_key_from_value(screen_Dict, v)
        if not df['start'].isin([start]).any():
            print(f'Transition Start: {start} does not exist in dataframe')
        if not df['end'].isin([end]).any():
            print(f'Transition End: {end} does not exist in dataframe')
        comp_info = df.loc[(df['start']==start) & (df['end']==end), ["transition"]].values.tolist()
        return comp_info[0][0]
    
    def get_next_state(self, df, u, transition, screen_Dict):
        start = self.get_key_from_value(screen_Dict, u)
        if not df['start'].isin([start]).any():
            print(f'State Start: {start} does not exist in dataframe')
        if not df['transition'].isin([transition]).any():
            print(f'State Transtion: {transition} does not exist in dataframe')
        comp_info = df.loc[(df['start']==start) & (df['transition']==transition), ["end"]].values.tolist()
        return self.get_value_from_key(screen_Dict, comp_info[0][0])
    
    def get_node_shortest_path_util(self, S, D, parent, screen_Dict, transition_df):
        path = []
        if S==D:
            return path
        parent_visited = set()

        current_node = D
        parent_visited.add(current_node)

        while (parent[current_node])!=-1 and parent[current_node] not in parent_visited:
            path.append(current_node)
            current_node = parent[current_node]
            parent_visited.add(current_node)
            if current_node == S:
                break

        if current_node!=S:
            return []
        return list(reversed(path)) 
    
    def get_node_shortest_path(self, S, S_interacted, D, D_interacted, parent, screen_Dict, transition_df, graph):
        path = []
        start_next_state = self.get_next_state(transition_df, S, S_interacted, screen_Dict)

        if S==D:
            path.append(S)
            return path

        if start_next_state==D:
            path.append(S)
            path.append(D)
            return path

        shortest_path = self.get_node_shortest_path_util(start_next_state, D, parent, screen_Dict, transition_df)

        if len(shortest_path)>0:
            path.append(S)
            path.extend(shortest_path)
            return path
        else:
            temp_parent = [-1] * len(transition_df)
            self.path(start_next_state, temp_parent, graph)
            alternate_shortest_path = self.get_node_shortest_path_util(start_next_state, D, temp_parent, screen_Dict, transition_df)
            if len(alternate_shortest_path)>0:
                path.append(S)
                path.extend(alternate_shortest_path)
                return path

        return []

    # S and D are a sequential number, and S_interacted and D_interacted are transition ids
    def get_shortest_path_util(self, S, D, parent, screen_Dict, transition_df):
        path = []
        if S==D:
            return path
        parent_visited = set()

        current_node = D
        parent_visited.add(current_node)
        while (parent[current_node])!=-1 and parent[current_node] not in parent_visited:
            cur_transition_interacted = self.get_transition(transition_df, parent[current_node], current_node, screen_Dict)
            path.append(cur_transition_interacted)
            current_node = parent[current_node]
            parent_visited.add(current_node)
            if current_node == S:
                break

        if current_node!=S:
            return []
        return list(reversed(path)) 
    
    def get_shortest_path(self, S, S_interacted, D, D_interacted, parent, screen_Dict, transition_df, graph):
        path = []

        # if S==0:
        #     print("0")

        start_next_state = self.get_next_state(transition_df, S, S_interacted, screen_Dict)

        if S==D and start_next_state==S:
            path.append(S_interacted)
            path.append(D_interacted)
            return path

        if start_next_state==D:
            path.append(S_interacted)
            path.append(D_interacted)
            return path

        shortest_path = self.get_shortest_path_util(start_next_state, D, parent, screen_Dict, transition_df)

        if len(shortest_path)>0:
            path.append(S_interacted)
            path.extend(shortest_path)
            path.append(D_interacted)
            return path
        else:
            temp_parent = [-1] * len(transition_df)
            self.path(start_next_state, temp_parent, graph)
            alternate_shortest_path = self.get_shortest_path_util(start_next_state, D, temp_parent, screen_Dict, transition_df)
            if len(alternate_shortest_path)>0:
                path.append(S_interacted)
                path.extend(alternate_shortest_path)
                path.append(D_interacted)
                return path

        return []       

