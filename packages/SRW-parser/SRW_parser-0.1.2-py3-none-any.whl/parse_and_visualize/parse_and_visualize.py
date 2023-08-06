# Parse the data from the dat file -> Points vs Horizontal Position = how many rows per column in the 2D array
#                                  -> Points vs Vertical Position = how many columns in the 2D array

#       Create a dictionary and populate it with other dictionaries based on the data in the dat file
#       Use this data to add to the graph

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.transforms as tf
from xray_vision.backend.mpl.cross_section_2d import CrossSection
from matplotlib import gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable



def get_parameters(d):
    """
    Read in first 10 lines of input file to get parameters for data

    Parameters
    ----------
    d : dictionary
        dictionary that is going to be populated by the parameter data

    """
    with open('res_int_pr_se.dat') as file:
        for i in range(10):
            line = file.readline()
            if '/' in line:
                populate_dictionary(line, d_to_populate = d,
                                    starting_point='[', ending_point=']',
                                    d='intensity', type1='string')
            elif 'Initial Photon' in line:
                populate_dictionary(line, d_to_populate = d,
                                    starting_point='#', ending_point=' ',
                                    d='photon', d1='initial_energy')
                populate_dictionary(line, d_to_populate=d,
                                    starting_point='[', ending_point=']',
                                    d='photon', d1='units', type1='string')
            elif 'Final Photon' in line:
                populate_dictionary(line, d_to_populate = d,
                                    starting_point='#', ending_point=' ',
                                    d='photon', d1='final_energy')
                populate_dictionary(line, d_to_populate = d,
                                    starting_point='[', ending_point=']',
                                    d='photon', d1='units', type1='string')
            elif 'Initial Horizontal' in line:
                populate_dictionary(line, d_to_populate = d,
                                    starting_point='#', ending_point=' ',
                                    d='horizontal', d1='initial_position')
                populate_dictionary(line, d_to_populate=d,
                                    starting_point='l', ending_point=' [',
                                    d='horizontal', d1='axis_label', type1='string')
            elif 'Final Horizontal' in line:
                populate_dictionary(line, d_to_populate = d,
                                    starting_point='#', ending_point=' ',
                                    d='horizontal', d1='final_position')
                populate_dictionary(line, d_to_populate = d,
                                    starting_point='[', ending_point=']',
                                    d='horizontal', d1='units', type1='string')
            elif 'vs Horizontal' in line:
                populate_dictionary(line, d_to_populate = d,
                                    starting_point='#', ending_point=' ',
                                    d='horizontal', d1='points', type1='int')
            elif 'Initial Vertical' in line:
                populate_dictionary(line, d_to_populate = d,
                                    starting_point='#', ending_point=' ',
                                    d='vertical', d1='initial_position')
                populate_dictionary(line, d_to_populate=d,
                                    starting_point='l', ending_point=' [',
                                    d='vertical', d1='axis_label',
                                    type1='string')
            elif 'Final Vertical' in line:
                populate_dictionary(line, d_to_populate = d,
                                    starting_point='#', ending_point=' ',
                                    d='vertical', d1='final_position')
                populate_dictionary(line, d_to_populate = d,
                                    starting_point='[', ending_point=']',
                                    d='vertical', d1='units', type1='string')
            elif 'vs Vertical' in line:
                populate_dictionary(line, d_to_populate = d,
                                    starting_point='#', ending_point=' ',
                                    d='vertical', d1='points', type1='int')


def populate_dictionary(line, d_to_populate, starting_point,
    ending_point, d, d1=None, type1='float'):
    """
    Populate dictionary based on wanting a certain portion of a string

    Parameters
    ----------
    line : string
        string that contains 'substring'
    d_to_populate : dictionary
        first level dictionary to store 'substring'
    starting_point : string
        string character that comes right before 'substring'
    ending_point : string
        string character that comes right after 'substring'
    d : dictionary
        second level dictionary to store 'substring'
    d1 : dictionary
        third level dictionary to store 'substring', optional
    type1 : string
        what type 'substring' is when stored in dictionary

    """
    start = line.find(starting_point) + 1
    end = line.find(ending_point)

    if type1 is 'string':
        substring_value = (line[start:end])
    elif type1 is 'int':
        substring_value = int(line[start:end])
    else:
        substring_value = float(line[start:end])

    #Checks to see if d1 is actually necessary
    if not d1:
        d_to_populate[d] = substring_value
    else:
        d_to_populate[d][d1] = substring_value

