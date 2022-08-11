# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 13:09:19 2017
--- Energy profile diagram---
This is a simple script to plot energy profile diagram using matplotlib.
E|          4__
n|   2__    /  \
e|1__/  \__/5   \
r|  3\__/       6\__
g|
y|
@original author: Giacomo Marchioro
Modified by: Vaidish Sumaria
"""
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib import rc
rc('font',**{'family':'serif','serif':['Helvetica']})
rc('text', usetex=True)

plt.rcParams["font.family"] = "Helvetica"

class ED:
    def __init__(self, aspect='equal'):
        # plot parameters
        self.ratio = 1.
        self.dimension = 'auto'
        self.space = 'auto'
        self.offset = 'auto'
        self.offset_ratio = 0.02
        self.topcolor = []
        self.bottomcolor = []
        self.aspect = aspect
        # data
        self.pos_number = 0
        self.energies = []
        self.positions = []
        self.colors = []
        self.top_texts = []
        self.bottom_texts = []
        self.left_texts = []
        self.right_texts = []
        self.links = []
        self.arrows = []
        self.top_fontsize = []
        self.bottom_fontsize = []
        # matplotlib fiugre handlers
        self.fig = None
        self.ax = None

    def add_level(self, energy, bottom_text='', position=None, color='k',
                  top_text='Energy', right_text='', left_text='', top_fontsize=10, bottom_fontsize=10, top_color='k', bottom_color='k'):
        '''
        Method of ED class
        This method add a new energy level to the plot.
        Parameters
        ----------
        energy : int
                The energy of the level in Kcal mol-1
        bottom_text  : str
                The text on the bottom of the level (label of the level)
                (default '')
        right_text  : str
                The text on the right of the level (default '')
        left_text  : str
                The text on the left of the level (default '')
        position  : str
                The position of the level in the plot. Keep it empty to add
                the level on the right of the previous level use 'last' as
                argument for adding the level to the last position used
                for the level before.
                An integer can be used for adding the level to an arbitrary
                position.
                (default  None)
        color  : str
                Color of the level  (default  'k')
        top_text  : str
                Text on the top of the level. By default it will print the energy of the level. (default  'Energy')
        top_fontsize, bottom_fontsize, top_color, bottom_color : float, float, str, str
                Defines the font size and color of the bottom & top text

        Returns
        -------
        Append to the class data all the informations regarding the level added
        '''

        if position is None:
            position = self.pos_number + 1
            self.pos_number += 1
        elif isinstance(position, (int, float)):
            pass
        elif position == 'last' or position == 'l':
            position = self.pos_number
        else:
            raise ValueError(
                "Position must be None or 'last' (abrv. 'l') or in case an integer or float specifing the position. It was: %s" % position)
        if top_text == 'Energy':
            top_text = energy

        link = []
        self.colors.append(color)
        self.energies.append(energy)
        self.positions.append(position)
        self.top_texts.append(top_text)
        self.bottom_texts.append(bottom_text)
        self.left_texts.append(left_text)
        self.right_texts.append(right_text)
        self.links.append(link)
        self.arrows.append([])
        self.top_fontsize.append(top_fontsize)
        self.bottom_fontsize.append(bottom_fontsize)
        self.topcolor.append(top_color)
        self.bottomcolor.append(bottom_color)

    def add_arrow(self, start_level_id, end_level_id):
        '''
        Method of ED class
        Add a arrow between two energy levels using IDs of the level. Use
        self.plot(show_index=True) to show the IDs of the levels.
        Parameters
        ----------
        start_level_id : int
                 Starting level ID
        end_level_id : int
                 Ending level ID
        Returns
        -------
        Append arrow to self.arrows
        '''
        self.arrows[start_level_id].append(end_level_id)

    def add_link(self, start_level_id, end_level_id,
                 color='k',
                 ls='--',
                 linewidth=1,
                 ):
        '''
        Method of ED class
        Add a link between two energy levels using IDs of the level. Use
        self.plot(show_index=True) to show the IDs of the levels.
        Parameters
        ----------
        start_level_id : int
                 Starting level ID
        end_level_id : int
                 Ending level ID
        color : str
                color of the line
        ls : str
                line styple e.g. -- , ..
        linewidth : int
                line width
        Returns
        -------
        Append link to self.links
        '''
        self.links[start_level_id].append((end_level_id, ls, linewidth, color))

    def plot(self, show_IDs=False, ylabel="Energy / $kcal$ $mol^{-1}$", ax: plt.Axes = None, figsize=[6.4, 4.8]):
        '''
        Method of ED class
        Plot the energy diagram. Use show_IDs=True for showing the IDs of the
        energy levels and allowing an easy linking.
        E|          4__
        n|   2__    /  \
        e|1__/  \__/5   \
        r|  3\__/       6\__
        g|
        y|
        Parameters
        ----------
        show_IDs : bool
            show the IDs of the energy levels
        ylabel : str
            The label to use on the left-side axis. "Energy / $kcal$
            $mol^{-1}$" by default.
        ax : plt.Axes
            The axes to plot onto. If not specified, a Figure and Axes will be
            created for you.
        Returns
        -------
        fig (plt.figure) and ax (fig.add_subplot())
        '''


        # Create a figure and axis if the user didn't specify them.
        if not ax:
            fig = plt.figure(figsize=figsize)
            ax = fig.add_subplot(111, aspect=self.aspect)
        # Otherwise register the axes and figure the user passed.
        else:
            self.ax = ax
            self.fig = ax.figure

            # Constrain the target axis to have the proper aspect ratio
            self.ax.set_aspect(self.aspect)

        ax.set_ylabel(ylabel, fontsize=12)
        ax.axes.get_xaxis().set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

        self.__auto_adjust()

        data = list(zip(self.energies,  # 0
                        self.positions,  # 1
                        self.bottom_texts,  # 2
                        self.top_texts,  # 3
                        self.colors,  # 4
                        self.right_texts,  # 5
                        self.left_texts, #6
                        self.top_fontsize, #7
                        self.bottom_fontsize, #8
                        self.topcolor, #9
                        self.bottomcolor,))  #10

        for level in data:
            start = level[1]*(self.dimension+self.space)
            ax.hlines(level[0], start, start + self.dimension, color=level[4])

            #TOP TEXT
            ax.text(x=start+self.dimension/2.,  # X
                    y=level[0]+self.offset,  # Y
                    s=level[3],  # self.top_texts
                    fontsize=level[7],
                    color = level[9],
                    horizontalalignment='center',
                    verticalalignment='bottom')

            #RIGHT TEXT
            ax.text(start + self.dimension,  # X
                    level[0],  # Y
                    level[5],  # self.right_text
                    fontsize=level[7],
                    color = level[9],
                    horizontalalignment='left',
                    verticalalignment='center')

            #LEFT TEXT
            ax.text(start,  # X
                    level[0],  # Y
                    level[6],  # self.left_text
                    fontsize=level[7],
                    color = level[10],
                    horizontalalignment='right',
                    verticalalignment='center')

            #BOTTOM TEXT
            ax.text(start + self.dimension/2.,  # X
                    level[0] - self.offset*2,  # Y
                    level[2],  # self.bottom_text
                    fontsize=level[8],
                    color = level[10],
                    horizontalalignment='center',
                    verticalalignment='top')

        if show_IDs:
            # for showing the ID allowing the user to identify the level
            for ind, level in enumerate(data):
                start = level[1]*(self.dimension+self.space)
                ax.text(start, level[0]+self.offset, str(ind),
                        horizontalalignment='right', color='red')

        for idx, arrow in enumerate(self.arrows):
            # by Kalyan Jyoti Kalita: put arrows between to levels
            # x1, x2   y1, y2
            for i in arrow:
                start = self.positions[idx]*(self.dimension+self.space)
                x1 = start + 0.5*self.dimension
                x2 = start + 0.5*self.dimension
                y1 = self.energies[idx]
                y2 = self.energies[i]
                gap = y1-y2
                gapnew = '{0:.2f}'.format(gap)
                middle = y1-0.5*gap  # warning: this way works for negative HOMO/LUMO energies
                ax.annotate("", xy=(x1, y1), xytext=(x2, middle), arrowprops=dict(
                    color='green', width=2.5, headwidth=5))
                ax.annotate(s=gapnew, xy=(x2, y2), xytext=(x1, middle), color='green', arrowprops=dict(width=2.5, headwidth=5, color='green'),
                            bbox=dict(boxstyle='round', fc='white'),
                            ha='center', va='center')

        for idx, link in enumerate(self.links):
            # here we connect the levels with the links
            # x1, x2   y1, y2
            for i in link:
                # i is a tuple: (end_level_id,ls,linewidth,color)
                start = self.positions[idx]*(self.dimension+self.space)
                x1 = start + self.dimension
                x2 = self.positions[i[0]]*(self.dimension+self.space)
                y1 = self.energies[idx]
                y2 = self.energies[i[0]]
                line = Line2D([x1, x2], [y1, y2],
                              ls=i[1],
                              linewidth=i[2],
                              color=i[3])
                ax.add_line(line)

        return fig,ax

    def __auto_adjust(self):
        '''
        Method of ED class
        This method use the ratio to set the best dimension and space between
        the levels.
        Affects
        -------
        self.dimension
        self.space
        self.offset
        '''
        # Max range between the energy
        Energy_variation = abs(max(self.energies) - min(self.energies))
        if self.dimension == 'auto' or self.space == 'auto':
            # Unique positions of the levels
            unique_positions = float(len(set(self.positions)))
            space_for_level = Energy_variation*self.ratio/unique_positions
            self.dimension = space_for_level*0.7
            self.space = space_for_level*0.3

        if self.offset == 'auto':
            self.offset = Energy_variation*self.offset_ratio


if __name__ == '__main__':
    a = ED()

    a.add_level(0.3,top_text='17', bottom_text='abc', color='darkblue', top_fontsize=15, bottom_fontsize=6, top_color='r', bottom_color='b')
    a.add_level(0.6,top_text='17', bottom_text='abc', color='darkblue', top_fontsize=15, bottom_fontsize=6, top_color='r', bottom_color='b')

    a.add_link(0, 1, color='r')
    a.plot(show_IDs=True)
    plt.show()
