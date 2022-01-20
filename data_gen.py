import igraph
import networkx as nx
import grinpy
import math
import contextlib
import os

os.chdir("/home/marc/OneDrive/Dades - UPC/Q5/AA2/Projecte/Coloring/")

OBS_BIN = 30
NMIN, NMAX = 6, 14

def isomorphic(g, lst):
    ''' Given a list of graphs lst, checks if graph g is isomorphic to any of them.
        g: an igraph object instance.
        lst: a list of igraph objects.

        return:
        boolean indicating if an isomorphism exists
    '''
    for i in lst:
        if(g.isomorphic(i)):
            return True
    return False


def generate_dataset(obs_bin, nmin, nmax, ps, cs, amount, method, show=False):
    ''' Generate dataset with the defined parameters.
        nreps: number of graphs of a same kind.
        nmin, nmax: generate graphs with number of nodes nmin <= n <= nmax
        ps: iterable with the different probabilities p.
        cs: iterable with different integer parameters (for WS and BA).
        amount: dictionary with the current graphs created
                (example: amount = {3: [], 4: [], 5: [], 6: [], 7: []})
        method: string indicating the method to generate the graphs:
                ER: Erdos-Renyi
                WS: Watts-Strogatz
                BA: Barabasi-Albert


        return:
        saves graphs in ./graph_data/id.GraphML
        and labels in .data.csv
        returns new amount (with new graphs)
    '''
    count = 0
    data = []

    total_obs = 4*obs_bin
    prev_obs = len(amount[3])

    while count < total_obs:
        for n in range(nmin, nmax+1):
            for c in cs:
                for p in ps:

                    if method=="ER":
                        g=igraph.Graph.Erdos_Renyi(n, p)
                    elif method=="WS":
                        g=igraph.Graph.Watts_Strogatz(1,n,c,p)
                    else:
                        g=igraph.Graph.Barabasi(n,c)

                    g_nx=g.to_networkx()
                    chromatic_number = grinpy.chromatic_number(g_nx, method="ilp")

                    # Store graph if it satisfies conditions
                    if chromatic_number >= 3 and chromatic_number <= 7 and \
                    len(amount[chromatic_number])-prev_obs < obs_bin and not \
                    isomorphic(g, amount[chromatic_number]) and not \
                    math.isnan(g.average_path_length()):

                        d=nx.coloring.greedy_color(g_nx)
                        greedy_chromatic=max(d.values())+1

                        if chromatic_number == 7:
                            total_obs += 1

                        id = '{0:04d}'.format(count)
                        g.write_graphml('graph_data/'+method+'_'+id+'.GraphML')
                        data.append([id, n, p, chromatic_number, greedy_chromatic, method])
                        print(data[-1])

                        count += 1

                        amount[chromatic_number].append(g)

                    if show == True:
                        draw_colored_graph(g, id=id)

    with open('data.csv', 'a') as f:
        for id, n, p, k, greed, met in data:
            f.write('{};{};{};{};{};{}\n'.format(id, n, p, k, greed, met))
    return amount

with open('data.csv', 'w') as f:
    f.write('id;n;p;chromatic;greedy;method\n')

amount = {3: [], 4: [], 5: [], 6: [], 7: []}

#Barabasi-Albert
PS = [1]
CS = [1,2,3,4,5]
amount = generate_dataset(OBS_BIN, NMIN, NMAX, PS, CS, amount, "BA")

#Erdos-Renyi
PS = [0.35, 0.4, 0.45, 0.5, 0.55, 0.6]
CS = [1]
amount = generate_dataset(OBS_BIN, NMIN, NMAX, PS, CS, amount, "ER")

#Watts-Strogatz
PS = [0.1, 0.2, 0.3, 0.4, 0.5]
CS = [1,2,3]
amount = generate_dataset(OBS_BIN, NMIN, NMAX, PS, CS, amount, "WS")