def _unit_change(value_to_be_changed, unit):
    """
    Changes value based on given unit
    Parameters
    ----------
    value_to_be_changed : float
        value that is returned once it is changed
    unit : string
        unit the value should be converted to
    """
    if unit is 'micro':
        return value_to_be_changed * 1e6
    elif unit is 'nano':
        return value_to_be_changed * 1e9



def populate_matrix_smart(matrix, horizontal, vertical):
    """
    Reads in all non-commented data from file, parses into 2D array based
    on Horizontal and Vertical Points (using numpy)

    Parameters
    ----------
    matrix : 2D array
        array that will be populated by the data parsed in the input file
    horizontal : int
        # of horizontal rows in matrix
    vertical : int
        # of vertical rows in matrix

    """
    d = np.loadtxt('res_int_pr_se.dat')
    d2 = d.reshape((vertical, horizontal))
    matrix = d2
    return matrix


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Plot image based on input file')
    parser.add_argument('-d', '--dat_file', dest='dat_file', default='',
                        help ='input .dat file')
    parser.add_argument('-vp', '--vert_pos', dest='vert_pos', default='',
                        help='input vertical slice position', type=str)
    parser.add_argument('-hp', '--horiz_pos', dest='horiz_pos', default='',
                        help='input horizontal slice position', type=str)
    parser.add_argument('-vl', '--vert_label', dest='vert_label', default='',
                        help='input vertical label string', type=str)
    parser.add_argument('-hl', '--horiz_label', dest='horiz_label', default='',
                        help='input horizontal label string', type=str)
    parser.add_argument('-e', '--extent_labels', dest='extent_labels', default=None,
                        help='input extent labels for image ranges', nargs='+', type=int)
    args = parser.parse_args()

    initial_data = {'photon': {}, 'horizontal': {}, 'vertical': {},}
    matrix = [[]]

    get_parameters(initial_data)
    horizontal = initial_data['horizontal']['points']
    vertical = initial_data['vertical']['points']

    horizontal_initial = _unit_change(initial_data['horizontal']
                                      ['initial_position'], 'micro')
    horizontal_final = _unit_change(initial_data['horizontal']
                                    ['final_position'], 'micro')
    vertical_initial = _unit_change(initial_data['vertical']
                                    ['initial_position'], 'micro')
    vertical_final = _unit_change(initial_data['vertical']
                                  ['final_position'], 'micro')
    if args.dat_file:
        img = np.loadtxt(args.dat_file)
        img = img.reshape((vertical, horizontal))
        fig = plt.figure()
        kwargs = {'fig': fig}

        if args.vert_pos:
            if args.vert_pos == 'right':
                args.vert_pos = 'right'
            kwargs['vert_loc'] = args.vert_pos

        if args.horiz_pos:
            if args.horiz_pos == 'bottom':
                args.horiz_pos = 'bottom'
            kwargs['horiz_loc'] = args.horiz_pos

        if args.vert_label:
            kwargs['vert_label'] = args.vert_label

        if args.horiz_label:
            kwargs['horiz_label'] = args.horiz_label

        if args.extent_labels:
            kwargs['extent_labels'] = args.extent_labels

        cs = CrossSection(**kwargs)
        cs.update_image(img)
        plt.show()
    else:

        matrix = populate_matrix_smart(matrix, horizontal, vertical)
        fig = plt.figure(figsize=(8, 10))
        title = f'After Propagation (E={initial_data["photon"]["initial_energy"]} {initial_data["photon"]["units"]})'
        axis_data = [initial_data['horizontal']['axis_label'] + " [µm]",
                     initial_data['vertical']['axis_label'] + " [µm]",
                     "Intensity " + initial_data['intensity']]
        cs = CrossSection(fig, horiz_loc= 'top', vert_loc='right', title=title,
                         vert_label=axis_data[1], horiz_label=axis_data[0],
                         extent_labels=[horizontal_initial, horizontal_final, vertical_initial, vertical_final])

        cs.update_image(matrix)
        plt.show()

