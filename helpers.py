from apollon import tools
from apollon.som import utilities, topologies
import matplotlib.pyplot as plt
from matplotlib import ticker
import numpy as np
from sklearn.decomposition import PCA


def init_pca(som, train_data):
    pca = PCA(2)
    pca.fit(train_data)
    for i in range(som.dx):
        for j in range(som.dy):
            som.weights[i*som.dy+j] = pca.components_[0] * i + pca.components_[1] * j


def match_counts(som, bmu_xy_w, meta):
    counts = {}
    for idx, bxy in enumerate(zip(*bmu_xy_w)):
        try:
            counts[bxy].append(meta.index[idx])
        except KeyError:
            counts[bxy] = [meta.index[idx]]
    return counts


def plot_counts(ax, counts, color='k'):
    for (x, y), vals in counts.items():
        ax.text(y-.35, x+.2, len(vals), fontdict={'color':color})


def plot_feature_importance(ax, xy, mfd, weights, shape):
    c = plt.cm.tab20(range(weights.shape[1]))
    idx = np.ravel_multi_index(xy[::-1], shape)
    ax.scatter(mfd[idx], weights[idx], c=c)
    ax.set_title('Unit ({}, {})'.format(*xy))


def plot_total_importance(axs, mfd, weights):
    axs = np.flipud(axs)
    c = plt.cm.tab20(range(weights.shape[1]))
    for ax, m, w in zip(axs.flatten(), mfd, weights):
        ax.scatter(m, w, c=c)


def plot_umatrix(ax, um):
    style = {'origin':'lower', 'cmap':'terrain', 'alpha':.8,
             'interpolation':'None', 'zorder':0}
    ax.set_title('u-matrix');
    xtl = ticker.MultipleLocator(1)
    ytl = ticker.MultipleLocator(1)
    ax.xaxis.set_major_locator(xtl)
    ax.yaxis.set_major_locator(ytl)
    ax.imshow(um, **style)


def plot_dominant_feat(ax, dfeat):
    style = {'origin':'lower', 'aspect':'auto', 'alpha':.8, 'zorder':0}
    ax.set_title('Dominant Feature');
    xtl = ticker.MultipleLocator(1)
    ytl = ticker.MultipleLocator(1)
    ax.xaxis.set_major_locator(xtl)
    ax.yaxis.set_major_locator(ytl)
    ax.imshow(dfeat, **style)


def plot_component(ax, som, num, name=None, cmap='inferno'):
    style = {'origin': 'lower', 'aspect': 'auto', 'cmap': cmap}
    ax.set_title('Component plane: {}'.format(name if name else num))
    xtl = ticker.MultipleLocator(1)
    ytl = ticker.MultipleLocator(1)
    ax.xaxis.set_major_locator(xtl)
    ax.yaxis.set_major_locator(ytl)
    ax.imshow(som.weights[:, num].reshape(som.shape), **style)


def plot_ethnic_group_marker(ax, px, py, target, marker_dict, groups=None, color=None):
    if groups is None:
        groups = np.unique(target)

    if isinstance(ax, np.ndarray) and ax.ndim == 2:
        axs = np.flipud(ax)
        for x, y, t in zip(px, py, target):
            if t in groups:
                axs[y, x].scatter(.8, .8, s=300, color=color, marker=marker_dict[t])
    else:
        for gr in groups:
            select = target == gr
            ax.scatter(px[select], py[select], s=150, c=color, marker=marker_dict[gr])


def unit_info(x, y, cc, meta):
    tmp = '{:<10}{:40}{:20}{:20}{:15}'
    print('--- Unit ({}, {}) ---\n'.format(x, y))
    try:
        ids = cc[(y, x)]
    except KeyError:
        print('\t* No entries.')
        return
    print(tmp.format('Index', 'Title', 'Ethnic Group', 'Style', 'Country'), '-'*115, '\n')
    for idx in ids:
        record = meta.loc[idx]
        print(tmp.format(idx, record.title, record.ethnic_group, record.style, record.country), end='\n\n')


def plot_marker_legend(etgr_marker):
    fig, ax = plt.subplots(1, figsize=(9, 10))
    for i, (etgr, sym) in enumerate(etgr_marker.items()):
        if i < 9:
            tx = -0.01
            sx = 0
        else:
            tx = 0.015
            sx = 0.025
        ax.text(tx, -(i%9)*10, etgr, {'fontsize':15}, ha='left', va='center')
        ax.scatter(sx, -(i%9)*10, s=100, c='k', marker=sym)
    ax.set_axis_off()


def mean_feat_dist(weights, dxy):
    out = np.zeros_like(weights)
    for i, mi in enumerate(np.ndindex(dxy)):
        nh_flat_idx = topologies.vn_neighbourhood(*mi, *dxy, flat=True)

        out[i] = np.mean(weights[nh_flat_idx] - weights[i], axis=0)
    return out

